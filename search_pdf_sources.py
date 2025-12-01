"""
Search for and scrape SC election result PDFs for:
- 2008 U.S. Senate (missing counties)
- 2010 statewide offices (all contests)
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from pathlib import Path

def search_scvotes_wayback():
    """Search Internet Archive for SC Election Commission PDFs"""
    print("\n🔍 Searching Internet Archive for SC Election Commission PDFs...")
    
    # Search for 2008 and 2010 results pages
    searches = [
        "https://web.archive.org/web/2008*/scvotes.gov/*results*",
        "https://web.archive.org/web/2010*/scvotes.gov/*results*",
        "https://web.archive.org/web/2008*/scvotes.org/*results*",
        "https://web.archive.org/web/2010*/scvotes.org/*results*",
    ]
    
    found_urls = []
    
    for search_url in searches:
        try:
            print(f"  Searching: {search_url}")
            response = requests.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                # Look for PDF links or results pages
                for link in links:
                    href = link['href']
                    if '.pdf' in href.lower() or 'result' in href.lower():
                        if 'web.archive.org' in href:
                            found_urls.append(href)
                            print(f"    ✅ Found: {href[:100]}...")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        time.sleep(1)  # Be nice to Archive
    
    return list(set(found_urls))  # Remove duplicates

def search_county_sites():
    """Search individual county election office websites"""
    print("\n🔍 Searching county election office websites...")
    
    # Priority counties with missing 2008 Senate data
    priority_counties = [
        ("Aiken", "https://www.aikencountysc.gov/government/voter-registration-elections"),
        ("Charleston", "https://www.charlestoncounty.org/departments/board-of-voter-registration-and-elections"),
        ("Anderson", "https://www.andersoncountysc.org/voter-registration-and-elections"),
        ("Beaufort", "https://www.bcgov.net/departments/board-of-elections-and-voter-registration"),
        ("Berkeley", "https://www.berkeleycountysc.gov/government/departments/voter-registration-elections"),
    ]
    
    found_pdfs = []
    
    for county, url in priority_counties:
        try:
            print(f"  Checking {county}...")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link['href']
                    text = link.get_text().lower()
                    
                    # Look for 2008/2010 results PDFs
                    if ('.pdf' in href.lower() and 
                        ('2008' in text or '2010' in text or '2008' in href or '2010' in href) and
                        ('result' in text or 'election' in text)):
                        
                        full_url = href if href.startswith('http') else url.rsplit('/', 2)[0] + href
                        found_pdfs.append((county, full_url))
                        print(f"    ✅ Found PDF: {text[:50]}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        time.sleep(2)  # Be respectful
    
    return found_pdfs

def search_scvotes_direct():
    """Try direct SC Election Commission URLs"""
    print("\n🔍 Trying direct SC Election Commission URLs...")
    
    # Common patterns for SC election result PDFs
    base_urls = [
        "https://www.scvotes.gov/sites/default/files/",
        "https://scvotes.gov/election-results/",
        "https://www.scvotes.org/",
    ]
    
    patterns = [
        "2008_general_election_results.pdf",
        "2010_general_election_results.pdf",
        "2008_November_General_Results.pdf",
        "2010_November_General_Results.pdf",
        "StatewideResultsDetail2008.pdf",
        "StatewideResultsDetail2010.pdf",
        "county_results_2008.pdf",
        "county_results_2010.pdf",
    ]
    
    found = []
    
    for base in base_urls:
        for pattern in patterns:
            url = base + pattern
            try:
                print(f"  Trying: {url}")
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    print(f"    ✅ FOUND: {url}")
                    found.append(url)
            except:
                pass
    
    return found

def search_ballotpedia_sources():
    """Check Ballotpedia citation sources for result PDFs"""
    print("\n🔍 Checking Ballotpedia sources...")
    
    pages = [
        "https://ballotpedia.org/United_States_Senate_election_in_South_Carolina,_2008",
        "https://ballotpedia.org/South_Carolina_gubernatorial_election,_2010",
        "https://ballotpedia.org/South_Carolina_elections,_2010",
    ]
    
    found_sources = []
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for page_url in pages:
        try:
            print(f"  Checking: {page_url}")
            response = requests.get(page_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for citation/reference links
                refs = soup.find_all(['a', 'cite'], href=True)
                for ref in refs:
                    href = ref.get('href', '')
                    if '.pdf' in href.lower() and ('result' in href.lower() or 'election' in href.lower()):
                        found_sources.append(href)
                        print(f"    ✅ Found source: {href[:80]}")
                
                # Look for "References" or "Sources" section
                sections = soup.find_all(['div', 'section'], class_=re.compile('reference|source', re.I))
                for section in sections:
                    links = section.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        if 'scvotes' in href.lower() or '.pdf' in href.lower():
                            found_sources.append(href)
                            print(f"    ✅ Found: {href[:80]}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        time.sleep(1)
    
    return list(set(found_sources))

def search_mit_dataverse():
    """Check MIT Election Lab for county-level data files"""
    print("\n🔍 Checking MIT Election Lab / Harvard Dataverse...")
    
    # MIT Election Lab dataset URLs
    urls = [
        "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VOQCHQ",  # County returns
        "https://electionlab.mit.edu/data",
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    found_datasets = []
    
    for url in urls:
        try:
            print(f"  Checking: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for download links
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    text = link.get_text().lower()
                    
                    if ('download' in href.lower() or 'access' in href.lower()) and \
                       ('senate' in text or 'county' in text or '2008' in text or '2010' in text):
                        found_datasets.append(href)
                        print(f"    ✅ Found: {text[:60]}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    return found_datasets

def main():
    """Search all sources for PDF election results"""
    print("=" * 80)
    print("SEARCHING FOR SC ELECTION RESULT PDFs")
    print("Target: 2008 U.S. Senate + 2010 Statewide Offices")
    print("=" * 80)
    
    # Try all sources
    wayback_urls = search_scvotes_wayback()
    county_pdfs = search_county_sites()
    direct_pdfs = search_scvotes_direct()
    ballotpedia_sources = search_ballotpedia_sources()
    mit_datasets = search_mit_dataverse()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print(f"\n📦 Internet Archive: {len(wayback_urls)} URLs")
    for url in wayback_urls[:5]:
        print(f"  • {url[:100]}")
    
    print(f"\n📦 County Sites: {len(county_pdfs)} PDFs")
    for county, url in county_pdfs[:5]:
        print(f"  • {county}: {url[:80]}")
    
    print(f"\n📦 Direct SC Election Commission: {len(direct_pdfs)} PDFs")
    for url in direct_pdfs:
        print(f"  • {url}")
    
    print(f"\n📦 Ballotpedia Sources: {len(ballotpedia_sources)} links")
    for url in ballotpedia_sources[:5]:
        print(f"  • {url[:100]}")
    
    print(f"\n📦 MIT Election Lab: {len(mit_datasets)} datasets")
    for url in mit_datasets[:5]:
        print(f"  • {url[:100]}")
    
    # Save results
    results = {
        'wayback': wayback_urls,
        'counties': county_pdfs,
        'direct': direct_pdfs,
        'ballotpedia': ballotpedia_sources,
        'mit': mit_datasets
    }
    
    import json
    output_dir = Path('workspace_files/pdf_search')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'found_sources.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Saved results to: {output_dir / 'found_sources.json'}")
    print("\n")

if __name__ == '__main__':
    main()
