import json
import os
import glob

def get_competitiveness_object(competitiveness_level, winner_party):
    """Convert competitiveness level to proper object structure"""
    
    # Define competitiveness categories and colors
    if competitiveness_level == 1:
        category = "Annihilation " + ("Democratic" if winner_party == "DEM" else "Republican")
        if winner_party == "DEM":
            color = "#08519c"  # Dark blue
        else:  # REP
            color = "#cb181d"  # Dark red
    elif competitiveness_level == 2:
        category = "Stronghold " + ("Democratic" if winner_party == "DEM" else "Republican")
        if winner_party == "DEM":
            color = "#3182bd"  # Medium blue
        else:  # REP
            color = "#fb6a4a"  # Medium red
    elif competitiveness_level == 3:
        category = "Lean " + ("Democratic" if winner_party == "DEM" else "Republican")
        if winner_party == "DEM":
            color = "#6baed6"  # Light blue
        else:  # REP
            color = "#fc9272"  # Light red
    elif competitiveness_level == 4:
        category = "Tossup"
        if winner_party == "DEM":
            color = "#c6dbef"  # Very light blue
        else:  # REP
            color = "#fee0d2"  # Very light red
    else:
        category = "Unknown"
        color = "#e0e0e0"  # Gray
    
    return {
        "category": category,
        "party": "Democratic" if winner_party == "DEM" else "Republican",
        "color": color
    }

def fix_competitiveness_in_file(filepath):
    """Fix competitiveness structure in a single JSON file"""
    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        modified = False
        for fips, county_data in data.items():
            # Check if competitiveness is just a number
            if 'competitiveness' in county_data and isinstance(county_data['competitiveness'], (int, float)):
                competitiveness_level = county_data['competitiveness']
                
                # Determine winner party
                if 'rep_pct' in county_data and 'dem_pct' in county_data:
                    winner_party = "REP" if county_data['rep_pct'] > county_data['dem_pct'] else "DEM"
                elif 'winner' in county_data:
                    winner_party = county_data['winner']
                else:
                    # Fallback: determine from vote counts
                    rep_votes = county_data.get('rep_votes', 0)
                    dem_votes = county_data.get('dem_votes', 0)
                    winner_party = "REP" if rep_votes > dem_votes else "DEM"
                
                # Replace with proper object structure
                county_data['competitiveness'] = get_competitiveness_object(competitiveness_level, winner_party)
                modified = True
        
        if modified:
            # Write back to file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"  ✅ Fixed competitiveness structure")
        else:
            print(f"  ℹ️ No changes needed")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Find all the contest-specific FIPS JSON files that need fixing
# These are the ones generated from CSV data, not the main year files
pattern = "workspace_files/county_results_*_*_fips.json"
files_to_fix = glob.glob(pattern)

# Filter out the main year files (just year, no contest)
contest_files = [f for f in files_to_fix if '_' in os.path.basename(f).replace('county_results_', '').replace('_fips.json', '') and 
                 os.path.basename(f).replace('county_results_', '').replace('_fips.json', '').count('_') >= 1]

print(f"Found {len(contest_files)} contest-specific files to process:")
for f in contest_files:
    print(f"  {os.path.basename(f)}")

print()

# Process each file
for filepath in contest_files:
    fix_competitiveness_in_file(filepath)

print(f"\n✅ Processing complete! Fixed {len(contest_files)} files.")