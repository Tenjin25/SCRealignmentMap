import csv
import json
from collections import defaultdict

INPUT_CSV = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\SC\Data\election_data_SC.v05_with_county.csv"
OUTPUT_JSON = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\president_2008_county_results.json"

county_results = defaultdict(lambda: {"E_08_PRES_Total": 0, "E_08_PRES_Dem": 0, "E_08_PRES_Rep": 0})

with open(INPUT_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, skipinitialspace=True)
    for row in reader:
        row = {k.strip(): v for k, v in row.items()}
        county = row.get('county', '').strip()
        if not county:
            continue
        try:
            total = int(row.get('E_08_PRES_Total', '0'))
            dem = int(row.get('E_08_PRES_Dem', '0'))
            rep = int(row.get('E_08_PRES_Rep', '0'))
        except ValueError:
            total, dem, rep = 0, 0, 0
        county_results[county]["E_08_PRES_Total"] += total
        county_results[county]["E_08_PRES_Dem"] += dem
        county_results[county]["E_08_PRES_Rep"] += rep


# Competitiveness scale
competitiveness_scale = {
    "Republican": [
        {"category": "Annihilation", "min": 40, "max": 1000, "color": "#67000d", "code": "R_ANNIHILATION"},
        {"category": "Dominant", "min": 30, "max": 40, "color": "#a50f15", "code": "R_DOMINANT"},
        {"category": "Stronghold", "min": 20, "max": 30, "color": "#cb181d", "code": "R_STRONGHOLD"},
        {"category": "Safe", "min": 10, "max": 20, "color": "#ef3b2c", "code": "R_SAFE"},
        {"category": "Likely", "min": 5.5, "max": 10, "color": "#fb6a4a", "code": "R_LIKELY"},
        {"category": "Lean", "min": 1, "max": 5.5, "color": "#fcae91", "code": "R_LEAN"},
        {"category": "Tilt", "min": 0.5, "max": 1, "color": "#fee8c8", "code": "R_TILT"}
    ],
    "Tossup": [
        {"category": "Tossup", "min": -0.5, "max": 0.5, "color": "#f7f7f7", "code": "TOSSUP"}
    ],
    "Democratic": [
        {"category": "Tilt", "min": 0.5, "max": 1, "color": "#e1f5fe", "code": "D_TILT"},
        {"category": "Lean", "min": 1, "max": 5.5, "color": "#c6dbef", "code": "D_LEAN"},
        {"category": "Likely", "min": 5.5, "max": 10, "color": "#9ecae1", "code": "D_LIKELY"},
        {"category": "Safe", "min": 10, "max": 20, "color": "#6baed6", "code": "D_SAFE"},
        {"category": "Stronghold", "min": 20, "max": 30, "color": "#3182bd", "code": "D_STRONGHOLD"},
        {"category": "Dominant", "min": 30, "max": 40, "color": "#08519c", "code": "D_DOMINANT"},
        {"category": "Annihilation", "min": 40, "max": 1000, "color": "#08306b", "code": "D_ANNIHILATION"}
    ]
}

def get_competitiveness(margin, margin_pct):
    if abs(margin_pct) <= 0.5:
        cat = competitiveness_scale["Tossup"][0]
        return {"category": cat["category"], "party": "Tossup", "code": cat["code"], "color": cat["color"]}
    if margin > 0:
        for cat in competitiveness_scale["Republican"]:
            if margin_pct >= cat["min"] and margin_pct < cat["max"]:
                return {"category": cat["category"], "party": "Republican", "code": cat["code"], "color": cat["color"]}
    elif margin < 0:
        for cat in competitiveness_scale["Democratic"]:
            if abs(margin_pct) >= cat["min"] and abs(margin_pct) < cat["max"]:
                return {"category": cat["category"], "party": "Democratic", "code": cat["code"], "color": cat["color"]}
    return {"category": "Unknown", "party": None, "code": "UNKNOWN", "color": "#cccccc"}

for county, res in county_results.items():
    res["margin"] = res["E_08_PRES_Rep"] - res["E_08_PRES_Dem"]
    res["margin_pct"] = round((res["margin"] / res["E_08_PRES_Total"] * 100) if res["E_08_PRES_Total"] else 0, 2)
    res["winner"] = "Republican" if res["margin"] > 0 else ("Democratic" if res["margin"] < 0 else "Tied")
    res["competitiveness"] = get_competitiveness(res["margin"], res["margin_pct"])

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(county_results, f, indent=2)

print(f"County-level 2008 President results saved to {OUTPUT_JSON}")
