import json
from pathlib import Path

def convert_2020_senate():
    """
    Convert 2020 US Senate data from workspace_files format to Data format.
    """
    
    # Read the workspace file
    workspace_file = Path('workspace_files/county_results_2020_us_senate_fips.json')
    output_file = Path('Data/county_results_2020_u.s._senate_fips_accurate.json')
    
    print(f"Reading: {workspace_file}")
    
    with open(workspace_file, 'r', encoding='utf-8') as f:
        workspace_data = json.load(f)
    
    # Convert to the proper format
    converted_data = {}
    
    for fips, county_data in workspace_data.items():
        # Extract values
        dem_votes = county_data.get('dem_votes', 0)
        rep_votes = county_data.get('rep_votes', 0)
        total_votes = county_data.get('total_votes', 0)
        
        # Calculate other_votes
        other_votes = total_votes - (dem_votes + rep_votes)
        
        # Calculate two_party_total
        two_party_total = dem_votes + rep_votes
        
        # Calculate margin
        margin = abs(rep_votes - dem_votes)
        margin_pct = (margin / two_party_total * 100) if two_party_total > 0 else 0
        
        # Determine winner
        winner = "REP" if rep_votes > dem_votes else "DEM"
        
        # Build all_parties dict (simple version with just DEM and REP)
        all_parties = {
            "DEM": dem_votes,
            "REP": rep_votes
        }
        if other_votes > 0:
            all_parties[""] = other_votes
        
        # Create the converted entry
        converted_data[fips] = {
            "county": county_data['county'].upper(),
            "contest": "U.S. SENATE",
            "year": "2020",
            "dem_candidate": county_data.get('dem_candidate', 'Jaime Harrison (D)'),
            "rep_candidate": county_data.get('rep_candidate', 'Lindsey Graham (R)'),
            "dem_votes": dem_votes,
            "rep_votes": rep_votes,
            "other_votes": other_votes,
            "total_votes": total_votes,
            "all_parties": all_parties,
            "county_fips": fips,
            "two_party_total": two_party_total,
            "margin": margin,
            "margin_pct": margin_pct,
            "winner": winner,
            "competitiveness": county_data.get('competitiveness', {
                "category": "Unknown",
                "party": "Unknown",
                "color": "#e0e0e0"
            })
        }
    
    # Write to output file
    print(f"Writing to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully created 2020 US Senate file with {len(converted_data)} counties")
    print(f"  Graham vs Harrison - One of the most competitive SC Senate races in history!")

if __name__ == '__main__':
    convert_2020_senate()
