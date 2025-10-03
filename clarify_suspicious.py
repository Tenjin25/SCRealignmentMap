import json

def check_suspicious_rural_counties():
    """Check counties that should be Republican but show Democratic wins"""
    
    files_to_check = [
        ('workspace_files/county_results_2020_fips_corrected.json', '2020 Presidential'),
        ('workspace_files/county_results_2018_fips_corrected.json', '2018 Governor'),
    ]
    
    # Known rural counties that should almost always be Republican
    rural_counties = [
        '45047',  # Greenwood
        '45065',  # McCormick  
        '45081',  # Union (from manual check, this was labeled "Saluda" but is actually Union)
        '45015',  # Cherokee
        '45023',  # Chester
        '45059',  # Laurens
        '45055',  # Kershaw
    ]
    
    print("Checking for suspicious Democratic wins in rural counties:\n")
    
    for file_path, election_name in files_to_check:
        print(f"=== {election_name} ===")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except:
            print(f"Could not load {file_path}")
            continue
            
        suspicious = []
        
        for fips in rural_counties:
            if fips in data:
                county_info = data[fips]
                county_name = county_info.get('county', 'Unknown')
                dem_votes = county_info.get('dem_votes', 0)
                rep_votes = county_info.get('rep_votes', 0)
                total = dem_votes + rep_votes
                
                if total > 0:
                    dem_pct = (dem_votes / total) * 100
                    if dem_pct > 50:  # Democratic win in rural county
                        suspicious.append({
                            'fips': fips,
                            'county': county_name,
                            'dem_pct': dem_pct,
                            'dem_votes': dem_votes,
                            'rep_votes': rep_votes
                        })
        
        if suspicious:
            print("Suspicious Democratic wins in rural counties:")
            for county in suspicious:
                print(f"  {county['county']} ({county['fips']}): {county['dem_pct']:.1f}% D ({county['dem_votes']:,} vs {county['rep_votes']:,})")
        else:
            print("No suspicious rural Democratic wins found")
        
        print()

if __name__ == "__main__":
    check_suspicious_rural_counties()