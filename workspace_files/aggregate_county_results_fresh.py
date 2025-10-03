# aggregate_county_results_fresh.py
"""
Aggregates county-level election results from CSV into a nested JSON structure matching your example.
Assumes CSV headers: county, precinct, office, district, party, candidate, votes
Optionally uses a FIPS reference CSV: county_name,fips
Output: {
  "results_by_year": {
    "year": {
      "contest_office_year": {
        "results": {
          "CountyNameOrFIPS": {
            "county_name": "...",
            "results": { ... }
          },
          ...
        },
        "contest_name": "..."
      },
      ...
    }
  }
}
"""
import csv
import json
from collections import defaultdict
import os

CSV_PATH = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\20081104__sc__general__precinct.csv"
FIPS_CSV_PATH = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\sc_county_fips.csv"
OUTPUT_JSON_PATH = r"county_results_2008_nested_fresh.json"

# --- LOAD FIPS REFERENCE ---
fips_map = {}
if os.path.exists(FIPS_CSV_PATH):
    with open(FIPS_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['county_name'].strip()
            fips = row['fips'].strip()
            fips_map[name] = fips

# --- AGGREGATE RESULTS ---
results_by_year = defaultdict(lambda: defaultdict(lambda: {'results': defaultdict(lambda: {'county_name': '', 'results': defaultdict(dict)}), 'contest_name': ''}))

with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        county = row['county'].strip()
        party = row['party'].strip()
        candidate = row['candidate'].strip()
        votes = int(row['votes']) if row['votes'].isdigit() else 0
        office = row['office'].strip()
        # Try to get year from row, fallback to 2008 if not present
        year = row.get('year', '2008')
        contest_key = f"{office.lower().replace(' ', '_')}_{year}"
        # Get FIPS code
        fips = fips_map.get(county)
        county_key = fips if fips else county
        # Set contest name
        results_by_year[year][contest_key]['contest_name'] = office
        # Set county name
        results_by_year[year][contest_key]['results'][county_key]['county_name'] = county
        # Aggregate votes
        if candidate:
            results_by_year[year][contest_key]['results'][county_key]['results'][party][candidate] = results_by_year[year][contest_key]['results'][county_key]['results'][party].get(candidate, 0) + votes

# --- SAVE OUTPUT ---
def dictify(d):
    if isinstance(d, defaultdict):
        d = {k: dictify(v) for k, v in d.items()}
    elif isinstance(d, dict):
        d = {k: dictify(v) for k, v in d.items()}
    return d

output = {'results_by_year': dictify(results_by_year)}
with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f'Aggregated nested results saved to {OUTPUT_JSON_PATH}')
