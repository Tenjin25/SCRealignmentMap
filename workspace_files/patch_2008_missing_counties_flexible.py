import csv
import gzip
import json
import os
from collections import defaultdict
import re

def pad_fips(fips):
    if isinstance(fips, int):
        return str(fips).zfill(5)
    if isinstance(fips, str):
        return fips.zfill(5)
    return None

def normalize_name(name):
    return re.sub(r'[^A-Z]', '', name.upper())

def build_fips_lookup(geojson_path):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    lookup = {}
    for feature in geojson.get('features', []):
        name = feature['properties'].get('NAME20')
        fips = feature['properties'].get('GEOID20')
        if name and fips:
            lookup[normalize_name(name)] = pad_fips(fips)
    return lookup

def aggregate_precinct_to_county(csv_path, geojson_path):
    fips_lookup = build_fips_lookup(geojson_path)
    county_results = defaultdict(lambda: {'dem_votes': 0, 'rep_votes': 0, 'total_votes': 0, 'county_name': '', 'competitiveness_color': '#CCCCCC'})
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            county = row['county'].strip()
            party = row['party'].strip().upper()
            votes = int(row['votes']) if row['votes'].isdigit() else 0
            norm_county = normalize_name(county)
            key = fips_lookup.get(norm_county)
            if not key:
                continue
            county_results[key]['county_name'] = county
            county_results[key]['total_votes'] += votes
            if party in ['DEM', 'DEMOCRAT', 'DEMOCRATIC']:
                county_results[key]['dem_votes'] += votes
            elif party in ['REP', 'REPUBLICAN']:
                county_results[key]['rep_votes'] += votes
    return county_results

def patch_missing_counties(results_path, csv_path, geojson_path):
    with gzip.open(results_path, 'rt', encoding='utf-8') as fh:
        data = json.load(fh)
    aggregated = aggregate_precinct_to_county(csv_path, geojson_path)
    missing_fips = [fips for fips in aggregated if fips not in data]
    for fips in missing_fips:
        data[fips] = aggregated[fips]
    with gzip.open(results_path, 'wt', encoding='utf-8') as fh:
        json.dump(data, fh)
    print(f"Patched {results_path} with {len(missing_fips)} missing counties from precinct CSV.")

if __name__ == '__main__':
    patch_missing_counties(
        'workspace_files/county_results_2008.json.gz',
        'repo-backup/Data/20081104__sc__general__precinct.csv',
        'tl_2020_45_county20.geojson'
    )
