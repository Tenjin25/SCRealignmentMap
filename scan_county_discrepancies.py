import json
from collections import defaultdict

# Path to the output JSON file
RESULTS_PATH = r"workspace_files/all_county_results.json"

# Load results
with open(RESULTS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Thresholds for sanity checks
MAX_REASONABLE_VOTES = 100000  # Most counties should not exceed this
MIN_REASONABLE_VOTES = 100     # Most counties should not be below this

problems = []
for year, contests in data.get("results_by_year", {}).items():
    for contest_type, contest_ids in contests.items():
        for contest_id, counties in contest_ids.items():
            for county, result in counties.items():
                rep_votes = result.get("rep_votes", 0)
                dem_votes = result.get("dem_votes", 0)
                total_votes = result.get("total_votes", 0)
                # Check for unrealistic totals
                if total_votes > MAX_REASONABLE_VOTES:
                    problems.append(f"{year} {contest_type} {contest_id} {county}: total_votes={total_votes} (HIGH)")
                if total_votes < MIN_REASONABLE_VOTES:
                    problems.append(f"{year} {contest_type} {contest_id} {county}: total_votes={total_votes} (LOW)")
                # Check for missing candidate names
                if not result.get("dem_candidate") or not result.get("rep_candidate"):
                    problems.append(f"{year} {contest_type} {contest_id} {county}: missing candidate name(s)")
                # Check for negative votes
                if rep_votes < 0 or dem_votes < 0:
                    problems.append(f"{year} {contest_type} {contest_id} {county}: negative vote count")

if problems:
    print("Discrepancies found:")
    for p in problems:
        print(p)
else:
    print("No major discrepancies found.")
