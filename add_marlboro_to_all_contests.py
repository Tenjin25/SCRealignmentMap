import json
import os
import re
from pathlib import Path

def add_marlboro_to_file(data_file_path, workspace_file_path):
    """
    Add Marlboro County (45069) data to a Data file using data from workspace_files.
    
    In workspace_files, Marlboro data is stored under FIPS 45067 (Marion's actual FIPS).
    We need to extract it and insert it as 45069 in the Data files.
    """
    
    # Check if workspace file exists
    if not os.path.exists(workspace_file_path):
        print(f"  ⚠ Workspace file not found: {workspace_file_path}")
        return False
    
    # Read workspace file to get Marlboro data (stored under 45067)
    try:
        with open(workspace_file_path, 'r', encoding='utf-8') as f:
            workspace_data = json.load(f)
    except Exception as e:
        print(f"  ⚠ Error reading workspace file: {e}")
        return False
    
    # Extract Marlboro data from workspace_files (under 45067)
    if '45067' not in workspace_data:
        print(f"  ⚠ No 45067 entry in workspace file (expected Marlboro data here)")
        return False
    
    marlboro_data = workspace_data['45067'].copy()
    
    # Verify this is actually Marlboro data
    if marlboro_data.get('county') != 'MARLBORO':
        print(f"  ⚠ 45067 entry is not MARLBORO, it's: {marlboro_data.get('county')}")
        return False
    
    # Update the FIPS code to the correct one (45069)
    marlboro_data['county_fips'] = '45069'
    
    # Read the Data file
    try:
        with open(data_file_path, 'r', encoding='utf-8') as f:
            data_content = json.load(f)
    except Exception as e:
        print(f"  ⚠ Error reading data file: {e}")
        return False
    
    # Check if Marlboro already exists
    if '45069' in data_content:
        print(f"  ✓ Already has Marlboro (45069)")
        return True
    
    # Insert Marlboro (45069) after Marion (45067)
    # We need to maintain order, so we'll rebuild the dict
    new_data = {}
    for fips, county_data in data_content.items():
        new_data[fips] = county_data
        # After Marion (45067), insert Marlboro (45069)
        if fips == '45067':
            new_data['45069'] = marlboro_data
    
    # Write back to file with proper formatting
    try:
        with open(data_file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Added Marlboro County (45069)")
        return True
    except Exception as e:
        print(f"  ⚠ Error writing data file: {e}")
        return False

def main():
    # Base directories
    data_dir = Path('Data')
    workspace_dir = Path('workspace_files')
    
    # List of files missing Marlboro (from our check)
    missing_files = [
        'county_results_2006_adjutant_general_fips_accurate.json',
        'county_results_2006_attorney_general_fips_accurate.json',
        'county_results_2006_commissioner_of_agriculture_fips_accurate.json',
        'county_results_2006_comptroller_general_fips_accurate.json',
        'county_results_2006_governor_fips_accurate.json',
        'county_results_2006_lieutenant_governor_fips_accurate.json',
        'county_results_2006_secretary_of_state_fips_accurate.json',
        'county_results_2006_state_superintendent_of_education_fips_accurate.json',
        'county_results_2006_state_treasurer_fips_accurate.json',
        'county_results_2014_adjutant_general_fips_accurate.json',
        'county_results_2014_attorney_general_fips_accurate.json',
        'county_results_2014_commissioner_of_agriculture_fips_accurate.json',
        'county_results_2014_comptroller_general_fips_accurate.json',
        'county_results_2014_governor_fips_accurate.json',
        'county_results_2014_lieutenant_governor_fips_accurate.json',
        'county_results_2014_secretary_of_state_fips_accurate.json',
        'county_results_2014_state_house_of_representatives_fips_accurate.json',
        'county_results_2014_state_superintendent_of_education_fips_accurate.json',
        'county_results_2014_state_treasurer_fips_accurate.json',
        'county_results_2014_u.s._house_fips_accurate.json',
        'county_results_2014_u.s._senate_(unexpired_term)_fips_accurate.json',
        'county_results_2014_u.s._senate_fips_accurate.json',
        'county_results_2018_attorney_general_fips_accurate.json',
        'county_results_2018_commissioner_of_agriculture_fips_accurate.json',
        'county_results_2018_comptroller_general_fips_accurate.json',
        'county_results_2018_governor_lieutenant_governor_fips_accurate.json',
        'county_results_2018_secretary_of_state_fips_accurate.json',
        'county_results_2018_state_house_fips_accurate.json',
        'county_results_2018_state_superintendent_of_education_fips_accurate.json',
        'county_results_2018_state_treasurer_fips_accurate.json',
        'county_results_2018_u.s._house_fips_accurate.json',
        'county_results_2022_attorney_general_fips_accurate.json',
        'county_results_2022_commissioner_of_agriculture_fips_accurate.json',
        'county_results_2022_comptroller_general_fips_accurate.json',
        'county_results_2022_governor_lieutenant_governor_fips_accurate.json',
        'county_results_2022_secretary_of_state_fips_accurate.json',
        'county_results_2022_state_house_fips_accurate.json',
        'county_results_2022_state_superintendent_of_education_fips_accurate.json',
        'county_results_2022_state_treasurer_fips_accurate.json',
        'county_results_2022_u.s._house_fips_accurate.json',
        'county_results_2022_u.s._senate_fips_accurate.json',
    ]
    
    print(f"\n🔧 Adding Marlboro County (45069) to {len(missing_files)} files...\n")
    
    success_count = 0
    failed_count = 0
    
    for filename in missing_files:
        print(f"Processing: {filename}")
        
        data_file = data_dir / filename
        workspace_file = workspace_dir / filename
        
        if not data_file.exists():
            print(f"  ⚠ Data file not found, skipping")
            failed_count += 1
            continue
        
        if add_marlboro_to_file(str(data_file), str(workspace_file)):
            success_count += 1
        else:
            failed_count += 1
        print()
    
    print(f"\n{'='*60}")
    print(f"✓ Successfully updated: {success_count} files")
    if failed_count > 0:
        print(f"⚠ Failed or skipped: {failed_count} files")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
