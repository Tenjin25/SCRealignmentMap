# Script: cross_reference_2024_results.py
"""
Compares 2024 county-level presidential results in sc_election_results_v06_structured.json
with the official Wikipedia results. If discrepancies are found, auto-corrects the JSON file.

- Loads your JSON results for 2024 (PRES_2024)
- Loads official results (hardcoded from Wikipedia)
- Compares vote counts and percentages
- If mismatches are found, updates the JSON and writes a corrected version
- Prints a summary of changes
"""
import json
import copy


# Official 2024 results from Wikipedia (all counties)
official_results = {
    'Abbeville':   {'rep_votes': 8509,  'dem_votes': 3399,  'other_votes': 140,  'rep_pct': 70.63, 'dem_pct': 28.21},
    'Aiken':       {'rep_votes': 53592, 'dem_votes': 31298, 'other_votes': 1201, 'rep_pct': 62.25, 'dem_pct': 36.35},
    'Allendale':   {'rep_votes': 813,   'dem_votes': 2165,  'other_votes': 45,   'rep_pct': 26.89, 'dem_pct': 71.62},
    'Anderson':    {'rep_votes': 71828, 'dem_votes': 25281, 'other_votes': 1187, 'rep_pct': 73.07, 'dem_pct': 25.72},
    'Bamberg':     {'rep_votes': 2376,  'dem_votes': 3245,  'other_votes': 73,   'rep_pct': 41.73, 'dem_pct': 56.99},
    'Barnwell':    {'rep_votes': 5605,  'dem_votes': 4082,  'other_votes': 116,  'rep_pct': 57.18, 'dem_pct': 41.64},
    'Beaufort':    {'rep_votes': 59123, 'dem_votes': 44002, 'other_votes': 1278, 'rep_pct': 56.63, 'dem_pct': 42.15},
    'Berkeley':    {'rep_votes': 64777, 'dem_votes': 46416, 'other_votes': 1641, 'rep_pct': 57.41, 'dem_pct': 41.14},
    'Calhoun':     {'rep_votes': 4474,  'dem_votes': 3339,  'other_votes': 101,  'rep_pct': 56.53, 'dem_pct': 42.19},
    'Charleston':  {'rep_votes': 99265, 'dem_votes': 111427,'other_votes': 3829, 'rep_pct': 46.27, 'dem_pct': 51.94},
    'Cherokee':    {'rep_votes': 18697, 'dem_votes': 5939,  'other_votes': 203,  'rep_pct': 75.27, 'dem_pct': 23.91},
    'Chester':     {'rep_votes': 9030,  'dem_votes': 6353,  'other_votes': 173,  'rep_pct': 58.05, 'dem_pct': 40.84},
    'Chesterfield':{'rep_votes': 11682, 'dem_votes': 6520,  'other_votes': 189,  'rep_pct': 63.52, 'dem_pct': 35.45},
    'Clarendon':   {'rep_votes': 9065,  'dem_votes': 7064,  'other_votes': 191,  'rep_pct': 55.55, 'dem_pct': 43.28},
    'Colleton':    {'rep_votes': 10696, 'dem_votes': 7376,  'other_votes': 204,  'rep_pct': 58.52, 'dem_pct': 40.36},
    'Darlington':  {'rep_votes': 17017, 'dem_votes': 12977, 'other_votes': 337,  'rep_pct': 56.10, 'dem_pct': 42.78},
    'Dillon':      {'rep_votes': 6526,  'dem_votes': 5241,  'other_votes': 94,   'rep_pct': 55.02, 'dem_pct': 44.19},
    'Dorchester':  {'rep_votes': 43839, 'dem_votes': 32489, 'other_votes': 1436, 'rep_pct': 56.37, 'dem_pct': 41.78},
    'Edgefield':   {'rep_votes': 9092,  'dem_votes': 4659,  'other_votes': 168,  'rep_pct': 65.32, 'dem_pct': 33.47},
    'Fairfield':   {'rep_votes': 4792,  'dem_votes': 6277,  'other_votes': 146,  'rep_pct': 42.73, 'dem_pct': 55.97},
    'Florence':    {'rep_votes': 32615, 'dem_votes': 27706, 'other_votes': 819,  'rep_pct': 53.34, 'dem_pct': 45.32},
    'Georgetown':  {'rep_votes': 22326, 'dem_votes': 14965, 'other_votes': 463,  'rep_pct': 59.14, 'dem_pct': 39.64},
    'Greenville':  {'rep_votes': 158541,'dem_votes': 100074,'other_votes': 4791, 'rep_pct': 60.21, 'dem_pct': 38.01},
    'Greenwood':   {'rep_votes': 19715, 'dem_votes': 10766, 'other_votes': 407,  'rep_pct': 63.83, 'dem_pct': 34.85},
    'Hampton':     {'rep_votes': 3801,  'dem_votes': 4328,  'other_votes': 104,  'rep_pct': 46.17, 'dem_pct': 52.57},
    'Horry':       {'rep_votes': 141719,'dem_votes': 62325, 'other_votes': 1910, 'rep_pct': 68.81, 'dem_pct': 30.26},
    'Jasper':      {'rep_votes': 9900,  'dem_votes': 8144,  'other_votes': 183,  'rep_pct': 54.32, 'dem_pct': 44.68},
    'Kershaw':     {'rep_votes': 21289, 'dem_votes': 11826, 'other_votes': 418,  'rep_pct': 63.49, 'dem_pct': 35.27},
    'Lancaster':   {'rep_votes': 33623, 'dem_votes': 20146, 'other_votes': 658,  'rep_pct': 61.78, 'dem_pct': 37.01},
    'Laurens':     {'rep_votes': 21110, 'dem_votes': 8769,  'other_votes': 334,  'rep_pct': 69.87, 'dem_pct': 29.02},
    'Lee':         {'rep_votes': 3078,  'dem_votes': 4505,  'other_votes': 493,  'rep_pct': 38.11, 'dem_pct': 55.78},
    'Lexington':   {'rep_votes': 96965, 'dem_votes': 47815, 'other_votes': 2123, 'rep_pct': 66.01, 'dem_pct': 32.55},
    'Marion':      {'rep_votes': 5906,  'dem_votes': 7316,  'other_votes': 166,  'rep_pct': 44.11, 'dem_pct': 54.65},
    'Marlboro':    {'rep_votes': 4896,  'dem_votes': 5137,  'other_votes': 119,  'rep_pct': 48.23, 'dem_pct': 50.60},
    'McCormick':   {'rep_votes': 3565,  'dem_votes': 2513,  'other_votes': 75,   'rep_pct': 57.94, 'dem_pct': 40.84},
    'Newberry':    {'rep_votes': 12067, 'dem_votes': 5841,  'other_votes': 221,  'rep_pct': 66.56, 'dem_pct': 32.22},
    'Oconee':      {'rep_votes': 31772, 'dem_votes': 9987,  'other_votes': 505,  'rep_pct': 75.18, 'dem_pct': 23.63},
    'Orangeburg':  {'rep_votes': 13750, 'dem_votes': 22832, 'other_votes': 388,  'rep_pct': 37.19, 'dem_pct': 61.76},
    'Pickens':     {'rep_votes': 45728, 'dem_votes': 13891, 'other_votes': 832,  'rep_pct': 75.64, 'dem_pct': 22.98},
    'Richland':    {'rep_votes': 58019, 'dem_votes': 121110,'other_votes': 3282, 'rep_pct': 31.81, 'dem_pct': 66.39},
    'Saluda':      {'rep_votes': 6452,  'dem_votes': 2454,  'other_votes': 108,  'rep_pct': 71.58, 'dem_pct': 27.22},
    'Spartanburg': {'rep_votes': 103032,'dem_votes': 50710, 'other_votes': 1855, 'rep_pct': 66.22, 'dem_pct': 32.59},
    'Sumter':      {'rep_votes': 21215, 'dem_votes': 23425, 'other_votes': 530,  'rep_pct': 46.97, 'dem_pct': 51.86},
    'Union':       {'rep_votes': 8102,  'dem_votes': 4084,  'other_votes': 103,  'rep_pct': 65.93, 'dem_pct': 33.23},
    'Williamsburg':{'rep_votes': 5524,  'dem_votes': 8634,  'other_votes': 172,  'rep_pct': 38.55, 'dem_pct': 60.25},
    'York':        {'rep_votes': 88239, 'dem_votes': 59600, 'other_votes': 2220, 'rep_pct': 58.80, 'dem_pct': 39.72},
}

json_path = 'sc_election_results_v06_structured.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

results_2024 = data['results_by_year']['2024']['PRES_2024']['results']
updated = False

# Track changes for summary
change_log = []
for county_fips, county_data in results_2024.items():
    name = county_data['county_name']
    if name in official_results:
        official = official_results[name]
        changed = False
        old = {
            'rep_votes': county_data.get('rep_votes'),
            'dem_votes': county_data.get('dem_votes'),
            'rep_pct': county_data.get('rep_pct'),
            'dem_pct': county_data.get('dem_pct'),
        }
        for key in ['rep_votes', 'dem_votes']:
            if county_data.get(key) != official[key]:
                county_data[key] = official[key]
                changed = True
        total_votes = official['rep_votes'] + official['dem_votes'] + official['other_votes']
        rep_pct = round(official['rep_votes'] / total_votes * 100, 2)
        dem_pct = round(official['dem_votes'] / total_votes * 100, 2)
        if abs(county_data.get('rep_pct', 0) - rep_pct) > 0.1:
            county_data['rep_pct'] = rep_pct
            changed = True
        if abs(county_data.get('dem_pct', 0) - dem_pct) > 0.1:
            county_data['dem_pct'] = dem_pct
            changed = True
        if changed:
            change_log.append({
                'county': name,
                'old_rep_votes': old['rep_votes'],
                'new_rep_votes': official['rep_votes'],
                'old_dem_votes': old['dem_votes'],
                'new_dem_votes': official['dem_votes'],
                'old_rep_pct': old['rep_pct'],
                'new_rep_pct': rep_pct,
                'old_dem_pct': old['dem_pct'],
                'new_dem_pct': dem_pct,
            })
            updated = True


if updated:
    with open('sc_election_results_v06_structured_corrected.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Corrections written to sc_election_results_v06_structured_corrected.json\n")
    print("Summary of changes:")
    print(f"{'County':<15} {'Old Rep':>8} {'New Rep':>8} {'Old Dem':>8} {'New Dem':>8} {'Old R%':>8} {'New R%':>8} {'Old D%':>8} {'New D%':>8}")
    for log in change_log:
        print(f"{log['county']:<15} {log['old_rep_votes']:>8} {log['new_rep_votes']:>8} {log['old_dem_votes']:>8} {log['new_dem_votes']:>8} {log['old_rep_pct']:>8} {log['new_rep_pct']:>8} {log['old_dem_pct']:>8} {log['new_dem_pct']:>8}")
else:
    print("No corrections needed. All results match official data.")
