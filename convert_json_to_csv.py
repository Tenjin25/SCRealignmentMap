#!/usr/bin/env python3
"""
Convert SC county results JSON files to CSV format for the map
"""
import json
import csv
import os
from pathlib import Path

def convert_county_results_to_csv():
    """Convert county results JSON to CSV format expected by the map"""
    
    # Define the data directory
    data_dir = Path("Data")
    
    # List of key election files to include
    election_files = [
        "county_results_2024_fips_accurate.json",
        "county_results_2022_fips_accurate.json", 
        "county_results_2020_fips_accurate.json",
        "county_results_2018_fips_accurate.json",
        "county_results_2016_fips_accurate.json",
        "county_results_2014_fips_accurate.json",
        "county_results_2012_fips_accurate.json",
        "county_results_2008_fips_accurate.json",
        "county_results_2006_fips_accurate.json"
    ]
    
    # CSV output file
    csv_file = data_dir / "sc_county_election_results.csv"
    
    # Collect all results
    all_results = []
    
    for json_file in election_files:
        json_path = data_dir / json_file
        
        if not json_path.exists():
            print(f"Warning: {json_file} not found, skipping...")
            continue
            
        print(f"Processing {json_file}...")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert each county record
            for fips, county_data in data.items():
                if isinstance(county_data, dict):
                    result = {
                        'year': county_data.get('year', ''),
                        'county_fips': fips,
                        'county': county_data.get('county', ''),
                        'contest': county_data.get('contest', ''),
                        'dem_candidate': county_data.get('dem_candidate', ''),
                        'rep_candidate': county_data.get('rep_candidate', ''),
                        'dem_votes': county_data.get('dem_votes', 0),
                        'rep_votes': county_data.get('rep_votes', 0),
                        'other_votes': county_data.get('other_votes', 0),
                        'total_votes': county_data.get('total_votes', 0),
                        'margin': county_data.get('margin', 0),
                        'margin_pct': county_data.get('margin_pct', 0),
                        'winner': county_data.get('winner', ''),
                        'two_party_total': county_data.get('two_party_total', 0)
                    }
                    
                    # Add competitiveness data if available
                    if 'competitiveness' in county_data and isinstance(county_data['competitiveness'], dict):
                        result['competitiveness_category'] = county_data['competitiveness'].get('category', '')
                        result['competitiveness_party'] = county_data['competitiveness'].get('party', '')
                        result['competitiveness_color'] = county_data['competitiveness'].get('color', '')
                    else:
                        result['competitiveness_category'] = ''
                        result['competitiveness_party'] = ''
                        result['competitiveness_color'] = ''
                    
                    all_results.append(result)
                    
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
            continue
    
    if not all_results:
        print("No results found to convert!")
        return
    
    # Write to CSV
    print(f"Writing {len(all_results)} records to {csv_file}...")
    
    # Define CSV columns
    fieldnames = [
        'year', 'county_fips', 'county', 'contest',
        'dem_candidate', 'rep_candidate', 
        'dem_votes', 'rep_votes', 'other_votes', 'total_votes',
        'margin', 'margin_pct', 'winner', 'two_party_total',
        'competitiveness_category', 'competitiveness_party', 'competitiveness_color'
    ]
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"Successfully created {csv_file} with {len(all_results)} records")
    
    # Show sample of what was created
    print("\nSample records:")
    for i, result in enumerate(all_results[:3]):
        print(f"  {i+1}. {result['year']} {result['county']} {result['contest']}: {result['winner']} (+{result['margin']})")

if __name__ == "__main__":
    convert_county_results_to_csv()