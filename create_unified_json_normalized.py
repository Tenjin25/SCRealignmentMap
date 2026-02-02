"""
Create Unified Election Data JSON with Normalized Candidate Names

Combines all individual county_results_*.json files into one comprehensive JSON file
organized by county, with all elections for each county in one place.
Standardizes candidate names so they're consistent across all counties.
"""

import json
from pathlib import Path
from collections import defaultdict
import re

def normalize_candidate_name(name, contest_type=None):
    """
    Normalize candidate names to be consistent across counties.
    
    For Governor races, keep running mates (Lt. Governor):
    - "Henry McMaster / Pamela Evette (R)" -> "Henry McMaster / Pamela Evette (R)"
    
    For Presidential races, remove running mates (VP):
    - "John Mccain / Sarah Palin (R)" -> "John McCain (R)"
    - "Joseph R Biden | Kamala D Harris (D)" -> "Joseph R Biden (D)"
    
    For other races:
    - "Tommy Moore (D)" -> "Tommy Moore (D)"
    """
    if not name or name == "":
        return name
    
    # Remove extra party designations like "REP", "Rep", "DEM", "Dem" prefix
    name = re.sub(r'^(REP|DEM|GRN|LIB|CON|IND)\s+', '', name, flags=re.IGNORECASE)
    
    # Remove running mate (VP) from presidential tickets, but keep for governor
    if contest_type and "president" in contest_type.lower():
        # Handle both "/" and "|" separators
        name = re.sub(r'\s*[/|]\s*[^(]+(?=\s*\()', '', name)
    
    # Fix capitalization issues (Mccain -> McCain, Mcmaster -> McMaster, etc.)
    name = re.sub(r'\bMccain\b', 'McCain', name, flags=re.IGNORECASE)
    name = re.sub(r'\bMcmaster\b', 'McMaster', name, flags=re.IGNORECASE)
    name = re.sub(r'\b(tally|pamela|henry|james|mandy|norrell)\b', lambda m: m.group(1).capitalize(), name, flags=re.IGNORECASE)
    
    # Standardize running mate separator to " / " (with spaces)
    name = re.sub(r'\s*/\s*', ' / ', name)
    
    # Ensure space before party designation
    name = re.sub(r'([^\s])\s*\((D|R|IND|GRN|LIB|CON)\)', r'\1 (\2)', name)
    
    return name.strip()

def get_most_common_name(names, contest_type=None):
    """
    From a list of candidate name variants, pick the most common one.
    For governor races: prefer longer names (with running mates)
    For other races: prefer shorter names (without running mates)
    """
    if not names:
        return ""
    
    name_counts = {}
    for name in names:
        name_counts[name] = name_counts.get(name, 0) + 1
    
    # For governor races, prefer longer names (with Lt. Governor)
    # For other races, prefer shorter names
    is_governor = contest_type and "governor" in contest_type.lower()
    
    if is_governor:
        # Sort by count (descending), then by length (descending for governor)
        sorted_names = sorted(name_counts.items(), 
                             key=lambda x: (-x[1], -len(x[0])))
    else:
        # Sort by count (descending), then by length (ascending for others)
        sorted_names = sorted(name_counts.items(), 
                             key=lambda x: (-x[1], len(x[0])))
    
    return sorted_names[0][0]

def create_unified_json(data_dir="Data", output_file="unified_sc_elections.json"):
    """
    Combine all election data files into one unified JSON structure.
    
    Structure:
    {
        "metadata": {
            "description": "...",
            "counties": 46,
            "elections": [...],
            "competitiveness_scale": {...}
        },
        "counties": {
            "45001": {
                "county_name": "Abbeville",
                "fips": "45001",
                "elections": {
                    "2024_president": {...},
                    "2022_governor": {...},
                    ...
                }
            },
            ...
        }
    }
    """
    
    data_path = Path(data_dir)
    
    # Find all *_fips_accurate.json files
    json_files = sorted(data_path.glob("county_results_*_fips_accurate.json"))
    
    print(f"Found {len(json_files)} election data files")
    
    # Initialize unified structure
    unified = {
        "metadata": {
            "description": "Unified South Carolina Election Results (2006-2024)",
            "source": "South Carolina State Election Commission",
            "counties": 46,
            "elections": [],
            "competitiveness_scale": None
        },
        "counties": defaultdict(lambda: {
            "county_name": None,
            "fips": None,
            "elections": {}
        })
    }
    
    # Track candidate names per election for normalization
    election_candidates = defaultdict(lambda: {"dem": [], "rep": []})
    
    # First pass: collect all candidate name variants
    print("\n=== Pass 1: Collecting candidate name variants ===")
    for json_file in json_files:
        # Skip U.S. House races
        if "house" in json_file.name.lower() or "u.s._house" in json_file.name.lower():
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get the first county to determine the contest type
            first_fips = None
            for fips in data.keys():
                if fips != "competitiveness_scale":
                    first_fips = fips
                    break
            
            if not first_fips:
                continue
            
            # Get contest name and year from the data itself
            contest_name = data[first_fips].get("contest", "").lower().replace(" ", "_").replace(".", "")
            year = data[first_fips].get("year", "")
            
            if not contest_name or not year:
                continue
            
            election_key = f"{year}_{contest_name}"
            
            # Store contest type for normalization
            if "contest_type" not in election_candidates[election_key]:
                election_candidates[election_key]["contest_type"] = contest_name
            
            # Collect all candidate name variants for this election
            for fips, county_data in data.items():
                if fips == "competitiveness_scale":
                    continue
                
                dem_name = normalize_candidate_name(county_data.get("dem_candidate", ""), contest_name)
                rep_name = normalize_candidate_name(county_data.get("rep_candidate", ""), contest_name)
                
                if dem_name and dem_name not in election_candidates[election_key]["dem"]:
                    election_candidates[election_key]["dem"].append(dem_name)
                if rep_name and rep_name not in election_candidates[election_key]["rep"]:
                    election_candidates[election_key]["rep"].append(rep_name)
        
        except Exception as e:
            print(f"  Error in pass 1 for {json_file.name}: {e}")
            continue
    
    # Normalize and pick the standard name for each election
    standard_names = {}
    print("\n=== Standardizing candidate names ===")
    for election_key, candidates in election_candidates.items():
        dem_variants = candidates["dem"]
        rep_variants = candidates["rep"]
        contest_type = candidates.get("contest_type", "")
        
        # Normalize all variants
        dem_normalized = [normalize_candidate_name(n, contest_type) for n in dem_variants]
        rep_normalized = [normalize_candidate_name(n, contest_type) for n in rep_variants]
        
        # Pick the most common normalized name
        standard_dem = get_most_common_name(dem_normalized, contest_type) if dem_normalized else ""
        standard_rep = get_most_common_name(rep_normalized, contest_type) if rep_normalized else ""
        
        standard_names[election_key] = {
            "dem": standard_dem,
            "rep": standard_rep
        }
        
        if len(dem_variants) > 1 or len(rep_variants) > 1:
            print(f"\n{election_key}:")
            if len(dem_variants) > 1:
                print(f"  DEM variants: {dem_variants}")
                print(f"  → Standardized: {standard_dem}")
            if len(rep_variants) > 1:
                print(f"  REP variants: {rep_variants}")
                print(f"  → Standardized: {standard_rep}")
    
    # Second pass: build unified structure with normalized names
    print("\n=== Pass 2: Building unified structure ===")
    for json_file in json_files:
        # Skip U.S. House races
        if "house" in json_file.name.lower() or "u.s._house" in json_file.name.lower():
            print(f"Skipping U.S. House: {json_file.name}")
            continue
            
        print(f"Processing: {json_file.name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Store competitiveness scale from first file
            if unified["metadata"]["competitiveness_scale"] is None and "competitiveness_scale" in data:
                unified["metadata"]["competitiveness_scale"] = data["competitiveness_scale"]
            
            # Determine the election key from the actual contest data
            first_fips = None
            for fips in data.keys():
                if fips != "competitiveness_scale":
                    first_fips = fips
                    break
            
            if not first_fips:
                print(f"  Skipping: No county data found")
                continue
            
            # Get contest name and year from the data itself
            contest_name = data[first_fips].get("contest", "").lower().replace(" ", "_").replace(".", "")
            year = data[first_fips].get("year", "")
            
            if not contest_name or not year:
                print(f"  Skipping: Missing contest name or year")
                continue
            
            election_key = f"{year}_{contest_name}"
            print(f"  Election key: {election_key}")
            
            # Get standardized names for this election
            std_dem = standard_names.get(election_key, {}).get("dem", "")
            std_rep = standard_names.get(election_key, {}).get("rep", "")
            
            # Process each county in this election
            for fips, county_data in data.items():
                if fips == "competitiveness_scale":
                    continue
                
                # Initialize county if first time seeing it
                if unified["counties"][fips]["county_name"] is None:
                    unified["counties"][fips]["county_name"] = county_data.get("county", "Unknown")
                    unified["counties"][fips]["fips"] = fips
                
                # Use standardized candidate names
                dem_candidate = std_dem if std_dem else county_data.get("dem_candidate")
                rep_candidate = std_rep if std_rep else county_data.get("rep_candidate")
                
                # Add this election's data
                unified["counties"][fips]["elections"][election_key] = {
                    "contest": county_data.get("contest"),
                    "year": county_data.get("year"),
                    "dem_candidate": dem_candidate,
                    "rep_candidate": rep_candidate,
                    "dem_votes": county_data.get("dem_votes"),
                    "rep_votes": county_data.get("rep_votes"),
                    "other_votes": county_data.get("other_votes"),
                    "total_votes": county_data.get("total_votes"),
                    "two_party_total": county_data.get("two_party_total"),
                    "margin": county_data.get("margin"),
                    "margin_pct": county_data.get("margin_pct"),
                    "winner": county_data.get("winner"),
                    "competitiveness": county_data.get("competitiveness"),
                    "all_parties": county_data.get("all_parties", {})
                }
                
                # Track election in metadata
                election_desc = f"{county_data.get('year')} {county_data.get('contest', contest_name)}"
                if election_desc not in unified["metadata"]["elections"]:
                    unified["metadata"]["elections"].append(election_desc)
        
        except Exception as e:
            print(f"  Error processing {json_file.name}: {e}")
            continue
    
    # Convert defaultdict to regular dict for JSON serialization
    unified["counties"] = dict(unified["counties"])
    
    # Sort elections list
    unified["metadata"]["elections"].sort()
    
    # Write unified JSON
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unified, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Created unified JSON: {output_path}")
    print(f"  Counties: {len(unified['counties'])}")
    print(f"  Elections: {len(unified['metadata']['elections'])}")
    print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    return unified

if __name__ == "__main__":
    create_unified_json()
