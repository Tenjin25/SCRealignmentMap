import json
import os
import csv

def pad_fips(fips):
    if isinstance(fips, int):
        return str(fips).zfill(5)
    if isinstance(fips, str):
        return fips.zfill(5)
    return None

def load_fips_names(csv_path):
    fips_to_name = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fips = pad_fips(row['county_fips'])
            name = row['county_name'].strip().upper()
            fips_to_name[fips] = name
    return fips_to_name

def patch_county_names(results_dir, fips_csv):
    fips_to_name = load_fips_names(fips_csv)
    for fname in os.listdir(results_dir):
        if fname.startswith('county_results_') and fname.endswith('_fips.json'):
            file_path = os.path.join(results_dir, fname)
            with open(file_path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            changed = False
            for fips in ['45045', '45047', '45049']:
                if fips in data:
                    correct_name = fips_to_name.get(fips)
                    if correct_name and data[fips].get('county', '').strip().upper() != correct_name:
                        data[fips]['county'] = correct_name
                        changed = True
            if changed:
                with open(file_path, 'w', encoding='utf-8') as fh:
                    json.dump(data, fh, indent=2)
                print(f"Patched {fname}")

if __name__ == '__main__':
    patch_county_names('workspace_files', 'sc_county_fips.csv')
