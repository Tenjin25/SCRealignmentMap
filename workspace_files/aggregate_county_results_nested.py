# aggregate_county_results_nested.py
"""
Aggregates county-level election results from CSV into a clean nested JSON structure.
Assumes CSV headers: county, precinct, office, district, party, candidate, votes
Optionally uses a FIPS reference CSV: county_name,fips
Output: {
  "county_fips": {
    "county_name": "...",
    "results": {
      "DEM": {"Democratic": vote_count, ...},
      "REP": {"Republican": vote_count, ...},
      ...
    }
  },
  ...
}
"""
import csv
import json
from collections import defaultdict
import os

CSV_PATH = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\20081104__sc__general__precinct.csv"
FIPS_CSV_PATH = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\sc_county_fips.csv"
OUTPUT_JSON_PATH = r"county_results_2008_nested.json"

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
# We'll dynamically detect year and contest from the CSV
results_by_year = defaultdict(lambda: defaultdict(dict))

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
    # Get FIPS code
    fips = fips_map.get(county)
    if not fips:
      fips = county
    contest_key = f"{office.lower()}_{year}"
    # Initialize county entry
    county_entry = results_by_year[year][contest_key].setdefault('results', {}).setdefault(fips, {'county_name': county, 'results': defaultdict(dict)})
    # Aggregate votes
    if candidate:
      county_entry['results'][party][candidate] = county_entry['results'][party].get(candidate, 0) + votes
    # Set contest_name
    results_by_year[year][contest_key]['contest_name'] = office

# --- SAVE OUTPUT ---
with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
  # Convert defaultdicts to dicts
  def dictify(d):
    if isinstance(d, defaultdict):
      d = {k: dictify(v) for k, v in d.items()}
    elif isinstance(d, dict):
      d = {k: dictify(v) for k, v in d.items()}
    return d
  output = {'results_by_year': dictify(results_by_year)}
  json.dump(output, f, indent=2)

print(f'Aggregated nested results saved to {OUTPUT_JSON_PATH}')
