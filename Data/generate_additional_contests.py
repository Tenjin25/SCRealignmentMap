#!/usr/bin/env python3
"""
Generate county-aggregated JSON files for additional statewide and US Senate contests
that are missing from the current SC Realignments map.
"""

import pandas as pd
import json
import os
from collections import defaultdict

# FIPS codes for SC counties
SC_FIPS = {
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

def normalize_office_name(office):
    """Normalize office names for consistency"""
    office = office.strip().upper()
    
    # Handle different variations of the same office
    if 'GOVERNOR' in office and 'LIEUTENANT' in office:
        return 'GOVERNOR AND LIEUTENANT GOVERNOR'
    elif office == 'GOVERNOR':
        return 'GOVERNOR'
    elif office == 'LIEUTENANT GOVERNOR':
        return 'LIEUTENANT GOVERNOR'
    elif 'SECRETARY' in office:
        return 'SECRETARY OF STATE'
    elif 'TREASURER' in office:
        return 'STATE TREASURER'
    elif 'ATTORNEY' in office:
        return 'ATTORNEY GENERAL'
    elif 'COMPTROLLER' in office:
        return 'COMPTROLLER GENERAL'
    elif 'SUPERINTENDENT' in office:
        return 'STATE SUPERINTENDENT OF EDUCATION'
    elif 'ADJUTANT' in office:
        return 'ADJUTANT GENERAL'
    elif 'AGRICULTURE' in office:
        return 'COMMISSIONER OF AGRICULTURE'
    elif 'U.S. SENATE' in office and 'UNEXPIRED' in office:
        return 'U.S. SENATE (UNEXPIRED TERM)'
    elif 'U.S. SENATE' in office:
        return 'U.S. SENATE'
    elif 'PRESIDENT' in office:
        return 'PRESIDENT'
    else:
        return office

def calculate_competitiveness(dem_pct, rep_pct):
    """Calculate competitiveness based on margin"""
    if dem_pct is None or rep_pct is None:
        return 0
    
    margin = abs(dem_pct - rep_pct)
    if margin >= 20:
        return 1  # Safe
    elif margin >= 10:
        return 2  # Likely
    elif margin >= 5:
        return 3  # Lean
    else:
        return 4  # Toss-up

def aggregate_county_data(file_path, target_offices):
    """Aggregate precinct data to county level for specified offices"""
    print(f"Processing {file_path}")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {}
    
    df = pd.read_csv(file_path)
    
    # Get available offices
    available_offices = df['office'].unique()
    print(f"Available offices: {available_offices}")
    
    results = {}
    
    for target_office in target_offices:
        # Find matching office in the data
        matching_office = None
        for office in available_offices:
            if normalize_office_name(office) == normalize_office_name(target_office):
                matching_office = office
                break
        
        if not matching_office:
            print(f"Office '{target_office}' not found in {file_path}")
            continue
        
        print(f"Processing {matching_office}")
        
        # Filter data for this office
        office_data = df[df['office'] == matching_office].copy()
        
        if office_data.empty:
            continue
        
        # Group by county and candidate, sum votes
        county_totals = office_data.groupby(['county', 'candidate', 'party'])['votes'].sum().reset_index()
        
        # Create county-level results
        county_results = {}
        
        for county in county_totals['county'].unique():
            county_data = county_totals[county_totals['county'] == county]
            
            # Get FIPS code
            fips = SC_FIPS.get(county, f'45{len(SC_FIPS)+1:03d}')
            
            # Calculate totals by party
            dem_votes = county_data[county_data['party'] == 'DEM']['votes'].sum()
            rep_votes = county_data[county_data['party'] == 'REP']['votes'].sum()
            total_votes = county_data['votes'].sum()
            
            if total_votes > 0:
                dem_pct = (dem_votes / total_votes) * 100
                rep_pct = (rep_votes / total_votes) * 100
            else:
                dem_pct = rep_pct = 0
            
            # Get candidate names
            dem_candidate = ""
            rep_candidate = ""
            
            dem_row = county_data[county_data['party'] == 'DEM']
            if not dem_row.empty:
                dem_candidate = dem_row.iloc[0]['candidate']
            
            rep_row = county_data[county_data['party'] == 'REP']
            if not rep_row.empty:
                rep_candidate = rep_row.iloc[0]['candidate']
            
            county_results[fips] = {
                "county": county,
                "fips": fips,
                "contest": normalize_office_name(target_office),
                "total_votes": int(total_votes),
                "dem_candidate": dem_candidate,
                "rep_candidate": rep_candidate,
                "dem_votes": int(dem_votes),
                "rep_votes": int(rep_votes),
                "dem_pct": round(dem_pct, 2),
                "rep_pct": round(rep_pct, 2),
                "competitiveness": calculate_competitiveness(dem_pct, rep_pct)
            }
        
        results[normalize_office_name(target_office)] = county_results
    
    return results

def process_2006_county_data():
    """Process 2006 county-level data for additional contests"""
    print("\n=== Processing 2006 County Data ===")
    
    file_path = "20061107__sc__general__county.csv"
    target_offices = [
        'LIEUTENANT GOVERNOR', 'SECRETARY OF STATE', 'STATE TREASURER', 
        'ATTORNEY GENERAL', 'COMPTROLLER GENERAL', 'STATE SUPERINTENDENT OF EDUCATION',
        'ADJUTANT GENERAL', 'COMMISSIONER OF AGRICULTURE'
    ]
    
    results = aggregate_county_data(file_path, target_offices)
    
    # Save each contest to separate JSON file
    for contest, data in results.items():
        if data:  # Only save if we have data
            contest_safe = contest.lower().replace(' ', '_').replace('(', '').replace(')', '')
            filename = f"../workspace_files/county_results_2006_{contest_safe}_fips.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Saved {filename}")

def process_precinct_data(year, file_pattern, target_offices):
    """Process precinct data for a specific year"""
    print(f"\n=== Processing {year} Precinct Data ===")
    
    all_county_data = {}
    
    # For years with county-specific files
    if year in ['2012', '2014', '2018', '2022']:
        county_dir = f"{year}"
        if year == '2022':
            county_dir = f"{year}/counties"
        
        if os.path.exists(county_dir):
            print(f"Processing county-specific files from {county_dir}")
            # Process county-specific files
            county_files = [f for f in os.listdir(county_dir) if f.endswith('_precinct.csv')]
            
            for county_file in county_files:
                county_name = county_file.split('__')[3]
                file_path = os.path.join(county_dir, county_file)
                print(f"Processing {county_name} from {file_path}")
                
                county_results = aggregate_county_data(file_path, target_offices)
                
                # Merge results
                for contest, data in county_results.items():
                    if contest not in all_county_data:
                        all_county_data[contest] = {}
                    all_county_data[contest].update(data)
        else:
            print(f"County directory {county_dir} not found")
            return
    else:
        # Process statewide precinct file
        if not file_pattern:
            print(f"No file pattern provided for {year}")
            return
            
        file_path = file_pattern
        print(f"Processing statewide file: {file_path}")
        all_county_data = aggregate_county_data(file_path, target_offices)
    
    # Save each contest to separate JSON file
    for contest, data in all_county_data.items():
        if data:  # Only save if we have data
            contest_safe = contest.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '')
            filename = f"../workspace_files/county_results_{year}_{contest_safe}_fips.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Saved {filename}")

def main():
    """Main processing function"""
    # Change to data directory
    os.chdir('C:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/SCRealignments/Data')
    
    # Process 2006 (county-level data)
    process_2006_county_data()
    
    # Process 2008 - US Senate only
    process_precinct_data(2008, "20081104__sc__general__precinct.csv", ['U.S. SENATE'])
    
    # Process 2014 - Additional statewide contests
    process_precinct_data(2014, "", [
        'LIEUTENANT GOVERNOR', 'SECRETARY OF STATE', 'STATE TREASURER', 
        'ATTORNEY GENERAL', 'COMPTROLLER GENERAL', 'STATE SUPERINTENDENT OF EDUCATION',
        'ADJUTANT GENERAL', 'COMMISSIONER OF AGRICULTURE', 'U.S. SENATE', 'U.S. SENATE (UNEXPIRED TERM)'
    ])
    
    # Process 2018 - Additional statewide contests
    process_precinct_data(2018, "", [
        'SECRETARY OF STATE', 'STATE TREASURER', 'ATTORNEY GENERAL', 
        'COMPTROLLER GENERAL', 'STATE SUPERINTENDENT OF EDUCATION', 'COMMISSIONER OF AGRICULTURE'
    ])
    
    # Process 2020 - US Senate only
    process_precinct_data(2020, "20201103__sc__general__precinct.csv", ['U.S. SENATE'])
    
    # Process 2022 - Additional statewide contests
    process_precinct_data(2022, "", [
        'SECRETARY OF STATE', 'STATE TREASURER', 'ATTORNEY GENERAL', 
        'COMPTROLLER GENERAL', 'STATE SUPERINTENDENT OF EDUCATION', 'COMMISSIONER OF AGRICULTURE', 'U.S. SENATE'
    ])
    
    print("\n=== Processing Complete ===")

if __name__ == "__main__":
    main()