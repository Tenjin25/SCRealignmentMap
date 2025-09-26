import csv
import glob
import os

# List of main precinct and county CSVs to scan
csv_patterns = [
    'Data/*__sc__general__precinct.csv',
    'Data/*__sc__general__county.csv',
    'Data/2018/*__sc__general__*_precinct.csv',
    'Data/2014/*__sc__general__*_precinct.csv'
]

unique_counties = set()

for pattern in csv_patterns:
    for file in glob.glob(pattern):
        print(f"Scanning: {file}")
        with open(file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                county = row.get('county')
                if county:
                    unique_counties.add(county.strip())

print("\nUnique county names found across all files:")
for county in sorted(unique_counties):
    print(county)
