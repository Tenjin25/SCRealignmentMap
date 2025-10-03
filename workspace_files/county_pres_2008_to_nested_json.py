import csv
import json

def load_fips_csv(fips_path):
    fips_map = {}
    with open(fips_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fips_map[row['fips']] = row['county']
    return fips_map

def load_main_results(main_path):
    results = {}
    with open(main_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fips = row.get('county_fips') or row.get('fips')
            if fips:
                results[fips] = row
    return results

def load_backup_pres_data(backup_path):
    pres_data = {}
    with open(backup_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fips = row.get('county_fips') or row.get('GEOID20') or row.get('fips')
            if not fips:
                continue
            pres_data[fips] = {
                "county": row.get('county_name') or row.get('Name'),
                "contest": "PRESIDENT",
                "year": "2008",
                "dem_candidate": "Barack Obama",
                "rep_candidate": "John McCain",
                "dem_votes": int(row.get('E_08_PRES_Dem', 0)),
                "rep_votes": int(row.get('E_08_PRES_Rep', 0)),
                "other_votes": 0,
                "total_votes": int(row.get('E_08_PRES_Total', 0)),
                "two_party_total": int(row.get('E_08_PRES_Dem', 0)) + int(row.get('E_08_PRES_Rep', 0)),
                "margin": abs(int(row.get('E_08_PRES_Dem', 0)) - int(row.get('E_08_PRES_Rep', 0))),
                "margin_pct": None,
                "winner": "DEM" if int(row.get('E_08_PRES_Dem', 0)) > int(row.get('E_08_PRES_Rep', 0)) else "REP",
                "competitiveness": None,
                "all_parties": {
                    "REPUBLICAN": int(row.get('E_08_PRES_Rep', 0)),
                    "DEMOCRAT": int(row.get('E_08_PRES_Dem', 0))
                },
                "county_fips": fips
            }
    return pres_data

def main(main_csv, fips_csv, backup_csv, output_path):
    fips_map = load_fips_csv(fips_csv)
    main_results = load_main_results(main_csv)
    backup_pres = load_backup_pres_data(backup_csv)
    results = {}
    for fips, county in fips_map.items():
        if fips in main_results:
            results[fips] = main_results[fips]
        elif fips in backup_pres:
            results[fips] = backup_pres[fips]
        else:
            results[fips] = {
                "county": county,
                "contest": "PRESIDENT",
                "year": "2008",
                "dem_candidate": None,
                "rep_candidate": None,
                "dem_votes": 0,
                "rep_votes": 0,
                "other_votes": 0,
                "total_votes": 0,
                "two_party_total": 0,
                "margin": 0,
                "margin_pct": None,
                "winner": None,
                "competitiveness": None,
                "all_parties": {},
                "county_fips": fips
            }
    nested = {
        "results_by_year": {
            "2008": {
                "president_2008": {
                    "contest_name": "PRESIDENT",
                    "results": results
                }
            }
        }
    }
    with open(output_path, 'w') as f:
        json.dump(nested, f, indent=2)
    print(f"Nested county results written to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert 2008 county president results to nested JSON format, filling missing counties from backup data.")
    parser.add_argument("--main_csv", required=True, help="Path to main 2008 county results CSV.")
    parser.add_argument("--fips_csv", required=True, help="Path to county FIPS CSV.")
    parser.add_argument("--backup_csv", required=True, help="Path to backup county results CSV with president data.")
    parser.add_argument("--output", required=True, help="Output path for nested JSON file.")
    args = parser.parse_args()
    main(args.main_csv, args.fips_csv, args.backup_csv, args.output)
