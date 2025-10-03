import json
import os
import glob

def get_new_competitiveness_category(competitiveness_level, winner_party):
    """Get the new dramatic competitiveness category"""
    
    if competitiveness_level == 1:
        return "Annihilation " + ("Democratic" if winner_party == "DEM" else "Republican")
    elif competitiveness_level == 2:
        return "Stronghold " + ("Democratic" if winner_party == "DEM" else "Republican")
    elif competitiveness_level == 3:
        return "Lean " + ("Democratic" if winner_party == "DEM" else "Republican")
    elif competitiveness_level == 4:
        return "Tossup"
    else:
        return "Unknown"

def determine_competitiveness_level(margin_pct):
    """Determine competitiveness level from margin percentage"""
    
    if margin_pct >= 40:
        return 1  # Annihilation
    elif margin_pct >= 20:
        return 2  # Stronghold
    elif margin_pct >= 10:
        return 3  # Lean
    else:
        return 4  # Tossup

def update_main_file_categories(filepath):
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
                winner = county_data.get('winner', 'REP')
                
                # Calculate competitiveness level
                competitiveness_level = determine_competitiveness_level(margin_pct)
                
                # Update category
                new_category = get_new_competitiveness_category(competitiveness_level, winner)
                
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

# Find all main year FIPS JSON files (not contest-specific)
pattern = "workspace_files/county_results_*_fips.json"
all_files = glob.glob(pattern)

# Filter to get only main year files (no contest suffix)
main_files = [f for f in all_files if '_' not in os.path.basename(f).replace('county_results_', '').replace('_fips.json', '')]

print(f"Found {len(main_files)} main year files to update:")
for f in main_files:
    print(f"  {os.path.basename(f)}")

print()

# Process each file
for filepath in main_files:
    update_main_file_categories(filepath)

print(f"\n✅ Main file category update complete! Updated {len(main_files)} files.")