

import json
import csv
import os
import gzip

# Paths
fips_csv_path = 'sc_county_fips.csv'
results_dir = 'workspace_files'

# Load FIPS lookup
fips_lookup = {}
with open(fips_csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fips_lookup[row['county_name'].strip().upper()] = row['county_fips']

# Process all county_results_*.json and .json.gz files

for fname in os.listdir(results_dir):
    # Only process files that are not already FIPS-keyed and do not contain '_fips' in their name
    if fname.startswith('county_results_') and (fname.endswith('.json') or fname.endswith('.json.gz')) and '_fips' not in fname:
        results_path = os.path.join(results_dir, fname)
        output_path = os.path.join(results_dir, fname.replace('.json', '_fips.json').replace('.json.gz', '_fips.json'))
        # Load JSON (handle gzip if needed)
        if fname.endswith('.json.gz'):
            with gzip.open(results_path, 'rt', encoding='utf-8') as f:
                results = json.load(f)
        else:
            with open(results_path, encoding='utf-8') as f:
                results = json.load(f)
        # If top-level is already FIPS-keyed, skip conversion
        if len(results) == 45 and all(k.isdigit() and len(k) == 5 for k in results.keys()):
            print(f"Skipping {fname}: already FIPS-keyed.")
            continue
        # Otherwise, convert
        contest_key = next(iter(results))
        county_results = results[contest_key]
        fips_results = {}
        for county_name, data in county_results.items():
            key = fips_lookup.get(county_name.strip().upper())
            if key:
                fips_results[key] = data
                fips_results[key]['county_fips'] = key
            else:
                print(f"Warning: No FIPS for county '{county_name}' in {fname}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fips_results, f, indent=2)
        print(f"Done. Output written to {output_path}")
