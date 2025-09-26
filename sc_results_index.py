import gzip
import json
import os

# Index file for compressed SC results
# This script lists all available years and contests in the compressed precinct and county results files

precinct_path = 'sc_precinct_results_structured.json.gz'
county_path = 'sc_county_results_structured.json.gz'

index = {}
for file_type, path in [('precinct', precinct_path), ('county', county_path)]:
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        data = json.load(f)
    years = list(data['results_by_year'].keys())
    contests = {}
    for year in years:
        contests[year] = list(data['results_by_year'][year].keys())
    index[file_type] = {'years': years, 'contests_by_year': contests}

with open('sc_results_index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, indent=2)
print('Index file sc_results_index.json created.')
