#!/usr/bin/env python3
"""
Fix all election data files to use official FIPS codes.

According to official FIPS reference:
- McCormick: 45065
- Marion: 45067  
- Marlboro: 45069

Current (wrong) mapping in data:
- 45065: MARION (should be McCormick)
- 45067: MARLBORO (should be Marion)
- 45069: MCCORMICK (should be Marlboro)
"""

import json
import os
import glob

def fix_election_data_fips():
    # Define the FIPS code corrections needed
    fips_corrections = {
        # Current wrong FIPS -> Correct FIPS
        '45065': '45067',  # MARION data should have FIPS 45067
        '45067': '45069',  # MARLBORO data should have FIPS 45069  
        '45069': '45065'   # MCCORMICK data should have FIPS 45065
    }
    
    # Find all FIPS accurate JSON files
    data_files = glob.glob('Data/*_fips_accurate.json') + glob.glob('Data/*_fips.json')
    
    total_files_fixed = 0
    total_counties_fixed = 0
    
    for file_path in data_files:
        print(f"\nProcessing {file_path}...")
        
        # Load the JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Create a new corrected data structure
        corrected_data = {}
        counties_fixed_in_file = 0
        
        for old_fips, county_data in data.items():
            if old_fips in fips_corrections:
                # This county needs FIPS correction
                new_fips = fips_corrections[old_fips]
                county_name = county_data.get('county', 'Unknown')
                
                # Update the FIPS code in the data
                county_data['county_fips'] = new_fips
                
                # Store with new FIPS code as key
                corrected_data[new_fips] = county_data
                print(f"  Fixed {county_name}: {old_fips} → {new_fips}")
                counties_fixed_in_file += 1
            else:
                # Keep unchanged
                corrected_data[old_fips] = county_data
        
        # Save the corrected file
        if counties_fixed_in_file > 0:
            with open(file_path, 'w') as f:
                json.dump(corrected_data, f, indent=2)
            total_files_fixed += 1
            total_counties_fixed += counties_fixed_in_file
            print(f"  Saved {file_path} with {counties_fixed_in_file} corrections")
        else:
            print(f"  No corrections needed for {file_path}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Files processed: {len(data_files)}")
    print(f"Files corrected: {total_files_fixed}")
    print(f"Total county FIPS corrections: {total_counties_fixed}")
    print("\nAll election data files now use official FIPS codes!")

if __name__ == "__main__":
    fix_election_data_fips()