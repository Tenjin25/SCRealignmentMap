import json

# Path to your merged county results JSON
json_path = 'workspace_files/all_county_results.json'

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

results_by_year = data.get('results_by_year', {})
print("Years found:", list(results_by_year.keys()))


# List of all SC counties (2024)
all_counties = [
    "ABBEVILLE", "AIKEN", "ALLENDALE", "ANDERSON", "BAMBERG", "BARNWELL", "BEAUFORT", "BERKELEY", "CALHOUN", "CHARLESTON", "CHEROKEE", "CHESTER", "CHESTERFIELD", "CLARENDON", "COLLETON", "DARLINGTON", "DILLON", "DORCHESTER", "EDGEFIELD", "FAIRFIELD", "FLORENCE", "GEORGETOWN", "GREENVILLE", "GREENWOOD", "HAMPTON", "HORRY", "JASPER", "KERSHAW", "LANCASTER", "LAURENS", "LEE", "LEXINGTON", "MARION", "MARLBORO", "MCCORMICK", "NEWBERRY", "OCONEE", "ORANGEBURG", "PICKENS", "RICHLAND", "SALUDA", "SPARTANBURG", "SUMTER", "UNION", "WILLIAMSBURG", "YORK"
]

for year in sorted(results_by_year.keys()):
    print(f"\nYear: {year}")
    for contest_type in results_by_year[year]:
        print(f"  Contest Type: {contest_type}")
        for contest_id in results_by_year[year][contest_type]:
            contest_name = results_by_year[year][contest_type][contest_id].get('contest_name', contest_id)
            print(f"    Contest ID: {contest_id} | Name: {contest_name}")
            # For 2024, list counties present and missing
            if year == "2024":
                results = results_by_year[year][contest_type][contest_id]["results"]
                found_counties = set()
                for key in results:
                    county = results[key]["county"]
                    found_counties.add(county)
                missing = [c for c in all_counties if c not in found_counties]
                print(f"      Counties present: {sorted(found_counties)}")
                if missing:
                    print(f"      Counties missing: {missing}")
                else:
                    print("      All counties present!")
