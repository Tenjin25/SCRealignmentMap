#!/usr/bin/env python3
"""
Fix FIPS code mismatches in the GeoJSON file.

The election data has the correct FIPS assignments:
- FIPS 45065: MARION
- FIPS 45067: MARLBORO  
- FIPS 45069: MCCORMICK

But the GeoJSON file has them wrong:
- FIPS 45065: McCormick
- FIPS 45067: Marion
- FIPS 45069: Marlboro

This script corrects the GeoJSON FIPS codes to match the election data.
"""

import json
import shutil
from datetime import datetime

def fix_geojson_fips():
    geojson_path = r'c:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\sc_counties.geojson'
    
    # Create backup
    backup_path = geojson_path.replace('.geojson', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.geojson')
    shutil.copy2(geojson_path, backup_path)
    print(f"Created backup: {backup_path}")
    
    # Load GeoJSON data
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    
    print("Original FIPS assignments:")
    # Track the corrections needed
    corrections = {}
    
    for feature in geojson_data['features']:
        county_name = feature['properties']['NAME20']
        current_fips = feature['properties']['GEOID20']
        
        if county_name in ['Marion', 'McCormick', 'Marlboro']:
            print(f"  {county_name}: FIPS {current_fips}")
            
            # Map to correct FIPS based on election data
            if county_name == 'Marion':
                correct_fips = '45065'
            elif county_name == 'Marlboro':
                correct_fips = '45067'
            elif county_name == 'McCormick':
                correct_fips = '45069'
            
            corrections[current_fips] = correct_fips
    
    print("\nCorrections needed:")
    for old_fips, new_fips in corrections.items():
        print(f"  {old_fips} -> {new_fips}")
    
    # Apply corrections
    corrected_count = 0
    for feature in geojson_data['features']:
        county_name = feature['properties']['NAME20']
        current_fips = feature['properties']['GEOID20']
        
        if current_fips in corrections:
            new_fips = corrections[current_fips]
            feature['properties']['GEOID20'] = new_fips
            print(f"Corrected {county_name}: {current_fips} -> {new_fips}")
            corrected_count += 1
    
    # Save corrected GeoJSON
    with open(geojson_path, 'w') as f:
        json.dump(geojson_data, f, separators=(',', ':'))
    
    print(f"\nCorrected {corrected_count} FIPS codes in GeoJSON file")
    
    # Verify corrections
    print("\nVerifying corrections:")
    with open(geojson_path, 'r') as f:
        verified_data = json.load(f)
    
    for feature in verified_data['features']:
        county_name = feature['properties']['NAME20']
        county_fips = feature['properties']['GEOID20']
        
        if county_name in ['Marion', 'McCormick', 'Marlboro']:
            print(f"  {county_name}: FIPS {county_fips}")

if __name__ == "__main__":
    fix_geojson_fips()