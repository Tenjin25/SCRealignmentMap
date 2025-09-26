import gzip
import json
import os

def pad_fips(fips):
    if isinstance(fips, int):
        return str(fips).zfill(5)
    if isinstance(fips, str):
        return fips.zfill(5)
    return None

def build_fips_lookup(geojson_path):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    lookup = {}
    for feature in geojson.get('features', []):
        name = feature['properties'].get('NAME20')
        fips = feature['properties'].get('GEOID20')
        if name and fips:
            lookup[name.strip().upper()] = pad_fips(fips)
    return lookup

def convert_results_to_fips_keys(results_dir, geojson_path):
    fips_lookup = build_fips_lookup(geojson_path)
    for fname in os.listdir(results_dir):
        if fname.startswith('county_results_') and fname.endswith('.json.gz'):
            with gzip.open(os.path.join(results_dir, fname), 'rt', encoding='utf-8') as fh:
                data = json.load(fh)
            # If top-level keys are contest names, try to restructure
            new_data = {}
            for contest_name, county_results in data.items():
                if isinstance(county_results, dict):
                    for county_name, result in county_results.items():
                        key = fips_lookup.get(county_name.strip().upper())
                        if key:
                            new_data[key] = result
                            new_data[key]['county_name'] = county_name
                        else:
                            print(f"Warning: No FIPS for county '{county_name}' in {fname}")
            if new_data:
                out_path = os.path.join(results_dir, fname)
                with gzip.open(out_path, 'wt', encoding='utf-8') as fh:
                    json.dump(new_data, fh)
                print(f"Converted {fname} to FIPS-keyed structure ({len(new_data)} counties)")
            else:
                print(f"No county results found in {fname}")

if __name__ == '__main__':
    convert_results_to_fips_keys('workspace_files', 'tl_2020_45_county20.geojson')
