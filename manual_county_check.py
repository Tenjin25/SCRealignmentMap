import json

def check_county_in_file(filename, fips, county_name):
    """Check specific county data in a file"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        if fips in data:
            county_data = data[fips]
            # Try both field name formats
            dem_votes = county_data.get('democratic_votes', county_data.get('dem_votes', 0))
            rep_votes = county_data.get('republican_votes', county_data.get('rep_votes', 0))
            county_name_in_data = county_data.get('county_name', county_data.get('county', 'Unknown'))
            total_votes = dem_votes + rep_votes
            
            if total_votes > 0:
                dem_pct = (dem_votes / total_votes) * 100
                rep_pct = (rep_votes / total_votes) * 100
                
                print(f"{county_name} ({fips}) in {filename}:")
                print(f"  Democratic: {dem_votes:,} votes ({dem_pct:.1f}%)")
                print(f"  Republican: {rep_votes:,} votes ({rep_pct:.1f}%)")
                print(f"  Winner: {'Democratic' if dem_pct > rep_pct else 'Republican'}")
                print(f"  Margin: {abs(dem_pct - rep_pct):.1f} points")
                
                # Flag suspicious results
                if dem_pct > 50 and county_name in ['McCormick', 'Saluda', 'Union', 'Cherokee', 'Chester']:
                    print(f"  🚨 SUSPICIOUS: Rural county won by Democrat")
                
                return {
                    'dem_pct': dem_pct,
                    'rep_pct': rep_pct,
                    'dem_votes': dem_votes,
                    'rep_votes': rep_votes,
                    'winner': 'Democratic' if dem_pct > rep_pct else 'Republican'
                }
            else:
                print(f"{county_name} ({fips}): No vote data")
                return None
        else:
            print(f"{county_name} ({fips}): Not found in {filename}")
            return None
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def main():
    print("=== MANUAL COUNTY INSPECTION ===\n")
    
    # Test files
    files_to_check = [
        'workspace_files/county_results_2020_fips.json',
        'workspace_files/county_results_2018_fips.json',
        'workspace_files/county_results_2016_fips.json',
        'workspace_files/county_results_2014_fips.json'
    ]
    
    # Very rural counties that should almost always be Republican
    test_counties = [
        ('45065', 'McCormick'),   # Smallest county, very rural
        ('45075', 'Saluda'),      # Very rural
        ('45081', 'Union'),       # Very rural
        ('45015', 'Cherokee'),    # Rural
        ('45017', 'Chester'),     # Rural
        ('45047', 'Greenwood'),   # We know this one has issues
        ('45059', 'Laurens'),     # Rural
        ('45055', 'Kershaw'),     # Rural
    ]
    
    for filename in files_to_check:
        print(f"\n{'='*60}")
        print(f"ANALYZING: {filename}")
        print('='*60)
        
        year = filename.split('_')[2]  # Extract year
        
        for fips, county_name in test_counties:
            result = check_county_in_file(filename, fips, county_name)
            print()  # Add spacing
    
    print("\n" + "="*60)
    print("CROSS-CHECKING SPECIFIC SUSPICIOUS PATTERNS")
    print("="*60)
    
    # Let's also check for counties that have impossible vote totals
    print("\nChecking for impossible vote totals...")
    
    # Load 2020 data to check vote totals
    try:
        with open('workspace_files/county_results_2020_fips.json', 'r') as f:
            data_2020 = json.load(f)
        
        suspicious_totals = []
        for fips, county_data in data_2020.items():
            county_name = county_data.get('county_name', county_data.get('county', 'Unknown'))
            dem_votes = county_data.get('democratic_votes', county_data.get('dem_votes', 0))
            rep_votes = county_data.get('republican_votes', county_data.get('rep_votes', 0))
            total_votes = dem_votes + rep_votes
            
            # Flag counties with suspiciously high or low totals
            if total_votes > 200000:  # Very high for SC county
                suspicious_totals.append((county_name, fips, total_votes, "Very high"))
            elif total_votes < 500 and county_name not in ['McCormick']:  # Very low (except McCormick)
                suspicious_totals.append((county_name, fips, total_votes, "Very low"))
            elif dem_votes == rep_votes and total_votes > 1000:  # Perfect ties
                suspicious_totals.append((county_name, fips, total_votes, "Perfect tie"))
                
        if suspicious_totals:
            print("\nSuspicious vote totals found:")
            for county_name, fips, total, reason in suspicious_totals:
                print(f"  {county_name} ({fips}): {total:,} votes - {reason}")
        else:
            print("No obviously suspicious vote totals found")
            
    except Exception as e:
        print(f"Error checking vote totals: {e}")

if __name__ == "__main__":
    main()