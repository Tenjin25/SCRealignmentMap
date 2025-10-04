#!/usr/bin/env python3
"""
Fix SC GeoJSON FIPS codes to match official FIPS reference.

According to https://unicede.air-worldwide.com/unicede/unicede_south-carolina_fips_2.html:
- McCormick: 065 (FIPS 45065)
- Marion: 067 (FIPS 45067)
- Marlboro: 069 (FIPS 45069)
"""

import json

def fix_geojson_fips():
    # Load the GeoJSON file
    with open('Data/sc_counties.geojson', 'r') as f:
        geojson = json.load(f)
    
    # Define the correct FIPS codes according to official reference
    corrections = {
        'Marion': {'COUNTYFP20': '067', 'GEOID20': '45067'},
        'McCormick': {'COUNTYFP20': '065', 'GEOID20': '45065'},
        'Marlboro': {'COUNTYFP20': '069', 'GEOID20': '45069'}
    }
    
    # Apply corrections
    fixed_count = 0
    for feature in geojson['features']:
        county_name = feature['properties'].get('NAME20', '')
        if county_name in corrections:
            old_fips = feature['properties']['GEOID20']
            feature['properties']['COUNTYFP20'] = corrections[county_name]['COUNTYFP20']
            feature['properties']['GEOID20'] = corrections[county_name]['GEOID20']
            print(f"Fixed {county_name}: {old_fips} → {corrections[county_name]['GEOID20']}")
            fixed_count += 1
    
    # Save the corrected GeoJSON
    with open('Data/sc_counties.geojson', 'w') as f:
        json.dump(geojson, f, separators=(',', ':'))
    
    print(f"\nFixed {fixed_count} counties in sc_counties.geojson")
    print("GeoJSON file has been updated with official FIPS codes.")

if __name__ == "__main__":
    fix_geojson_fips()