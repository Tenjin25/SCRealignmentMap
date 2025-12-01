"""
Download county-level data from SC ENR (Election Night Reporting) system
Sources found from Ballotpedia:
- 2008: http://www.enr-scvotes.org/SC/19077/40245/en/summary.html
- 2010: http://www.enr-scvotes.org/SC/16117/27822/en/summary.html
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import re

def download_2008_senate_enr():
    """Download 2008 U.S. Senate from ENR system"""
    print("\n📥 Downloading 2008 U.S. Senate from ENR system...")
    
    # Correct URL with county selector
    url = "https://www.enr-scvotes.org/SC/19077/40477/en/select-county.html"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"  ❌ Failed to load: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"  ✅ Loaded ENR page")
        
        # Save raw HTML for inspection
        output_dir = Path('workspace_files/enr_downloads')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / '2008_senate_select_county.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"  💾 Saved HTML to: {output_dir / '2008_senate_select_county.html'}")
        
        # Find county selector links
        county_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            # County links typically contain county names
            if text and len(text) > 2 and 'County' not in text and text[0].isupper():
                full_url = href if href.startswith('http') else 'https://www.enr-scvotes.org/SC/19077/40477/en/' + href.lstrip('./')
                county_links.append((text, full_url))
        
        print(f"  📍 Found {len(county_links)} county links")
        if county_links:
            print(f"  Example: {county_links[0]}")
        
        return {'main_url': url, 'soup': soup, 'county_links': county_links}
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def download_2010_statewide_enr():
    """Download 2010 statewide offices from ENR system"""
    print("\n📥 Downloading 2010 Statewide from ENR system...")
    
    # Correct URL with county selector
    url = "https://www.enr-scvotes.org/SC/8562/15723/en/select-county.html"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"  ❌ Failed: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"  ✅ Loaded ENR page")
        
        # Save raw HTML
        output_dir = Path('workspace_files/enr_downloads')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / '2010_select_county.html'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"  💾 Saved: {filepath}")
        
        # Find county selector links
        county_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            # County links
            if text and len(text) > 2 and 'County' not in text and text[0].isupper():
                full_url = href if href.startswith('http') else 'https://www.enr-scvotes.org/SC/8562/15723/en/' + href.lstrip('./')
                county_links.append((text, full_url))
        
        print(f"  � Found {len(county_links)} county links")
        if county_links:
            print(f"  Example: {county_links[0]}")
        
        return {'main_url': url, 'soup': soup, 'county_links': county_links}
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def main():
    """Download ENR data"""
    print("=" * 80)
    print("DOWNLOADING SC ENR ELECTION DATA")
    print("=" * 80)
    
    # Download data
    senate_2008 = download_2008_senate_enr()
    statewide_2010 = download_2010_statewide_enr()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if senate_2008:
        print(f"\n✅ 2008 Senate: Downloaded HTML, found {len(senate_2008.get('county_links', []))} county links")
    else:
        print("\n❌ 2008 Senate: Failed to download")
    
    if statewide_2010:
        print(f"✅ 2010 Statewide: Downloaded HTML, found {len(statewide_2010.get('county_links', []))} county links")
    else:
        print("❌ 2010 Statewide: Failed to download")
    
    print("\n💡 Next: Download individual county pages and extract vote data")
    print("\n")

if __name__ == '__main__':
    main()
