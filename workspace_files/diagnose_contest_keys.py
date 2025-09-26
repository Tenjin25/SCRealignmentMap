import gzip
import json

def check_contest_keys(results_path):
    with gzip.open(results_path, 'rt', encoding='utf-8') as fh:
        data = json.load(fh)
    print(f"Keys in {results_path}:")
    for k in list(data.keys())[:5]:
        print(f"  {k}")
    print(f"... total keys: {len(data)}")
    # Show a sample value
    sample = list(data.values())[0]
    print("Sample value:")
    for key in sample.keys():
        print(f"  {key}")

if __name__ == '__main__':
    files = [
        'workspace_files/county_results_2006.json.gz',
        'workspace_files/county_results_2008.json.gz',
        'workspace_files/county_results_2012.json.gz',
        'workspace_files/county_results_2014.json.gz',
        'workspace_files/county_results_2016.json.gz',
        'workspace_files/county_results_2018.json.gz',
        'workspace_files/county_results_2020.json.gz',
        'workspace_files/county_results_2022.json.gz',
        'workspace_files/county_results_2024.json.gz',
    ]
    for f in files:
        check_contest_keys(f)
