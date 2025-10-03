import csv
import json

csv_path = r"SC/Data/election_data_SC.v05_with_county.csv"
json_path = r"workspace_files/precinct_results_2008.json"

# Load JSON
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Prepare for header cleanup
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    reader.fieldnames = [name.strip() for name in reader.fieldnames]
    rows = [ {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()} for row in reader ]

# For each precinct in JSON, try to match and update 2008 results
for precinct in data:
    # Try to match by county name
    json_county = data[precinct].get("PRESIDENT", {}).get("county", "").upper()
    for row in rows:
        csv_county = row.get("county", "").upper()
        if csv_county == json_county:
            # Extract 2008 results
            pres_total = int(row.get("E_08_PRES_Total", 0))
            pres_dem = int(row.get("E_08_PRES_Dem", 0))
            pres_rep = int(row.get("E_08_PRES_Rep", 0))
            # Update JSON
            if "PRESIDENT" in data[precinct]:
                data[precinct]["PRESIDENT"]["dem_votes"] = pres_dem
                data[precinct]["PRESIDENT"]["rep_votes"] = pres_rep
                data[precinct]["PRESIDENT"]["total_votes"] = pres_total
            else:
                data[precinct]["PRESIDENT"] = {
                    "dem_votes": pres_dem,
                    "rep_votes": pres_rep,
                    "total_votes": pres_total,
                    "county": csv_county
                }
            break  # Stop after first match

# Save updated JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Updated 2008 JSON with matching county results from CSV.")
