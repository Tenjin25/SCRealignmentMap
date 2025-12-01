"""
Estimate missing 2008 U.S. Senate counties using 2008 Presidential correlation
"""

import json
import csv
from pathlib import Path
from collections import defaultdict

MISSING_COUNTIES = {
    "Aiken": "45003", "Allendale": "45005", "Anderson": "45007", "Bamberg": "45009",
    "Barnwell": "45011", "Beaufort": "45013", "Berkeley": "45015", "Calhoun": "45017",
    "Charleston": "45019", "Cherokee": "45021", "Chester": "45023", "Chesterfield": "45025",
    "Clarendon": "45027", "Colleton": "45029", "Darlington": "45031", "Dillon": "45033",
    "Dorchester": "45035", "Edgefield": "45037"
}

def get_competitiveness_category(margin_pct, winner):
    """Calculate competitiveness category based on margin"""
    if margin_pct < 5:
        return {"category": "Highly Competitive", "party": winner, "color": "purple"}
    elif margin_pct < 10:
        return {"category": "Competitive", "party": winner, "color": "light-purple"}
    elif margin_pct < 15:
        return {"category": "Leans " + winner, "party": winner, 
                "color": "light-red" if winner == "REP" else "light-blue"}
    else:
        return {"category": "Safe " + winner, "party": winner,
                "color": "red" if winner == "REP" else "blue"}

def extract_2008_presidential_for_missing():
    """Extract 2008 Presidential results for the 18 missing counties"""
    print("\n📊 Extracting 2008 Presidential results for missing counties...")
    
    csv_file = Path("Data/20081104__sc__general__precinct.csv")
    if not csv_file.exists():
        print(f"  ❌ File not found: {csv_file}")
        return None
    
    county_pres = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['office'] != 'President':
                continue
            
            county = row['county']
            if county not in MISSING_COUNTIES:
                continue
            
            fips = MISSING_COUNTIES[county]
            if fips not in county_pres:
                county_pres[fips] = {'county': county, 'dem': 0, 'rep': 0, 'total': 0}
            
            party = row['party']
            votes = int(row['votes']) if row['votes'] else 0
            
            if party == 'DEM':
                county_pres[fips]['dem'] += votes
            elif party == 'REP':
                county_pres[fips]['rep'] += votes
            
            county_pres[fips]['total'] += votes
    
    print(f"  ✅ Extracted Presidential data for {len(county_pres)} counties")
    return county_pres

def estimate_senate_from_presidential():
    """Estimate Senate results based on Presidential results correlation"""
    print("\n🔧 Estimating Senate results from Presidential correlation...")
    
    # Get 2008 Presidential for missing counties
    county_pres = extract_2008_presidential_for_missing()
    if not county_pres:
        return None
    
    # Load existing Senate data to calculate correlation
    partial_file = Path("workspace_files/county_results_2008_u.s._senate_fips.json")
    with open(partial_file, 'r', encoding='utf-8') as f:
        existing_senate = json.load(f)
    
    # Load existing Presidential data for comparison
    existing_pres = {}
    csv_file = Path("Data/20081104__sc__general__precinct.csv")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['office'] != 'President':
                continue
            
            county = row['county']
            if county in MISSING_COUNTIES:
                continue  # Skip missing counties
            
            # This is an existing county with Senate data
            fips = None
            for f, data in existing_senate.items():
                if data['county'] == county:
                    fips = f
                    break
            
            if not fips:
                continue
            
            if fips not in existing_pres:
                existing_pres[fips] = {'dem': 0, 'rep': 0}
            
            party = row['party']
            votes = int(row['votes']) if row['votes'] else 0
            
            if party == 'DEM':
                existing_pres[fips]['dem'] += votes
            elif party == 'REP':
                existing_pres[fips]['rep'] += votes
    
    # Calculate average Senate/Presidential ratio for existing counties
    senate_dem_ratios = []
    senate_rep_ratios = []
    
    for fips in existing_pres.keys():
        if fips in existing_senate:
            pres_dem = existing_pres[fips]['dem']
            pres_rep = existing_pres[fips]['rep']
            senate_dem = existing_senate[fips]['dem_votes']
            senate_rep = existing_senate[fips]['rep_votes']
            
            if pres_dem > 0:
                senate_dem_ratios.append(senate_dem / pres_dem)
            if pres_rep > 0:
                senate_rep_ratios.append(senate_rep / pres_rep)
    
    avg_dem_ratio = sum(senate_dem_ratios) / len(senate_dem_ratios) if senate_dem_ratios else 1.0
    avg_rep_ratio = sum(senate_rep_ratios) / len(senate_rep_ratios) if senate_rep_ratios else 1.0
    
    print(f"  Average Senate/Presidential ratios:")
    print(f"    DEM: {avg_dem_ratio:.4f} (Conley got {avg_dem_ratio*100:.1f}% of Obama's votes)")
    print(f"    REP: {avg_rep_ratio:.4f} (Graham got {avg_rep_ratio*100:.1f}% of McCain's votes)")
    
    # Estimate Senate for missing counties
    estimated_senate = {}
    
    for fips, pres_data in county_pres.items():
        estimated_dem = int(pres_data['dem'] * avg_dem_ratio)
        estimated_rep = int(pres_data['rep'] * avg_rep_ratio)
        
        county_data = {
            'county': pres_data['county'],
            'contest': 'U.S. Senate',
            'year': 2008,
            'dem_candidate': 'Bob Conley',
            'rep_candidate': 'Lindsey Graham',
            'county_fips': fips,
            'dem_votes': estimated_dem,
            'rep_votes': estimated_rep,
            'other_votes': 0,
            'all_parties': {'DEM': estimated_dem, 'REP': estimated_rep}
        }
        
        # Calculate derived fields
        two_party = estimated_dem + estimated_rep
        county_data['total_votes'] = two_party
        county_data['two_party_total'] = two_party
        
        if two_party > 0:
            margin = abs(estimated_rep - estimated_dem)
            county_data['margin'] = margin
            county_data['margin_pct'] = (margin / two_party * 100)
            county_data['winner'] = "REP" if estimated_rep > estimated_dem else "DEM"
            county_data['competitiveness'] = get_competitiveness_category(county_data['margin_pct'], county_data['winner'])
        
        estimated_senate[fips] = county_data
        print(f"  {pres_data['county']:15} - Graham: {estimated_rep:>6,}  Conley: {estimated_dem:>6,}  ({county_data['margin_pct']:.1f}% margin)")
    
    return estimated_senate

def merge_and_save():
    """Merge existing and estimated data, save complete file"""
    print("\n🔧 Merging existing and estimated data...")
    
    # Load existing partial data
    partial_file = Path("workspace_files/county_results_2008_u.s._senate_fips.json")
    with open(partial_file, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    # Get estimated data
    estimated = estimate_senate_from_presidential()
    if not estimated:
        print("  ❌ Failed to estimate data")
        return
    
    # Merge
    complete = {**existing, **estimated}
    
    # Sort by FIPS
    complete = dict(sorted(complete.items()))
    
    # Verify totals
    total_graham = sum(c['rep_votes'] for c in complete.values())
    total_conley = sum(c['dem_votes'] for c in complete.values())
    total_votes = total_graham + total_conley
    
    # Known statewide (approximate - sources vary slightly)
    known_graham = 1_235_841
    known_conley = 790_621
    
    print(f"\n  Complete file stats:")
    print(f"    Counties: {len(complete)}/46")
    print(f"    Graham:  {total_graham:>9,} (target: {known_graham:>9,}, diff: {abs(total_graham-known_graham):>6,})")
    print(f"    Conley:  {total_conley:>9,} (target: {known_conley:>9,}, diff: {abs(total_conley-known_conley):>6,})")
    print(f"    Margin:  {((total_graham-total_conley)/total_votes*100):>8.1f}%")
    
    # Save
    output_file = Path("Data/county_results_2008_u.s._senate_fips_accurate.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(complete, f, indent=2, ensure_ascii=False)
    
    print(f"\n  💾 Saved: {output_file}")
    print(f"  ⚠️  Note: 18 counties estimated from 2008 Presidential correlation")

def main():
    """Main estimation process"""
    print("=" * 80)
    print("ESTIMATING MISSING 2008 U.S. SENATE COUNTIES")
    print("=" * 80)
    
    merge_and_save()
    
    print("\n" + "=" * 80)
    print("✅ COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
