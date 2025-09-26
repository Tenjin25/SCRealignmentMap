import csv
import json

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

def list_missing_counties(csv_path, geojson_path, missing_fips):
    fips_lookup = build_fips_lookup(geojson_path)
    county_names = {v: k for k, v in fips_lookup.items()}
    found_counties = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            county = row['county'].strip().upper()
            if county in fips_lookup:
                found_counties.add(fips_lookup[county])
    print('Missing counties in 2008 results but present in CSV:')
    for fips in missing_fips:
        name = county_names.get(fips, 'Unknown')
        if fips in found_counties:
            print(f"{fips}: {name} (FOUND in CSV)")
        else:
            print(f"{fips}: {name} (NOT FOUND in CSV)")

if __name__ == '__main__':
    missing_fips = ['45005', '45007', '45009', '45011', '45013', '45015', '45017', '45019', '45021', '45023', '45025', '45027', '45029', '45031', '45033', '45035']
    list_missing_counties(
        'repo-backup/Data/20081104__sc__general__precinct.csv',
        'tl_2020_45_county20.geojson',
        missing_fips
    )
