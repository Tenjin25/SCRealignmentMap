"""
Scrape county-level election results from SC ENR system
- 2008 U.S. Senate (Graham vs Conley) - Missing 18 counties
- 2010 Statewide offices (all contests)
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from pathlib import Path
from collections import defaultdict

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

# Missing counties for 2008 Senate
MISSING_2008 = [
    'Aiken', 'Allendale', 'Anderson', 'Bamberg', 'Barnwell', 'Beaufort', 
    'Berkeley', 'Calhoun', 'Charleston', 'Cherokee', 'Chester', 'Chesterfield', 
    'Clarendon', 'Colleton', 'Darlington', 'Dillon', 'Dorchester', 'Edgefield'
]

def extract_county_links(html_file):
    """Extract county links from select-county.html file"""
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    counties = {}
    for link in soup.find_all('a', id=True, value=True):
        county_name = link['id']
        county_path = link['value']
        if county_name and county_path and county_name in FIPS_MAP:
            counties[county_name] = county_path
    
    return counties

def scrape_county_page_2008(county_name, county_path, base_url):
    """Scrape a single county page for 2008 U.S. Senate"""
    full_url = base_url.replace('/40477/en/select-county.html', county_path)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(full_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for U.S. Senate results table
        # ENR pages typically have contest tables with candidate names and vote totals
        results = {}
        
        # Find all tables
        tables = soup.find_all('table')
        
        for table in tables:
            # Look for "U.S. Senate" or "United States Senate" header
            headers = table.find_all(['th', 'td'])
            table_text = ' '.join([h.get_text().strip() for h in headers])
            
            if 'U.S. Senate' in table_text or 'United States Senate' in table_text:
                # Parse candidate rows
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        text = cells[0].get_text().strip()
                        
                        # Look for Graham (REP) and Conley (DEM)
                        if 'Graham' in text or 'GRAHAM' in text:
                            # Extract vote count
                            for cell in cells[1:]:
                                vote_text = cell.get_text().strip().replace(',', '')
                                if vote_text.isdigit():
                                    results['Graham'] = int(vote_text)
                                    break
                        
                        elif 'Conley' in text or 'CONLEY' in text:
                            for cell in cells[1:]:
                                vote_text = cell.get_text().strip().replace(',', '')
                                if vote_text.isdigit():
                                    results['Conley'] = int(vote_text)
                                    break
        
        return results if results else None
        
    except Exception as e:
        print(f"  ❌ Error scraping {county_name}: {e}")
        return None

def scrape_county_page_2010(county_name, county_path, base_url):
    """Scrape a single county page for 2010 statewide offices"""
    full_url = base_url.replace('/15723/en/select-county.html', county_path)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(full_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all contest results
        contests = {}
        
        # Look for statewide offices
        office_patterns = {
            'Governor': ['Governor', 'GOVERNOR'],
            'Lieutenant Governor': ['Lieutenant Governor', 'Lt. Governor', 'LIEUTENANT GOVERNOR'],
            'Attorney General': ['Attorney General', 'ATTORNEY GENERAL'],
            'Secretary of State': ['Secretary of State', 'SECRETARY OF STATE'],
            'State Treasurer': ['State Treasurer', 'Treasurer', 'STATE TREASURER'],
            'Comptroller General': ['Comptroller General', 'COMPTROLLER GENERAL'],
            'Commissioner of Agriculture': ['Commissioner of Agriculture', 'Agriculture', 'COMMISSIONER OF AGRICULTURE'],
            'State Superintendent of Education': ['Superintendent of Education', 'STATE SUPERINTENDENT']
        }
        
        tables = soup.find_all('table')
        
        for table in tables:
            headers = table.find_all(['th', 'td'])
            table_text = ' '.join([h.get_text().strip() for h in headers])
            
            # Check which office this table represents
            for office_name, patterns in office_patterns.items():
                if any(pattern in table_text for pattern in patterns):
                    # Parse candidate votes
                    rows = table.find_all('tr')
                    candidates = {}
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            name_cell = cells[0].get_text().strip()
                            
                            # Extract candidate name and party
                            # Usually format: "Name (PARTY)" or "Name - PARTY"
                            for cell in cells[1:]:
                                vote_text = cell.get_text().strip().replace(',', '')
                                if vote_text.isdigit() and name_cell:
                                    # Store candidate with votes
                                    candidates[name_cell] = int(vote_text)
                                    break
                    
                    if candidates:
                        contests[office_name] = candidates
                    break
        
        return contests if contests else None
        
    except Exception as e:
        print(f"  ❌ Error scraping {county_name}: {e}")
        return None

def main():
    """Main scraping function"""
    print("=" * 80)
    print("SCRAPING SC ENR COUNTY DATA")
    print("=" * 80)
    
    # Extract county links from saved HTML
    print("\n📋 Extracting county links...")
    counties_2008 = extract_county_links('workspace_files/enr_downloads/2008_senate_select_county.html')
    counties_2010 = extract_county_links('workspace_files/enr_downloads/2010_select_county.html')
    
    print(f"  Found {len(counties_2008)} counties for 2008")
    print(f"  Found {len(counties_2010)} counties for 2010")
    
    # Scrape 2008 U.S. Senate (only missing counties)
    print("\n" + "=" * 80)
    print("2008 U.S. SENATE - Missing Counties")
    print("=" * 80)
    
    results_2008 = {}
    base_url_2008 = "https://www.enr-scvotes.org/SC/19077/40477/en/select-county.html"
    
    for county in MISSING_2008:
        if county in counties_2008:
            print(f"\n  Scraping {county}...")
            result = scrape_county_page_2008(county, counties_2008[county], base_url_2008)
            
            if result:
                results_2008[county] = result
                print(f"    ✅ Graham: {result.get('Graham', 0):,} | Conley: {result.get('Conley', 0):,}")
            else:
                print(f"    ⚠️  No data found")
            
            time.sleep(0.5)  # Rate limiting
    
    # Save 2008 results
    if results_2008:
        output_dir = Path('workspace_files/enr_scraped')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / '2008_senate_missing_counties.json', 'w') as f:
            json.dump(results_2008, f, indent=2)
        
        print(f"\n💾 Saved {len(results_2008)} counties to: {output_dir / '2008_senate_missing_counties.json'}")
    
    # Scrape 2010 Statewide (sample first few counties to see structure)
    print("\n" + "=" * 80)
    print("2010 STATEWIDE OFFICES - Sample Counties")
    print("=" * 80)
    
    results_2010 = {}
    base_url_2010 = "https://www.enr-scvotes.org/SC/8562/15723/en/select-county.html"
    
    # Sample first 3 counties to understand structure
    sample_counties = list(counties_2010.keys())[:3]
    
    for county in sample_counties:
        print(f"\n  Scraping {county}...")
        result = scrape_county_page_2010(county, counties_2010[county], base_url_2010)
        
        if result:
            results_2010[county] = result
            print(f"    ✅ Found {len(result)} contests")
            for office, candidates in result.items():
                print(f"      • {office}: {len(candidates)} candidates")
        else:
            print(f"    ⚠️  No data found")
        
        time.sleep(0.5)
    
    # Save 2010 results
    if results_2010:
        output_dir = Path('workspace_files/enr_scraped')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / '2010_statewide_sample.json', 'w') as f:
            json.dump(results_2010, f, indent=2)
        
        print(f"\n💾 Saved sample to: {output_dir / '2010_statewide_sample.json'}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n✅ 2008 Senate: Scraped {len(results_2008)}/{len(MISSING_2008)} missing counties")
    print(f"✅ 2010 Sample: Scraped {len(results_2010)}/3 counties")
    print("\n💡 Next: Parse results and convert to JSON format")
    print()

if __name__ == '__main__':
    main()
