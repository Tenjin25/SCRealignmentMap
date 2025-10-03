import csv
import json
from collections import defaultdict

# Load county FIPS reference
fips_path = "sc_county_fips.csv"
county_fips = {}
with open(fips_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get("county_name") or row.get("County") or row.get("NAME")
        fips = row.get("fips") or row.get("FIPS") or row.get("COUNTYFP")
        if name and fips:
            county_fips[name.strip().lower()] = fips.strip()

# Aggregate from precinct-level CSV to county-level JSON
input_csv = "Data/20081104__sc__general__precinct.csv"  # Change to desired file
output_json = "county_aggregates_2008_new.json"

# Only include President, US Senate, and statewide offices
include_keywords = ["president", "us senate", "governor", "secretary of state", "attorney general", "treasurer", "comptroller", "superintendent", "agriculture", "lieutenant governor"]
exclude_keywords = ["state house", "us house", "state senate", "house", "senate district"]

def office_ok(office):
    office_l = office.lower()
    return any(k in office_l for k in include_keywords) and not any(x in office_l for x in exclude_keywords)

county_results = defaultdict(lambda: defaultdict(int))
with open(input_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        office = row.get("office") or row.get("OFFICE")
        candidate = row.get("candidate") or row.get("CANDIDATE")
        party = row.get("party") or row.get("PARTY")
        votes = row.get("votes") or row.get("VOTES")
        county = row.get("county") or row.get("COUNTY")
        if not office or not candidate or not party or not votes or not county:
            continue
        if not office_ok(office):
            continue
        try:
            votes = int(votes)
        except:
            continue
        county_key = county.strip().lower()
        fips = county_fips.get(county_key)
        if not fips:
            continue
        # Aggregate by FIPS
        county_results[fips][f"{office}|{candidate}|{party}"] += votes

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(county_results, f, indent=2)
print(f"County-level results saved to {output_json}")
