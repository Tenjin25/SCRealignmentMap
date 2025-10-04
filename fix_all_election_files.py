#!/usr/bin/env python3
"""
Script to apply FIPS corrections to all SC election data files.
Uses the same correction mapping discovered from the 2024 file.
"""

import json
import os
import shutil
from typing import Dict, Any

# Correction mapping discovered from analysis
FIPS_CORRECTIONS = {
    "45065": "45067",  # MARION data → correct MARION FIPS
    "45067": "45069",  # MARLBORO data → correct MARLBORO FIPS  
    "45069": "45065"   # MCCORMICK data → correct MCCORMICK FIPS
}

# Official FIPS to county mapping for validation
OFFICIAL_FIPS_TO_COUNTY = {
    "45065": "MCCORMICK",
    "45067": "MARION", 
    "45069": "MARLBORO"
}

def fix_election_data_file(input_file: str) -> bool:
    """Apply FIPS corrections to an election data file."""
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return False
        
    print(f"\n🔧 Fixing {input_file}")
    
    # Create backup
    backup_file = input_file.replace(".json", "_backup.json")
    if not os.path.exists(backup_file):
        shutil.copy2(input_file, backup_file)
        print(f"   💾 Backup created: {backup_file}")
    else:
        print(f"   💾 Backup already exists: {backup_file}")
    
    try:
        with open(input_file, 'r') as f:
            election_data = json.load(f)
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False
    
    # Check if corrections are needed
    needs_correction = False
    for incorrect_fips in FIPS_CORRECTIONS.keys():
        if incorrect_fips in election_data:
            county_name = election_data[incorrect_fips].get("county", "")
            if county_name in ["MARION", "MARLBORO", "MCCORMICK"]:
                needs_correction = True
                break
    
    if not needs_correction:
        print(f"   ✅ File already appears to be corrected")
        return True
    
    # Create a mapping of data that needs to be moved
    data_to_move = {}
    original_count = len(election_data)
    
    for incorrect_fips, correct_fips in FIPS_CORRECTIONS.items():
        if incorrect_fips in election_data:
            data_to_move[correct_fips] = election_data[incorrect_fips].copy()
            # Update the county_fips field in the data
            data_to_move[correct_fips]["county_fips"] = correct_fips
            # Update the county name to match official FIPS
            data_to_move[correct_fips]["county"] = OFFICIAL_FIPS_TO_COUNTY[correct_fips]
    
    # Remove old entries and add corrected ones
    corrected_data = {}
    
    # Add all data with correct FIPS codes
    for fips, data in election_data.items():
        if fips in FIPS_CORRECTIONS:
            # This FIPS code was wrong, data will be moved
            continue
        elif fips in data_to_move:
            # This FIPS code is getting corrected data
            corrected_data[fips] = data_to_move[fips]
        else:
            # This FIPS code is already correct
            corrected_data[fips] = data
    
    # Add any remaining corrected data
    for correct_fips, data in data_to_move.items():
        if correct_fips not in corrected_data:
            corrected_data[correct_fips] = data
    
    # Sort by FIPS code for consistent output
    sorted_data = dict(sorted(corrected_data.items()))
    
    try:
        # Write corrected data
        with open(input_file, 'w') as f:
            json.dump(sorted_data, f, indent=2)
        
        print(f"   ✅ Fixed {len(FIPS_CORRECTIONS)} FIPS assignments")
        print(f"   📊 Counties: {original_count} → {len(sorted_data)}")
        
        # Verify the corrections
        for correct_fips, expected_county in OFFICIAL_FIPS_TO_COUNTY.items():
            if correct_fips in sorted_data:
                actual_county = sorted_data[correct_fips].get("county", "")
                if actual_county == expected_county:
                    print(f"   ✅ FIPS {correct_fips}: {expected_county}")
                else:
                    print(f"   ❌ FIPS {correct_fips}: Expected {expected_county}, got {actual_county}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error writing file: {e}")
        return False

def main():
    """Fix FIPS codes in all election data files."""
    
    print("🔧 FIXING FIPS CODES IN ALL ELECTION DATA FILES")
    print("=" * 55)
    
    # Find all election data files
    data_dir = "Data"
    election_files = []
    
    for filename in os.listdir(data_dir):
        if (filename.startswith("county_results_") and 
            filename.endswith("_fips_accurate.json") and
            not filename.endswith("_backup.json")):
            election_files.append(os.path.join(data_dir, filename))
    
    # Also include the us_senate files that might have different naming
    for filename in os.listdir(data_dir):
        if (filename.startswith("county_results_") and 
            "senate" in filename and
            filename.endswith(".json") and
            not filename.endswith("_backup.json")):
            election_files.append(os.path.join(data_dir, filename))
    
    # Remove duplicates and sort
    election_files = sorted(list(set(election_files)))
    
    print(f"📋 Found {len(election_files)} election data files to check:")
    for file in election_files:
        print(f"   • {file}")
    
    # Apply corrections to each file
    success_count = 0
    for file in election_files:
        if fix_election_data_file(file):
            success_count += 1
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Successfully processed: {success_count}/{len(election_files)} files")
    
    if success_count == len(election_files):
        print(f"\n🎉 All FIPS code corrections completed successfully!")
        print(f"   📍 Marlboro County should now appear blue on the map")
        print(f"   📍 Marion and McCormick counties should also display correctly")
    else:
        print(f"\n⚠️  Some files had issues. Check the output above for details.")

if __name__ == "__main__":
    main()