import csv
import json
import os
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

def clean_candidate_name(candidate_name, party):
    """Clean candidate name format to 'Name (Party)' format"""
    if not candidate_name:
        return candidate_name
    
    # Add standardized party suffix
    party_short = 'R' if party == 'REP' else 'D' if party == 'DEM' else party
    
    return f"{candidate_name} ({party_short})"

def process_csv_to_county_json(csv_file_path, year, contest_type="PRESIDENT"):
    """Process CSV file and create accurate county-level JSON"""
    print(f"Processing {csv_file_path} for {contest_type}...")
    
    fips_map = load_fips_mapping()
    county_results = defaultdict(lambda: {
        'county': '',
        'contest': contest_type,
        'year': year,
        'dem_candidate': '',
        'rep_candidate': '',
        'dem_votes': 0,
        'rep_votes': 0,
        'other_votes': 0,
        'total_votes': 0,
        'all_parties': defaultdict(int)
    })
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                office = row.get('office', '').upper()
                if office != contest_type:
                    continue
                
                county_name = row.get('county', '').upper()
                party = row.get('party', '')
                candidate = row.get('candidate', '')
                votes = int(row.get('votes', 0))
                
                if county_name in fips_map:
                    fips = fips_map[county_name]
                    
                    # Initialize county data
                    if not county_results[fips]['county']:
                        county_results[fips]['county'] = county_name
                        county_results[fips]['county_fips'] = fips
                    
                    # Add votes by party
                    county_results[fips]['all_parties'][party] += votes
                    county_results[fips]['total_votes'] += votes
                    
                    # Track major party candidates and votes
                    if party == 'DEM':
                        county_results[fips]['dem_votes'] += votes
                        if not county_results[fips]['dem_candidate']:
                            county_results[fips]['dem_candidate'] = clean_candidate_name(candidate, party)
                    elif party == 'REP':
                        county_results[fips]['rep_votes'] += votes
                        if not county_results[fips]['rep_candidate']:
                            county_results[fips]['rep_candidate'] = clean_candidate_name(candidate, party)
                    else:
                        county_results[fips]['other_votes'] += votes
        
        # Calculate derived fields for each county
        final_results = {}
        for fips, data in county_results.items():
            dem_votes = data['dem_votes']
            rep_votes = data['rep_votes']
            two_party_total = dem_votes + rep_votes
            
            if two_party_total > 0:
                margin = abs(dem_votes - rep_votes)
                margin_pct = (margin / two_party_total) * 100
                winner = 'DEM' if dem_votes > rep_votes else 'REP'
                
                data.update({
                    'two_party_total': two_party_total,
                    'margin': margin,
                    'margin_pct': margin_pct,
                    'winner': winner,
                    'competitiveness': calculate_competitiveness(dem_votes, rep_votes),
                    'all_parties': dict(data['all_parties'])  # Convert defaultdict to dict
                })
                
                final_results[fips] = data
                
                # Show results for verification
                county_name = data['county']
                dem_pct = (dem_votes / two_party_total) * 100
                rep_pct = (rep_votes / two_party_total) * 100
                comp_category = data['competitiveness']['category']
                comp_party = data['competitiveness']['party']
                
                print(f"  {county_name}: {dem_pct:.1f}% D, {rep_pct:.1f}% R - {comp_category} {comp_party}")
        
        return final_results
        
    except Exception as e:
        print(f"Error processing {csv_file_path}: {e}")
        return {}

def create_accurate_2024_data():
    """Create accurate 2024 Presidential data from CSV files"""
    print("=== CREATING ACCURATE 2024 DATA FROM CSV ===\n")
    
    # Aggregate all 2024 county CSVs
    county_csv_dir = 'Data/2024/counties'
    all_county_data = defaultdict(lambda: {
        'county': '',
        'contest': 'PRESIDENT',
        'year': '2024',
        'dem_candidate': '',
        'rep_candidate': '',
        'dem_votes': 0,
        'rep_votes': 0,
        'other_votes': 0,
        'total_votes': 0,
        'all_parties': defaultdict(int)
    })
    
    fips_map = load_fips_mapping()
    
    # Process each county CSV file
    for filename in os.listdir(county_csv_dir):
        if filename.endswith('_precinct.csv'):
            county_name_from_file = filename.split('__')[3].upper()
            csv_path = os.path.join(county_csv_dir, filename)
            
            print(f"Processing {county_name_from_file}...")
            
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        office = row.get('office', '').upper()
                        if office != 'PRESIDENT':
                            continue
                        
                        county_name = row.get('county', '').upper()
                        party = row.get('party', '')
                        candidate = row.get('candidate', '')
                        votes = int(row.get('votes', 0))
                        
                        if county_name in fips_map:
                            fips = fips_map[county_name]
                            
                            # Initialize county data
                            if not all_county_data[fips]['county']:
                                all_county_data[fips]['county'] = county_name
                                all_county_data[fips]['county_fips'] = fips
                            
                            # Add votes by party
                            all_county_data[fips]['all_parties'][party] += votes
                            all_county_data[fips]['total_votes'] += votes
                            
                            # Track major party candidates and votes
                            if party == 'DEM':
                                all_county_data[fips]['dem_votes'] += votes
                                if not all_county_data[fips]['dem_candidate']:
                                    all_county_data[fips]['dem_candidate'] = clean_candidate_name(candidate, party)
                            elif party == 'REP':
                                all_county_data[fips]['rep_votes'] += votes
                                if not all_county_data[fips]['rep_candidate']:
                                    all_county_data[fips]['rep_candidate'] = clean_candidate_name(candidate, party)
                            else:
                                all_county_data[fips]['other_votes'] += votes
                        
            except Exception as e:
                print(f"  ❌ Error processing {filename}: {e}")
    
    # Calculate derived fields
    final_results = {}
    print(f"\nFinal county results:")
    
    for fips, data in all_county_data.items():
        dem_votes = data['dem_votes']
        rep_votes = data['rep_votes']
        two_party_total = dem_votes + rep_votes
        
        if two_party_total > 0:
            margin = abs(dem_votes - rep_votes)
            margin_pct = (margin / two_party_total) * 100
            winner = 'DEM' if dem_votes > rep_votes else 'REP'
            
            data.update({
                'two_party_total': two_party_total,
                'margin': margin,
                'margin_pct': margin_pct,
                'winner': winner,
                'competitiveness': calculate_competitiveness(dem_votes, rep_votes),
                'all_parties': dict(data['all_parties'])  # Convert defaultdict to dict
            })
            
            final_results[fips] = data
            
            # Show results for key counties
            county_name = data['county']
            dem_pct = (dem_votes / two_party_total) * 100
            rep_pct = (rep_votes / two_party_total) * 100
            comp_category = data['competitiveness']['category']
            comp_party = data['competitiveness']['party']
            
            print(f"  {county_name}: {dem_pct:.1f}% D, {rep_pct:.1f}% R - {comp_category} {comp_party}")
    
    # Save the accurate data
    output_file = 'workspace_files/county_results_2024_fips_accurate.json'
    with open(output_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n✅ Saved accurate 2024 data to: {output_file}")
    
    # Check Greenwood specifically
    if '45047' in final_results:
        greenwood = final_results['45047']
        dem_pct = (greenwood['dem_votes'] / greenwood['two_party_total']) * 100
        rep_pct = (greenwood['rep_votes'] / greenwood['two_party_total']) * 100
        print(f"\n🔍 Greenwood County (accurate from CSV):")
        print(f"   {dem_pct:.1f}% D ({greenwood['dem_votes']:,} votes)")
        print(f"   {rep_pct:.1f}% R ({greenwood['rep_votes']:,} votes)")
        print(f"   Winner: {greenwood['competitiveness']['party']}")
        print(f"   Category: {greenwood['competitiveness']['category']}")
    
    return final_results

def main():
    print("Creating accurate data source directly from CSV files...\n")
    
    # Create accurate 2024 data
    accurate_2024 = create_accurate_2024_data()
    
    print("\n" + "="*60)
    print("COMPARISON WITH PREVIOUS CORRUPTED DATA")
    print("="*60)
    
    # Compare with the corrupted data we identified
    corrupted_counties = ['GREENWOOD', 'FAIRFIELD', 'MCCORMICK']
    
    for county_name in corrupted_counties:
        fips = None
        for f, data in accurate_2024.items():
            if data['county'] == county_name:
                fips = f
                break
        
        if fips:
            accurate_data = accurate_2024[fips]
            dem_pct = (accurate_data['dem_votes'] / accurate_data['two_party_total']) * 100
            rep_pct = (accurate_data['rep_votes'] / accurate_data['two_party_total']) * 100
            
            print(f"\n{county_name} County (FIPS {fips}):")
            print(f"  Accurate from CSV: {dem_pct:.1f}% D, {rep_pct:.1f}% R")
            print(f"  Winner: {accurate_data['competitiveness']['party']}")
            print(f"  Competitiveness: {accurate_data['competitiveness']['category']}")

if __name__ == "__main__":
    main()