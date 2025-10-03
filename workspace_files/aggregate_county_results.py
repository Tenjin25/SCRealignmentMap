# aggregate_county_results.py
"""
Aggregates county-level election results from CSV and fills a nested JSON template.
Assumes CSV headers: county, precinct, office, district, party, candidate, votes
Assumes template JSON structure keyed by year, contest, and county FIPS.
"""
import csv
import json
from collections import defaultdict

# --- CONFIG ---
import os

CSV_PATH = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\20081104__sc__general__precinct.csv"  # Update path if needed
TEMPLATE_JSON_PATH = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\workspace_files\county_results_2008_president_nested.json"  # Update path if needed
OUTPUT_JSON_PATH = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\workspace_files\county_results_2008_president_filled.json"

# Check if input files exist
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")
if not os.path.exists(TEMPLATE_JSON_PATH):
    raise FileNotFoundError(f"Template JSON file not found: {TEMPLATE_JSON_PATH}")

# --- LOAD TEMPLATE ---
with open(TEMPLATE_JSON_PATH, 'r', encoding='utf-8') as f:
    template = json.load(f)


# --- AGGREGATE RESULTS ---
county_results = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
county_candidates = defaultdict(lambda: defaultdict(set))

with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        county = row['county'].strip()
        party = row['party'].strip()
        candidate = row['candidate'].strip()
        votes = int(row['votes']) if row['votes'].isdigit() else 0
        # Aggregate votes by county, party, candidate
        county_results[county][party][candidate] += votes
        county_candidates[county][party].add(candidate)

# --- FILL TEMPLATE (updated for actual structure) ---
results_by_year = template['results_by_year']
for year, contests in results_by_year.items():
    for contest, counties in contests.items():
        # Only process the 'results' key
        if 'results' not in counties:
            continue
        for county_fips, county_data in counties['results'].items():
            county_name = county_data.get('county', '').strip()
            results = county_results.get(county_name, {})
            candidates = county_candidates.get(county_name, {})
            # Fill results for each party
            for party, cand_votes in results.items():
                party_obj = county_data.setdefault('results', {}).setdefault(party, {})
                for candidate, votes in cand_votes.items():
                    party_obj[candidate] = votes
            # Optionally, add candidate list
            county_data['candidates'] = {p: sorted(list(candidates[p])) for p in candidates}

# --- SAVE OUTPUT ---
with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(template, f, indent=2)

print(f'Aggregated results saved to {OUTPUT_JSON_PATH}')
