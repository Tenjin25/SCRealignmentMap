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

def clean_candidate_name(candidate_name, party):
    """Clean candidate name format to 'Name (Party)' format"""
    if not candidate_name:
        return candidate_name
    
    party_short = 'R' if party == 'REPUBLICAN' else 'D' if party == 'DEMOCRAT' else party
    return f"{candidate_name} ({party_short})"

def normalize_office_name(office):
    """Normalize office names for file naming"""
    return office.lower().replace(' ', '_').replace('/', '_')

def process_2006_all_offices():
    """Process all 2006 offices from county CSV"""
    print("Processing all 2006 offices...")
    
    fips_map = load_fips_mapping()
    
    # Get list of all offices
    offices = set()
    with open('Data/20061107__sc__general__county.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            office = row.get('office', '').upper()
            if office:
                offices.add(office)
    
    print(f"Found offices: {sorted(offices)}")
    
    files_created = []
    
    # Process each office separately
    for office in sorted(offices):
        print(f"\nProcessing {office}...")
        
        office_results = defaultdict(lambda: {
            'county': '',
            'contest': office,
            'year': '2006',
            'dem_candidate': '',
            'rep_candidate': '',
            'dem_votes': 0,
            'rep_votes': 0,
            'other_votes': 0,
            'total_votes': 0,
            'all_parties': defaultdict(int)
        })
        
        try:
            with open('Data/20061107__sc__general__county.csv', 'r', encoding='utf-8') as f:
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
                        if party == 'DEMOCRAT':
                            office_results[fips]['dem_votes'] += votes
                            if not office_results[fips]['dem_candidate']:
                                office_results[fips]['dem_candidate'] = clean_candidate_name(candidate, party)
                        elif party == 'REPUBLICAN':
                            office_results[fips]['rep_votes'] += votes
                            if not office_results[fips]['rep_candidate']:
                                office_results[fips]['rep_candidate'] = clean_candidate_name(candidate, party)
                        else:
                            office_results[fips]['other_votes'] += votes
            
            # Calculate derived fields
            final_results = {}
            counties_processed = 0
            
            for fips, data in office_results.items():
                dem_votes = data['dem_votes']
                rep_votes = data['rep_votes']
                two_party_total = dem_votes + rep_votes
                
                if two_party_total > 0:
                    counties_processed += 1
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
            if final_results:
                normalized_office = normalize_office_name(office)
                output_file = f'workspace_files/county_results_2006_{normalized_office}_fips_accurate.json'
                with open(output_file, 'w') as f:
                    json.dump(final_results, f, indent=2)
                
                print(f"✅ Saved: {output_file} ({counties_processed} counties)")
                files_created.append((office, output_file, counties_processed))
                
                # Show key counties for major offices
                if office in ['GOVERNOR', 'LIEUTENANT GOVERNOR']:
                    key_counties = [
                        ('45047', 'GREENWOOD'),
                        ('45069', 'MCCORMICK'), 
                        ('45039', 'FAIRFIELD')
                    ]
                    
                    print(f"  Key counties for {office}:")
                    for fips, county_name in key_counties:
                        if fips in final_results:
                            county_data = final_results[fips]
                            dem_votes = county_data['dem_votes']
                            rep_votes = county_data['rep_votes']
                            total_votes = dem_votes + rep_votes
                            
                            if total_votes > 0:
                                dem_pct = (dem_votes / total_votes) * 100
                                rep_pct = (rep_votes / total_votes) * 100
                                winner = county_data['competitiveness']['party']
                                category = county_data['competitiveness']['category']
                                
                                print(f"    {county_name}: {dem_pct:.1f}% D, {rep_pct:.1f}% R - {category} {winner}")
            else:
                print(f"  ⚠️ No data found for {office}")
                
        except Exception as e:
            print(f"  ❌ Error processing {office}: {e}")
    
    return files_created

def main():
    print("=== PROCESSING ALL 2006 OFFICES ===\n")
    
    files_created = process_2006_all_offices()
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Successfully processed {len(files_created)} offices for 2006:")
    
    for office, filename, counties in files_created:
        print(f"  ✅ {office}: {counties} counties → {filename.split('/')[-1]}")
    
    print(f"\n{'='*60}")
    print("TOTAL 2006 FILES CREATED")
    print('='*60)
    total_files = len(files_created)
    print(f"Created {total_files} accurate data files for 2006 election")

if __name__ == "__main__":
    main()