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
    
    party_short = 'R' if party in ['REPUBLICAN', 'REP'] else 'D' if party in ['DEMOCRAT', 'DEM'] else party
    return f"{candidate_name} ({party_short})"

def normalize_office_name(office):
    """Normalize office names for file naming"""
    return office.lower().replace(' ', '_').replace('/', '_').replace('and_', '')

def process_county_csv_files_all_offices(year, csv_dir):
    """Process all offices from county CSV files for a given year"""
    print(f"\n=== PROCESSING ALL OFFICES FOR {year} FROM {csv_dir} ===")
    
    if not os.path.exists(csv_dir):
        print(f"Directory {csv_dir} does not exist")
        return []
    
    fips_map = load_fips_mapping()
    
    # Get list of all offices across all files
    offices = set()
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('_precinct.csv')]
    
    if not csv_files:
        print(f"No precinct CSV files found in {csv_dir}")
        return []
    
    print(f"Found {len(csv_files)} county files")
    
    # Scan first file to get offices
    sample_file = os.path.join(csv_dir, csv_files[0])
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                office = row.get('office', '').upper()
                if office and office != 'STRAIGHT PARTY' and office != 'STRAIGHT PARTY 1':
                    offices.add(office)
    except Exception as e:
        print(f"Error reading sample file {sample_file}: {e}")
        return []
    
    print(f"Found offices: {sorted(offices)}")
    
    files_created = []
    
    # Process each office separately
    for office in sorted(offices):
        print(f"\nProcessing {office}...")
        
        office_results = defaultdict(lambda: {
            'county': '',
            'contest': office,
            'year': year,
            'dem_candidate': '',
            'rep_candidate': '',
            'dem_votes': 0,
            'rep_votes': 0,
            'other_votes': 0,
            'total_votes': 0,
            'all_parties': defaultdict(int)
        })
        
        counties_with_data = 0
        
        # Process all county files for this office
        for filename in csv_files:
            csv_path = os.path.join(csv_dir, filename)
            
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        row_office = row.get('office', '').upper()
                        if row_office != office:
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
                            if not office_results[fips]['county']:
                                office_results[fips]['county'] = county_name
                                office_results[fips]['county_fips'] = fips
                            
                            # Add votes by party
                            office_results[fips]['all_parties'][party] += votes
                            office_results[fips]['total_votes'] += votes
                            
                            # Track major party candidates and votes
                            if party in ['DEMOCRAT', 'DEM']:
                                office_results[fips]['dem_votes'] += votes
                                if not office_results[fips]['dem_candidate']:
                                    office_results[fips]['dem_candidate'] = clean_candidate_name(candidate, party)
                            elif party in ['REPUBLICAN', 'REP']:
                                office_results[fips]['rep_votes'] += votes
                                if not office_results[fips]['rep_candidate']:
                                    office_results[fips]['rep_candidate'] = clean_candidate_name(candidate, party)
                            else:
                                office_results[fips]['other_votes'] += votes
                
            except Exception as e:
                print(f"  ❌ Error processing {filename}: {e}")
        
        # Calculate derived fields
        final_results = {}
        
        for fips, data in office_results.items():
            dem_votes = data['dem_votes']
            rep_votes = data['rep_votes']
            two_party_total = dem_votes + rep_votes
            
            if two_party_total > 0:
                counties_with_data += 1
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
        
        # Save results if we have data
        if final_results and counties_with_data >= 40:  # Require data from most counties
            normalized_office = normalize_office_name(office)
            output_file = f'workspace_files/county_results_{year}_{normalized_office}_fips_accurate.json'
            with open(output_file, 'w') as f:
                json.dump(final_results, f, indent=2)
            
            print(f"✅ Saved: {output_file} ({counties_with_data} counties)")
            files_created.append((office, output_file, counties_with_data))
        else:
            print(f"  ⚠️ Insufficient data for {office} ({counties_with_data} counties)")
    
    return files_created

def process_single_csv_all_offices(csv_file, year):
    """Process all offices from a single statewide CSV file"""
    print(f"\n=== PROCESSING ALL OFFICES FOR {year} FROM {csv_file} ===")
    
    if not os.path.exists(csv_file):
        print(f"File {csv_file} does not exist")
        return []
    
    fips_map = load_fips_mapping()
    
    # Get list of all offices
    offices = set()
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                office = row.get('office', '').upper()
                if office and office != 'STRAIGHT PARTY' and office != 'STRAIGHT PARTY 1':
                    offices.add(office)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return []
    
    print(f"Found offices: {sorted(offices)}")
    
    files_created = []
    
    # Process each office separately
    for office in sorted(offices):
        print(f"\nProcessing {office}...")
        
        office_results = defaultdict(lambda: {
            'county': '',
            'contest': office,
            'year': year,
            'dem_candidate': '',
            'rep_candidate': '',
            'dem_votes': 0,
            'rep_votes': 0,
            'other_votes': 0,
            'total_votes': 0,
            'all_parties': defaultdict(int)
        })
        
        counties_with_data = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    row_office = row.get('office', '').upper()
                    if row_office != office:
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
                        if not office_results[fips]['county']:
                            office_results[fips]['county'] = county_name
                            office_results[fips]['county_fips'] = fips
                        
                        # Add votes by party
                        office_results[fips]['all_parties'][party] += votes
                        office_results[fips]['total_votes'] += votes
                        
                        # Track major party candidates and votes
                        if party in ['DEMOCRAT', 'DEM']:
                            office_results[fips]['dem_votes'] += votes
                            if not office_results[fips]['dem_candidate']:
                                office_results[fips]['dem_candidate'] = clean_candidate_name(candidate, party)
                        elif party in ['REPUBLICAN', 'REP']:
                            office_results[fips]['rep_votes'] += votes
                            if not office_results[fips]['rep_candidate']:
                                office_results[fips]['rep_candidate'] = clean_candidate_name(candidate, party)
                        else:
                            office_results[fips]['other_votes'] += votes
        
        except Exception as e:
            print(f"  ❌ Error processing {office}: {e}")
            continue
        
        # Calculate derived fields
        final_results = {}
        
        for fips, data in office_results.items():
            dem_votes = data['dem_votes']
            rep_votes = data['rep_votes']
            two_party_total = dem_votes + rep_votes
            
            if two_party_total > 0:
                counties_with_data += 1
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
        
        # Save results if we have data
        if final_results and counties_with_data >= 40:  # Require data from most counties
            normalized_office = normalize_office_name(office)
            output_file = f'workspace_files/county_results_{year}_{normalized_office}_fips_accurate.json'
            with open(output_file, 'w') as f:
                json.dump(final_results, f, indent=2)
            
            print(f"✅ Saved: {output_file} ({counties_with_data} counties)")
            files_created.append((office, output_file, counties_with_data))
        else:
            print(f"  ⚠️ Insufficient data for {office} ({counties_with_data} counties)")
    
    return files_created

def main():
    print("=== PROCESSING ALL OFFICES FOR ALL MIDTERM YEARS ===\n")
    
    all_files_created = []
    
    # 2022 - From Data/2022/counties directory
    files_2022 = process_county_csv_files_all_offices("2022", "Data/2022/counties")
    all_files_created.extend([(year, office, file, counties) for year in ["2022"] for office, file, counties in files_2022])
    
    # 2018 - From statewide precinct file
    if os.path.exists("Data/20181106__sc__general__precinct.csv"):
        files_2018 = process_single_csv_all_offices("Data/20181106__sc__general__precinct.csv", "2018")
        all_files_created.extend([(year, office, file, counties) for year in ["2018"] for office, file, counties in files_2018])
    
    # 2014 - From Data/2014 directory
    files_2014 = process_county_csv_files_all_offices("2014", "Data/2014")
    all_files_created.extend([(year, office, file, counties) for year in ["2014"] for office, file, counties in files_2014])
    
    # 2006 - Already processed, just list files
    existing_2006_files = []
    for filename in os.listdir('workspace_files'):
        if filename.startswith('county_results_2006_') and filename.endswith('_accurate.json'):
            office = filename.replace('county_results_2006_', '').replace('_fips_accurate.json', '').replace('_', ' ').upper()
            existing_2006_files.append(("2006", office, f'workspace_files/{filename}', 46))
    
    all_files_created.extend(existing_2006_files)
    
    print(f"\n{'='*80}")
    print("COMPREHENSIVE SUMMARY - ALL MIDTERM YEARS")
    print('='*80)
    
    # Group by year
    by_year = defaultdict(list)
    for year, office, file, counties in all_files_created:
        by_year[year].append((office, file, counties))
    
    total_files = 0
    for year in sorted(by_year.keys()):
        files = by_year[year]
        print(f"\n{year} ({len(files)} offices):")
        for office, file, counties in sorted(files):
            filename = file.split('/')[-1] if '/' in file else file.split('\\')[-1]
            print(f"  ✅ {office}: {counties} counties → {filename}")
        total_files += len(files)
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {total_files} accurate office files across all midterm years")
    print('='*80)

if __name__ == "__main__":
    main()