import csv
from collections import Counter

csv_path = r"SC/Data/election_data_SC.v05_with_county.csv"

county_counter = Counter()
year_counter = Counter()
contest_counter = Counter()
missing_county_rows = []

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        year = str(row.get("year", "") or row.get("YEAR", "")).strip()
        county = str(row.get("county", "") or row.get("COUNTY", "")).strip().upper()
        contest = row.get("contest") or row.get("office") or row.get("CONTEST") or row.get("OFFICE") or "UNKNOWN"
        county_counter[county] += 1
        year_counter[year] += 1
        contest_counter[contest] += 1
        if not county:
            missing_county_rows.append(row)

print("Year counts:", dict(year_counter))
print("County counts (top 10):", county_counter.most_common(10))
print("Contest counts (top 10):", contest_counter.most_common(10))
print(f"Rows missing county: {len(missing_county_rows)}")
if missing_county_rows:
    print("Sample row missing county:", missing_county_rows[0])
