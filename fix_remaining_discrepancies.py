#!/usr/bin/env python3
"""
Fix remaining data discrepancies:
1. Restore missing Marlboro County
2. Standardize candidate names
"""

import json
import os
import glob
import re

def restore_marlboro_county():
    """Restore Marlboro County from backup data"""
    print("🔧 Restoring Marlboro County...")
    
    # Read backup to get Marlboro data
    with open('./Data/county_results_2024_fips_accurate_backup.json', 'r') as f:
        backup_data = json.load(f)
    
    marlboro_data = backup_data.get('45067')  # Marlboro should be at 45067
    if not marlboro_data or marlboro_data.get('county') != 'MARLBORO':
        print("❌ Could not find Marlboro in backup at FIPS 45067")
        return False
    
    # Read current data
    with open('./Data/county_results_2024_fips_accurate.json', 'r') as f:
        current_data = json.load(f)
    
    # Check if 45067 is occupied by something else
    if '45067' in current_data:
        print(f"⚠️  FIPS 45067 is occupied by {current_data['45067'].get('county')}")
        return False
    
    # Add Marlboro back
    current_data['45067'] = marlboro_data.copy()
    current_data['45067']['county'] = 'MARLBORO'
    current_data['45067']['county_fips'] = '45067'
    
    # Save updated data
    with open('./Data/county_results_2024_fips_accurate.json', 'w') as f:
        json.dump(current_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Marlboro County restored to FIPS 45067")
    return True

def standardize_candidate_names():
    """Standardize candidate names across all files"""
    print("\n🎭 Standardizing candidate names...")
    
    # Standard candidate names for 2024
    standard_names = {
        'dem_2024': 'Kamala D Harris/Tim Walz (D)',
        'rep_2024': 'Donald J Trump/JD Vance (R)'
    }
    
    data_dir = "./Data"
    files = glob.glob(os.path.join(data_dir, "*2024*fips_accurate.json"))
    files = [f for f in files if "_backup.json" not in f]
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            updated = False
            for fips, county_data in data.items():
                # Standardize Democratic candidate
                dem_candidate = county_data.get('dem_candidate', '')
                if dem_candidate and 'harris' in dem_candidate.lower():
                    if dem_candidate != standard_names['dem_2024']:
                        county_data['dem_candidate'] = standard_names['dem_2024']
                        updated = True
                
                # Standardize Republican candidate  
                rep_candidate = county_data.get('rep_candidate', '')
                if rep_candidate and 'trump' in rep_candidate.lower():
                    if rep_candidate != standard_names['rep_2024']:
                        county_data['rep_candidate'] = standard_names['rep_2024']
                        updated = True
            
            if updated:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✅ Updated candidate names in {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

def verify_fixes():
    """Verify that all fixes were applied correctly"""
    print("\n🔍 Verifying fixes...")
    
    with open('./Data/county_results_2024_fips_accurate.json', 'r') as f:
        data = json.load(f)
    
    # Check Marlboro County
    marlboro_data = data.get('45067')
    if marlboro_data and marlboro_data.get('county') == 'MARLBORO':
        dem_votes = marlboro_data.get('dem_votes', 0)
        rep_votes = marlboro_data.get('rep_votes', 0)
        winner = 'Democratic' if dem_votes > rep_votes else 'Republican'
        print(f"✅ Marlboro County (FIPS 45067): {winner} win")
        print(f"   Dem: {dem_votes:,} | Rep: {rep_votes:,}")
    else:
        print("❌ Marlboro County still missing")
    
    # Check candidate name consistency
    dem_candidates = set()
    rep_candidates = set()
    
    for county_data in data.values():
        dem_cand = county_data.get('dem_candidate', '').strip()
        rep_cand = county_data.get('rep_candidate', '').strip()
        
        if dem_cand:
            dem_candidates.add(dem_cand)
        if rep_cand:
            rep_candidates.add(rep_cand)
    
    print(f"\nCandidate name consistency:")
    print(f"   Democratic candidates: {len(dem_candidates)} unique names")
    print(f"   Republican candidates: {len(rep_candidates)} unique names")
    
    if len(dem_candidates) == 1 and len(rep_candidates) == 1:
        print("✅ Candidate names are now consistent")
    else:
        print("⚠️  Multiple candidate names still exist:")
        if len(dem_candidates) > 1:
            for name in dem_candidates:
                print(f"      Dem: {name}")
        if len(rep_candidates) > 1:
            for name in rep_candidates:
                print(f"      Rep: {name}")
    
    # Final county count
    counties = set()
    for county_data in data.values():
        county = county_data.get('county', '').upper()
        if county:
            counties.add(county)
    
    print(f"\nFinal county count: {len(counties)}/46")
    if len(counties) == 46:
        print("✅ All 46 SC counties are now present")

def main():
    print("🔧 Fixing Remaining Data Discrepancies")
    print("=" * 50)
    
    # Fix missing Marlboro County
    marlboro_success = restore_marlboro_county()
    
    # Standardize candidate names
    standardize_candidate_names()
    
    # Verify fixes
    verify_fixes()
    
    print("\n" + "=" * 50)
    print("🎉 Data discrepancy fixes completed!")
    
    if marlboro_success:
        print("\nFixed issues:")
        print("   ✅ Restored missing Marlboro County")
        print("   ✅ Standardized candidate names")
        print("   ✅ All 46 counties should now be present")

if __name__ == "__main__":
    main()