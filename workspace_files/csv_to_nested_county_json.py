import csv
import json
import os

def load_fips_list(geojson_path):
    with open(geojson_path, 'r') as f:
        geo = json.load(f)
    return [feat['properties']['GEOID20'] for feat in geo['features']], {feat['properties']['GEOID20']: feat['properties']['NAME20'] for feat in geo['features']}

def load_csv_results(csv_path):
    results = {}
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fips = row.get('county_fips') or row.get('FIPS') or row.get('fips')
            if not fips:
                continue
            results[fips] = row
    return results

def get_placeholder(fips, county_name, year, contest_name):
    return {
        "county": county_name,
        "contest": contest_name,
        "year": year,
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

def main(csv_path, geojson_path, year, contest_key, contest_name, output_path):
    fips_list, fips_to_name = load_fips_list(geojson_path)
    csv_results = load_csv_results(csv_path)
    results = {}
    for fips in fips_list:
        if fips in csv_results:
            results[fips] = csv_results[fips]
        else:
            results[fips] = get_placeholder(fips, fips_to_name.get(fips, "UNKNOWN"), year, contest_name)
    nested = {
        "results_by_year": {
            year: {
                contest_key: {
                    "contest_name": contest_name,
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
    parser = argparse.ArgumentParser(description="Convert county results CSV to nested JSON format.")
    parser.add_argument("--csv", required=True, help="Path to county results CSV file.")
    parser.add_argument("--geojson", required=True, help="Path to county GeoJSON file.")
    parser.add_argument("--year", required=True, help="Year (e.g. '2006')")
    parser.add_argument("--contest_key", required=True, help="Contest key (e.g. 'governor_2006')")
    parser.add_argument("--contest_name", required=True, help="Contest name (e.g. 'GOVERNOR')")
    parser.add_argument("--output", required=True, help="Output path for nested JSON file.")
    args = parser.parse_args()
    main(args.csv, args.geojson, args.year, args.contest_key, args.contest_name, args.output)
