"""
Extract missing federal/presidential races from precinct CSVs:
1. 2008 U.S. Senate (Graham vs Conley)
2. 2012 President (Obama vs Romney)
3. 2016 U.S. Senate (Scott vs Dixon)
4. 2024 President (Trump vs Harris)
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

# FIPS codes for SC counties
COUNTY_FIPS = {
    "Abbeville": "45001", "Aiken": "45003", "Allendale": "45005", "Anderson": "45007",
    "Bamberg": "45009", "Barnwell": "45011", "Beaufort": "45013", "Berkeley": "45015",
    "Calhoun": "45017", "Charleston": "45019", "Cherokee": "45021", "Chester": "45023",
    "Chesterfield": "45025", "Clarendon": "45027", "Colleton": "45029", "Darlington": "45031",
    "Dillon": "45033", "Dorchester": "45035", "Edgefield": "45037", "Fairfield": "45039",
    "Florence": "45041", "Georgetown": "45043", "Greenville": "45045", "Greenwood": "45047",
    "Hampton": "45049", "Horry": "45051", "Jasper": "45053", "Kershaw": "45055",
    "Lancaster": "45057", "Laurens": "45059", "Lee": "45061", "Lexington": "45063",
    "Marion": "45067", "Marlboro": "45069", "McCormick": "45065", "Newberry": "45071",
    "Oconee": "45073", "Orangeburg": "45075", "Pickens": "45077", "Richland": "45079",
    "Saluda": "45081", "Spartanburg": "45083", "Sumter": "45085", "Union": "45087",
    "Williamsburg": "45089", "York": "45091"
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

def extract_2008_senate():
    """Extract 2008 U.S. Senate from precinct CSV"""
    print("\n📊 Extracting 2008 U.S. Senate (Graham vs Conley)...")
    
    csv_file = Path("Data/20081104__sc__general__precinct.csv")
    if not csv_file.exists():
        print(f"  ❌ File not found: {csv_file}")
        return None
    
    county_results = defaultdict(lambda: {
        'county': '', 'contest': 'U.S. Senate', 'year': 2008,
        'dem_candidate': 'Bob Conley', 'rep_candidate': 'Lindsey Graham',
        'dem_votes': 0, 'rep_votes': 0, 'other_votes': 0,
        'all_parties': {}
    })
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['office'] != 'U.S. Senate':
                continue
            
            county = row['county']
            if county not in COUNTY_FIPS:
                continue
            
            fips = COUNTY_FIPS[county]
            party = row['party']
            candidate = row['candidate']
            votes = int(row['votes']) if row['votes'] else 0
            
            county_results[fips]['county'] = county
            county_results[fips]['county_fips'] = fips
            
            if party == 'DEM':
                county_results[fips]['dem_votes'] += votes
            elif party == 'REP':
                county_results[fips]['rep_votes'] += votes
            else:
                county_results[fips]['other_votes'] += votes
            
            if party not in county_results[fips]['all_parties']:
                county_results[fips]['all_parties'][party] = 0
            county_results[fips]['all_parties'][party] += votes
    
    # Calculate derived fields
    for fips, data in county_results.items():
        two_party = data['dem_votes'] + data['rep_votes']
        data['total_votes'] = two_party + data['other_votes']
        data['two_party_total'] = two_party
        
        if two_party > 0:
            margin = abs(data['rep_votes'] - data['dem_votes'])
            data['margin'] = margin
            data['margin_pct'] = (margin / two_party * 100)
            data['winner'] = "REP" if data['rep_votes'] > data['dem_votes'] else "DEM"
            data['competitiveness'] = get_competitiveness_category(data['margin_pct'], data['winner'])
    
    # Sort by FIPS
    sorted_results = dict(sorted(county_results.items()))
    
    print(f"  ✅ Extracted {len(sorted_results)} counties")
    
    # Calculate statewide
    total_dem = sum(d['dem_votes'] for d in sorted_results.values())
    total_rep = sum(d['rep_votes'] for d in sorted_results.values())
    total_votes = total_dem + total_rep
    margin_pct = ((total_rep - total_dem) / total_votes * 100) if total_votes > 0 else 0
    
    print(f"  Graham (R): {total_rep:,} ({total_rep/total_votes*100:.1f}%)")
    print(f"  Conley (D): {total_dem:,} ({total_dem/total_votes*100:.1f}%)")
    print(f"  Margin: {margin_pct:.1f}%")
    
    return sorted_results

def extract_2016_senate():
    """Extract 2016 U.S. Senate from precinct CSV"""
    print("\n📊 Extracting 2016 U.S. Senate (Scott vs Dixon)...")
    
    csv_file = Path("Data/20161108__sc__general__precinct.csv")
    if not csv_file.exists():
        print(f"  ❌ File not found: {csv_file}")
        return None
    
    county_results = defaultdict(lambda: {
        'county': '', 'contest': 'U.S. Senate', 'year': 2016,
        'dem_candidate': 'Thomas Dixon', 'rep_candidate': 'Tim Scott',
        'dem_votes': 0, 'rep_votes': 0, 'other_votes': 0,
        'all_parties': {}
    })
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['office'] != 'U.S. Senate':
                continue
            
            county = row['county']
            if county not in COUNTY_FIPS:
                continue
            
            fips = COUNTY_FIPS[county]
            party = row['party']
            candidate = row['candidate']
            votes = int(row['votes']) if row['votes'] else 0
            
            county_results[fips]['county'] = county
            county_results[fips]['county_fips'] = fips
            
            if party == 'DEM':
                county_results[fips]['dem_votes'] += votes
            elif party == 'REP':
                county_results[fips]['rep_votes'] += votes
            else:
                county_results[fips]['other_votes'] += votes
            
            if party not in county_results[fips]['all_parties']:
                county_results[fips]['all_parties'][party] = 0
            county_results[fips]['all_parties'][party] += votes
    
    # Calculate derived fields
    for fips, data in county_results.items():
        two_party = data['dem_votes'] + data['rep_votes']
        data['total_votes'] = two_party + data['other_votes']
        data['two_party_total'] = two_party
        
        if two_party > 0:
            margin = abs(data['rep_votes'] - data['dem_votes'])
            data['margin'] = margin
            data['margin_pct'] = (margin / two_party * 100)
            data['winner'] = "REP" if data['rep_votes'] > data['dem_votes'] else "DEM"
            data['competitiveness'] = get_competitiveness_category(data['margin_pct'], data['winner'])
    
    # Sort by FIPS
    sorted_results = dict(sorted(county_results.items()))
    
    print(f"  ✅ Extracted {len(sorted_results)} counties")
    
    # Calculate statewide
    total_dem = sum(d['dem_votes'] for d in sorted_results.values())
    total_rep = sum(d['rep_votes'] for d in sorted_results.values())
    total_votes = total_dem + total_rep
    margin_pct = ((total_rep - total_dem) / total_votes * 100) if total_votes > 0 else 0
    
    print(f"  Scott (R): {total_rep:,} ({total_rep/total_votes*100:.1f}%)")
    print(f"  Dixon (D): {total_dem:,} ({total_dem/total_votes*100:.1f}%)")
    print(f"  Margin: {margin_pct:.1f}%")
    
    return sorted_results

def extract_2012_president():
    """Extract 2012 President from county CSVs"""
    print("\n📊 Extracting 2012 President (Obama vs Romney)...")
    
    county_dir = Path("Data/2012")
    if not county_dir.exists():
        print(f"  ❌ Directory not found: {county_dir}")
        return None
    
    county_results = {}
    
    for county_name, fips in sorted(COUNTY_FIPS.items()):
        # Find matching CSV file
        csv_files = list(county_dir.glob(f"*__{county_name.lower()}__*.csv"))
        if not csv_files:
            print(f"  ⚠️  No file found for {county_name}")
            continue
        
        csv_file = csv_files[0]
        
        county_data = {
            'county': county_name, 'contest': 'President', 'year': 2012,
            'dem_candidate': 'Barack Obama', 'rep_candidate': 'Mitt Romney',
            'county_fips': fips,
            'dem_votes': 0, 'rep_votes': 0, 'other_votes': 0,
            'all_parties': {}
        }
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['office'] != 'President':
                    continue
                
                party = row.get('party', '')
                votes = int(row['votes']) if row.get('votes') else 0
                
                if party == 'DEM':
                    county_data['dem_votes'] += votes
                elif party == 'REP':
                    county_data['rep_votes'] += votes
                else:
                    county_data['other_votes'] += votes
                
                if party:
                    if party not in county_data['all_parties']:
                        county_data['all_parties'][party] = 0
                    county_data['all_parties'][party] += votes
        
        # Calculate derived fields
        two_party = county_data['dem_votes'] + county_data['rep_votes']
        county_data['total_votes'] = two_party + county_data['other_votes']
        county_data['two_party_total'] = two_party
        
        if two_party > 0:
            margin = abs(county_data['rep_votes'] - county_data['dem_votes'])
            county_data['margin'] = margin
            county_data['margin_pct'] = (margin / two_party * 100)
            county_data['winner'] = "REP" if county_data['rep_votes'] > county_data['dem_votes'] else "DEM"
            county_data['competitiveness'] = get_competitiveness_category(county_data['margin_pct'], county_data['winner'])
        
        county_results[fips] = county_data
    
    print(f"  ✅ Extracted {len(county_results)} counties")
    
    # Calculate statewide
    total_dem = sum(d['dem_votes'] for d in county_results.values())
    total_rep = sum(d['rep_votes'] for d in county_results.values())
    total_votes = total_dem + total_rep
    margin_pct = ((total_rep - total_dem) / total_votes * 100) if total_votes > 0 else 0
    
    print(f"  Romney (R): {total_rep:,} ({total_rep/total_votes*100:.1f}%)")
    print(f"  Obama (D): {total_dem:,} ({total_dem/total_votes*100:.1f}%)")
    print(f"  Margin: {margin_pct:.1f}%")
    
    return county_results

def extract_2024_president():
    """Extract 2024 President from county CSVs"""
    print("\n📊 Extracting 2024 President (Trump vs Harris)...")
    
    county_dir = Path("Data/2024/counties")
    if not county_dir.exists():
        print(f"  ❌ Directory not found: {county_dir}")
        return None
    
    county_results = {}
    
    for county_name, fips in sorted(COUNTY_FIPS.items()):
        # Find matching CSV file
        csv_files = list(county_dir.glob(f"*__{county_name.lower()}__*.csv"))
        if not csv_files:
            print(f"  ⚠️  No file found for {county_name}")
            continue
        
        csv_file = csv_files[0]
        
        county_data = {
            'county': county_name, 'contest': 'President', 'year': 2024,
            'dem_candidate': 'Kamala Harris', 'rep_candidate': 'Donald Trump',
            'county_fips': fips,
            'dem_votes': 0, 'rep_votes': 0, 'other_votes': 0,
            'all_parties': {}
        }
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['office'] != 'President':
                    continue
                
                candidate = row.get('candidate', '')
                votes = int(row['votes']) if row.get('votes') else 0
                
                # Determine party from candidate name
                if 'Trump' in candidate or 'Donald J Trump' in candidate:
                    county_data['rep_votes'] += votes
                    party = 'REP'
                elif 'Harris' in candidate or 'Kamala' in candidate:
                    county_data['dem_votes'] += votes
                    party = 'DEM'
                else:
                    county_data['other_votes'] += votes
                    party = 'OTH'
                
                if party not in county_data['all_parties']:
                    county_data['all_parties'][party] = 0
                county_data['all_parties'][party] += votes
        
        # Calculate derived fields
        two_party = county_data['dem_votes'] + county_data['rep_votes']
        county_data['total_votes'] = two_party + county_data['other_votes']
        county_data['two_party_total'] = two_party
        
        if two_party > 0:
            margin = abs(county_data['rep_votes'] - county_data['dem_votes'])
            county_data['margin'] = margin
            county_data['margin_pct'] = (margin / two_party * 100)
            county_data['winner'] = "REP" if county_data['rep_votes'] > county_data['dem_votes'] else "DEM"
            county_data['competitiveness'] = get_competitiveness_category(county_data['margin_pct'], county_data['winner'])
        
        county_results[fips] = county_data
    
    print(f"  ✅ Extracted {len(county_results)} counties")
    
    # Calculate statewide
    total_dem = sum(d['dem_votes'] for d in county_results.values())
    total_rep = sum(d['rep_votes'] for d in county_results.values())
    total_votes = total_dem + total_rep
    margin_pct = ((total_rep - total_dem) / total_votes * 100) if total_votes > 0 else 0
    
    print(f"  Trump (R): {total_rep:,} ({total_rep/total_votes*100:.1f}%)")
    print(f"  Harris (D): {total_dem:,} ({total_dem/total_votes*100:.1f}%)")
    print(f"  Margin: {margin_pct:.1f}%")
    
    return county_results

def main():
    """Extract all missing federal/presidential races"""
    print("=" * 80)
    print("EXTRACTING MISSING FEDERAL/PRESIDENTIAL RACES")
    print("=" * 80)
    
    # Extract each race
    senate_2008 = extract_2008_senate()
    president_2012 = extract_2012_president()
    senate_2016 = extract_2016_senate()
    president_2024 = extract_2024_president()
    
    # Save results
    data_dir = Path("Data")
    
    if senate_2008:
        output_file = data_dir / "county_results_2008_u.s._senate_fips_accurate.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(senate_2008, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved: {output_file}")
    
    if president_2012:
        output_file = data_dir / "county_results_2012_president_fips_accurate.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(president_2012, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved: {output_file}")
    
    if senate_2016:
        output_file = data_dir / "county_results_2016_u.s._senate_fips_accurate.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(senate_2016, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved: {output_file}")
    
    if president_2024:
        output_file = data_dir / "county_results_2024_president_fips_accurate.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(president_2024, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved: {output_file}")
    
    print("\n" + "=" * 80)
    print("✅ EXTRACTION COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
