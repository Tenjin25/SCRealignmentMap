"""
Scraper for 2010 South Carolina Governor Election Results
Haley (R) vs Sheheen (D) - Historic first woman governor elected

Data Sources:
1. SC State Election Commission: https://www.scvotes.gov/election-results
2. Ballotpedia: https://ballotpedia.org/South_Carolina_gubernatorial_election,_2010
3. Wikipedia: https://en.wikipedia.org/wiki/2010_South_Carolina_gubernatorial_election
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import re

# FIPS codes for SC counties
SC_COUNTY_FIPS = {
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

def get_competitiveness_category(margin_pct, winner):
    """Determine competitiveness based on margin percentage"""
    if margin_pct >= 40:
        category = "Annihilation"
        colors = {"DEM": "#08519c", "REP": "#67000d"}
    elif margin_pct >= 30:
        category = "Dominant"
        colors = {"DEM": "#2171b5", "REP": "#a50f15"}
    elif margin_pct >= 20:
        category = "Stronghold"
        colors = {"DEM": "#4292c6", "REP": "#cb181d"}
    elif margin_pct >= 10:
        category = "Safe"
        colors = {"DEM": "#6baed6", "REP": "#ef3b2c"}
    elif margin_pct >= 5:
        category = "Likely"
        colors = {"DEM": "#9ecae1", "REP": "#fc9272"}
    elif margin_pct >= 2:
        category = "Lean"
        colors = {"DEM": "#c6dbef", "REP": "#fcbba1"}
    else:
        category = "Tilt"
        colors = {"DEM": "#deebf7", "REP": "#fee5d9"}
    
    party = "Democratic" if winner == "DEM" else "Republican"
    return {
        "category": category,
        "party": party,
        "color": colors[winner]
    }

def create_manual_entry_template():
    """
    Create a template JSON file for manual data entry based on known statewide results.
    2010 SC Governor: Haley (R) 51.4% vs Sheheen (D) 46.9%
    """
    print("\n📝 Creating template for manual data entry...")
    
    template = {}
    
    for county, fips in sorted(SC_COUNTY_FIPS.items()):
        template[fips] = {
            "county": county.upper(),
            "contest": "GOVERNOR",
            "year": "2010",
            "dem_candidate": "Vincent Sheheen (D)",
            "rep_candidate": "Nikki Haley (R)",
            "dem_votes": 0,  # FILL IN
            "rep_votes": 0,  # FILL IN
            "other_votes": 0,  # FILL IN (includes Green, Libertarian, etc.)
            "total_votes": 0,  # FILL IN
            "all_parties": {
                "DEM": 0,
                "REP": 0,
                "GRN": 0,  # Green Party - Morgan Bruce Reeves
                "LIB": 0,  # Libertarian - others
                "": 0  # Write-ins
            },
            "county_fips": fips,
            "two_party_total": 0,  # Will be calculated
            "margin": 0,  # Will be calculated
            "margin_pct": 0.0,  # Will be calculated
            "winner": "UNKNOWN",  # Will be calculated
            "competitiveness": {
                "category": "Unknown",
                "party": "Unknown",
                "color": "#e0e0e0"
            }
        }
    
    output_file = Path('Data/county_results_2010_governor_fips_accurate_TEMPLATE.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Template created: {output_file}")
    print(f"  Contains {len(template)} counties ready for data entry")
    print(f"\n📌 To complete:")
    print(f"  1. Find county-by-county results from SC Election Commission")
    print(f"  2. Fill in the vote counts for each county")
    print(f"  3. Run calculate_and_update() to compute margins and competitiveness")
    print(f"  4. Rename file to remove '_TEMPLATE' suffix")
    
    return output_file

def calculate_and_update_template():
    """
    Calculate margins, percentages, and competitiveness for a filled-in template.
    Run this after manually entering vote data.
    """
    template_file = Path('Data/county_results_2010_governor_fips_accurate_TEMPLATE.json')
    
    if not template_file.exists():
        print(f"❌ Template file not found: {template_file}")
        return
    
    print(f"\n🔢 Calculating margins and competitiveness...")
    
    with open(template_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated_count = 0
    for fips, county_data in data.items():
        dem_votes = county_data['dem_votes']
        rep_votes = county_data['rep_votes']
        
        # Skip if no data entered yet
        if dem_votes == 0 and rep_votes == 0:
            continue
        
        # Calculate fields
        two_party_total = dem_votes + rep_votes
        margin = abs(rep_votes - dem_votes)
        margin_pct = (margin / two_party_total * 100) if two_party_total > 0 else 0
        winner = "REP" if rep_votes > dem_votes else "DEM"
        
        # Update the entry
        county_data['two_party_total'] = two_party_total
        county_data['margin'] = margin
        county_data['margin_pct'] = margin_pct
        county_data['winner'] = winner
        county_data['competitiveness'] = get_competitiveness_category(margin_pct, winner)
        
        # Update all_parties
        county_data['all_parties']['DEM'] = dem_votes
        county_data['all_parties']['REP'] = rep_votes
        
        updated_count += 1
    
    # Write back
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Updated {updated_count} counties with calculated values")
    print(f"  File: {template_file}")

def scrape_wikipedia():
    """
    Attempt to scrape county results from Wikipedia.
    """
    print("\n🌐 Attempting to scrape Wikipedia for 2010 SC Governor results...")
    
    url = "https://en.wikipedia.org/wiki/2010_South_Carolina_gubernatorial_election"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for results tables
        tables = soup.find_all('table', {'class': 'wikitable'})
        
        print(f"  Found {len(tables)} tables on Wikipedia page")
        
        # Try to find county-level results
        for i, table in enumerate(tables):
            # Check if table has county data
            if 'County' in str(table):
                print(f"  Table {i} appears to have county data")
                # This would require custom parsing based on Wikipedia's format
                # For now, just indicate it's available
        
        print(f"  ⚠️ Wikipedia data found but requires manual parsing")
        print(f"  Visit: {url}")
        return None
        
    except Exception as e:
        print(f"  ❌ Error scraping Wikipedia: {e}")
        return None

def print_data_sources():
    """
    Print information about where to find the 2010 Governor election data.
    """
    print("\n" + "="*70)
    print("📊 DATA SOURCES FOR 2010 SC GOVERNOR ELECTION")
    print("="*70)
    print("\n🏛️  OFFICIAL SOURCE (Best):")
    print("   SC State Election Commission")
    print("   https://www.scvotes.gov/election-results")
    print("   → Navigate to: 2010 → General Election → Governor")
    print("   → Download county-by-county Excel/CSV if available")
    
    print("\n📖 ALTERNATIVE SOURCES:")
    print("   1. Ballotpedia:")
    print("      https://ballotpedia.org/South_Carolina_gubernatorial_election,_2010")
    
    print("\n   2. Wikipedia (has county data):")
    print("      https://en.wikipedia.org/wiki/2010_South_Carolina_gubernatorial_election")
    
    print("\n   3. Our Campaigns (historical archive):")
    print("      http://www.ourcampaigns.com/RaceDetail.html?RaceID=559319")
    
    print("\n📈 KNOWN STATEWIDE RESULTS:")
    print("   Nikki Haley (R):     1,041,896 votes (51.4%)")
    print("   Vincent Sheheen (D):   950,683 votes (46.9%)")
    print("   Others:                 35,000 votes (~1.7%)")
    print("   Total:               2,027,579 votes")
    print("\n" + "="*70 + "\n")

def main():
    """Main execution function"""
    print("\n🗳️  2010 SC GOVERNOR ELECTION DATA RETRIEVAL")
    print("   Nikki Haley (R) vs Vincent Sheheen (D)")
    print("   Historic race - First woman governor of SC\n")
    
    # Show data sources
    print_data_sources()
    
    # Try Wikipedia scraping
    scrape_wikipedia()
    
    # Create template
    template_file = create_manual_entry_template()
    
    print("\n" + "="*70)
    print("✅ NEXT STEPS:")
    print("="*70)
    print("1. Visit SC State Election Commission website to get official data")
    print("2. Fill in vote counts in the template file:")
    print(f"   {template_file}")
    print("3. After filling in data, run:")
    print("   python scrape_2010_governor.py --calculate")
    print("4. Rename the file to remove '_TEMPLATE' suffix")
    print("5. Add to git and push!")
    print("="*70 + "\n")

if __name__ == '__main__':
    import sys
    
    if '--calculate' in sys.argv or '-c' in sys.argv:
        calculate_and_update_template()
    else:
        main()
