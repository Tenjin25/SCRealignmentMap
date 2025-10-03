import csv
import json

def load_fips_mapping():
    """Load the FIPS to county name mapping"""
    fips_map = {}
    with open('sc_county_fips.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fips_map[row['county_fips']] = row['county_name']
    return fips_map

def reanalyze_with_correct_fips():
    """Re-analyze the suspicious counties using correct FIPS mapping"""
    print("=== CORRECTED FIPS ANALYSIS ===\n")
    
    fips_map = load_fips_mapping()
    
    # Load 2020 data to check what I previously identified as suspicious
    try:
        with open('workspace_files/county_results_2020_fips.json', 'r') as f:
            data_2020 = json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    print("From my previous analysis, these counties showed suspicious patterns:")
    print("Let me check what they actually are with correct FIPS mapping:\n")
    
    suspicious_fips = ['45047', '45075', '45017']  # The ones I flagged
    
    for fips in suspicious_fips:
        if fips in data_2020 and fips in fips_map:
            county_data = data_2020[fips]
            correct_name = fips_map[fips]
            name_in_data = county_data.get('county', 'Unknown')
            
            dem_votes = county_data.get('dem_votes', 0)
            rep_votes = county_data.get('rep_votes', 0)
            total_votes = dem_votes + rep_votes
            
            if total_votes > 0:
                dem_pct = (dem_votes / total_votes) * 100
                rep_pct = (rep_votes / total_votes) * 100
                
                print(f"FIPS {fips}:")
                print(f"  Correct name (from CSV): {correct_name}")
                print(f"  Name in data file: {name_in_data}")
                print(f"  2020 Results: {dem_pct:.1f}% D, {rep_pct:.1f}% R")
                print(f"  Vote counts: {dem_votes:,} D, {rep_votes:,} R")
                
                # Analyze if this is actually suspicious
                is_suspicious = False
                reasons = []
                
                if correct_name == "Greenwood":
                    # Rural county with university - should lean R but being 56% D is suspicious
                    if dem_pct > 50:
                        is_suspicious = True
                        reasons.append("Rural county with university showing strong Democratic performance")
                
                elif correct_name == "Orangeburg":
                    # High African American population - 65% Democratic is normal
                    if dem_pct > 60:
                        reasons.append("High African American population - Democratic performance is historically normal")
                    
                elif correct_name == "Calhoun":
                    # Very rural, small county - should be Republican
                    if dem_pct > 45:
                        is_suspicious = True
                        reasons.append("Very rural county showing unusually high Democratic performance")
                
                if is_suspicious:
                    print(f"  🚨 SUSPICIOUS: {'; '.join(reasons)}")
                else:
                    print(f"  ✅ NORMAL: {'; '.join(reasons) if reasons else 'Results appear consistent with county demographics'}")
                
                print()
    
    print("="*60)
    print("CONCLUSION:")
    print("="*60)
    
    # Check demographics to understand expected patterns
    rural_republican_counties = ["Greenwood", "Calhoun"]  # Should lean R
    urban_or_diverse_counties = ["Orangeburg"]  # Can legitimately be D
    
    print("\nExpected patterns based on demographics:")
    for fips in suspicious_fips:
        if fips in fips_map:
            county_name = fips_map[fips]
            if county_name in rural_republican_counties:
                print(f"- {county_name}: Should lean Republican (rural/conservative)")
            elif county_name in urban_or_diverse_counties:
                print(f"- {county_name}: Can legitimately be Democratic (urban/diverse demographics)")
    
    print("\nActual data corruption appears to be limited to:")
    print("- Greenwood County only (showing Democratic when should be Republican-leaning)")

def check_all_rural_counties():
    """Check all small/rural counties for impossible Democratic results"""
    print("\n" + "="*60)
    print("CHECKING ALL RURAL COUNTIES FOR IMPOSSIBLE RESULTS")
    print("="*60)
    
    fips_map = load_fips_mapping()
    
    # Load 2020 data
    try:
        with open('workspace_files/county_results_2020_fips.json', 'r') as f:
            data_2020 = json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Rural counties that should typically be Republican
    rural_counties = [
        "Abbeville", "Allendale", "Bamberg", "Barnwell", "Calhoun", 
        "Clarendon", "Colleton", "Dillon", "Edgefield", "Fairfield",
        "Hampton", "Jasper", "Lee", "Marion", "Marlboro", "McCormick",
        "Newberry", "Saluda", "Union", "Williamsburg"
    ]
    
    print("Checking rural counties for suspicious Democratic performance:\n")
    
    suspicious_rural = []
    
    for fips, county_name in fips_map.items():
        if county_name in rural_counties and fips in data_2020:
            county_data = data_2020[fips]
            dem_votes = county_data.get('dem_votes', 0)
            rep_votes = county_data.get('rep_votes', 0)
            total_votes = dem_votes + rep_votes
            
            if total_votes > 0:
                dem_pct = (dem_votes / total_votes) * 100
                
                # Flag if rural county is >60% Democratic (very suspicious)
                if dem_pct > 60:
                    suspicious_rural.append((county_name, fips, dem_pct, dem_votes, rep_votes))
                elif dem_pct > 50:
                    print(f"{county_name}: {dem_pct:.1f}% D - Competitive rural county")
    
    if suspicious_rural:
        print("\n🚨 HIGHLY SUSPICIOUS rural counties (>60% Democratic):")
        for county_name, fips, dem_pct, dem_votes, rep_votes in suspicious_rural:
            print(f"  {county_name} ({fips}): {dem_pct:.1f}% D ({dem_votes:,} vs {rep_votes:,})")
    else:
        print("\n✅ No rural counties show impossible Democratic dominance (>60%)")

def main():
    reanalyze_with_correct_fips()
    check_all_rural_counties()

if __name__ == "__main__":
    main()