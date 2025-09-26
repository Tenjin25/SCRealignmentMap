import gzip
import json

def pad_fips(fips):
    if isinstance(fips, int):
        return str(fips).zfill(5)
    if isinstance(fips, str):
        return fips.zfill(5)
    return None

def get_missing_fips(results_path, geojson_path):
    with gzip.open(results_path, 'rt', encoding='utf-8') as fh:
        data = json.load(fh)
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    all_fips = set(pad_fips(f['properties']['GEOID20']) for f in geojson['features'])
    missing = [fips for fips in all_fips if fips not in data]
    return missing

def extract_2008_results(v05_path, missing_fips):
    with open(v05_path, 'r', encoding='utf-8') as f:
        v05 = json.load(f)
    results = v05['results_by_year']['2008']['PRES_2008']['results']
    patch = {}
    for fips in missing_fips:
        if fips in results:
            r = results[fips]
            patch[fips] = {
                'county_name': r.get('county_name', ''),
                'dem_votes': r.get('dem_votes', 0),
                'rep_votes': r.get('rep_votes', 0),
                'total_votes': r.get('total_votes', 0),
                'competitiveness_color': '#CCCCCC'  # Default, can be updated later
            }
    return patch

def patch_2008_results(results_path, geojson_path, v05_path):
    missing_fips = get_missing_fips(results_path, geojson_path)
    patch = extract_2008_results(v05_path, missing_fips)
    with gzip.open(results_path, 'rt', encoding='utf-8') as fh:
        data = json.load(fh)
    for fips, result in patch.items():
        data[fips] = result
    with gzip.open(results_path, 'wt', encoding='utf-8') as fh:
        json.dump(data, fh)
    print(f"Patched {results_path} with {len(patch)} counties from v05 structured results.")

if __name__ == '__main__':
    patch_2008_results(
        'workspace_files/county_results_2008.json.gz',
        'tl_2020_45_county20.geojson',
        'sc_election_results_v05_structured.json'
    )
