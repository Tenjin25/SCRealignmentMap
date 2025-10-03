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

def analyze_historical_patterns():
    """Deep analysis of historical voting patterns to identify anomalies"""
    print("=== DEEP HISTORICAL ANALYSIS ===\n")
    
    # Load key years for comparison
    data_2020_pres = load_json_file('workspace_files/county_results_2020_fips.json')
    data_2018_gov = load_json_file('workspace_files/county_results_2018_fips.json')
    data_2016_pres = load_json_file('workspace_files/county_results_2016_fips.json')
    data_2014_gov = load_json_file('workspace_files/county_results_2014_fips.json')
    data_2012_pres = load_json_file('workspace_files/county_results_2012_fips.json')
    
    datasets = {
        '2020_pres': data_2020_pres,
        '2018_gov': data_2018_gov,
        '2016_pres': data_2016_pres,
        '2014_gov': data_2014_gov,
        '2012_pres': data_2012_pres
    }
    
    # Filter out None datasets
    datasets = {k: v for k, v in datasets.items() if v is not None}
    
    if not datasets:
        print("No datasets available for analysis")
        return
    
    print(f"Analyzing {len(datasets)} datasets...")
    
    # Known historically Republican counties in SC (rural, conservative areas)
    # These counties should almost never go Democratic in statewide races
    historical_red_counties = {
        '45003': 'Anderson',      # Rural, conservative
        '45007': 'Bamberg',       # Rural
        '45009': 'Barnwell',      # Rural
        '45015': 'Cherokee',      # Rural, conservative
        '45017': 'Chester',       # Rural
        '45019': 'Chesterfield', # Rural
        '45021': 'Clarendon',     # Rural
        '45025': 'Edgefield',     # Rural
        '45033': 'Fairfield',     # Rural
        '45047': 'Greenwood',     # Semi-rural with university (should still be R)
        '45049': 'Hampton',       # Rural
        '45053': 'Jasper',        # Rural
        '45055': 'Kershaw',       # Rural
        '45057': 'Lancaster',     # Rural
        '45059': 'Laurens',       # Rural
        '45061': 'Lee',           # Rural
        '45065': 'McCormick',     # Very rural
        '45067': 'Marion',        # Rural
        '45069': 'Marlboro',      # Rural
        '45075': 'Saluda',        # Rural
        '45081': 'Union',         # Rural
        '45087': 'Williamsburg'   # Rural
    }
    
    # Known competitive/swing counties
    swing_counties = {
        '45079': 'Sumter',        # Mix of urban/rural
        '45043': 'Georgetown',    # Tourism/retirees
        '45031': 'Florence',      # Regional center
        '45035': 'Greenville',    # Urban but conservative
        '45077': 'Spartanburg',   # Urban but conservative
    }
    
    # Known Democratic counties (urban areas, high African American population)
    historical_blue_counties = {
        '45013': 'Berkeley',      # Charleston metro
        '45019': 'Charleston',    # Urban, diverse
        '45001': 'Allendale',     # High African American %
        '45011': 'Bamberg',       # High African American %
        '45027': 'Dillon',        # High African American %
        '45041': 'Florence',      # Regional center, diverse
        '45061': 'Lee',           # High African American %
        '45083': 'Spartanburg',   # Urban areas
        '45089': 'York'           # Charlotte metro
    }
    
    suspicious_patterns = []
    
    # Check each county across all datasets
    all_counties = set()
    for dataset in datasets.values():
        all_counties.update(dataset.keys())
    
    for county_fips in all_counties:
        county_name = None
        county_results = {}
        
        # Collect results across all years
        for year, dataset in datasets.items():
            if county_fips in dataset:
                data = dataset[county_fips]
                county_name = data.get('county_name', 'Unknown')
                dem_votes = data.get('democratic_votes', 0)
                rep_votes = data.get('republican_votes', 0)
                total_votes = dem_votes + rep_votes
                
                if total_votes > 0:
                    dem_pct = (dem_votes / total_votes) * 100
                    rep_pct = (rep_votes / total_votes) * 100
                    county_results[year] = {
                        'dem_pct': dem_pct,
                        'rep_pct': rep_pct,
                        'dem_votes': dem_votes,
                        'rep_votes': rep_votes,
                        'total_votes': total_votes
                    }
        
        if len(county_results) < 2:
            continue  # Need at least 2 data points
            
        # Analyze patterns
        issues = []
        
        # Check if historically Republican county has Democratic wins
        if county_fips in historical_red_counties:
            dem_wins = sum(1 for result in county_results.values() if result['dem_pct'] > 50)
            if dem_wins > 0:
                issues.append(f"Historically Republican county shows {dem_wins} Democratic wins")
                
        # Check for impossible swings (>40 points between similar elections)
        years = list(county_results.keys())
        for i in range(len(years)):
            for j in range(i+1, len(years)):
                year1, year2 = years[i], years[j]
                result1, result2 = county_results[year1], county_results[year2]
                
                swing = abs(result1['dem_pct'] - result2['dem_pct'])
                if swing > 40:
                    issues.append(f"Massive swing: {year1} {result1['dem_pct']:.1f}%D -> {year2} {result2['dem_pct']:.1f}%D ({swing:+.1f} points)")
        
        # Check for vote totals that don't make sense
        vote_totals = [result['total_votes'] for result in county_results.values()]
        if max(vote_totals) > 3 * min(vote_totals) and min(vote_totals) > 1000:
            issues.append(f"Inconsistent turnout: {min(vote_totals):,} to {max(vote_totals):,}")
            
        # Check for exact same percentages (suspicious)
        dem_pcts = [result['dem_pct'] for result in county_results.values()]
        if len(set(dem_pcts)) < len(dem_pcts):
            issues.append("Duplicate percentages across years (suspicious)")
        
        if issues:
            suspicious_patterns.append({
                'county_name': county_name,
                'fips': county_fips,
                'results': county_results,
                'issues': issues,
                'is_historical_red': county_fips in historical_red_counties,
                'is_swing': county_fips in swing_counties,
                'is_historical_blue': county_fips in historical_blue_counties
            })
    
    return suspicious_patterns

def check_specific_counties():
    """Check specific counties that user mentioned might have issues"""
    print("=== SPECIFIC COUNTY ANALYSIS ===\n")
    
    # Focus on 2020 Presidential and 2018 Governor (most reliable comparisons)
    data_2020 = load_json_file('workspace_files/county_results_2020_fips.json')
    data_2018 = load_json_file('workspace_files/county_results_2018_fips.json')
    
    if not data_2020 or not data_2018:
        print("Missing comparison files")
        return []
    
    # Counties to specifically examine
    counties_to_check = [
        '45047',  # Greenwood (already known issue)
        '45003',  # Anderson (should be very red)
        '45055',  # Kershaw (should be red) 
        '45059',  # Laurens (should be red)
        '45065',  # McCormick (very rural, should be red)
        '45075',  # Saluda (very rural, should be red)
        '45081',  # Union (very rural, should be red)
        '45015',  # Cherokee (should be red)
        '45017',  # Chester (should be red)
    ]
    
    problematic = []
    
    for fips in counties_to_check:
        if fips not in data_2020 or fips not in data_2018:
            continue
            
        # 2020 data
        d2020 = data_2020[fips]
        county_name = d2020.get('county_name', 'Unknown')
        dem_2020 = d2020.get('democratic_votes', 0)
        rep_2020 = d2020.get('republican_votes', 0)
        total_2020 = dem_2020 + rep_2020
        
        # 2018 data
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
        
        # Flag if Democratic in what should be Republican areas
        issues = []
        if dem_pct_2020 > 50:
            issues.append(f"2020: Democratic win ({dem_pct_2020:.1f}%) in rural/conservative county")
        if dem_pct_2018 > 50:
            issues.append(f"2018: Democratic win ({dem_pct_2018:.1f}%) in rural/conservative county")
        if dem_pct_2020 > 45 and dem_pct_2018 > 45:
            issues.append("Consistently competitive in historically safe Republican area")
            
        if issues:
            problematic.append({
                'county_name': county_name,
                'fips': fips,
                'dem_2020': dem_pct_2020,
                'rep_2020': rep_pct_2020,
                'dem_2018': dem_pct_2018,
                'rep_2018': rep_pct_2018,
                'votes_2020': f"{dem_2020:,} D, {rep_2020:,} R",
                'votes_2018': f"{dem_2018:,} D, {rep_2018:,} R",
                'issues': issues
            })
    
    return problematic

def main():
    print("=== ENHANCED DATA DISCREPANCY ANALYSIS ===\n")
    
    # Run specific county checks first
    specific_issues = check_specific_counties()
    if specific_issues:
        print("SPECIFIC COUNTY ISSUES FOUND:")
        for county in specific_issues:
            print(f"\n{county['county_name']} ({county['fips']}):")
            print(f"  2020 Presidential: {county['dem_2020']:.1f}% D, {county['rep_2020']:.1f}% R")
            print(f"  2018 Governor: {county['dem_2018']:.1f}% D, {county['rep_2018']:.1f}% R")
            print(f"  Vote counts 2020: {county['votes_2020']}")
            print(f"  Vote counts 2018: {county['votes_2018']}")
            for issue in county['issues']:
                print(f"  🚨 {issue}")
    else:
        print("No specific county issues detected in primary check")
    
    print("\n" + "="*60 + "\n")
    
    # Run comprehensive historical analysis
    historical_issues = analyze_historical_patterns()
    if historical_issues:
        print(f"HISTORICAL PATTERN ISSUES FOUND ({len(historical_issues)} counties):")
        for county in sorted(historical_issues, key=lambda x: len(x['issues']), reverse=True):
            print(f"\n{county['county_name']} ({county['fips']}):")
            
            # Show category
            category = "Unknown"
            if county['is_historical_red']:
                category = "Historically Republican"
            elif county['is_historical_blue']:
                category = "Historically Democratic" 
            elif county['is_swing']:
                category = "Swing County"
            print(f"  Category: {category}")
            
            # Show results across years
            for year, result in county['results'].items():
                print(f"  {year}: {result['dem_pct']:.1f}% D ({result['dem_votes']:,} votes), {result['rep_pct']:.1f}% R ({result['rep_votes']:,} votes)")
            
            # Show issues
            for issue in county['issues']:
                print(f"  🚨 {issue}")
    else:
        print("No historical pattern issues detected")

if __name__ == "__main__":
    main()