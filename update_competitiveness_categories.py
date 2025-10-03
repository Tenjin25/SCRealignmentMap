import json
import os
import glob

def get_new_competitiveness_category(competitiveness_level, winner_party):
    """Get the competitiveness category based on exact specifications"""
    
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

def determine_competitiveness_level(rep_pct, dem_pct):
    """Determine competitiveness level from percentages using exact ranges"""
    margin = abs(rep_pct - dem_pct)
    
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

def update_competitiveness_categories(filepath):
    """Update competitiveness categories in a JSON file"""
    print(f"Updating: {filepath}")
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        modified = False
        for fips, county_data in data.items():
            if 'competitiveness' in county_data and isinstance(county_data['competitiveness'], dict):
                # Get current data
                rep_pct = county_data.get('rep_pct', 0)
                dem_pct = county_data.get('dem_pct', 0)
                winner_party = "REP" if rep_pct > dem_pct else "DEM"
                
                # Calculate competitiveness level
                competitiveness_level = determine_competitiveness_level(rep_pct, dem_pct)
                
                # Update category
                new_category = get_new_competitiveness_category(competitiveness_level, winner_party)
                
                if county_data['competitiveness']['category'] != new_category:
                    county_data['competitiveness']['category'] = new_category
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

# Find all contest-specific FIPS JSON files
pattern = "workspace_files/county_results_*_*_fips.json"
files_to_update = glob.glob(pattern)

# Filter out the main year files (just year, no contest)
contest_files = [f for f in files_to_update if '_' in os.path.basename(f).replace('county_results_', '').replace('_fips.json', '') and 
                 os.path.basename(f).replace('county_results_', '').replace('_fips.json', '').count('_') >= 1]

print(f"Found {len(contest_files)} contest-specific files to update:")
for f in contest_files[:5]:  # Show first 5
    print(f"  {os.path.basename(f)}")
if len(contest_files) > 5:
    print(f"  ... and {len(contest_files) - 5} more")

print()

# Process each file
for filepath in contest_files:
    update_competitiveness_categories(filepath)

print(f"\n✅ Category update complete! Updated {len(contest_files)} files.")