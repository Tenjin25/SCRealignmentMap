# aggregate_precinct_results_president_2008.py
"""
Aggregates 2008 President results by county/precinct, calculates margin, winner, competitiveness, and fills missing county data.
Output matches the requested detailed format.
"""
import csv
import json
from collections import defaultdict
import os

CSV_PATH = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\SC\Data\election_data_SC.v05_with_county.csv"
OUTPUT_JSON_PATH = r"president_2008_precinct_results.json"

# --- Competitiveness categorization system ---
categorization_system = {
    "Republican": [
        {"category": "Annihilation", "range": (40, 1000), "color": "#67000d", "code": "R_ANNIHILATION"},
        {"category": "Dominant", "range": (30, 40), "color": "#a50f15", "code": "R_DOMINANT"},
        {"category": "Stronghold", "range": (20, 30), "color": "#cb181d", "code": "R_STRONGHOLD"},
        {"category": "Safe", "range": (10, 20), "color": "#ef3b2c", "code": "R_SAFE"},
        {"category": "Likely", "range": (5.5, 10), "color": "#fb6a4a", "code": "R_LIKELY"},
        {"category": "Lean", "range": (1, 5.5), "color": "#fcae91", "code": "R_LEAN"},
        {"category": "Tilt", "range": (0.5, 1), "color": "#fee8c8", "code": "R_TILT"}
    ],
    "Tossup": [
        {"category": "Tossup", "range": (-0.5, 0.5), "color": "#f7f7f7", "code": "TOSSUP"}
    ],
    "Democratic": [
        {"category": "Tilt", "range": (0.5, 1), "color": "#e1f5fe", "code": "D_TILT"},
        {"category": "Lean", "range": (1, 5.5), "color": "#c6dbef", "code": "D_LEAN"},
        {"category": "Likely", "range": (5.5, 10), "color": "#9ecae1", "code": "D_LIKELY"},
        {"category": "Safe", "range": (10, 20), "color": "#6baed6", "code": "D_SAFE"},
        {"category": "Stronghold", "range": (20, 30), "color": "#3182bd", "code": "D_STRONGHOLD"},
        {"category": "Dominant", "range": (30, 40), "color": "#08519c", "code": "D_DOMINANT"},
        {"category": "Annihilation", "range": (40, 1000), "color": "#08306b", "code": "D_ANNIHILATION"}
    ]
}

def get_competitiveness(margin_pct):
    if abs(margin_pct) <= 0.5:
        return categorization_system["Tossup"][0]
    if margin_pct > 0.5:
        for cat in categorization_system["Republican"]:
            if margin_pct >= cat["range"][0] and margin_pct < cat["range"][1]:
                return cat
    if margin_pct < -0.5:
        for cat in categorization_system["Democratic"]:
            if abs(margin_pct) >= cat["range"][0] and abs(margin_pct) < cat["range"][1]:
                return cat
    return {"category": "Unknown", "color": "#cccccc", "code": "UNKNOWN"}

# --- Aggregate results ---
results = defaultdict(lambda: defaultdict(dict))

with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, skipinitialspace=True)
    fieldnames = [fn.strip() for fn in reader.fieldnames]
    for row in reader:
        # Strip keys to handle extra spaces
        row = {k.strip(): v for k, v in row.items()}
        if row.get('contest', '').strip().lower() != 'president' or row.get('year', '').strip() != '2008':
            continue
        county = row.get('county', '').strip()
        precinct = row.get('precinct', '').strip()
        party = row.get('party', '').strip().upper()
        candidate = row.get('candidate', '').strip()
        votes = int(row.get('votes', '0')) if row.get('votes', '0').isdigit() else 0
        key = f"{county}_{precinct}"
        if key not in results:
            results[key] = {
                "county": county,
                "precinct": precinct,
                "contest": row.get('contest', ''),
                "year": row.get('year', ''),
                "dem_candidate": None,
                "rep_candidate": None,
                "dem_votes": 0,
                "rep_votes": 0,
                "other_votes": 0,
                "total_votes": 0,
                "two_party_total": 0,
                "margin": 0,
                "margin_pct": 0.0,
                "winner": None,
                "competitiveness": {},
                "all_parties": defaultdict(int)
            }
        # Assign candidate names and votes
        if party == "DEM":
            results[key]["dem_candidate"] = candidate
            results[key]["dem_votes"] += votes
        elif party == "REP":
            results[key]["rep_candidate"] = candidate
            results[key]["rep_votes"] += votes
        else:
            results[key]["other_votes"] += votes
        results[key]["all_parties"][party] += votes
        results[key]["total_votes"] += votes

# --- Calculate margin, winner, competitiveness ---
for res in results.values():
    res["two_party_total"] = res["dem_votes"] + res["rep_votes"]
    res["margin"] = res["rep_votes"] - res["dem_votes"]
    if res["two_party_total"] > 0:
        res["margin_pct"] = round(abs(res["margin"]) / res["two_party_total"] * 100, 2)
        if res["margin"] > 0:
            res["winner"] = "REP"
            comp = get_competitiveness(res["margin_pct"])
            res["competitiveness"] = {"category": comp["category"], "party": "Republican", "code": comp["code"], "color": comp["color"]}
        elif res["margin"] < 0:
            res["winner"] = "DEM"
            comp = get_competitiveness(-res["margin_pct"])
            res["competitiveness"] = {"category": comp["category"], "party": "Democratic", "code": comp["code"], "color": comp["color"]}
        else:
            res["winner"] = "Tossup"
            comp = get_competitiveness(0)
            res["competitiveness"] = {"category": comp["category"], "party": "Tossup", "code": comp["code"], "color": comp["color"]}
    else:
        res["winner"] = None
        res["competitiveness"] = {"category": "Unknown", "party": None, "code": "UNKNOWN", "color": "#cccccc"}
    res["all_parties"] = dict(res["all_parties"])

# --- Output ---
output = {
    "results_by_year": {
        "2008": {
            "president_2008": {
                "contest_name": "President",
                "results": results
            }
        }
    }
}
with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f'Aggregated President 2008 precinct results saved to {OUTPUT_JSON_PATH}')
