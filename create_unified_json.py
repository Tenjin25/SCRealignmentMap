"""
Create Unified Election Data JSON

Combines all individual county_results_*.json files into one comprehensive JSON file
organized by county, with all elections for each county in one place.
"""

import json
from pathlib import Path
from collections import defaultdict

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
    
    # Process each file
    for json_file in json_files:
        # Skip U.S. House races
        if "house" in json_file.name.lower() or "u.s._house" in json_file.name.lower():
            print(f"Skipping U.S. House: {json_file.name}")
            continue
            
        print(f"Processing: {json_file.name}")
        
        # Extract election identifier from filename
        # e.g., "county_results_2024_president_fips_accurate.json" -> "2024_president"
        filename_parts = json_file.stem.replace("county_results_", "").replace("_fips_accurate", "").split("_")
        
        # Handle different filename patterns
        if filename_parts[0].isdigit():  # Year is first
            year = filename_parts[0]
            office = "_".join(filename_parts[1:]) if len(filename_parts) > 1 else "president"
            election_key = f"{year}_{office}"
        else:
            continue  # Skip files that don't match expected pattern
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Store competitiveness scale from first file
            if unified["metadata"]["competitiveness_scale"] is None and "competitiveness_scale" in data:
                unified["metadata"]["competitiveness_scale"] = data["competitiveness_scale"]
            
            # Process each county in this election
            for fips, county_data in data.items():
                if fips == "competitiveness_scale":
                    continue
                
                # Initialize county if first time seeing it
                if unified["counties"][fips]["county_name"] is None:
                    unified["counties"][fips]["county_name"] = county_data.get("county", "Unknown")
                    unified["counties"][fips]["fips"] = fips
                
                # Add this election's data
                unified["counties"][fips]["elections"][election_key] = {
                    "contest": county_data.get("contest"),
                    "year": county_data.get("year"),
                    "dem_candidate": county_data.get("dem_candidate"),
                    "rep_candidate": county_data.get("rep_candidate"),
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
                election_desc = f"{county_data.get('year')} {county_data.get('contest', office)}"
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
