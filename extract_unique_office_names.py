
import os
import glob
import pandas as pd
import re

# Set the data directory (update this path as needed)
data_dir = os.path.join(os.getcwd(), 'Data')

# Find all CSV files recursively in the data directory and subfolders
csv_files = glob.glob(os.path.join(data_dir, '**', '*.csv'), recursive=True)
if not csv_files:
    print(f"No CSV files found in {data_dir}")

year_office_names = {}
year_pattern = re.compile(r'(20\d{2})')
for csv_file in csv_files:
    print(f"Processing: {csv_file}")
    # Try to extract year from filename (search for any 4-digit year)
    basename = os.path.basename(csv_file)
    match = year_pattern.search(basename)
    year = int(match.group(1)) if match else None
    if not year:
        print(f"  Skipped (no year found): {csv_file}")
        continue
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"  Failed to read {csv_file}: {e}")
        continue
    print(f"  Columns: {list(df.columns)}")
    # Try to find the office/contest column
    office_col = None
    for col in df.columns:
        if 'office' in col.lower() or 'contest' in col.lower():
            office_col = col
            break
    if not office_col:
        print(f"  Skipped (no office/contest column): {csv_file}")
        continue
    offices = set(df[office_col].dropna().unique())
    print(f"  Found {len(offices)} offices for year {year}")
    if year not in year_office_names:
        year_office_names[year] = set()
    year_office_names[year].update(offices)

# Write results to CSV
output_rows = []
for year in sorted(year_office_names.keys()):
    for office in sorted(year_office_names[year]):
        output_rows.append({'year': year, 'office_name': office})
output_df = pd.DataFrame(output_rows)
output_df.to_csv('unique_office_names_by_year.csv', index=False)
print(f"Wrote {len(output_rows)} office names to unique_office_names_by_year.csv")
