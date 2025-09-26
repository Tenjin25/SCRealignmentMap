import gzip
import json
import os

results_dir = 'workspace_files'
def patch_missing_competitiveness_color(default_color='#CCCCCC'):
    for f in os.listdir(results_dir):
        if f.startswith('county_results_') and f.endswith('.json.gz'):
            year = f.split('_')[2][:4]
            file_path = os.path.join(results_dir, f)
            with gzip.open(file_path, 'rt', encoding='utf-8') as fh:
                data = json.load(fh)
            changed = False
            for county, contests in data.items():
                if 'competitiveness_color' not in contests or not contests['competitiveness_color']:
                    contests['competitiveness_color'] = default_color
                    changed = True
            if changed:
                with gzip.open(file_path, 'wt', encoding='utf-8') as fh:
                    json.dump(data, fh)
                print(f'Patched {file_path} for year {year}')
            else:
                print(f'No patch needed for {file_path} ({year})')

if __name__ == '__main__':
    patch_missing_competitiveness_color()