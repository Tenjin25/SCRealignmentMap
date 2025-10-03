import json
import os

results_dir = 'workspace_files'
scan_output = 'workspace_files/scan_county_json_output.txt'

with open(scan_output, 'w', encoding='utf-8') as out:
    for fname in os.listdir(results_dir):
        if fname.endswith('_fips.json'):
            path = os.path.join(results_dir, fname)
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
            out.write(f"{fname}: {len(data)} counties\n")
            # Optionally, list FIPS codes
            out.write(f"FIPS codes: {sorted(data.keys())}\n\n")
print(f"Scan complete. See {scan_output}")
