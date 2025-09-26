import json
import os

years = [
    2006, 2008, 2012, 2014, 2016, 2018, 2020, 2022, 2024
]
merged = {}

for year in years:
    path = f"workspace_files/county_results_{year}.json"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            merged[str(year)] = json.load(f)

with open("workspace_files/all_county_results.json", "w", encoding="utf-8") as out:
    json.dump(merged, out, indent=2)

print("Merged all years into workspace_files/all_county_results.json")
