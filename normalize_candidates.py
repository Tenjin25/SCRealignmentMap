"""
Candidate Name Normalization System

Normalizes candidate names within each data file to ensure consistency.
Keeps contests separate (e.g., President 2024 vs President 2020) but ensures
candidate name variations are standardized within each file.
"""

import re
import json
from pathlib import Path

# Known candidate name mappings - maps variations to canonical names
CANDIDATE_MAPPINGS = {
    # 2024 Presidential
    "donald trump": "Donald J. Trump",
    "donald j trump": "Donald J. Trump",
    "donald j. trump": "Donald J. Trump",
    "trump, donald": "Donald J. Trump",
    
    "kamala harris": "Kamala D. Harris",
    "kamala d harris": "Kamala D. Harris",
    "kamala d. harris": "Kamala D. Harris",
    "harris, kamala": "Kamala D. Harris",
    
    # 2020 Presidential
    "joe biden": "Joseph R. Biden",
    "joseph biden": "Joseph R. Biden",
    "joseph r biden": "Joseph R. Biden",
    "joseph r. biden": "Joseph R. Biden",
    "biden, joe": "Joseph R. Biden",
    "biden, joseph": "Joseph R. Biden",
    
    # 2016 Presidential
    "hillary clinton": "Hillary R. Clinton",
    "hillary r clinton": "Hillary R. Clinton",
    "hillary rodham clinton": "Hillary R. Clinton",
    "clinton, hillary": "Hillary R. Clinton",
    
    # 2012 Presidential
    "mitt romney": "Mitt Romney",
    "willard romney": "Mitt Romney",
    "romney, mitt": "Mitt Romney",
    
    "barack obama": "Barack Obama",
    "barack h obama": "Barack Obama",
    "obama, barack": "Barack Obama",
    
    # 2008 Presidential
    "john mccain": "John McCain",
    "john s mccain": "John McCain",
    "mccain, john": "John McCain",
    
    # SC Gubernatorial
    "nikki haley": "Nikki R. Haley",
    "nikki r haley": "Nikki R. Haley",
    "haley, nikki": "Nikki R. Haley",
    
    "vincent sheheen": "Vincent A. Sheheen",
    "vincent a sheheen": "Vincent A. Sheheen",
    "sheheen, vincent": "Vincent A. Sheheen",
    
    "henry mcmaster": "Henry D. McMaster",
    "henry d mcmaster": "Henry D. McMaster",
    "mcmaster, henry": "Henry D. McMaster",
    
    "james smith": "James E. Smith",
    "james e smith": "James E. Smith",
    "smith, james": "James E. Smith",
    
    # SC Senate
    "lindsey graham": "Lindsey O. Graham",
    "lindsey o graham": "Lindsey O. Graham",
    "graham, lindsey": "Lindsey O. Graham",
    
    "jaime harrison": "Jaime R. Harrison",
    "jaime r harrison": "Jaime R. Harrison",
    "harrison, jaime": "Jaime R. Harrison",
    
    "tim scott": "Tim E. Scott",
    "timothy scott": "Tim E. Scott",
    "tim e scott": "Tim E. Scott",
    "scott, tim": "Tim E. Scott",
    
    # 2010 SC Statewide
    "mick zais": "Mick Zais",
    "michael zais": "Mick Zais",
    "zais, mick": "Mick Zais",
    
    "frank holleman": "Frank Holleman",
    "holleman, frank": "Frank Holleman",
    
    "alan wilson": "Alan Wilson",
    "wilson, alan": "Alan Wilson",
    
    "matthew richardson": "Matthew Richardson",
    "richardson, matthew": "Matthew Richardson",
    
    "mark hammond": "Mark Hammond",
    "hammond, mark": "Mark Hammond",
    
    "marjorie johnson": "Marjorie L. Johnson",
    "marjorie l johnson": "Marjorie L. Johnson",
    "johnson, marjorie": "Marjorie L. Johnson",
    
    "curtis loftis": "Curtis Loftis",
    "loftis, curtis": "Curtis Loftis",
    
    "richard eckstrom": "Richard A. Eckstrom",
    "richard a eckstrom": "Richard A. Eckstrom",
    "eckstrom, richard": "Richard A. Eckstrom",
    
    "robert barber": "Robert Barber",
    "barber, robert": "Robert Barber",
    
    "hugh weathers": "Hugh Weathers",
    "weathers, hugh": "Hugh Weathers",
    
    "tom elliott": "Tom E. Elliott",
    "tom e elliott": "Tom E. Elliott",
    "elliott, tom": "Tom E. Elliott",
    
    "ken ard": "Ken Ard",
    "ard, ken": "Ken Ard",
    
    "ashley cooper": "Ashley Cooper",
    "cooper, ashley": "Ashley Cooper",
}

def normalize_name(name):
    """
    Normalize a candidate name to its canonical form, preserving party designation.
    
    Args:
        name: Raw candidate name from any source
        
    Returns:
        Normalized canonical name with party designation
    """
    if not name or not isinstance(name, str):
        return name
    
    # Extract party designation if present
    party_match = re.search(r'\s*\(([DRLIG])\)$', name)
    party_suffix = f" ({party_match.group(1)})" if party_match else ""
    
    # Remove party designation for normalization
    name_without_party = re.sub(r'\s*\([DRLIG]\)$', '', name)
    
    # Basic cleaning
    original = name_without_party
    name_clean = name_without_party.strip()
    name_clean = re.sub(r'\s+', ' ', name_clean)  # Multiple spaces to single
    
    # Create lookup key (lowercase, no periods)
    lookup_key = name_clean.lower().replace('.', '')
    
    # Check direct mapping
    if lookup_key in CANDIDATE_MAPPINGS:
        return CANDIDATE_MAPPINGS[lookup_key] + party_suffix
    
    # If not found, do some smart formatting
    # Capitalize each word properly
    name_clean = ' '.join(word.capitalize() for word in name_clean.split())
    
    print(f"Warning: No mapping found for '{original}' -> using '{name_clean}'")
    return name_clean + party_suffix

def add_candidate_mapping(variation, canonical):
    """
    Add a new candidate name mapping.
    
    Args:
        variation: Name variation to map
        canonical: Canonical name to use
    """
    lookup_key = variation.lower().replace('.', '')
    CANDIDATE_MAPPINGS[lookup_key] = canonical
    print(f"Added mapping: '{variation}' -> '{canonical}'")

def normalize_json_file(filepath, dry_run=True):
    """
    Normalize candidate names in a JSON election data file.
    
    Args:
        filepath: Path to JSON file
        dry_run: If True, only report changes without modifying file
        
    Returns:
        Dictionary with changes made
    """
    changes = {
        'file': str(filepath),
        'dem_candidates': [],
        'rep_candidates': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[!] Skipping {filepath.name}: JSON parse error - {e}")
        return changes
    
    # Process each county's data
    modified = False
    for key, value in data.items():
        if key == 'competitiveness_scale':
            continue
            
        if isinstance(value, dict) and 'dem_candidate' in value:
            # Normalize Democratic candidate
            old_dem = value['dem_candidate']
            new_dem = normalize_name(old_dem)
            if old_dem != new_dem:
                changes['dem_candidates'].append({
                    'old': old_dem,
                    'new': new_dem,
                    'county': value.get('county', 'Unknown')
                })
                if not dry_run:
                    value['dem_candidate'] = new_dem
                    modified = True
            
            # Normalize Republican candidate
            old_rep = value['rep_candidate']
            new_rep = normalize_name(old_rep)
            if old_rep != new_rep:
                changes['rep_candidates'].append({
                    'old': old_rep,
                    'new': new_rep,
                    'county': value.get('county', 'Unknown')
                })
                if not dry_run:
                    value['rep_candidate'] = new_rep
                    modified = True
    
    # Save if modified
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[+] Updated {filepath.name}")
    
    return changes

def normalize_directory(directory_path, pattern="*.json", dry_run=True):
    """
    Normalize candidate names in all JSON files in a directory.
    
    Args:
        directory_path: Path to directory
        pattern: File pattern to match
        dry_run: If True, only report changes without modifying files
        
    Returns:
        List of all changes
    """
    directory = Path(directory_path)
    all_changes = []
    
    print(f"\n{'DRY RUN - ' if dry_run else ''}Normalizing candidate names in {directory}")
    print("=" * 70)
    
    for filepath in sorted(directory.glob(pattern)):
        # Skip backup files
        if 'backup' in filepath.name.lower():
            continue
        
        print(f"\nProcessing: {filepath.name}...", end=" ")
        
        try:
            changes = normalize_json_file(filepath, dry_run=dry_run)
        except Exception as e:
            print(f"[!] ERROR")
            print(f"  {type(e).__name__}: {e}")
            continue
        
        if changes['dem_candidates'] or changes['rep_candidates']:
            all_changes.append(changes)
            
            print(f"[Changes found]:")
            if changes['dem_candidates']:
                dem_change = changes['dem_candidates'][0]
                print(f"  DEM: '{dem_change['old']}' -> '{dem_change['new']}'")
            if changes['rep_candidates']:
                rep_change = changes['rep_candidates'][0]
                print(f"  REP: '{rep_change['old']}' -> '{rep_change['new']}'")
        else:
            print("No changes needed")
    
    print("\n" + "=" * 70)
    print(f"Total files with changes: {len(all_changes)}")
    
    if dry_run:
        print("\nThis was a DRY RUN. No files were modified.")
        print("Run with dry_run=False to apply changes.")
    
    return all_changes

def export_mappings(output_file="candidate_mappings.json"):
    """Export current candidate mappings to JSON file for reference."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(CANDIDATE_MAPPINGS, f, indent=2, ensure_ascii=False)
    print(f"Exported {len(CANDIDATE_MAPPINGS)} mappings to {output_file}")

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python normalize_candidates.py <data_directory> [--apply]")
        print("\nExample:")
        print("  python normalize_candidates.py Data/               # Dry run")
        print("  python normalize_candidates.py Data/ --apply       # Apply changes")
        sys.exit(1)
    
    data_dir = sys.argv[1]
    apply_changes = '--apply' in sys.argv
    
    # Run normalization
    changes = normalize_directory(
        data_dir,
        pattern="county_results_*.json",
        dry_run=not apply_changes
    )
    
    # Optionally export mappings
    if '--export-mappings' in sys.argv:
        export_mappings()
