import json

json_path = "workspace_files/county_results_2012.json"  # Change year as needed

with open(json_path, encoding="utf-8") as f:
    data = json.load(f)

print("Counties in output JSON:")
for county in sorted(data.keys()):
    print(county)
print(f"Total counties: {len(data)}")
