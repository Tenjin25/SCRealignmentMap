import json
import os

def load_fips_list(geojson_path):
    with open(geojson_path, 'r') as f:
        geo = json.load(f)
    # Return county names from GeoJSON
    return [feat['properties'].get('NAME20') or feat['properties'].get('county_name') for feat in geo['features'] if feat['properties'].get('NAME20') or feat['properties'].get('county_name')]

def load_flat_results(results_path):
    import csv
    def load_flat_results(results_path):
        # Try JSON first
        try:
            with open(results_path, 'r') as f:
                return json.load(f)
        except Exception:
            # Fallback to CSV
            results = {}
            with open(results_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Use county_fips as key if present, else try to infer
                    fips = row.get('county_fips') or row.get('FIPS') or row.get('fips')
                    if fips:
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

def main(flat_path, geojson_path, year, contest_key, contest_name, output_path):
    county_names = load_fips_list(geojson_path)
    flat = load_flat_results(flat_path)
    if not isinstance(flat, dict):
        print("Warning: Flat results could not be loaded as a dictionary. No county results will be filled from flat data.")
        flat = {}
    # Load county FIPS and names from CSV
    import csv
    name_to_fips = {}
    with open('sc_county_fips.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Normalize names for matching
            name_to_fips[row['county_name'].strip().lower()] = row['county_fips']
    results = {}
    for county_name in county_names:
        norm_name = county_name.strip().lower() if county_name else None
        fips = name_to_fips.get(norm_name)
        if not fips:
            print(f"Warning: County name '{county_name}' not found in CSV. Skipping.")
            continue
        if fips in flat:
            results[fips] = flat[fips]
        else:
            results[fips] = get_placeholder(fips, county_name, year, contest_name)
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
    parser = argparse.ArgumentParser(description="Convert flat county results to nested format.")
    parser.add_argument("--flat", required=True, help="Path to flat county results JSON file.")
    parser.add_argument("--geojson", required=True, help="Path to county GeoJSON file.")
    parser.add_argument("--year", required=True, help="Year (e.g. '2006')")
    parser.add_argument("--contest_key", required=True, help="Contest key (e.g. 'governor_2006')")
    parser.add_argument("--contest_name", required=True, help="Contest name (e.g. 'GOVERNOR')")
    parser.add_argument("--output", required=True, help="Output path for nested JSON file.")
    args = parser.parse_args()
    main(args.flat, args.geojson, args.year, args.contest_key, args.contest_name, args.output)
