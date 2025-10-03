import csv
import json

# Read county FIPS and names from CSV
fips_path = "sc_county_fips.csv"
counties = {}
with open(fips_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        fips = row['county_fips']
        name = row['county_name']
        counties[fips] = {
            "county": name,
            "contest": "President",
            "year": 2008,
            "dem_candidate": None,
            "rep_candidate": None,
            "dem_votes": 0,
            "rep_votes": 0,
            "other_votes": 0,
            "total_votes": 0,
            "two_party_total": 0,
            "margin": 0,
            "margin_pct": None,
            "winner": None,
            "competitiveness": None,
            "all_parties": {},
            "county_fips": fips
        }

nested = {
    "results_by_year": {
        "2008": {
            "president": {
                "contest_name": "President",
                "results": counties
            }
        }
    }
}

with open("Data/county_results_2008_president_nested.json", "w", encoding="utf-8") as f:
    json.dump(nested, f, indent=2)
