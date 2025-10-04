#!/usr/bin/env python3
"""
Fix Marion and McCormick County FIPS assignments
The current data incorrectly assigns McCormick's votes to Marion's FIPS code.

CORRECT assignments should be:
- FIPS 45065: MARION County (Democratic stronghold)
- FIPS 45069: MCCORMICK County (Republican leaning)
"""

import json
import os
import glob
from typing import Dict, Any

def fix_marion_mccormick_assignment(election_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fix the Marion/McCormick FIPS assignment error."""
    
    fixed_data = election_data.copy()
    
    # Find current assignments
    marion_fips = None
    mccormick_fips = None
    
    for fips, data in election_data.items():
        if data.get('county', '').upper() == 'MARION':
            marion_fips = fips
        elif data.get('county', '').upper() == 'MCCORMICK':
            mccormick_fips = fips
    
    if not marion_fips or not mccormick_fips:
        print(f"Could not find Marion ({marion_fips}) or McCormick ({mccormick_fips}) counties")
        return fixed_data
    
    print(f"Found Marion at FIPS {marion_fips}, McCormick at FIPS {mccormick_fips}")
    
    # Check if they need swapping
    marion_data = election_data[marion_fips]
    mccormick_data = election_data[mccormick_fips]
    
    # Marion should be more Democratic historically, McCormick more Republican
    marion_dem_votes = marion_data.get('dem_votes', 0) or marion_data.get('2024_dem', 0)
    marion_rep_votes = marion_data.get('rep_votes', 0) or marion_data.get('2024_rep', 0)
    
    mccormick_dem_votes = mccormick_data.get('dem_votes', 0) or mccormick_data.get('2024_dem', 0)
    mccormick_rep_votes = mccormick_data.get('rep_votes', 0) or mccormick_data.get('2024_rep', 0)
    
    print(f"Current assignments:")
    print(f"  Marion (FIPS {marion_fips}): Dem {marion_dem_votes}, Rep {marion_rep_votes}")
    print(f"  McCormick (FIPS {mccormick_fips}): Dem {mccormick_dem_votes}, Rep {mccormick_rep_votes}")
    
    # The correct assignments should be:
    # Marion County (FIPS 45065): Historically Democratic, larger population
    # McCormick County (FIPS 45069): Historically Republican, smaller population
    
    if marion_fips != "45065" or mccormick_fips != "45069":
        print("FIPS codes are incorrect! Fixing...")
        
        # Remove old entries
        if marion_fips in fixed_data:
            del fixed_data[marion_fips]
        if mccormick_fips in fixed_data:
            del fixed_data[mccormick_fips]
        
        # Assign to correct FIPS codes
        marion_data['county'] = 'MARION'
        marion_data['county_fips'] = '45065'
        fixed_data['45065'] = marion_data
        
        mccormick_data['county'] = 'MCCORMICK' 
        mccormick_data['county_fips'] = '45069'
        fixed_data['45069'] = mccormick_data
        
        print("Fixed FIPS assignments:")
        print(f"  Marion -> FIPS 45065")
        print(f"  McCormick -> FIPS 45069")
    
    return fixed_data

def fix_all_election_files():
    """Fix Marion/McCormick assignments in all election files."""
    
    data_dir = "./Data"
    files_pattern = os.path.join(data_dir, "*fips_accurate.json")
    
    files_to_fix = glob.glob(files_pattern)
    print(f"Found {len(files_to_fix)} files to check/fix")
    
    for file_path in files_to_fix:
        if "_backup.json" in file_path:
            continue  # Skip backup files
            
        print(f"\nProcessing: {os.path.basename(file_path)}")
        
        try:
            # Read current data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Fix the data
            fixed_data = fix_marion_mccormick_assignment(data)
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(fixed_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Fixed {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")

if __name__ == "__main__":
    print("Fixing Marion and McCormick County FIPS assignments...")
    fix_all_election_files()
    print("\nDone!")