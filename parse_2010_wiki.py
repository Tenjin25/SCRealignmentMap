"""
Parse 2010 statewide office results from Wikipedia and Ballotpedia
Extract county-level data for all statewide executive offices
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import re

# FIPS codes for SC counties
COUNTY_FIPS = {
    "Abbeville": "45001", "Aiken": "45003", "Allendale": "45005", "Anderson": "45007",
    "Bamberg": "45009", "Barnwell": "45011", "Beaufort": "45013", "Berkeley": "45015",
    "Calhoun": "45017", "Charleston": "45019", "Cherokee": "45021", "Chester": "45023",
    "Chesterfield": "45025", "Clarendon": "45027", "Colleton": "45029", "Darlington": "45031",
    "Dillon": "45033", "Dorchester": "45035", "Edgefield": "45037", "Fairfield": "45039",
    "Florence": "45041", "Georgetown": "45043", "Greenville": "45045", "Greenwood": "45047",
    "Hampton": "45049", "Horry": "45051", "Jasper": "45053", "Kershaw": "45055",
    "Lancaster": "45057", "Laurens": "45059", "Lee": "45061", "Lexington": "45063",
    "Marion": "45067", "Marlboro": "45069", "McCormick": "45065", "Newberry": "45071",
    "Oconee": "45073", "Orangeburg": "45075", "Pickens": "45077", "Richland": "45079",
    "Saluda": "45081", "Spartanburg": "45083", "Sumter": "45085", "Union": "45087",
    "Williamsburg": "45089", "York": "45091"
}

def parse_wikipedia_2010():
    """Parse Wikipedia 2010 South Carolina elections page"""
    print("\n📖 Parsing Wikipedia 2010 Elections...")
    
    url = "https://en.wikipedia.org/wiki/2010_South_Carolina_elections"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for sections with office names
        results = {}
        
        # Find all headers
        headers_found = soup.find_all(['h2', 'h3', 'h4'])
        
        for header in headers_found:
            header_text = header.get_text().strip()
            
            # Look for statewide offices
            if any(office in header_text for office in ['Lieutenant Governor', 'Attorney General', 
                                                          'Secretary of State', 'Treasurer',
                                                          'Comptroller', 'Agriculture', 'Superintendent']):
                print(f"  Found section: {header_text}")
                
                # Find the next table after this header
                next_elem = header.find_next('table', class_='wikitable')
                if next_elem:
                    print(f"    ✅ Found table with {len(next_elem.find_all('tr'))} rows")
                    results[header_text] = next_elem
        
        return results
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {}

def extract_county_data_from_table(table, office_name):
    """Extract county-level vote data from a Wikipedia table"""
    print(f"\n  Extracting county data for {office_name}...")
    
    rows = table.find_all('tr')
    
    # Find header row to identify columns
    headers = []
    for row in rows[:3]:  # Check first few rows for headers
        cells = row.find_all(['th', 'td'])
        if cells and any('county' in cell.get_text().lower() for cell in cells):
            headers = [cell.get_text().strip() for cell in cells]
            print(f"    Found headers: {headers[:5]}...")
            break
    
    if not headers:
        print(f"    ⚠️  No county header found, skipping")
        return {}
    
    # Extract data rows
    county_results = {}
    
    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])
        if len(cells) < 2:
            continue
        
        row_data = [cell.get_text().strip() for cell in cells]
        
        # First cell should be county name
        county_name = row_data[0].replace(' County', '').strip()
        
        if county_name in COUNTY_FIPS:
            # Parse vote counts (remove commas, handle percentages)
            votes = []
            for val in row_data[1:]:
                # Remove commas and percentage signs
                clean_val = re.sub(r'[,%]', '', val).strip()
                try:
                    votes.append(int(clean_val))
                except:
                    continue
            
            if votes:
                county_results[county_name] = votes
                print(f"    {county_name}: {votes}")
    
    print(f"  ✅ Extracted {len(county_results)} counties")
    return county_results

def main():
    """Main extraction"""
    print("=" * 80)
    print("PARSING 2010 STATEWIDE OFFICE RESULTS")
    print("=" * 80)
    
    # Parse Wikipedia
    wiki_results = parse_wikipedia_2010()
    
    if wiki_results:
        print(f"\n✅ Found {len(wiki_results)} office sections on Wikipedia")
        
        for office, table in wiki_results.items():
            county_data = extract_county_data_from_table(table, office)
            
            if county_data:
                # Save raw extraction
                output_dir = Path('workspace_files/2010_extraction')
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_file = output_dir / f"{office.replace(' ', '_').lower()}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(county_data, f, indent=2)
                
                print(f"  💾 Saved to {output_file}")
    else:
        print("\n❌ No Wikipedia results found")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
