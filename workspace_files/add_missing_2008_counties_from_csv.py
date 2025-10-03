import csv
import json

# Paths
csv_path = r"SC/Data/election_data_SC.v05_with_county.csv"
json_path = r"workspace_files/precinct_results_2008.json"

# Load existing 2008 JSON
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Find present counties
present_counties = set()
for precinct in data:
    for contest in data[precinct]:
        county = data[precinct][contest].get('county', '').upper()
        if county:
            present_counties.add(county)

# Scan CSV for 2008 rows with missing counties
missing_counties = set()
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        year = str(row.get("year", "") or row.get("YEAR", "")).strip()
        county = str(row.get("county", "") or row.get("COUNTY", "")).strip().upper()
        if year == "2008" and county and county not in present_counties:
            missing_counties.add(county)

# Aggregate missing county data
county_results = {}
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        year = str(row.get("year", "") or row.get("YEAR", "")).strip()
        county = str(row.get("county", "") or row.get("COUNTY", "")).strip().upper()
        if year == "2008" and county in missing_counties:
            contest = row.get("contest") or row.get("office") or row.get("CONTEST") or row.get("OFFICE") or "UNKNOWN"
            dem_votes = int(row.get("dem_votes", 0) or row.get("DEM_VOTES", 0) or 0)
            rep_votes = int(row.get("rep_votes", 0) or row.get("REP_VOTES", 0) or 0)
            other_votes = int(row.get("other_votes", 0) or row.get("OTHER_VOTES", 0) or 0)
            total_votes = int(row.get("total_votes", 0) or row.get("TOTAL_VOTES", 0) or 0)
            if county not in county_results:
                county_results[county] = {}
            county_results[county][contest] = {
                "county": county,
                "contest": contest,
                "year": year,
                "dem_votes": dem_votes,
                "rep_votes": rep_votes,
                "other_votes": other_votes,
                "total_votes": total_votes
            }

# Add missing county results to your JSON
for county, contests in county_results.items():
    placeholder_precinct = f"{county}_MISSING"
    data[placeholder_precinct] = contests

# Save updated JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Added missing 2008 county data from CSV to JSON.")
