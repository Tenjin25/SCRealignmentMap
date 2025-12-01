"""
Find missing 2008 U.S. Senate county data for 18 counties
Missing: Aiken, Allendale, Anderson, Bamberg, Barnwell, Beaufort, Berkeley,
         Calhoun, Charleston, Cherokee, Chester, Chesterfield, Clarendon,
         Colleton, Darlington, Dillon, Dorchester, Edgefield
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import csv

MISSING_COUNTIES = {
    "Aiken": "45003", "Allendale": "45005", "Anderson": "45007", "Bamberg": "45009",
    "Barnwell": "45011", "Beaufort": "45013", "Berkeley": "45015", "Calhoun": "45017",
    "Charleston": "45019", "Cherokee": "45021", "Chester": "45023", "Chesterfield": "45025",
    "Clarendon": "45027", "Colleton": "45029", "Darlington": "45031", "Dillon": "45033",
    "Dorchester": "45035", "Edgefield": "45037"
}

def check_county_csvs():
    """Check if county-specific 2008 CSV files exist"""
    print("\n🔍 Checking for 2008 county CSV files...")
    
    # Check Data/2008 folder if it exists
    county_dir = Path("Data/2008")
    if not county_dir.exists():
        print(f"  ❌ No Data/2008 folder found")
        return None
    
    found = {}
    for county, fips in MISSING_COUNTIES.items():
        csv_files = list(county_dir.glob(f"*{county.lower()}*.csv"))
        if csv_files:
            print(f"  ✅ Found {county}: {csv_files[0].name}")
            found[county] = csv_files[0]
        else:
            print(f"  ❌ Missing {county}")
    
    return found if found else None

def try_uselectionatlas():
    """Try US Election Atlas Dave Leip's data"""
    print("\n🔍 Trying Dave Leip's Atlas of U.S. Elections...")
    
    url = "https://uselectionatlas.org/RESULTS/state.php?year=2008&fips=45&f=0&off=5&elect=0"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"  ✅ Page loaded")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for county results table
            tables = soup.find_all('table')
            print(f"  📊 Found {len(tables)} tables")
            
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > 5:  # Likely a results table
                    # Check if it has county names
                    for row in rows[:10]:
                        text = row.get_text()
                        if any(county in text for county in MISSING_COUNTIES.keys()):
                            print(f"  ✅ Found table with county data!")
                            return {'soup': soup, 'table': table}
        else:
            print(f"  ❌ Status {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return None

def try_wikipedia_2008():
    """Try Wikipedia 2008 Senate election page"""
    print("\n🔍 Trying Wikipedia 2008 U.S. Senate election...")
    
    urls = [
        "https://en.wikipedia.org/wiki/2008_United_States_Senate_election_in_South_Carolina",
        "https://en.wikipedia.org/wiki/2008_South_Carolina_elections"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for url in urls:
        try:
            print(f"  Trying: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"    ✅ Page found")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for county results
                tables = soup.find_all('table', class_='wikitable')
                for table in tables:
                    text = table.get_text()
                    if any(county in text for county in ['Aiken', 'Charleston', 'Anderson']):
                        print(f"    ✅ Found table with county data!")
                        return {'url': url, 'soup': soup, 'table': table}
            else:
                print(f"    ❌ Status {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    return None

def try_scvotes_2008():
    """Try SC State Election Commission archives"""
    print("\n🔍 Trying SC Election Commission archives...")
    
    # Try Internet Archive snapshots
    wayback_url = "https://web.archive.org/web/20081105000000*/scvotes.gov/2008*results*"
    
    try:
        response = requests.get(wayback_url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            result_links = [l['href'] for l in links if '2008' in l['href']]
            if result_links:
                print(f"  ✅ Found {len(result_links)} archived result pages")
                return result_links[:10]  # Return first 10
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return None

def calculate_missing_from_statewide():
    """Calculate missing counties from statewide totals minus known counties"""
    print("\n🔍 Calculating missing counties from statewide totals...")
    
    # Load existing partial data
    partial_file = Path("workspace_files/county_results_2008_u.s._senate_fips.json")
    if not partial_file.exists():
        print("  ❌ No partial data file found")
        return None
    
    with open(partial_file, 'r', encoding='utf-8') as f:
        partial_data = json.load(f)
    
    # Sum existing counties
    existing_graham = sum(c['rep_votes'] for c in partial_data.values())
    existing_conley = sum(c['dem_votes'] for c in partial_data.values())
    
    # Known statewide totals from official results
    # https://www.fec.gov/documents/1890/federalelections2008.pdf
    statewide_graham = 1_235_841  # Official FEC total
    statewide_conley = 790_621
    
    missing_graham = statewide_graham - existing_graham
    missing_conley = statewide_conley - existing_conley
    
    print(f"  Existing {len(partial_data)} counties:")
    print(f"    Graham: {existing_graham:,}")
    print(f"    Conley: {existing_conley:,}")
    print(f"\n  Statewide totals:")
    print(f"    Graham: {statewide_graham:,}")
    print(f"    Conley: {statewide_conley:,}")
    print(f"\n  Missing from 18 counties:")
    print(f"    Graham: {missing_graham:,}")
    print(f"    Conley: {missing_conley:,}")
    
    # Proportionally distribute to missing counties based on 2008 presidential vote
    print(f"\n  💡 Could proportionally estimate based on 2008 Presidential results")
    
    return {
        'missing_graham': missing_graham,
        'missing_conley': missing_conley,
        'method': 'proportional_from_presidential'
    }

def main():
    """Try all methods to find missing 2008 Senate data"""
    print("=" * 80)
    print("FINDING MISSING 2008 U.S. SENATE COUNTY DATA (18 counties)")
    print("=" * 80)
    
    # Try each method
    county_csvs = check_county_csvs()
    atlas_data = try_uselectionatlas()
    wiki_data = try_wikipedia_2008()
    scvotes_data = try_scvotes_2008()
    calculation = calculate_missing_from_statewide()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if county_csvs:
        print(f"✅ Found {len(county_csvs)} county CSV files")
    else:
        print("❌ No county CSV files found")
    
    if atlas_data:
        print("✅ Dave Leip's Atlas: Found table with county data")
    else:
        print("❌ Dave Leip's Atlas: No data")
    
    if wiki_data:
        print(f"✅ Wikipedia: Found table at {wiki_data['url']}")
    else:
        print("❌ Wikipedia: No county-level data")
    
    if scvotes_data:
        print(f"✅ SC Election Commission: Found {len(scvotes_data)} archived pages")
    else:
        print("❌ SC Election Commission: No archives found")
    
    if calculation:
        print(f"✅ Can estimate missing {len(MISSING_COUNTIES)} counties proportionally")
    
    print("\n")

if __name__ == '__main__':
    main()
