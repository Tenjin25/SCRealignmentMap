import json
import os
import re

def clean_candidate_name(candidate_name, party):
    """Clean candidate name format to 'Name (Party)' format"""
    if not candidate_name:
        return candidate_name
    
    # Remove party prefix if it exists (REP, DEM, etc.)
    name = re.sub(r'^(REP|DEM|LIB|GRN|IND|CON|WFP)\s+', '', candidate_name)
    
    # Remove party suffix in parentheses if it exists
    name = re.sub(r'\s*\([A-Z]+\)$', '', name)
    
    # Add standardized party suffix
    party_short = 'R' if party == 'REP' or party == 'Republican' else 'D' if party == 'DEM' or party == 'Democratic' else party
    
    return f"{name} ({party_short})"

def standardize_candidate_names():
    """Standardize candidate name format across all data files"""
    print("=== STANDARDIZING CANDIDATE NAME FORMAT ===\n")
    
    workspace_dir = './workspace_files'
    files_processed = 0
    changes_made = 0
    
    # Find all county results files
    for filename in os.listdir(workspace_dir):
        if filename.startswith('county_results_') and filename.endswith('_fips.json'):
            file_path = os.path.join(workspace_dir, filename)
            
            print(f"Processing: {filename}")
            
            try:
                # Load the data
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                file_changes = 0
                
                # Process each county
                for fips, county_data in data.items():
                    # Clean Republican candidate name
                    if 'rep_candidate' in county_data and county_data['rep_candidate']:
                        original_rep = county_data['rep_candidate']
                        cleaned_rep = clean_candidate_name(original_rep, 'R')
                        if cleaned_rep != original_rep:
                            county_data['rep_candidate'] = cleaned_rep
                            file_changes += 1
                    
                    # Clean Democratic candidate name  
                    if 'dem_candidate' in county_data and county_data['dem_candidate']:
                        original_dem = county_data['dem_candidate']
                        cleaned_dem = clean_candidate_name(original_dem, 'D')
                        if cleaned_dem != original_dem:
                            county_data['dem_candidate'] = cleaned_dem
                            file_changes += 1
                
                # Save if changes were made
                if file_changes > 0:
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"  ✅ Updated {file_changes} candidate names")
                    changes_made += file_changes
                else:
                    print(f"  📋 No changes needed")
                
                files_processed += 1
                
            except Exception as e:
                print(f"  ❌ Error processing {filename}: {e}")
    
    print(f"\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Files processed: {files_processed}")
    print(f"Total candidate names updated: {changes_made}")
    print("\nCandidate names now use format: 'Name (R)' or 'Name (D)'")

def show_examples():
    """Show examples of the name format changes"""
    print("\n" + "="*60)
    print("EXAMPLE NAME FORMAT CHANGES")
    print("="*60)
    
    examples = [
        ("REP Ellen Weaver", "Ellen Weaver (R)"),
        ("DEM Lisa Ellis", "Lisa Ellis (D)"),
        ("REP Henry McMaster", "Henry McMaster (R)"),
        ("Donald J Trump | Michael R Pence", "Donald J Trump | Michael R Pence (R)"),
        ("Joseph R Biden | Kamala D Harris", "Joseph R Biden | Kamala D Harris (D)")
    ]
    
    for before, after in examples:
        print(f"Before: {before}")
        print(f"After:  {after}")
        print()

def main():
    print("Standardizing candidate name format to remove redundant party prefixes...")
    print("This will change 'REP Ellen Weaver' to 'Ellen Weaver (R)'\n")
    
    show_examples()
    standardize_candidate_names()

if __name__ == "__main__":
    main()