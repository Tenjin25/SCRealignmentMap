"""
Extract complete county-level election data from SC ENR JSON files
- 2008 U.S. Senate (Graham vs Conley) - Election ID 8562
- 2010 Statewide offices - Election ID 19077
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

# Missing counties for 2008 Senate (FIPS 45003-45037)
MISSING_2008 = [
    'Aiken', 'Allendale', 'Anderson', 'Bamberg', 'Barnwell', 'Beaufort', 
    'Berkeley', 'Calhoun', 'Charleston', 'Cherokee', 'Chester', 'Chesterfield', 
    'Clarendon', 'Colleton', 'Darlington', 'Dillon', 'Dorchester', 'Edgefield'
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
    # county_path format: /CountyName/12345/index.html
    # Need to get redirect to find contest ID
    
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

def extract_2008_senate(json_data):
    """Extract 2008 U.S. Senate data (Graham vs Conley)"""
    if not json_data or 'Contests' not in json_data:
        return None
    
    # Find U.S. Senate contest
    for contest in json_data['Contests']:
        if contest['C'] == 'U.S. Senate':
            # Check candidates - 2008 had Graham (REP) and Conley (DEM)
            candidates = contest['CH']
            parties = contest['P']
            votes = contest['V']
            
            # Map to candidates
            results = {}
            for i, name in enumerate(candidates):
                if 'Graham' in name:
                    results['Graham'] = votes[i]
                elif 'Conley' in name:
                    results['Conley'] = votes[i]
                else:
                    # Other candidates
                    if 'other' not in results:
                        results['other'] = 0
                    results['other'] += votes[i]
            
            return results
    
    return None

def extract_2010_statewide(json_data):
    """Extract all 2010 statewide office data"""
    if not json_data or 'Contests' not in json_data:
        return None
    
    statewide_offices = [
        'Governor',
        'Lieutenant Governor',
        'Attorney General',
        'Secretary of State',
        'State Treasurer',
        'Comptroller General',
        'Commissioner of Agriculture',
        'Superintendent of Education'
    ]
    
    results = {}
    
    for contest in json_data['Contests']:
        contest_name = contest['C']
        
        if contest_name in statewide_offices:
            candidates = contest['CH']
            parties = contest['P']
            votes = contest['V']
            
            # Store all candidates
            contest_results = {}
            for i, name in enumerate(candidates):
                party = parties[i] if i < len(parties) else 'NON'
                contest_results[name] = {
                    'votes': votes[i],
                    'party': party
                }
            
            results[contest_name] = contest_results
    
    return results if results else None

def main():
    print("=" * 80)
    print("EXTRACTING SC ENR DATA FROM JSON")
    print("=" * 80)
    
    # Extract county links
    print("\n📋 Reading county links...")
    counties_2008 = extract_county_links('workspace_files/enr_downloads/2010_select_county.html')  # 8562 = 2008
    counties_2010 = extract_county_links('workspace_files/enr_downloads/2008_senate_select_county.html')  # 19077 = 2010
    
    print(f"  2008 election: {len(counties_2008)} counties")
    print(f"  2010 election: {len(counties_2010)} counties")
    
    # Extract 2008 U.S. Senate (missing counties only)
    print("\n" + "=" * 80)
    print("2008 U.S. SENATE (Graham vs Conley)")
    print("=" * 80)
    
    results_2008 = {}
    
    for county in MISSING_2008:
        if county not in counties_2008:
            print(f"  ⚠️  {county}: Not in county list")
            continue
        
        print(f"  Fetching {county}...", end=' ')
        
        json_data = get_county_json(county, counties_2008[county])
        if json_data:
            senate_data = extract_2008_senate(json_data)
            if senate_data:
                results_2008[county] = senate_data
                graham = senate_data.get('Graham', 0)
                conley = senate_data.get('Conley', 0)
                print(f"✅ Graham: {graham:,} | Conley: {conley:,}")
            else:
                print("❌ No Senate data")
        else:
            print("❌ Failed to fetch")
        
        time.sleep(0.3)  # Rate limiting
    
    # Save 2008 results
    if results_2008:
        output_dir = Path('workspace_files/enr_scraped')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / '2008_senate_missing.json', 'w') as f:
            json.dump(results_2008, f, indent=2)
        
        print(f"\n💾 Saved {len(results_2008)} counties")
    
    # Extract 2010 statewide (all counties, sample first)
    print("\n" + "=" * 80)
    print("2010 STATEWIDE OFFICES (Sample)")
    print("=" * 80)
    
    sample_counties = ['Abbeville', 'Aiken', 'Allendale']
    results_2010 = {}
    
    for county in sample_counties:
        if county not in counties_2010:
            continue
        
        print(f"\n  Fetching {county}...")
        
        json_data = get_county_json(county, counties_2010[county])
        if json_data:
            statewide_data = extract_2010_statewide(json_data)
            if statewide_data:
                results_2010[county] = statewide_data
                print(f"    ✅ Found {len(statewide_data)} offices")
                for office in statewide_data.keys():
                    print(f"      • {office}")
            else:
                print("    ❌ No statewide data")
        else:
            print("    ❌ Failed to fetch")
        
        time.sleep(0.3)
    
    # Save 2010 sample
    if results_2010:
        output_dir = Path('workspace_files/enr_scraped')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / '2010_statewide_sample.json', 'w') as f:
            json.dump(results_2010, f, indent=2)
        
        print(f"\n💾 Saved {len(results_2010)} sample counties")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if results_2008:
        total_graham = sum(c.get('Graham', 0) for c in results_2008.values())
        total_conley = sum(c.get('Conley', 0) for c in results_2008.values())
        print(f"\n✅ 2008 Senate: {len(results_2008)}/{len(MISSING_2008)} missing counties extracted")
        print(f"   Graham: {total_graham:,} votes")
        print(f"   Conley: {total_conley:,} votes")
    else:
        print("\n❌ 2008 Senate: No data extracted")
    
    if results_2010:
        print(f"\n✅ 2010 Statewide: {len(results_2010)} sample counties")
    
    print()

if __name__ == '__main__':
    main()
