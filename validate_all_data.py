import json
import os

def load_json_file(filename):
    """Load and return JSON data from file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {filename}")
        return None

def analyze_county_data(county_data, contest_name, year):
    """Analyze county data for potential discrepancies"""
    suspicious_counties = []
    
    for county_fips, data in county_data.items():
        county_name = data.get('county_name', 'Unknown')
        dem_votes = data.get('democratic_votes', 0)
        rep_votes = data.get('republican_votes', 0)
        total_votes = dem_votes + rep_votes
        
        if total_votes == 0:
            continue
            
        dem_percentage = (dem_votes / total_votes) * 100
        rep_percentage = (rep_votes / total_votes) * 100
        margin = abs(dem_percentage - rep_percentage)
        
        # Flag potential issues
        issues = []
        
        # Check for unrealistic vote totals
        if total_votes > 500000:  # Unrealistically high for any SC county
            issues.append(f"Extremely high vote total: {total_votes:,}")
        
        # Check for very close races that might indicate data swapping
        if 48 <= dem_percentage <= 52:
            issues.append(f"Very close race (potential swap): {dem_percentage:.1f}% D, {rep_percentage:.1f}% R")
        
        # Check for exact ties (suspicious)
        if dem_votes == rep_votes:
            issues.append("Exact tie (suspicious)")
        
        # Check for round numbers that might indicate fake data
        if dem_votes % 1000 == 0 or rep_votes % 1000 == 0:
            if total_votes > 5000:  # Only flag if significant vote total
                issues.append(f"Round number votes: D={dem_votes:,}, R={rep_votes:,}")
        
        # Flag counties with very low turnout compared to others
        if total_votes < 1000 and county_name not in ['McCormick', 'Allendale']:  # Known small counties
            issues.append(f"Unusually low turnout: {total_votes:,}")
        
        if issues:
            suspicious_counties.append({
                'county_name': county_name,
                'fips': county_fips,
                'dem_votes': dem_votes,
                'rep_votes': rep_votes,
                'dem_percentage': dem_percentage,
                'rep_percentage': rep_percentage,
                'margin': margin,
                'issues': issues
            })
    
    return suspicious_counties

def check_historical_consistency():
    """Check for counties that flip unrealistically between elections"""
    print("=== CHECKING HISTORICAL CONSISTENCY ===\n")
    
    # Load 2020 Presidential and 2018 Governor data for comparison
    data_2020 = load_json_file('workspace_files/county_results_2020_fips.json')
    data_2018 = load_json_file('workspace_files/county_results_2018_fips.json')
    
    if not data_2020 or not data_2018:
        print("Could not load comparison files")
        return
    
    suspicious_flips = []
    
    for fips in data_2020.keys():
        if fips not in data_2018:
            continue
            
        # 2020 Presidential data
        d2020 = data_2020[fips]
        dem_2020 = d2020.get('democratic_votes', 0)
        rep_2020 = d2020.get('republican_votes', 0)
        total_2020 = dem_2020 + rep_2020
        
        # 2018 Governor data  
        d2018 = data_2018[fips]
        dem_2018 = d2018.get('democratic_votes', 0)
        rep_2018 = d2018.get('republican_votes', 0)
        total_2018 = dem_2018 + rep_2018
        
        if total_2020 == 0 or total_2018 == 0:
            continue
            
        dem_pct_2020 = (dem_2020 / total_2020) * 100
        rep_pct_2020 = (rep_2020 / total_2020) * 100
        dem_pct_2018 = (dem_2018 / total_2018) * 100
        rep_pct_2018 = (rep_2018 / total_2018) * 100
        
        # Check for massive swings (> 30 points)
        dem_swing = dem_pct_2020 - dem_pct_2018
        rep_swing = rep_pct_2020 - rep_pct_2018
        
        if abs(dem_swing) > 30:
            county_name = d2020.get('county_name', 'Unknown')
            suspicious_flips.append({
                'county_name': county_name,
                'fips': fips,
                'dem_2018': dem_pct_2018,
                'dem_2020': dem_pct_2020,
                'dem_swing': dem_swing,
                'rep_2018': rep_pct_2018,
                'rep_2020': rep_pct_2020,
                'rep_swing': rep_swing
            })
    
    if suspicious_flips:
        print("Counties with suspicious swings (>30 points):")
        for county in sorted(suspicious_flips, key=lambda x: abs(x['dem_swing']), reverse=True):
            print(f"  {county['county_name']}:")
            print(f"    2018 Gov: {county['dem_2018']:.1f}% D, {county['rep_2018']:.1f}% R")
            print(f"    2020 Pres: {county['dem_2020']:.1f}% D, {county['rep_2020']:.1f}% R")
            print(f"    Swing: {county['dem_swing']:+.1f}% D, {county['rep_swing']:+.1f}% R")
            print()
    else:
        print("No suspicious swings found")

def main():
    print("=== COMPREHENSIVE DATA VALIDATION ===\n")
    
    # Get list of all county data files
    files_to_check = []
    workspace_dir = './workspace_files'
    if os.path.exists(workspace_dir):
        for file in os.listdir(workspace_dir):
            if file.startswith('county_results_') and file.endswith('_fips.json') and not file.endswith('_corrected.json'):
                files_to_check.append(os.path.join(workspace_dir, file))
    
    print(f"Found {len(files_to_check)} data files to check:")
    for file in files_to_check:
        print(f"  - {file}")
    print()
    
    all_suspicious = []
    
    # Check each file
    for filename in files_to_check:
        print(f"=== ANALYZING {filename} ===")
        
        # Extract year and contest from filename
        parts = filename.replace('county_results_', '').replace('_fips.json', '')
        year = parts[:4]
        contest = parts[5:] if len(parts) > 4 else "Unknown"
        
        data = load_json_file(filename)
        if data:
            suspicious = analyze_county_data(data, contest, year)
            if suspicious:
                print(f"Found {len(suspicious)} suspicious counties:")
                for county in suspicious:
                    print(f"  {county['county_name']} ({county['fips']}):")
                    print(f"    Votes: {county['dem_votes']:,} D, {county['rep_votes']:,} R")
                    print(f"    Percentages: {county['dem_percentage']:.1f}% D, {county['rep_percentage']:.1f}% R")
                    for issue in county['issues']:
                        print(f"    ISSUE: {issue}")
                    print()
                all_suspicious.extend(suspicious)
            else:
                print("No obvious issues found")
        print()
    
    # Check historical consistency
    check_historical_consistency()
    
    # Summary
    if all_suspicious:
        print("=== SUMMARY ===")
        print(f"Total suspicious entries found: {len(all_suspicious)}")
        
        # Group by county name
        by_county = {}
        for entry in all_suspicious:
            county = entry['county_name']
            if county not in by_county:
                by_county[county] = []
            by_county[county].append(entry)
        
        print(f"Counties with issues: {len(by_county)}")
        for county, entries in by_county.items():
            print(f"  {county}: {len(entries)} issue(s)")
    else:
        print("No suspicious data patterns detected")

if __name__ == "__main__":
    main()