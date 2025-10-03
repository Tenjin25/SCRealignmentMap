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
    
    party_short = 'R' if party == 'REP' else 'D' if party == 'DEM' else party
    return f"{candidate_name} ({party_short})"

def process_individual_county_csvs(year_date, contest_office="PRESIDENT"):
    """Process individual county CSV files for a given year (from Data directory root)"""
    print(f"\n=== PROCESSING {year_date} {contest_office} ===")
    
    fips_map = load_fips_mapping()
    all_county_data = defaultdict(lambda: {
        'county': '',
        'contest': contest_office,
        'year': year_date[:4],  # Extract year from date
        'dem_candidate': '',
        'rep_candidate': '',
        'dem_votes': 0,
        'rep_votes': 0,
        'other_votes': 0,
        'total_votes': 0,
        'all_parties': defaultdict(int)
    })
    
    csv_files_found = 0
    
    # Look for individual county files in Data directory root
    data_dir = "Data"
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.startswith(year_date) and '__precinct.csv' in filename and '__general__' in filename:
                parts = filename.split('__')
                if len(parts) >= 4 and parts[3] != 'precinct':  # Has county name
                    csv_files_found += 1
                    county_name_from_file = parts[3].upper()
                    csv_path = os.path.join(data_dir, filename)
                    
                    try:
                        with open(csv_path, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            
                            for row in reader:
                                office = row.get('office', '').upper()
                                if office != contest_office.upper():
                                    continue
                                
                                county_name = row.get('county', '').upper()
                                party = row.get('party', '')
                                candidate = row.get('candidate', '')
                                votes_str = row.get('votes', '0')
                                
                                # Handle empty vote counts
                                try:
                                    votes = int(votes_str) if votes_str else 0
                                except ValueError:
                                    votes = 0
                                
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
    
    print(f"Processed {csv_files_found} county CSV files")
    
    # Calculate derived fields
    final_results = {}
    
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
                'all_parties': dict(data['all_parties'])
            })
            
            final_results[fips] = data
    
    return final_results, csv_files_found > 0

def process_county_csv_files(year, csv_dir, contest_office="PRESIDENT"):
    """Process all county CSV files for a given year (from subdirectory)"""
    print(f"\n=== PROCESSING {year} {contest_office} FROM {csv_dir} ===")
    
    fips_map = load_fips_mapping()
    all_county_data = defaultdict(lambda: {
        'county': '',
        'contest': contest_office,
        'year': year,
        'dem_candidate': '',
        'rep_candidate': '',
        'dem_votes': 0,
        'rep_votes': 0,
        'other_votes': 0,
        'total_votes': 0,
        'all_parties': defaultdict(int)
    })
    
    csv_files_found = 0
    
    if os.path.exists(csv_dir):
        for filename in os.listdir(csv_dir):
            if filename.endswith('_precinct.csv') or filename.endswith('__precinct.csv'):
                csv_files_found += 1
                # Handle different filename patterns
                if '__' in filename:
                    parts = filename.split('__')
                    if len(parts) >= 4:
                        county_name_from_file = parts[3].upper()
                else:
                    county_name_from_file = filename.split('_')[0].upper()
                
                csv_path = os.path.join(csv_dir, filename)
                
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        
                        for row in reader:
                            office = row.get('office', '').upper()
                            if office != contest_office.upper():
                                continue
                            
                            county_name = row.get('county', '').upper()
                            party = row.get('party', '')
                            candidate = row.get('candidate', '')
                            votes_str = row.get('votes', '0')
                            
                            # Handle empty vote counts
                            try:
                                votes = int(votes_str) if votes_str else 0
                            except ValueError:
                                votes = 0
                            
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
    
    print(f"Processed {csv_files_found} county CSV files")
    
    # Calculate derived fields
    final_results = {}
    
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
                'all_parties': dict(data['all_parties'])
            })
            
            final_results[fips] = data
    
    return final_results, csv_files_found > 0

def process_single_county_csv(csv_file_path, year, contest_office="PRESIDENT"):
    """Process a single county-level CSV file"""
    print(f"\nProcessing {csv_file_path}...")
    
    fips_map = load_fips_mapping()
    county_results = defaultdict(lambda: {
        'county': '',
        'contest': contest_office,
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
                if office != contest_office.upper():
                    continue
                
                county_name = row.get('county', '').upper()
                party = row.get('party', '')
                candidate = row.get('candidate', '')
                votes_str = row.get('votes', '0')
                
                # Handle empty vote counts
                try:
                    votes = int(votes_str) if votes_str else 0
                except ValueError:
                    votes = 0
                
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
        
        # Calculate derived fields
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
                    'all_parties': dict(data['all_parties'])
                })
                
                final_results[fips] = data
        
        return final_results, True
        
    except Exception as e:
        print(f"Error processing {csv_file_path}: {e}")
        return {}, False

def create_all_accurate_data():
    """Create accurate data for all available years"""
    print("=== CREATING ACCURATE DATA FOR ALL YEARS FROM CSV ===\n")
    
    # Track what we process
    years_processed = []
    
    # 2024 - From Data/2024/counties directory
    results_2024, success = process_county_csv_files("2024", "Data/2024/counties", "PRESIDENT")
    if success and results_2024:
        output_file = 'workspace_files/county_results_2024_fips_accurate.json'
        with open(output_file, 'w') as f:
            json.dump(results_2024, f, indent=2)
        print(f"✅ Saved: {output_file}")
        years_processed.append("2024 Presidential")
    else:
        # Try individual county files
        results_2024, success = process_individual_county_csvs("20241105", "PRESIDENT")
        if success and results_2024:
            output_file = 'workspace_files/county_results_2024_fips_accurate.json'
            with open(output_file, 'w') as f:
                json.dump(results_2024, f, indent=2)
            print(f"✅ Saved: {output_file}")
            years_processed.append("2024 Presidential")
    
    # 2022 - From Data/2022/counties directory or individual files
    results_2022, success = process_county_csv_files("2022", "Data/2022/counties", "Governor and Lieutenant Governor")
    if success and results_2022:
        output_file = 'workspace_files/county_results_2022_fips_accurate.json'
        with open(output_file, 'w') as f:
            json.dump(results_2022, f, indent=2)
        print(f"✅ Saved: {output_file}")
        years_processed.append("2022 Governor")
    else:
        # Try individual county files
        results_2022, success = process_individual_county_csvs("20221108", "Governor and Lieutenant Governor")
        if success and results_2022:
            output_file = 'workspace_files/county_results_2022_fips_accurate.json'
            with open(output_file, 'w') as f:
                json.dump(results_2022, f, indent=2)
            print(f"✅ Saved: {output_file}")
            years_processed.append("2022 Governor")
    
    # 2020 - Try individual county files first
    results_2020, success = process_individual_county_csvs("20201103", "PRESIDENT")
    if success and results_2020:
        output_file = 'workspace_files/county_results_2020_fips_accurate.json'
        with open(output_file, 'w') as f:
            json.dump(results_2020, f, indent=2)
        print(f"✅ Saved: {output_file}")
        years_processed.append("2020 Presidential")
    
    # 2018 - Try individual county files first
    results_2018, success = process_individual_county_csvs("20181106", "Governor and Lieutenant Governor")
    if success and results_2018:
        output_file = 'workspace_files/county_results_2018_fips_accurate.json'
        with open(output_file, 'w') as f:
            json.dump(results_2018, f, indent=2)
        print(f"✅ Saved: {output_file}")
        years_processed.append("2018 Governor")
    else:
        # Try statewide precinct file
        if os.path.exists("Data/20181106__sc__general__precinct.csv"):
            results_2018, success = process_single_county_csv("Data/20181106__sc__general__precinct.csv", "2018", "Governor and Lieutenant Governor")
            if success and results_2018:
                output_file = 'workspace_files/county_results_2018_fips_accurate.json'
                with open(output_file, 'w') as f:
                    json.dump(results_2018, f, indent=2)
                print(f"✅ Saved: {output_file}")
                years_processed.append("2018 Governor")
    
    # 2016 - Try statewide precinct file
    if os.path.exists("Data/20161108__sc__general__precinct.csv"):
        results_2016, success = process_single_county_csv("Data/20161108__sc__general__precinct.csv", "2016", "PRESIDENT")
        if success and results_2016:
            output_file = 'workspace_files/county_results_2016_fips_accurate.json'
            with open(output_file, 'w') as f:
                json.dump(results_2016, f, indent=2)
            print(f"✅ Saved: {output_file}")
            years_processed.append("2016 Presidential")
    
    # 2014 - Try files in Data/2014 directory
    results_2014, success = process_county_csv_files("2014", "Data/2014", "Governor")
    if success and results_2014:
        output_file = 'workspace_files/county_results_2014_fips_accurate.json'
        with open(output_file, 'w') as f:
            json.dump(results_2014, f, indent=2)
        print(f"✅ Saved: {output_file}")
        years_processed.append("2014 Governor")
    
    # 2012 - Try files in Data/2012 directory
    results_2012, success = process_county_csv_files("2012", "Data/2012", "PRESIDENT")
    if success and results_2012:
        output_file = 'workspace_files/county_results_2012_fips_accurate.json'
        with open(output_file, 'w') as f:
            json.dump(results_2012, f, indent=2)
        print(f"✅ Saved: {output_file}")
        years_processed.append("2012 Presidential")
    
    # 2008 - Try statewide precinct file
    if os.path.exists("Data/20081104__sc__general__precinct.csv"):
        results_2008, success = process_single_county_csv("Data/20081104__sc__general__precinct.csv", "2008", "PRESIDENT")
        if success and results_2008:
            output_file = 'workspace_files/county_results_2008_fips_accurate.json'
            with open(output_file, 'w') as f:
                json.dump(results_2008, f, indent=2)
            print(f"✅ Saved: {output_file}")
            years_processed.append("2008 Presidential")
    
    # 2006 - Try county-level CSV with better error handling
    if os.path.exists("Data/20061107__sc__general__county.csv"):
        results_2006, success = process_single_county_csv("Data/20061107__sc__general__county.csv", "2006", "GOVERNOR")
        if success and results_2006:
            output_file = 'workspace_files/county_results_2006_fips_accurate.json'
            with open(output_file, 'w') as f:
                json.dump(results_2006, f, indent=2)
            print(f"✅ Saved: {output_file}")
            years_processed.append("2006 Governor")
    
    return years_processed

def check_key_counties_across_years():
    """Check key counties across all accurate data files"""
    print(f"\n{'='*60}")
    print("KEY COUNTIES COMPARISON (CSV vs Previously Corrupted Data)")
    print('='*60)
    
    key_counties = [
        ('45047', 'GREENWOOD'),
        ('45069', 'MCCORMICK'), 
        ('45039', 'FAIRFIELD')
    ]
    
    # Check available accurate files
    accurate_files = []
    for filename in os.listdir('workspace_files'):
        if filename.startswith('county_results_') and filename.endswith('_accurate.json'):
            year = filename.split('_')[2]
            election_type = "Presidential" if "2024" in filename or "2020" in filename or "2016" in filename or "2012" in filename else "Governor"
            accurate_files.append((f'workspace_files/{filename}', f'{year} {election_type}'))
    
    for fips, county_name in key_counties:
        print(f"\n🔍 {county_name} County ({fips}):")
        
        for file_path, election in accurate_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if fips in data:
                    county_data = data[fips]
                    dem_votes = county_data['dem_votes']
                    rep_votes = county_data['rep_votes']
                    total_votes = dem_votes + rep_votes
                    
                    if total_votes > 0:
                        dem_pct = (dem_votes / total_votes) * 100
                        rep_pct = (rep_votes / total_votes) * 100
                        winner = county_data['competitiveness']['party']
                        category = county_data['competitiveness']['category']
                        
                        print(f"  {election}: {dem_pct:.1f}% D, {rep_pct:.1f}% R - {category} {winner}")
                
            except Exception as e:
                print(f"  {election}: Error loading - {e}")

def main():
    print("Creating accurate data from CSV sources for all available years...\n")
    
    # Create accurate data for all years
    years_processed = create_all_accurate_data()
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Successfully processed {len(years_processed)} elections:")
    for year in years_processed:
        print(f"  ✅ {year}")
    
    # Check key counties across years
    check_key_counties_across_years()
    
    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print('='*60)
    print("1. Update sc_results_index_corrected.json to reference *_accurate.json files")
    print("2. Test the map with accurate CSV-based data")
    print("3. Verify all corruption issues are resolved")

if __name__ == "__main__":
    main()