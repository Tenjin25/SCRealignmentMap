#!/usr/bin/env python3
"""
Verification script for the enhanced SC Political Map
Tests key functionality and data integrity
"""

import json
import os

def test_data_integrity():
    """Test that Marion and McCormick data is correct"""
    print("🔍 Testing data integrity...")
    
    # Test 2024 data
    with open('./Data/county_results_2024_fips_accurate.json', 'r') as f:
        data = json.load(f)
    
    # Check Marion County (should be FIPS 45065, Democratic)
    marion_data = data.get('45065')
    if marion_data and marion_data.get('county') == 'MARION':
        dem_votes = marion_data.get('dem_votes', 0)
        rep_votes = marion_data.get('rep_votes', 0)
        if dem_votes > rep_votes:
            print("✅ Marion County (45065): Correctly shows Democratic win")
        else:
            print("❌ Marion County (45065): Should be Democratic but shows Republican")
    else:
        print("❌ Marion County not found at FIPS 45065")
    
    # Check McCormick County (should be FIPS 45069, Republican)
    mccormick_data = data.get('45069')
    if mccormick_data and mccormick_data.get('county') == 'MCCORMICK':
        dem_votes = mccormick_data.get('dem_votes', 0)
        rep_votes = mccormick_data.get('rep_votes', 0)
        if rep_votes > dem_votes:
            print("✅ McCormick County (45069): Correctly shows Republican win")
        else:
            print("❌ McCormick County (45069): Should be Republican but shows Democratic")
    else:
        print("❌ McCormick County not found at FIPS 45069")

def test_contest_availability():
    """Test that all contest files exist"""
    print("\n📊 Testing contest data availability...")
    
    contests = [
        'county_results_2024_fips_accurate.json',
        'county_results_2022_governor_lieutenant_governor_fips_accurate.json',
        'county_results_2022_u.s._senate_fips_accurate.json',
        'county_results_2022_attorney_general_fips_accurate.json',
        'county_results_2020_fips_accurate.json',
        'county_results_2018_governor_lieutenant_governor_fips_accurate.json',
        'county_results_2018_attorney_general_fips_accurate.json',
        'county_results_2016_fips_accurate.json',
        'county_results_2014_governor_fips_accurate.json',
        'county_results_2014_u.s._senate_fips_accurate.json',
        'county_results_2012_fips_accurate.json',
        'county_results_2008_fips_accurate.json',
        'county_results_2006_governor_fips_accurate.json'
    ]
    
    available = 0
    for contest in contests:
        file_path = f'./Data/{contest}'
        if os.path.exists(file_path):
            available += 1
            print(f"✅ {contest}")
        else:
            print(f"❌ Missing: {contest}")
    
    print(f"\n📈 Contest Summary: {available}/{len(contests)} contests available")

def test_county_count():
    """Test that we have all 46 SC counties"""
    print("\n🏛️ Testing county coverage...")
    
    with open('./Data/county_results_2024_fips_accurate.json', 'r') as f:
        data = json.load(f)
    
    counties = set()
    for fips, county_data in data.items():
        county_name = county_data.get('county')
        if county_name:
            counties.add(county_name)
    
    print(f"✅ Found {len(counties)} counties in 2024 data")
    if len(counties) >= 46:
        print("✅ County coverage looks complete")
    else:
        print(f"⚠️  Expected 46 counties, found {len(counties)}")

def main():
    print("🗳️ SC Political Map - Enhanced Features Test")
    print("=" * 50)
    
    test_data_integrity()
    test_contest_availability()
    test_county_count()
    
    print("\n🎉 Verification complete!")
    print("\n📍 Next steps:")
    print("   1. Open http://localhost:8080 in your browser")
    print("   2. Select a contest from the organized dropdown")
    print("   3. Click on Marion County - should show Democratic win")
    print("   4. Click on McCormick County - should show Republican win")
    print("   5. Test the enhanced sidebar with detailed analysis")

if __name__ == "__main__":
    main()