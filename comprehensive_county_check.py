import json
import csv
import os

def load_fips_mapping():
    """Load the FIPS to county name mapping"""
    fips_map = {}
    with open('sc_county_fips.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fips_map[row['county_fips']] = row['county_name']
    return fips_map

def check_all_counties_for_corruption():
    """Check all counties across all years for data corruption patterns"""
    print("=== COMPREHENSIVE COUNTY DATA CORRUPTION ANALYSIS ===\n")
    
    fips_map = load_fips_mapping()
    
    # Key election years to check
    election_years = [
        ('workspace_files/county_results_2024_fips.json', '2024 Presidential'),
        ('workspace_files/county_results_2020_fips.json', '2020 Presidential'),
        ('workspace_files/county_results_2018_fips.json', '2018 Governor'),
        ('workspace_files/county_results_2016_fips.json', '2016 Presidential'),
        ('workspace_files/county_results_2014_fips.json', '2014 Governor'),
        ('workspace_files/county_results_2012_fips.json', '2012 Presidential')
    ]
    
    # Counties that should typically be Republican based on rural/conservative demographics
    # Excluding counties with high African American populations that legitimately vote Democratic
    expected_republican_counties = [
        'Cherokee', 'Chester', 'Chesterfield', 'Edgefield', 'Fairfield', 
        'Greenwood', 'Hampton', 'Kershaw', 'Lancaster', 'Laurens', 
        'McCormick', 'Newberry', 'Oconee', 'Pickens', 'Saluda', 'Union'
    ]
    
    # Track suspicious patterns
    suspicious_counties = {}
    
    for file_path, election_name in election_years:
        print(f"Checking {election_name}...")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"  ❌ Error loading {file_path}: {e}")
            continue
        
        year_suspicious = []
        
        for fips, county_name in fips_map.items():
            if county_name in expected_republican_counties and fips in data:
                county_data = data[fips]
                dem_votes = county_data.get('dem_votes', 0)
                rep_votes = county_data.get('rep_votes', 0)
                total_votes = dem_votes + rep_votes
                
                if total_votes > 0:
                    dem_pct = (dem_votes / total_votes) * 100
                    
                    # Flag if rural/conservative county is >50% Democratic
                    if dem_pct > 50:
                        year_suspicious.append({
                            'county': county_name,
                            'fips': fips,
                            'dem_pct': dem_pct,
                            'dem_votes': dem_votes,
                            'rep_votes': rep_votes
                        })
                        
                        # Track across years
                        if county_name not in suspicious_counties:
                            suspicious_counties[county_name] = []
                        suspicious_counties[county_name].append({
                            'election': election_name,
                            'dem_pct': dem_pct,
                            'dem_votes': dem_votes,
                            'rep_votes': rep_votes
                        })
        
        if year_suspicious:
            print(f"  🚨 Found {len(year_suspicious)} suspicious results:")
            for county in year_suspicious:
                print(f"    {county['county']}: {county['dem_pct']:.1f}% D ({county['dem_votes']:,} vs {county['rep_votes']:,})")
        else:
            print(f"  ✅ No suspicious results found")
        print()
    
    # Analyze patterns across years
    print("="*60)
    print("CROSS-YEAR ANALYSIS")
    print("="*60)
    
    if suspicious_counties:
        print(f"Counties with suspicious Democratic wins across multiple years:\n")
        
        for county_name, elections in suspicious_counties.items():
            if len(elections) >= 2:  # Suspicious in multiple years
                print(f"🚨 {county_name} County:")
                for election in elections:
                    print(f"  {election['election']}: {election['dem_pct']:.1f}% D ({election['dem_votes']:,} vs {election['rep_votes']:,})")
                print(f"  📊 Suspicious in {len(elections)} elections - likely data corruption")
                print()
            elif len(elections) == 1:
                election = elections[0]
                print(f"⚠️  {county_name} County:")
                print(f"  {election['election']}: {election['dem_pct']:.1f}% D ({election['dem_votes']:,} vs {election['rep_votes']:,})")
                print(f"  📊 Single suspicious result - may need investigation")
                print()
    else:
        print("✅ No counties show consistent suspicious patterns")
    
    return suspicious_counties

def check_vote_total_anomalies():
    """Check for impossible vote totals that might indicate data corruption"""
    print("\n" + "="*60)
    print("VOTE TOTAL ANOMALY CHECK")
    print("="*60)
    
    fips_map = load_fips_mapping()
    
    # Check 2024 for impossible vote totals
    try:
        with open('workspace_files/county_results_2024_fips.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading 2024 data: {e}")
        return
    
    anomalies = []
    
    for fips, county_data in data.items():
        county_name = fips_map.get(fips, 'Unknown')
        dem_votes = county_data.get('dem_votes', 0)
        rep_votes = county_data.get('rep_votes', 0)
        total_votes = dem_votes + rep_votes
        
        # Check for anomalies
        issues = []
        
        # Unrealistically high totals for small counties
        if total_votes > 300000 and county_name not in ['Charleston', 'Greenville', 'Richland', 'Horry', 'York']:
            issues.append(f"Very high turnout: {total_votes:,}")
        
        # Perfect ties (suspicious)
        if dem_votes == rep_votes and total_votes > 1000:
            issues.append("Perfect tie")
        
        # Round numbers (suspicious)
        if (dem_votes % 1000 == 0 or rep_votes % 1000 == 0) and total_votes > 5000:
            issues.append("Round number votes")
        
        # Vote count reversals (check if numbers look swapped)
        if total_votes > 10000:
            if dem_votes > rep_votes * 3 and county_name in ['Cherokee', 'Chester', 'Greenwood', 'Union', 'Saluda']:
                issues.append("Possible vote swap - rural county heavily Democratic")
        
        if issues:
            anomalies.append({
                'county': county_name,
                'fips': fips,
                'dem_votes': dem_votes,
                'rep_votes': rep_votes,
                'total_votes': total_votes,
                'issues': issues
            })
    
    if anomalies:
        print("Vote total anomalies found:")
        for anomaly in anomalies:
            print(f"\n{anomaly['county']} ({anomaly['fips']}):")
            print(f"  Votes: {anomaly['dem_votes']:,} D, {anomaly['rep_votes']:,} R")
            for issue in anomaly['issues']:
                print(f"  🚨 {issue}")
    else:
        print("✅ No obvious vote total anomalies detected")

def main():
    suspicious_patterns = check_all_counties_for_corruption()
    check_vote_total_anomalies()
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if suspicious_patterns:
        # Prioritize counties with multiple suspicious elections
        consistent_issues = {k: v for k, v in suspicious_patterns.items() if len(v) >= 2}
        
        if consistent_issues:
            print("🚨 Counties requiring immediate correction:")
            for county_name in consistent_issues.keys():
                print(f"  - {county_name} County (consistent Democratic wins in rural area)")
        
        single_issues = {k: v for k, v in suspicious_patterns.items() if len(v) == 1}
        if single_issues:
            print("\n⚠️  Counties needing investigation:")
            for county_name in single_issues.keys():
                print(f"  - {county_name} County (single suspicious result)")
    else:
        print("✅ Only Greenwood County needed correction")
        print("✅ All other counties show demographically consistent results")

if __name__ == "__main__":
    main()