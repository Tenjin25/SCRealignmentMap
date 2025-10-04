#!/usr/bin/env python3
"""
Comprehensive data discrepancy checker for SC Political Map
This script will identify any remaining data issues across all election files.
"""

import json
import os
import glob
from collections import defaultdict

def check_all_fips_assignments():
    """Check FIPS assignments across all election files for consistency"""
    print("🔍 Checking FIPS assignments across all election files...")
    
    data_dir = "./Data"
    files = glob.glob(os.path.join(data_dir, "*fips_accurate.json"))
    files = [f for f in files if "_backup.json" not in f]
    
    # Track county-FIPS mappings across files
    county_fips_map = defaultdict(set)
    fips_county_map = defaultdict(set)
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for fips, county_data in data.items():
                county = county_data.get('county', '').upper()
                if county:
                    county_fips_map[county].add(fips)
                    fips_county_map[fips].add(county)
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
    
    # Find inconsistencies
    print("\n📊 FIPS Assignment Analysis:")
    inconsistencies = []
    
    for county, fips_set in county_fips_map.items():
        if len(fips_set) > 1:
            print(f"❌ {county} mapped to multiple FIPS: {list(fips_set)}")
            inconsistencies.append(f"{county} -> {list(fips_set)}")
    
    for fips, county_set in fips_county_map.items():
        if len(county_set) > 1:
            print(f"❌ FIPS {fips} mapped to multiple counties: {list(county_set)}")
            inconsistencies.append(f"FIPS {fips} -> {list(county_set)}")
    
    if not inconsistencies:
        print("✅ All FIPS assignments are consistent across files")
    
    return inconsistencies

def check_specific_counties():
    """Check specific counties that have been problematic"""
    print("\n🎯 Checking specific problematic counties...")
    
    problem_counties = ['MARION', 'MCCORMICK', 'MARLBORO']
    
    with open('./Data/county_results_2024_fips_accurate.json', 'r') as f:
        data = json.load(f)
    
    for county_name in problem_counties:
        found = False
        for fips, county_data in data.items():
            if county_data.get('county', '').upper() == county_name:
                dem_votes = county_data.get('dem_votes', 0)
                rep_votes = county_data.get('rep_votes', 0)
                total_votes = county_data.get('total_votes', 0)
                winner = 'Democratic' if dem_votes > rep_votes else 'Republican'
                
                print(f"✅ {county_name} (FIPS {fips}):")
                print(f"   Dem: {dem_votes:,} | Rep: {rep_votes:,} | Total: {total_votes:,}")
                print(f"   Winner: {winner}")
                found = True
                break
        
        if not found:
            print(f"❌ {county_name} not found in 2024 data")

def check_vote_data_integrity():
    """Check for impossible vote counts or percentages"""
    print("\n🧮 Checking vote data integrity...")
    
    with open('./Data/county_results_2024_fips_accurate.json', 'r') as f:
        data = json.load(f)
    
    issues = []
    
    for fips, county_data in data.items():
        county = county_data.get('county', 'Unknown')
        dem_votes = county_data.get('dem_votes', 0)
        rep_votes = county_data.get('rep_votes', 0)
        other_votes = county_data.get('other_votes', 0)
        total_votes = county_data.get('total_votes', 0)
        
        calculated_total = dem_votes + rep_votes + other_votes
        
        # Check if totals match
        if total_votes != calculated_total and abs(total_votes - calculated_total) > 5:
            issues.append(f"{county}: Total mismatch - recorded: {total_votes}, calculated: {calculated_total}")
        
        # Check for negative votes
        if dem_votes < 0 or rep_votes < 0 or other_votes < 0:
            issues.append(f"{county}: Negative vote counts detected")
        
        # Check for impossibly high percentages
        if total_votes > 0:
            dem_pct = (dem_votes / total_votes) * 100
            rep_pct = (rep_votes / total_votes) * 100
            if dem_pct > 100 or rep_pct > 100:
                issues.append(f"{county}: Impossible percentages - Dem: {dem_pct:.1f}%, Rep: {rep_pct:.1f}%")
    
    if issues:
        print("❌ Vote data issues found:")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"   {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more issues")
    else:
        print("✅ Vote data integrity looks good")

def check_missing_counties():
    """Check for missing counties compared to expected SC counties"""
    print("\n🏛️ Checking for missing counties...")
    
    # Official SC counties (46 total)
    expected_counties = {
        'ABBEVILLE', 'AIKEN', 'ALLENDALE', 'ANDERSON', 'BAMBERG', 'BARNWELL',
        'BEAUFORT', 'BERKELEY', 'CALHOUN', 'CHARLESTON', 'CHEROKEE', 'CHESTER',
        'CHESTERFIELD', 'CLARENDON', 'COLLETON', 'DARLINGTON', 'DILLON',
        'DORCHESTER', 'EDGEFIELD', 'FAIRFIELD', 'FLORENCE', 'GEORGETOWN',
        'GREENVILLE', 'GREENWOOD', 'HAMPTON', 'HORRY', 'JASPER', 'KERSHAW',
        'LANCASTER', 'LAURENS', 'LEE', 'LEXINGTON', 'MARION', 'MARLBORO',
        'MCCORMICK', 'NEWBERRY', 'OCONEE', 'ORANGEBURG', 'PICKENS', 'RICHLAND',
        'SALUDA', 'SPARTANBURG', 'SUMTER', 'UNION', 'WILLIAMSBURG', 'YORK'
    }
    
    with open('./Data/county_results_2024_fips_accurate.json', 'r') as f:
        data = json.load(f)
    
    found_counties = set()
    for county_data in data.values():
        county = county_data.get('county', '').upper()
        if county:
            found_counties.add(county)
    
    missing = expected_counties - found_counties
    extra = found_counties - expected_counties
    
    print(f"Expected: {len(expected_counties)} counties")
    print(f"Found: {len(found_counties)} counties")
    
    if missing:
        print(f"❌ Missing counties: {sorted(missing)}")
    
    if extra:
        print(f"⚠️  Extra counties: {sorted(extra)}")
    
    if not missing and not extra:
        print("✅ All expected counties are present")

def check_candidate_names():
    """Check for inconsistent candidate names"""
    print("\n👥 Checking candidate name consistency...")
    
    with open('./Data/county_results_2024_fips_accurate.json', 'r') as f:
        data = json.load(f)
    
    dem_candidates = set()
    rep_candidates = set()
    
    for county_data in data.values():
        dem_cand = county_data.get('dem_candidate', '').strip()
        rep_cand = county_data.get('rep_candidate', '').strip()
        
        if dem_cand:
            dem_candidates.add(dem_cand)
        if rep_cand:
            rep_candidates.add(rep_cand)
    
    print(f"Democratic candidates found: {len(dem_candidates)}")
    for cand in sorted(dem_candidates):
        print(f"   {cand}")
    
    print(f"Republican candidates found: {len(rep_candidates)}")
    for cand in sorted(rep_candidates):
        print(f"   {cand}")
    
    if len(dem_candidates) > 1 or len(rep_candidates) > 1:
        print("⚠️  Multiple candidate names found - may indicate data inconsistency")

def main():
    print("🕵️ SC Political Map - Data Discrepancy Checker")
    print("=" * 60)
    
    inconsistencies = check_all_fips_assignments()
    check_specific_counties()
    check_vote_data_integrity()
    check_missing_counties()
    check_candidate_names()
    
    print("\n" + "=" * 60)
    if inconsistencies:
        print("❌ SUMMARY: Data discrepancies found!")
        print("Issues to investigate:")
        for issue in inconsistencies:
            print(f"   • {issue}")
    else:
        print("✅ SUMMARY: No major data discrepancies detected!")
    
    print("\n📋 If you're still seeing issues, please specify:")
    print("   • Which counties look wrong?")
    print("   • What contest/year?")
    print("   • What specific data seems incorrect?")

if __name__ == "__main__":
    main()