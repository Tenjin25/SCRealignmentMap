import requests
import json
import time

# SC County FIPS codes and ENR IDs for 2010
COUNTIES = {
    "45001": {"name": "Abbeville", "enr_id": "40479"},
    "45003": {"name": "Aiken", "enr_id": "40481"},
    "45005": {"name": "Allendale", "enr_id": "40483"},
    "45007": {"name": "Anderson", "enr_id": "40485"},
    "45009": {"name": "Bamberg", "enr_id": "40487"},
    "45011": {"name": "Barnwell", "enr_id": "40489"},
    "45013": {"name": "Beaufort", "enr_id": "40491"},
    "45015": {"name": "Berkeley", "enr_id": "40493"},
    "45017": {"name": "Calhoun", "enr_id": "40495"},
    "45019": {"name": "Charleston", "enr_id": "40497"},
    "45021": {"name": "Cherokee", "enr_id": "40499"},
    "45023": {"name": "Chester", "enr_id": "40501"},
    "45025": {"name": "Chesterfield", "enr_id": "40503"},
    "45027": {"name": "Clarendon", "enr_id": "40505"},
    "45029": {"name": "Colleton", "enr_id": "40507"},
    "45031": {"name": "Darlington", "enr_id": "40509"},
    "45033": {"name": "Dillon", "enr_id": "40511"},
    "45035": {"name": "Dorchester", "enr_id": "40513"},
    "45037": {"name": "Edgefield", "enr_id": "40515"},
    "45039": {"name": "Fairfield", "enr_id": "40517"},
    "45041": {"name": "Florence", "enr_id": "40519"},
    "45043": {"name": "Georgetown", "enr_id": "40521"},
    "45045": {"name": "Greenville", "enr_id": "40523"},
    "45047": {"name": "Greenwood", "enr_id": "40525"},
    "45049": {"name": "Hampton", "enr_id": "40527"},
    "45051": {"name": "Horry", "enr_id": "40529"},
    "45053": {"name": "Jasper", "enr_id": "40531"},
    "45055": {"name": "Kershaw", "enr_id": "40533"},
    "45057": {"name": "Lancaster", "enr_id": "40535"},
    "45059": {"name": "Laurens", "enr_id": "40537"},
    "45061": {"name": "Lee", "enr_id": "40539"},
    "45063": {"name": "Lexington", "enr_id": "40541"},
    "45065": {"name": "McCormick", "enr_id": "40543"},
    "45067": {"name": "Marion", "enr_id": "40545"},
    "45069": {"name": "Marlboro", "enr_id": "40547"},
    "45071": {"name": "Newberry", "enr_id": "40549"},
    "45073": {"name": "Oconee", "enr_id": "40551"},
    "45075": {"name": "Orangeburg", "enr_id": "40553"},
    "45077": {"name": "Pickens", "enr_id": "40555"},
    "45079": {"name": "Richland", "enr_id": "40557"},
    "45081": {"name": "Saluda", "enr_id": "40559"},
    "45083": {"name": "Spartanburg", "enr_id": "40561"},
    "45085": {"name": "Sumter", "enr_id": "40563"},
    "45087": {"name": "Union", "enr_id": "40565"},
    "45089": {"name": "Williamsburg", "enr_id": "40567"},
    "45091": {"name": "York", "enr_id": "40569"}
}

# Contest ID for State Superintendent of Education
CONTEST_ID = "1004"  # This is the typical contest ID for Superintendent in SC ENR

def fetch_county_data(fips, county_info):
    """Fetch superintendent data for a single county from ENR."""
    county_name = county_info["name"]
    enr_id = county_info["enr_id"]
    
    url = f"https://www.enr-scvotes.org/SC/{enr_id}/{CONTEST_ID}/json/sum.json"
    
    print(f"Fetching {county_name} County (FIPS {fips})...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract candidate votes
        candidates = {}
        for choice in data.get("Choices", []):
            party = choice.get("Party", "")
            votes = choice.get("Votes", 0)
            candidate = choice.get("Choice", "")
            
            if party in ["DEM", "REP"]:
                candidates[party] = {
                    "name": candidate,
                    "votes": votes
                }
            elif party in ["UNC", "NON", "CON", "LIB", "GRN"]:
                candidates.setdefault("other", 0)
                candidates["other"] += votes
        
        if "DEM" in candidates and "REP" in candidates:
            dem_votes = candidates["DEM"]["votes"]
            rep_votes = candidates["REP"]["votes"]
            other_votes = candidates.get("other", 0)
            total_votes = dem_votes + rep_votes + other_votes
            two_party_total = dem_votes + rep_votes
            margin = rep_votes - dem_votes
            margin_pct = round((margin / two_party_total * 100), 2) if two_party_total > 0 else 0
            
            return {
                "fips": fips,
                "county": county_name,
                "dem_candidate": candidates["DEM"]["name"],
                "rep_candidate": candidates["REP"]["name"],
                "dem_votes": dem_votes,
                "rep_votes": rep_votes,
                "other_votes": other_votes,
                "total_votes": total_votes,
                "two_party_total": two_party_total,
                "margin": margin,
                "margin_pct": margin_pct,
                "winner": "REP" if margin > 0 else "DEM"
            }
        else:
            print(f"  ⚠ Missing DEM or REP candidate data")
            return None
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None

def main():
    results = {}
    
    for fips, county_info in COUNTIES.items():
        county_data = fetch_county_data(fips, county_info)
        if county_data:
            results[fips] = county_data
            print(f"  ✓ {county_data['county']}: {county_data['dem_candidate']} {county_data['dem_votes']:,} vs {county_data['rep_candidate']} {county_data['rep_votes']:,}")
        time.sleep(0.5)  # Rate limiting
    
    # Save results
    output_file = "Data/county_results_2010_superintendent_raw.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Extracted {len(results)} counties")
    print(f"✓ Saved to {output_file}")
    
    # Calculate statewide totals
    total_dem = sum(c["dem_votes"] for c in results.values())
    total_rep = sum(c["rep_votes"] for c in results.values())
    total_other = sum(c["other_votes"] for c in results.values())
    print(f"\nStatewide totals:")
    print(f"  DEM: {total_dem:,}")
    print(f"  REP: {total_rep:,}")
    print(f"  Other: {total_other:,}")
    print(f"  Margin: R+{(total_rep - total_dem):,} ({((total_rep - total_dem) / (total_dem + total_rep) * 100):.2f}%)")

if __name__ == "__main__":
    main()
