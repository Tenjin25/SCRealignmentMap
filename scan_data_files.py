import os
import json
import csv
from collections import Counter

DATA_DIR = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data"
SAMPLE_SIZE = 3

def scan_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        sample_rows = [row for _, row in zip(range(SAMPLE_SIZE), reader)]
    return columns, sample_rows

def scan_json(file_path):
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, list):
            sample_objs = data[:SAMPLE_SIZE]
            keys = set()
            for obj in sample_objs:
                if isinstance(obj, dict):
                    keys.update(obj.keys())
            return list(keys), sample_objs
        elif isinstance(data, dict):
            return list(data.keys()), [data]
        else:
            return [], [data]

def suggest_aggregation(fields):
    suggestions = []
    if 'county' in fields and 'year' in fields and 'votes' in fields:
        suggestions.append("Aggregate total votes by county and year.")
    if 'precinct' in fields:
        suggestions.append("Aggregate by precinct for more granularity.")
    if 'candidate' in fields:
        suggestions.append("Include candidate-level breakdowns if needed.")
    if 'contest' in fields:
        suggestions.append("Consider removing contest-based grouping for simpler output.")
    return suggestions

def main():
    print(f"Scanning data files in: {DATA_DIR}\n")
    # Recursively find all CSV/JSON files
    files = []
    for root, dirs, file_names in os.walk(DATA_DIR):
        for fname in file_names:
            if fname.endswith('.csv') or fname.endswith('.json'):
                files.append(os.path.join(root, fname))
    if not files:
        print("No CSV or JSON files found.")
        return
    for fpath in files:
        fname = os.path.relpath(fpath, DATA_DIR)
        fsize = os.path.getsize(fpath)
        print(f"File: {fname} ({'CSV' if fname.endswith('.csv') else 'JSON'}, {fsize/1024:.1f} KB)")
        try:
            if fname.endswith('.csv'):
                columns, samples = scan_csv(fpath)
            else:
                columns, samples = scan_json(fpath)
            print(f"  Columns/Keys: {columns}")
            print(f"  Sample data:")
            for sample in samples:
                print(f"    {sample}")
            suggestions = suggest_aggregation([c.lower() for c in columns])
            if suggestions:
                print("  Aggregation suggestions:")
                for s in suggestions:
                    print(f"    - {s}")
        except Exception as e:
            print(f"  Error reading file: {e}")
        print()
if __name__ == "__main__":
    main()
