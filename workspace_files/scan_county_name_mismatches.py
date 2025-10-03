import json
import os
import csv

def pad_fips(fips):
    if isinstance(fips, int):
        return str(fips).zfill(5)
    if isinstance(fips, str):
        return fips.zfill(5)
    return None

def load_geojson_fips_names(geojson_path):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    fips_to_name = {}
    for feature in geojson.get('features', []):
        fips = pad_fips(feature['properties'].get('GEOID20'))
        name = feature['properties'].get('NAME20', '').strip().upper()
        if fips:
            fips_to_name[fips] = name
    return fips_to_name

def scan_county_jsons(results_dir, geojson_path, output_csv):
    fips_to_name = load_geojson_fips_names(geojson_path)
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['year', 'file', 'fips', 'county_name_in_json', 'county_name_geojson', 'mismatch'])
        for fname in os.listdir(results_dir):
            if fname.startswith('county_results_') and fname.endswith('_fips.json'):
                year = fname.split('_')[2]
                with open(os.path.join(results_dir, fname), 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                for fips, entry in data.items():
                    fips_padded = pad_fips(fips)
                    name_json = entry.get('county', '').strip().upper()
                    name_geojson = fips_to_name.get(fips_padded, '')
                    mismatch = name_json != name_geojson
                    if mismatch:
                        writer.writerow([year, fname, fips_padded, name_json, name_geojson, 'YES'])
    print(f"Scan complete. Results written to {output_csv}")

if __name__ == '__main__':
    scan_county_jsons('workspace_files', 'tl_2020_45_county20.geojson', 'workspace_files/county_mismatches.csv')
