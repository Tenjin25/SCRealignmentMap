"""
Add competitiveness_scale to JSON files that are missing it
"""

import json
from pathlib import Path

# The competitiveness scale to add
COMPETITIVENESS_SCALE = {
    "Republican": [
        {"category": "Annihilation", "range": "R+40%+", "color": "#67000d", "min": 40.0, "max": 100.0},
        {"category": "Dominant", "range": "R+30-40%", "color": "#a50f15", "min": 30.0, "max": 40.0},
        {"category": "Stronghold", "range": "R+20-30%", "color": "#cb181d", "min": 20.0, "max": 30.0},
        {"category": "Safe", "range": "R+10-20%", "color": "#ef3b2c", "min": 10.0, "max": 20.0},
        {"category": "Likely", "range": "R+5.5-10%", "color": "#fb6a4a", "min": 5.5, "max": 10.0},
        {"category": "Lean", "range": "R+1-5.5%", "color": "#fcae91", "min": 1.0, "max": 5.5},
        {"category": "Tilt", "range": "R+0.5-1%", "color": "#fee8c8", "min": 0.5, "max": 1.0}
    ],
    "Tossup": [
        {"category": "Tossup", "range": "±0.5%", "color": "#f7f7f7", "min": -0.5, "max": 0.5}
    ],
    "Democratic": [
        {"category": "Tilt", "range": "D+0.5-1%", "color": "#e1f5fe", "min": -1.0, "max": -0.5},
        {"category": "Lean", "range": "D+1-5.5%", "color": "#c6dbef", "min": -5.5, "max": -1.0},
        {"category": "Likely", "range": "D+5.5-10%", "color": "#9ecae1", "min": -10.0, "max": -5.5},
        {"category": "Safe", "range": "D+10-20%", "color": "#6baed6", "min": -20.0, "max": -10.0},
        {"category": "Stronghold", "range": "D+20-30%", "color": "#3182bd", "min": -30.0, "max": -20.0},
        {"category": "Dominant", "range": "D+30-40%", "color": "#08519c", "min": -40.0, "max": -30.0},
        {"category": "Annihilation", "range": "D+40%+", "color": "#08306b", "min": -100.0, "max": -40.0}
    ]
}

def fix_json_file(filepath):
    """Add competitiveness_scale to a JSON file if missing"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Check if it already has competitiveness_scale
    if 'competitiveness_scale' in data:
        return False  # Already has it
    
    # Create new structure with competitiveness_scale first
    new_data = {
        'competitiveness_scale': COMPETITIVENESS_SCALE
    }
    
    # Add all existing data
    new_data.update(data)
    
    # Write back
    with open(filepath, 'w') as f:
        json.dump(new_data, f, indent=2)
    
    return True  # Modified

def main():
    print("=" * 80)
    print("ADDING COMPETITIVENESS SCALE TO JSON FILES")
    print("=" * 80)
    
    # Find all JSON files in Data directory
    data_dir = Path('Data')
    json_files = list(data_dir.glob('*.json'))
    
    print(f"\nFound {len(json_files)} JSON files")
    
    modified_files = []
    skipped_files = []
    
    for filepath in sorted(json_files):
        if fix_json_file(filepath):
            modified_files.append(filepath.name)
            print(f"  ✅ Modified: {filepath.name}")
        else:
            skipped_files.append(filepath.name)
            print(f"  ⏭️  Skipped: {filepath.name} (already has scale)")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n✅ Modified: {len(modified_files)} files")
    print(f"⏭️  Skipped: {len(skipped_files)} files")
    
    if modified_files:
        print("\nModified files:")
        for name in modified_files:
            print(f"  • {name}")
    
    print()

if __name__ == '__main__':
    main()
