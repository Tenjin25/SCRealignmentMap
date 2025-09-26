# scan_unique_contests.py
"""
Scans all CSVs in the main Data folder and subfolders for unique contest names (office column).
Outputs a summary of contests per file.

Dependencies: pandas
"""
import os
import pandas as pd

data_root = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data'
out_path = os.path.join(data_root, 'unique_contests_by_file.txt')

csv_files = []
for root, dirs, files in os.walk(data_root):
    for f in files:
        if f.lower().endswith('.csv'):
            csv_files.append(os.path.join(root, f))

summary = []
for csv in csv_files:
    try:
        df = pd.read_csv(csv, usecols=['office'])
        contests = sorted(set(df['office'].dropna().unique()))
        summary.append(f'{os.path.basename(csv)}:\n' + '\n'.join(f'  {c}' for c in contests) + '\n')
    except Exception as e:
        summary.append(f'{os.path.basename(csv)}: ERROR - {e}\n')

with open(out_path, 'w') as f:
    f.write('\n'.join(summary))
print(f'Unique contests summary saved to {out_path}')
