import gzip
import json
import os

results_dir = 'workspace_files'
results = {}
for f in os.listdir(results_dir):
    if f.startswith('county_results_') and f.endswith('.json.gz'):
        year = f.split('_')[2][:4]
        with gzip.open(os.path.join(results_dir, f), 'rt', encoding='utf-8') as fh:
            data = json.load(fh)
        missing = [c for c, v in data.items() if 'competitiveness_color' not in v or not v['competitiveness_color']]
        results[year] = missing
        print(f'Year {year}: {len(missing)} counties missing competitiveness_color')
        if missing:
            print(missing)
        else:
            print('All counties OK')
