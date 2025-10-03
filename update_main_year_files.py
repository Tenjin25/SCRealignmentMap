import json
import os
import glob

def get_new_competitiveness_category(competitiveness_level, winner_party):
    """Get the competitiveness category based on your exact specifications"""
    
    categories = [
        "Annihilation",    # 1 - 40%+
        "Dominant",        # 2 - 30-40%
        "Stronghold",      # 3 - 20-30%
        "Safe",            # 4 - 10-20%
        "Likely",          # 5 - 5.5-10%
        "Lean",            # 6 - 1-5.5%
        "Tilt",            # 7 - 0.5-1%
        "Tossup"           # 8 - ±0.5%
    ]
    
    if competitiveness_level == 8:
        return "Tossup"
    elif 1 <= competitiveness_level <= 7:
        return categories[competitiveness_level - 1]
    else:
        return "Unknown"

def determine_competitiveness_level(margin_pct):
    """Determine competitiveness level from margin percentage using your exact ranges"""
    margin = abs(margin_pct)
    
    if margin >= 40:
        return 1   # Annihilation (40%+)
    elif margin >= 30:
        return 2   # Dominant (30-40%)
    elif margin >= 20:
        return 3   # Stronghold (20-30%)
    elif margin >= 10:
        return 4   # Safe (10-20%)
    elif margin >= 5.5:
        return 5   # Likely (5.5-10%)
    elif margin >= 1:
        return 6   # Lean (1-5.5%)
    elif margin >= 0.5:
        return 7   # Tilt (0.5-1%)
    else:
        return 8   # Tossup (±0.5%)

def get_competitiveness_color(competitiveness_level, winner_party):
    """Get the color for competitiveness level using your exact color specifications"""
    
    # Republican colors
    rep_colors = {
        1: "#67000d",  # Annihilation
        2: "#a50f15",  # Dominant
        3: "#cb181d",  # Stronghold
        4: "#ef3b2c",  # Safe
        5: "#fb6a4a",  # Likely
        6: "#fcae91",  # Lean
        7: "#fee8c8",  # Tilt
        8: "#f7f7f7"   # Tossup
    }
    
    # Democratic colors
    dem_colors = {
        1: "#08306b",  # Annihilation
        2: "#08519c",  # Dominant
        3: "#3182bd",  # Stronghold
        4: "#6baed6",  # Safe
        5: "#9ecae1",  # Likely
        6: "#c6dbef",  # Lean
        7: "#e1f5fe",  # Tilt
        8: "#f7f7f7"   # Tossup
    }
    
    if competitiveness_level == 8:  # Tossup
        return "#f7f7f7"
    elif winner_party == "DEM":
        return dem_colors.get(competitiveness_level, "#e0e0e0")
    else:
        return rep_colors.get(competitiveness_level, "#e0e0e0")

def update_main_year_files(filepath):
    """Update competitiveness categories in main year files"""
    print(f"Updating: {filepath}")
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        modified = False
        for fips, county_data in data.items():
            if 'competitiveness' in county_data and isinstance(county_data['competitiveness'], dict):
                # Get current data
                margin_pct = county_data.get('margin_pct', 0)
                winner = county_data.get('winner', 'DEM')
                
                # Calculate competitiveness level from margin
                competitiveness_level = determine_competitiveness_level(margin_pct)
                
                # Update category and color
                new_category = get_new_competitiveness_category(competitiveness_level, winner)
                new_color = get_competitiveness_color(competitiveness_level, winner)
                
                if (county_data['competitiveness']['category'] != new_category or 
                    county_data['competitiveness']['color'] != new_color):
                    
                    county_data['competitiveness']['category'] = new_category
                    county_data['competitiveness']['party'] = "Democratic" if winner == "DEM" else "Republican"
                    county_data['competitiveness']['color'] = new_color
                    modified = True
        
        if modified:
            # Write back to file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"  ✅ Updated categories")
        else:
            print(f"  ℹ️ No changes needed")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Find all main year files (these are the ones with just year, no specific contest)
main_year_files = [
    "workspace_files/county_results_2006_fips.json",
    "workspace_files/county_results_2008_fips.json", 
    "workspace_files/county_results_2012_fips.json",
    "workspace_files/county_results_2014_fips.json",
    "workspace_files/county_results_2016_fips.json",
    "workspace_files/county_results_2018_fips.json",
    "workspace_files/county_results_2020_fips.json",
    "workspace_files/county_results_2022_fips.json",
    "workspace_files/county_results_2024_fips.json"
]

# Filter to only existing files
existing_files = [f for f in main_year_files if os.path.exists(f)]

print(f"Found {len(existing_files)} main year files to update:")
for f in existing_files:
    print(f"  {os.path.basename(f)}")

print()

# Process each file
for filepath in existing_files:
    update_main_year_files(filepath)

print(f"\n✅ Main year file update complete! Updated {len(existing_files)} files.")