import csv
import json
from collections import defaultdict

def load_fips_mapping():
    """Load the FIPS to county name mapping"""
    fips_map = {}
    with open('sc_county_fips.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fips_map[row['county_name'].upper()] = row['county_fips']
    return fips_map

def calculate_competitiveness(dem_votes, rep_votes):
    """Calculate competitiveness category based on vote counts"""
    total_votes = dem_votes + rep_votes
    if total_votes == 0:
        return {"category": "No Data", "party": "None", "color": "#gray"}
    
    dem_pct = (dem_votes / total_votes) * 100
    rep_pct = (rep_votes / total_votes) * 100
    margin = abs(dem_pct - rep_pct)
    
    # Determine winner and competitiveness
    if dem_pct > rep_pct:
        winner_party = "Democratic"
        colors = ["#08519c", "#2171b5", "#4292c6", "#6baed6", "#9ecae1", "#c6dbef", "#deebf7", "#f7fbff"]
    else:
        winner_party = "Republican"
        colors = ["#67000d", "#a50f15", "#cb181d", "#ef3b2c", "#fb6a4a", "#fc9272", "#fcbba1", "#fee0d2"]
    
    # Categorize by margin
    if margin >= 40:
        category = "Annihilation"
        color = colors[0]
    elif margin >= 30:
        category = "Dominant"
        color = colors[1]
    elif margin >= 20:
        category = "Stronghold"
        color = colors[2]
    elif margin >= 10:
        category = "Safe"
        color = colors[3]
    elif margin >= 5.5:
        category = "Likely"
        color = colors[4]
    elif margin >= 1:
        category = "Lean"
        color = colors[5]
    elif margin >= 0.5:
        category = "Tilt"
        color = colors[6]
    else:
        category = "Tossup"
        color = colors[7]
    
    return {
        "category": category,
        "party": winner_party,
        "color": color
    }

def supplement_2008_presidential_data():
    """Supplement 2008 Presidential data using the additional CSV"""
    print("Supplementing 2008 Presidential data with additional CSV source...")
    
    # Load existing 2008 data
    existing_data = {}
    try:
        with open('workspace_files/county_results_2008_fips_accurate.json', 'r') as f:
            existing_data = json.load(f)
        print(f"Loaded existing 2008 data: {len(existing_data)} counties")
    except Exception as e:
        print(f"Error loading existing 2008 data: {e}")
    
    # Load FIPS mapping
    fips_map = load_fips_mapping()
    
    # Load new data from CSV
    new_county_data = defaultdict(lambda: {
        'county': '',
        'contest': 'PRESIDENT',
        'year': '2008',
        'dem_candidate': 'Barack Obama (D)',
        'rep_candidate': 'John McCain (R)',
        'dem_votes': 0,
        'rep_votes': 0,
        'other_votes': 0,
        'total_votes': 0,
        'all_parties': {}
    })
    
    # Process the CSV file
    csv_file = 'SC/Data/election_data_SC.v05_with_county.csv'
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Group by county and sum votes
            county_totals = defaultdict(lambda: {'dem': 0, 'rep': 0, 'total': 0})
            
            for row in reader:
                county_name = row.get('county', '').upper()
                
                # Get 2008 Presidential data
                total_votes = int(row.get('E_08_PRES_Total', 0) or 0)
                dem_votes = int(row.get('E_08_PRES_Dem', 0) or 0)
                rep_votes = int(row.get('E_08_PRES_Rep', 0) or 0)
                
                if county_name and total_votes > 0:
                    county_totals[county_name]['dem'] += dem_votes
                    county_totals[county_name]['rep'] += rep_votes
                    county_totals[county_name]['total'] += total_votes
            
            print(f"Found 2008 data for {len(county_totals)} counties in CSV")
            
            # Convert to our format
            for county_name, votes in county_totals.items():
                if county_name in fips_map:
                    fips = fips_map[county_name]
                    
                    dem_votes = votes['dem']
                    rep_votes = votes['rep']
                    total_votes = votes['total']
                    other_votes = total_votes - dem_votes - rep_votes
                    two_party_total = dem_votes + rep_votes
                    
                    if two_party_total > 0:
                        margin = abs(dem_votes - rep_votes)
                        margin_pct = (margin / two_party_total) * 100
                        winner = 'DEM' if dem_votes > rep_votes else 'REP'
                        
                        new_county_data[fips] = {
                            'county': county_name,
                            'county_fips': fips,
                            'contest': 'PRESIDENT',
                            'year': '2008',
                            'dem_candidate': 'Barack Obama (D)',
                            'rep_candidate': 'John McCain (R)',
                            'dem_votes': dem_votes,
                            'rep_votes': rep_votes,
                            'other_votes': other_votes,
                            'total_votes': total_votes,
                            'two_party_total': two_party_total,
                            'margin': margin,
                            'margin_pct': margin_pct,
                            'winner': winner,
                            'competitiveness': calculate_competitiveness(dem_votes, rep_votes),
                            'all_parties': {
                                'DEM': dem_votes,
                                'REP': rep_votes,
                                'OTHER': other_votes
                            }
                        }
                        
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return False
    
    # Merge existing and new data, prioritizing existing where available
    merged_data = {}
    
    # Start with existing data
    for fips, data in existing_data.items():
        merged_data[fips] = data
        print(f"  ✅ Kept existing: {data.get('county', 'Unknown')} County")
    
    # Add new data for missing counties
    counties_added = 0
    for fips, data in new_county_data.items():
        if fips not in merged_data:
            merged_data[fips] = data
            counties_added += 1
            print(f"  ➕ Added: {data['county']} County")
    
    # Save enhanced data
    output_file = 'workspace_files/county_results_2008_fips_accurate_enhanced.json'
    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=2)
    
    print(f"\n✅ Enhanced 2008 data saved: {output_file}")
    print(f"📊 Total counties: {len(merged_data)} (was {len(existing_data)}, added {counties_added})")
    
    # Replace the original file
    original_file = 'workspace_files/county_results_2008_fips_accurate.json'
    with open(original_file, 'w') as f:
        json.dump(merged_data, f, indent=2)
    
    print(f"🔄 Updated original file: {original_file}")
    
    # Show key counties
    key_counties = [
        ('45047', 'GREENWOOD'),
        ('45069', 'MCCORMICK'), 
        ('45039', 'FAIRFIELD')
    ]
    
    print(f"\n2008 Presidential Results (Key Counties):")
    for fips, county_name in key_counties:
        if fips in merged_data:
            county_data = merged_data[fips]
            dem_votes = county_data['dem_votes']
            rep_votes = county_data['rep_votes']
            total_votes = dem_votes + rep_votes
            
            if total_votes > 0:
                dem_pct = (dem_votes / total_votes) * 100
                rep_pct = (rep_votes / total_votes) * 100
                winner = county_data['competitiveness']['party']
                category = county_data['competitiveness']['category']
                
                print(f"  {county_name}: {dem_pct:.1f}% D, {rep_pct:.1f}% R - {category} {winner}")
        else:
            print(f"  {county_name}: No data found")
    
    return True

if __name__ == "__main__":
    success = supplement_2008_presidential_data()
    if success:
        print("\n2008 Presidential data successfully enhanced!")
    else:
        print("\nFailed to enhance 2008 data.")