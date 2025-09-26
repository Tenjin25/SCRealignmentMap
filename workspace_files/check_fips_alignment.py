import gzip
import json
import os

def pad_fips(fips):
    if isinstance(fips, int):
        return str(fips).zfill(5)
    if isinstance(fips, str):
        return fips.zfill(5)
    return None

def check_fips_alignment(geojson_path, results_dir):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    geojson_fips = set()
    for feature in geojson.get('features', []):
        fips = feature['properties'].get('GEOID20')
        if fips:
            geojson_fips.add(pad_fips(fips))
    print(f"GeoJSON counties: {len(geojson_fips)} FIPS codes")
    for fname in os.listdir(results_dir):
        if fname.startswith('county_results_') and fname.endswith('.json.gz'):
            with gzip.open(os.path.join(results_dir, fname), 'rt', encoding='utf-8') as fh:
                data = json.load(fh)
            result_fips = set(pad_fips(fips) for fips in data.keys())
            missing_in_results = geojson_fips - result_fips
            missing_in_geojson = result_fips - geojson_fips
            print(f"{fname}: {len(result_fips)} FIPS codes")
            if missing_in_results:
                print(f"  FIPS in GeoJSON but missing in results: {sorted(missing_in_results)}")
            if missing_in_geojson:
                print(f"  FIPS in results but missing in GeoJSON: {sorted(missing_in_geojson)}")
            if not missing_in_results and not missing_in_geojson:
                print("  All FIPS codes aligned!")

if __name__ == '__main__':
    check_fips_alignment('tl_2020_45_county20.geojson', 'workspace_files')
