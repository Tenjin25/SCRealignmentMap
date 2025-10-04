#!/usr/bin/env python3
"""
Properly fix Marion and McCormick County data using backup files
Restore the correct vote data for each county from backup files.
"""

import json
import os
import glob
from typing import Dict, Any

def restore_marion_mccormick_data():
    """Restore correct Marion and McCormick data from backup files."""
    
    data_dir = "./Data"
    
    # Find all main files and their backups
    main_files = glob.glob(os.path.join(data_dir, "*fips_accurate.json"))
    main_files = [f for f in main_files if "_backup.json" not in f]
    
    print(f"Found {len(main_files)} files to restore")
    
    for main_file in main_files:
        backup_file = main_file.replace(".json", "_backup.json")
        
        if not os.path.exists(backup_file):
            print(f"⚠️  No backup found for {os.path.basename(main_file)}")
            continue
            
        try:
            # Read backup data
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Read current data
            with open(main_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            
            # Find Marion and McCormick in backup
            marion_backup = None
            mccormick_backup = None
            marion_fips = None
            mccormick_fips = None
            
            for fips, data in backup_data.items():
                county = data.get('county', '').upper()
                if county == 'MARION':
                    marion_backup = data.copy()
                    marion_fips = fips
                elif county == 'MCCORMICK':
                    mccormick_backup = data.copy()
                    mccormick_fips = fips
            
            if not marion_backup or not mccormick_backup:
                print(f"⚠️  Could not find Marion/McCormick in backup for {os.path.basename(main_file)}")
                continue
            
            print(f"\nRestoring {os.path.basename(main_file)}:")
            print(f"  Marion backup FIPS: {marion_fips}")
            print(f"  McCormick backup FIPS: {mccormick_fips}")
            
            # Remove any existing Marion/McCormick entries in current data
            keys_to_remove = []
            for fips, data in current_data.items():
                county = data.get('county', '').upper()
                if county in ['MARION', 'MCCORMICK']:
                    keys_to_remove.append(fips)
            
            for key in keys_to_remove:
                del current_data[key]
            
            # Add corrected entries with proper FIPS codes
            # Marion should be FIPS 45065
            marion_backup['county'] = 'MARION'
            marion_backup['county_fips'] = '45065'
            current_data['45065'] = marion_backup
            
            # McCormick should be FIPS 45069  
            mccormick_backup['county'] = 'MCCORMICK'
            mccormick_backup['county_fips'] = '45069'
            current_data['45069'] = mccormick_backup
            
            # Write corrected data
            with open(main_file, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Restored correct data for {os.path.basename(main_file)}")
            
        except Exception as e:
            print(f"✗ Error processing {main_file}: {e}")

if __name__ == "__main__":
    print("Restoring Marion and McCormick County data from backups...")
    restore_marion_mccormick_data()
    print("\nDone!")