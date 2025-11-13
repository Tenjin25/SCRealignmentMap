import json
import os

# Competitiveness scale definition
COMPETITIVENESS_SCALE = {
    "Republican": [
        {"category": "Annihilation", "range": "R+40%+", "color": "#67000d", "min": 40, "max": 100},
        {"category": "Dominant", "range": "R+30-40%", "color": "#a50f15", "min": 30, "max": 40},
        {"category": "Stronghold", "range": "R+20-30%", "color": "#cb181d", "min": 20, "max": 30},
        {"category": "Safe", "range": "R+10-20%", "color": "#ef3b2c", "min": 10, "max": 20},
        {"category": "Likely", "range": "R+5.5-10%", "color": "#fb6a4a", "min": 5.5, "max": 10},
        {"category": "Lean", "range": "R+1-5.5%", "color": "#fc9272", "min": 1, "max": 5.5},
        {"category": "Tilt", "range": "R+0.5-1%", "color": "#fee8c8", "min": 0.5, "max": 1}
    ],
    "Tossup": [
        {"category": "Tossup", "range": "±0.5%", "color": "#f7f7f7", "min": -0.5, "max": 0.5}
    ],
    "Democratic": [
        {"category": "Tilt", "range": "D+0.5-1%", "color": "#e1f5fe", "min": -1, "max": -0.5},
        {"category": "Lean", "range": "D+1-5.5%", "color": "#b3e5fc", "min": -5.5, "max": -1},
        {"category": "Likely", "range": "D+5.5-10%", "color": "#4fc3f7", "min": -10, "max": -5.5},
        {"category": "Safe", "range": "D+10-20%", "color": "#0288d1", "min": -20, "max": -10},
        {"category": "Stronghold", "range": "D+20-30%", "color": "#01579b", "min": -30, "max": -20},
        {"category": "Dominant", "range": "D+30-40%", "color": "#014a7f", "min": -40, "max": -30},
        {"category": "Annihilation", "range": "D+40%+", "color": "#08306b", "min": -100, "max": -40}
    ]
}

# SC County FIPS to name mapping
COUNTY_NAMES = {
    "45001": "Abbeville", "45003": "Aiken", "45005": "Allendale", "45007": "Anderson",
    "45009": "Bamberg", "45011": "Barnwell", "45013": "Beaufort", "45015": "Berkeley",
    "45017": "Calhoun", "45019": "Charleston", "45021": "Cherokee", "45023": "Chester",
    "45025": "Chesterfield", "45027": "Clarendon", "45029": "Colleton", "45031": "Darlington",
    "45033": "Dillon", "45035": "Dorchester", "45037": "Edgefield", "45039": "Fairfield",
    "45041": "Florence", "45043": "Georgetown", "45045": "Greenville", "45047": "Greenwood",
    "45049": "Hampton", "45051": "Horry", "45053": "Jasper", "45055": "Kershaw",
    "45057": "Lancaster", "45059": "Laurens", "45061": "Lee", "45063": "Lexington",
    "45065": "McCormick", "45067": "Marion", "45069": "Marlboro", "45071": "Newberry",
    "45073": "Oconee", "45075": "Orangeburg", "45077": "Pickens", "45079": "Richland",
    "45081": "Saluda", "45083": "Spartanburg", "45085": "Sumter", "45087": "Union",
    "45089": "Williamsburg", "45091": "York"
}

# Candidate information by contest
CANDIDATES = {
    "2008_u.s._senate": {"dem": "Bob Conley (D)", "rep": "Lindsey Graham (R)"},
    "2010_governor": {"dem": "Vincent Sheheen (D)", "rep": "Nikki Haley (R)"},
    "2010_lieutenant_governor": {"dem": "Ashley Cooper (D)", "rep": "Ken Ard (R)"},
    "2010_attorney_general": {"dem": "Matthew Richardson (D)", "rep": "Alan Wilson (R)"},
    "2010_secretary_of_state": {"dem": "Marjorie L. Johnson (D)", "rep": "Mark Hammond (R)"},
    "2010_state_treasurer": {"dem": "Curtis Loftis (D)", "rep": "Curtis Loftis (R)"},  # Both parties nominated same
    "2010_comptroller_general": {"dem": "Robert J. Clink, Jr. (D)", "rep": "Richard Eckstrom (R)"},
    "2010_commissioner_of_agriculture": {"dem": "Tom E. Elliott (D)", "rep": "Hugh Weathers (R)"},
    "2012_president": {"dem": "Barack Obama (D)", "rep": "Mitt Romney (R)"},
    "2016_u.s._senate": {"dem": "Thomas Dixon (D)", "rep": "Tim Scott (R)"},
    "2024_president": {"dem": "Kamala Harris (D)", "rep": "Donald Trump (R)"}
}

def get_competitiveness(margin_pct):
    """Determine competitiveness category, party, and color based on margin percentage."""
    # Check Republican categories
    for cat in COMPETITIVENESS_SCALE["Republican"]:
        if cat["min"] <= margin_pct < cat["max"]:
            return {
                "category": cat["category"],
                "party": "Republican",
                "color": cat["color"]
            }
    
    # Check Tossup
    for cat in COMPETITIVENESS_SCALE["Tossup"]:
        if cat["min"] <= margin_pct < cat["max"]:
            return {
                "category": cat["category"],
                "party": "Tossup",
                "color": cat["color"]
            }
    
    # Check Democratic categories
    for cat in COMPETITIVENESS_SCALE["Democratic"]:
        if cat["min"] <= margin_pct < cat["max"]:
            return {
                "category": cat["category"],
                "party": "Democratic",
                "color": cat["color"]
            }
    
    # Fallback for edge cases
    if margin_pct >= 40:
        return {"category": "Annihilation", "party": "Republican", "color": "#67000d"}
    elif margin_pct <= -40:
        return {"category": "Annihilation", "party": "Democratic", "color": "#08306b"}
    
    return {"category": "Tossup", "party": "Tossup", "color": "#f7f7f7"}

def fix_json_file(filepath, contest_key):
    """Fix a single JSON file to match the required structure."""
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Create new structure with competitiveness_scale
    new_data = {
        "competitiveness_scale": COMPETITIVENESS_SCALE
    }
    
    # Extract year and contest from key
    parts = contest_key.split('_')
    year = parts[0]
    contest_name = ' '.join(parts[1:]).title().replace('U.S.', 'U.S.')
    
    # Get candidates
    candidates = CANDIDATES.get(contest_key, {"dem": "Unknown", "rep": "Unknown"})
    
    # Process each county
    for fips, county_data in data.items():
        if fips == "competitiveness_scale":
            continue
            
        # Calculate two_party_total
        two_party_total = county_data.get("dem_votes", 0) + county_data.get("rep_votes", 0)
        
        # Recalculate competitiveness with correct format
        margin_pct = county_data.get("margin_pct", 0)
        competitiveness = get_competitiveness(margin_pct)
        
        # Build complete county object
        new_data[fips] = {
            "county": COUNTY_NAMES.get(fips, "Unknown"),
            "contest": contest_name,
            "year": year,
            "dem_candidate": candidates["dem"],
            "rep_candidate": candidates["rep"],
            "county_fips": fips,
            "dem_votes": county_data.get("dem_votes", 0),
            "rep_votes": county_data.get("rep_votes", 0),
            "other_votes": county_data.get("other_votes", 0),
            "all_parties": county_data.get("all_parties", {}),
            "total_votes": county_data.get("total_votes", 0),
            "two_party_total": two_party_total,
            "margin": county_data.get("margin", 0),
            "margin_pct": margin_pct,
            "winner": county_data.get("winner", ""),
            "competitiveness": competitiveness
        }
    
    # Write back to file
    with open(filepath, 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print(f"✓ Fixed {filepath}")

def main():
    data_dir = r"c:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data"
    
    # Files to fix with their contest keys
    files_to_fix = [
        # 2008 Senate
        ("county_results_2008_us_senate_fips_accurate.json", "2008_u.s._senate"),
        ("county_results_2008_u.s._senate_fips_accurate.json", "2008_u.s._senate"),
        ("county_results_2008_us_senate_fips.json", "2008_u.s._senate"),
        ("county_results_2008_u.s._senate_fips.json", "2008_u.s._senate"),
        
        # 2010 contests
        ("county_results_2010_governor_fips_accurate.json", "2010_governor"),
        ("county_results_2010_lieutenant_governor_fips_accurate.json", "2010_lieutenant_governor"),
        ("county_results_2010_attorney_general_fips_accurate.json", "2010_attorney_general"),
        ("county_results_2010_secretary_of_state_fips_accurate.json", "2010_secretary_of_state"),
        ("county_results_2010_state_treasurer_fips_accurate.json", "2010_state_treasurer"),
        ("county_results_2010_comptroller_general_fips_accurate.json", "2010_comptroller_general"),
        ("county_results_2010_commissioner_of_agriculture_fips_accurate.json", "2010_commissioner_of_agriculture"),
        
        # 2012 President
        ("county_results_2012_president_fips_accurate.json", "2012_president"),
        ("county_results_2012_fips_accurate.json", "2012_president"),
        
        # 2016 Senate
        ("county_results_2016_us_senate_fips_accurate.json", "2016_u.s._senate"),
        ("county_results_2016_u.s._senate_fips_accurate.json", "2016_u.s._senate"),
        
        # 2024 President
        ("county_results_2024_president_fips_accurate.json", "2024_president"),
        ("county_results_2024_fips_accurate.json", "2024_president")
    ]
    
    for filename, contest_key in files_to_fix:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            try:
                fix_json_file(filepath, contest_key)
            except Exception as e:
                print(f"✗ Error processing {filename}: {e}")
        else:
            print(f"⚠ File not found: {filename}")
    
    print("\n✓ All files processed!")

if __name__ == "__main__":
    main()
