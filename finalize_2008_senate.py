"""
Convert 2008 Senate scraped data to final JSON format and merge with existing data
"""

import json
from pathlib import Path

# FIPS mapping
FIPS_MAP = {
    'Abbeville': '45001', 'Aiken': '45003', 'Allendale': '45005', 'Anderson': '45007',
    'Bamberg': '45009', 'Barnwell': '45011', 'Beaufort': '45013', 'Berkeley': '45015',
    'Calhoun': '45017', 'Charleston': '45019', 'Cherokee': '45021', 'Chester': '45023',
    'Chesterfield': '45025', 'Clarendon': '45027', 'Colleton': '45029', 'Darlington': '45031',
    'Dillon': '45033', 'Dorchester': '45035', 'Edgefield': '45037', 'Fairfield': '45039',
    'Florence': '45041', 'Georgetown': '45043', 'Greenville': '45045', 'Greenwood': '45047',
    'Hampton': '45049', 'Horry': '45051', 'Jasper': '45053', 'Kershaw': '45055',
    'Lancaster': '45057', 'Laurens': '45059', 'Lee': '45061', 'Lexington': '45063',
    'McCormick': '45065', 'Marion': '45067', 'Marlboro': '45069', 'Newberry': '45071',
    'Oconee': '45073', 'Orangeburg': '45075', 'Pickens': '45077', 'Richland': '45079',
    'Saluda': '45081', 'Spartanburg': '45083', 'Sumter': '45085', 'Union': '45087',
    'Williamsburg': '45089', 'York': '45091'
}

def calculate_competitiveness(margin_pct):
    """Determine competitiveness category"""
    abs_margin = abs(margin_pct)
    
    if abs_margin < 5:
        return {"category": "Safe", "party": "Tossup", "color": "#CCCCCC"}
    elif abs_margin < 10:
        if margin_pct > 0:
            return {"category": "Competitive", "party": "Republican", "color": "#FF9999"}
        else:
            return {"category": "Competitive", "party": "Democratic", "color": "#9999FF"}
    elif abs_margin < 20:
        if margin_pct > 0:
            return {"category": "Likely", "party": "Republican", "color": "#FF6666"}
        else:
            return {"category": "Likely", "party": "Democratic", "color": "#6666FF"}
    else:
        if margin_pct > 0:
            return {"category": "Safe", "party": "Republican", "color": "#FF0000"}
        else:
            return {"category": "Safe", "party": "Democratic", "color": "#0000FF"}

def convert_to_final_format(scraped_data):
    """Convert scraped data to final JSON format"""
    final_data = {}
    
    for county_name, results in scraped_data.items():
        fips = FIPS_MAP[county_name]
        
        graham = results.get('Graham', 0)
        conley = results.get('Conley', 0)
        other = results.get('other', 0)
        
        total = graham + conley + other
        margin = graham - conley
        margin_pct = (margin / total * 100) if total > 0 else 0
        
        winner = "REP" if graham > conley else "DEM"
        competitiveness = calculate_competitiveness(margin_pct)
        
        final_data[fips] = {
            "dem_votes": conley,
            "rep_votes": graham,
            "other_votes": other,
            "total_votes": total,
            "all_parties": {
                "REP": graham,
                "DEM": conley
            },
            "margin": margin,
            "margin_pct": round(margin_pct, 2),
            "winner": winner,
            "competitiveness": competitiveness
        }
        
        if other > 0:
            final_data[fips]["all_parties"]["OTH"] = other
    
    return final_data

def merge_with_existing(new_data, existing_file):
    """Merge new data with existing partial data"""
    # Load existing data
    if Path(existing_file).exists():
        with open(existing_file, 'r') as f:
            existing = json.load(f)
    else:
        existing = {}
    
    # Merge
    merged = {**existing, **new_data}
    
    # Sort by FIPS code
    merged = dict(sorted(merged.items()))
    
    return merged

def main():
    print("=" * 80)
    print("CONVERTING 2008 SENATE DATA TO FINAL FORMAT")
    print("=" * 80)
    
    # Load scraped data
    scraped_file = Path('workspace_files/enr_scraped/2008_senate_missing.json')
    with open(scraped_file, 'r') as f:
        scraped_data = json.load(f)
    
    print(f"\n📥 Loaded {len(scraped_data)} counties from scraped data")
    
    # Convert to final format
    final_data = convert_to_final_format(scraped_data)
    
    print(f"✅ Converted to final format")
    
    # Check if we have existing partial data
    existing_file = Path('Data/county_results_2008_u.s._senate_fips_accurate.json')
    
    if existing_file.exists():
        print(f"\n📂 Found existing file: {existing_file}")
        merged_data = merge_with_existing(final_data, existing_file)
        print(f"✅ Merged: {len(merged_data)} total counties")
    else:
        print(f"\n⚠️  No existing file, creating new one")
        merged_data = final_data
    
    # Save final file
    output_file = Path('Data/county_results_2008_u.s._senate_fips_accurate.json')
    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    
    # Calculate totals
    total_graham = sum(c['rep_votes'] for c in merged_data.values())
    total_conley = sum(c['dem_votes'] for c in merged_data.values())
    total_other = sum(c.get('other_votes', 0) for c in merged_data.values())
    total_votes = total_graham + total_conley + total_other
    
    print("\n" + "=" * 80)
    print("FINAL TOTALS")
    print("=" * 80)
    print(f"\nCounties: {len(merged_data)}/46")
    print(f"Graham (REP): {total_graham:,}")
    print(f"Conley (DEM): {total_conley:,}")
    print(f"Other: {total_other:,}")
    print(f"Total: {total_votes:,}")
    print(f"\nMargin: {total_graham - total_conley:,} ({(total_graham - total_conley) / total_votes * 100:.2f}%)")
    
    # Compare to known statewide
    known_graham = 1_235_841
    known_conley = 790_621
    
    print(f"\n📊 Comparison to known statewide:")
    print(f"Graham: {total_graham:,} / {known_graham:,} ({total_graham/known_graham*100:.1f}%)")
    print(f"Conley: {total_conley:,} / {known_conley:,} ({total_conley/known_conley*100:.1f}%)")
    
    if len(merged_data) == 46:
        print(f"\n✅ ALL 46 COUNTIES COMPLETE!")
    else:
        print(f"\n⚠️  Still missing {46 - len(merged_data)} counties")
    
    print()

if __name__ == '__main__':
    main()
