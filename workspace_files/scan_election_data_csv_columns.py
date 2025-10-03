import csv
from collections import Counter

csv_path = r"SC/Data/election_data_SC.v05_with_county.csv"

# Scan and print all column names and a sample row
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    reader.fieldnames = [name.strip() for name in reader.fieldnames]
    sample_rows = []
    for i, row in enumerate(reader):
        if i < 5:
            sample_rows.append({k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()})
        if i == 5:
            break

print("Column names:", reader.fieldnames)
print("Sample rows:")
for r in sample_rows:
    print(r)
