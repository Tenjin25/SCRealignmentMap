"""
Extract complete 2010 statewide office data for all 46 SC counties
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from pathlib import Path

# FIPS code mapping
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

STATEWIDE_OFFICES = [
    'Governor',
    'Lieutenant Governor',
    'Attorney General',
    'Secretary of State',
    'State Treasurer',
    'Comptroller General',
    'Commissioner of Agriculture',
    'State Superintendent of Education'
]

def extract_county_links(html_file):
    """Extract county links from select-county.html"""
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    counties = {}
    for link in soup.find_all('a', id=True, value=True):
        county_name = link['id']
        county_path = link['value']
        if county_name and county_path and county_name in FIPS_MAP:
            counties[county_name] = county_path
    
    return counties

def get_county_json(county_name, county_path):
    """Get JSON data for a county by following redirects"""
    base_url = f"https://www.enr-scvotes.org/SC{county_path}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        # Get redirect page
        r = requests.get(base_url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        
        # Extract contest ID from redirect
        match = re.search(r'URL=\./(\d+)/en/summary\.html', r.text)
        if not match:
            return None
        
        contest_id = match.group(1)
        
        # Build JSON URL
        json_url = base_url.replace('/index.html', f'/{contest_id}/json/sum.json')
        
        # Get JSON
        r2 = requests.get(json_url, headers=headers, timeout=10)
        if r2.status_code == 200:
            return r2.json()
        
        return None
        
    except Exception as e:
        print(f"  ❌ Error for {county_name}: {e}")
        return None

def extract_2010_statewide(json_data):
    """Extract all 2010 statewide office data"""
    if not json_data or 'Contests' not in json_data:
        return None
    
    results = {}
    
    for contest in json_data['Contests']:
        contest_name = contest['C']
        
        if contest_name in STATEWIDE_OFFICES:
            candidates = contest['CH']
            parties = contest['P']
            votes = contest['V']
            
            # Store all candidates with votes and party
            contest_results = {}
            for i, name in enumerate(candidates):
                party = parties[i] if i < len(parties) else 'NON'
                vote_count = votes[i] if i < len(votes) else 0
                
                contest_results[name] = {
                    'votes': vote_count,
                    'party': party
                }
            
            results[contest_name] = contest_results
    
    return results if results else None

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

def convert_office_to_final_format(office_name, county_data):
    """Convert one office's data to final JSON format"""
    final_data = {}
    
    for county_name, candidates in county_data.items():
        fips = FIPS_MAP[county_name]
        
        # Find DEM and REP candidates
        dem_votes = 0
        rep_votes = 0
        other_votes = 0
        all_parties = {}
        
        for candidate_name, info in candidates.items():
            party = info['party']
            votes = info['votes']
            
            if party == 'DEM':
                dem_votes += votes
            elif party == 'REP':
                rep_votes += votes
            else:
                other_votes += votes
            
            # Add to all_parties
            if party not in all_parties:
                all_parties[party] = 0
            all_parties[party] += votes
        
        total_votes = dem_votes + rep_votes + other_votes
        margin = rep_votes - dem_votes
        margin_pct = (margin / total_votes * 100) if total_votes > 0 else 0
        
        winner = "REP" if rep_votes > dem_votes else "DEM"
        competitiveness = calculate_competitiveness(margin_pct)
        
        final_data[fips] = {
            "dem_votes": dem_votes,
            "rep_votes": rep_votes,
            "other_votes": other_votes,
            "total_votes": total_votes,
            "all_parties": all_parties,
            "margin": margin,
            "margin_pct": round(margin_pct, 2),
            "winner": winner,
            "competitiveness": competitiveness
        }
    
    # Sort by FIPS
    return dict(sorted(final_data.items()))

def main():
    print("=" * 80)
    print("EXTRACTING 2010 STATEWIDE OFFICES - ALL COUNTIES")
    print("=" * 80)
    
    # Extract county links (2010 data is in election ID 19077)
    print("\n📋 Reading county links...")
    counties = extract_county_links('workspace_files/enr_downloads/2008_senate_select_county.html')
    
    print(f"  Found {len(counties)} counties")
    
    # Extract all counties
    print("\n" + "=" * 80)
    print("FETCHING DATA FROM ALL COUNTIES")
    print("=" * 80)
    
    all_county_data = {}
    failed_counties = []
    
    for i, (county, path) in enumerate(counties.items(), 1):
        print(f"  [{i:2d}/46] {county:15s} ", end='')
        
        json_data = get_county_json(county, path)
        if json_data:
            statewide_data = extract_2010_statewide(json_data)
            if statewide_data:
                all_county_data[county] = statewide_data
                print(f"✅ {len(statewide_data)} offices")
            else:
                print("❌ No statewide data")
                failed_counties.append(county)
        else:
            print("❌ Failed to fetch")
            failed_counties.append(county)
        
        time.sleep(0.2)  # Rate limiting
    
    print(f"\n✅ Successfully fetched {len(all_county_data)}/46 counties")
    if failed_counties:
        print(f"❌ Failed: {', '.join(failed_counties)}")
    
    # Save raw data
    output_dir = Path('workspace_files/enr_scraped')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / '2010_statewide_all_raw.json', 'w') as f:
        json.dump(all_county_data, f, indent=2)
    
    print(f"\n💾 Saved raw data to: {output_dir / '2010_statewide_all_raw.json'}")
    
    # Reorganize by office
    print("\n" + "=" * 80)
    print("CONVERTING TO FINAL FORMAT BY OFFICE")
    print("=" * 80)
    
    offices_by_county = {}
    for office in STATEWIDE_OFFICES:
        offices_by_county[office] = {}
    
    # Reorganize data: office -> county -> candidates
    for county_name, offices in all_county_data.items():
        for office_name, candidates in offices.items():
            if office_name in offices_by_county:
                offices_by_county[office_name][county_name] = candidates
    
    # Convert each office to final format and save
    data_dir = Path('Data')
    
    for office_name, county_data in offices_by_county.items():
        if not county_data:
            print(f"  ⚠️  {office_name}: No data")
            continue
        
        print(f"\n  {office_name}:")
        print(f"    Counties: {len(county_data)}/46")
        
        # Convert to final format
        final_data = convert_office_to_final_format(office_name, county_data)
        
        # Calculate totals
        total_dem = sum(c['dem_votes'] for c in final_data.values())
        total_rep = sum(c['rep_votes'] for c in final_data.values())
        total_other = sum(c['other_votes'] for c in final_data.values())
        total = total_dem + total_rep + total_other
        margin_pct = (total_rep - total_dem) / total * 100 if total > 0 else 0
        
        print(f"    REP: {total_rep:,} | DEM: {total_dem:,} | Other: {total_other:,}")
        print(f"    Margin: {margin_pct:+.2f}%")
        
        # Save to file
        filename = office_name.lower().replace(' ', '_')
        output_file = data_dir / f'county_results_2010_{filename}_fips_accurate.json'
        
        with open(output_file, 'w') as f:
            json.dump(final_data, f, indent=2)
        
        print(f"    💾 {output_file.name}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n✅ Extracted {len(all_county_data)}/46 counties")
    print(f"✅ Created files for {len([o for o in offices_by_county.values() if o])} offices")
    print()

if __name__ == '__main__':
    main()
