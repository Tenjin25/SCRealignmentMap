#!/usr/bin/env python3
"""
Script to fix FIPS code assignments in SC election data files.
Corrects the mismatch between official FIPS codes and the county names in election data.
"""

import json
import os
from typing import Dict, Any

# Official FIPS codes for South Carolina counties (from unicede.air-worldwide.com)
OFFICIAL_FIPS_TO_COUNTY = {
    "45001": "ABBEVILLE",
    "45003": "AIKEN", 
    "45005": "ALLENDALE",
    "45007": "ANDERSON",
    "45009": "BAMBERG",
    "45011": "BARNWELL",
    "45013": "BEAUFORT",
    "45015": "BERKELEY",
    "45017": "CALHOUN",
    "45019": "CHARLESTON",
    "45021": "CHEROKEE",
    "45023": "CHESTER",
    "45025": "CHESTERFIELD",
    "45027": "CLARENDON",
    "45029": "COLLETON",
    "45031": "DARLINGTON",
    "45033": "DILLON",
    "45035": "DORCHESTER",
    "45037": "EDGEFIELD",
    "45039": "FAIRFIELD",
    "45041": "FLORENCE",
    "45043": "GEORGETOWN",
    "45045": "GREENVILLE",
    "45047": "GREENWOOD",
    "45049": "HAMPTON",
    "45051": "HORRY",
    "45053": "JASPER",
    "45055": "KERSHAW",
    "45057": "LANCASTER",
    "45059": "LAURENS",
    "45061": "LEE",
    "45063": "LEXINGTON",
    "45065": "MCCORMICK",
    "45067": "MARION",
    "45069": "MARLBORO",
    "45071": "NEWBERRY",
    "45073": "OCONEE",
    "45075": "ORANGEBURG",
    "45077": "PICKENS",
    "45079": "RICHLAND",
    "45081": "SALUDA",
    "45083": "SPARTANBURG",
    "45085": "SUMTER",
    "45087": "UNION",
    "45089": "WILLIAMSBURG",
    "45091": "YORK"
}

def analyze_fips_discrepancies(election_file: str) -> Dict[str, Dict[str, str]]:
    """Analyze discrepancies between official FIPS codes and election data."""
    print(f"\n=== Analyzing {election_file} ===")
    
    with open(election_file, 'r') as f:
        election_data = json.load(f)
    
    discrepancies = {}
    corrections_needed = {}
    
    for fips, data in election_data.items():
        county_in_data = data.get("county", "").upper()
        official_county = OFFICIAL_FIPS_TO_COUNTY.get(fips, "")
        
        if county_in_data != official_county:
            discrepancies[fips] = {
                "current": county_in_data,
                "should_be": official_county
            }
            print(f"❌ FIPS {fips}: Data shows '{county_in_data}' but should be '{official_county}'")
            
            # Find where this county should actually be
            for correct_fips, correct_county in OFFICIAL_FIPS_TO_COUNTY.items():
                if correct_county == county_in_data:
                    corrections_needed[fips] = correct_fips
                    print(f"   → '{county_in_data}' should have FIPS {correct_fips}")
                    break
        else:
            print(f"✅ FIPS {fips}: '{county_in_data}' is correct")
    
    return discrepancies, corrections_needed

def fix_election_data_file(input_file: str, output_file: str, corrections: Dict[str, str]) -> None:
    """Apply FIPS corrections to an election data file."""
    print(f"\n=== Fixing {input_file} → {output_file} ===")
    
    with open(input_file, 'r') as f:
        election_data = json.load(f)
    
    # Create a mapping of data that needs to be moved
    data_to_move = {}
    for incorrect_fips, correct_fips in corrections.items():
        if incorrect_fips in election_data:
            data_to_move[correct_fips] = election_data[incorrect_fips].copy()
            # Update the county_fips field in the data
            data_to_move[correct_fips]["county_fips"] = correct_fips
            # Update the county name to match official FIPS
            data_to_move[correct_fips]["county"] = OFFICIAL_FIPS_TO_COUNTY[correct_fips]
    
    # Remove old entries and add corrected ones
    corrected_data = {}
    
    # Add all data with correct FIPS codes
    for fips, data in election_data.items():
        if fips in corrections:
            # This FIPS code was wrong, data will be moved
            continue
        elif fips in data_to_move:
            # This FIPS code is getting corrected data
            corrected_data[fips] = data_to_move[fips]
        else:
            # This FIPS code is already correct
            corrected_data[fips] = data
    
    # Add any remaining corrected data
    for correct_fips, data in data_to_move.items():
        if correct_fips not in corrected_data:
            corrected_data[correct_fips] = data
    
    # Sort by FIPS code for consistent output
    sorted_data = dict(sorted(corrected_data.items()))
    
    # Write corrected data
    with open(output_file, 'w') as f:
        json.dump(sorted_data, f, indent=2)
    
    print(f"✅ Fixed {len(corrections)} FIPS code assignments")
    print(f"   Total counties: {len(sorted_data)}")

def main():
    """Main function to analyze and fix FIPS codes."""
    
    # Analyze the 2024 file first
    election_file = "Data/county_results_2024_fips_accurate.json"
    
    print("🔍 ANALYZING FIPS CODE DISCREPANCIES")
    print("=" * 50)
    
    discrepancies, corrections = analyze_fips_discrepancies(election_file)
    
    if not discrepancies:
        print("✅ No FIPS code discrepancies found!")
        return
    
    print(f"\n📋 SUMMARY:")
    print(f"   Found {len(discrepancies)} FIPS code discrepancies")
    print(f"   Corrections needed: {len(corrections)}")
    
    print(f"\n🔧 CORRECTION MAPPING:")
    for incorrect_fips, correct_fips in corrections.items():
        incorrect_county = discrepancies[incorrect_fips]["current"]
        correct_county = OFFICIAL_FIPS_TO_COUNTY[correct_fips]
        print(f"   {incorrect_fips} ({incorrect_county}) → {correct_fips} ({correct_county})")
    
    # Apply fixes
    backup_file = election_file.replace(".json", "_backup.json")
    
    print(f"\n💾 Creating backup: {backup_file}")
    import shutil
    shutil.copy2(election_file, backup_file)
    
    print(f"🔧 Applying corrections to {election_file}")
    fix_election_data_file(election_file, election_file, corrections)
    
    print(f"\n✅ FIPS code corrections completed!")
    print(f"   Original data backed up to: {backup_file}")
    print(f"   Fixed data written to: {election_file}")

if __name__ == "__main__":
    main()