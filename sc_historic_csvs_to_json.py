import pandas as pd
import json
import os
from collections import defaultdict
from datetime import date

# List of input CSVs (add or remove as needed)
csv_files = [
    'SC/Data/election_data_SC.v04.csv',
    'SC/Data/election_data_SC.v05.csv',
    'SC/Data/election_data_SC.v06.csv',
]

# Output JSON path
json_path = 'sc_election_results_historic.json'

# Helper: parse year and contest from column name
def parse_col(col):
    # Example: E_16_PRES_Dem, E_18_GOV_Rep, etc.
    parts = col.split('_')
    if len(parts) < 4:
        return None, None, None
    year = '20' + parts[1] if parts[1].isdigit() else None
    office = parts[2]
    party = parts[3]
    return year, office, party

# Build results structure
results_by_year = defaultdict(lambda: defaultdict(dict))
all_years = set()
all_contests = set()
total_results = 0

for csv_file in csv_files:
    if not os.path.exists(csv_file):
        continue
    df = pd.read_csv(csv_file, dtype=str)
    df.columns = [c.strip() for c in df.columns]  # Strip whitespace from column names
    df = df.fillna(0)
    print(f"Processing {csv_file} columns: {[col for col in df.columns if col.startswith('E_') and ('_Dem' in col or '_Rep' in col)]}")
    for _, row in df.iterrows():
        geo_id = str(row.get('GEOID20', '')).strip()
        name = str(row.get('Name', '')).strip()
        for col in df.columns:
            if col.startswith('E_') and ('_Dem' in col or '_Rep' in col):
                year, office, party = parse_col(col)
                if not year or not office or not party:
                    continue
                contest = office
                contest_key = f'{contest}_{year}'
                all_years.add(year)
                all_contests.add(contest_key)
                # Build unique key for this geo unit
                geo_key = geo_id or name
                # Initialize contest entry
                if contest_key not in results_by_year[year]:
                    results_by_year[year][contest_key] = {
                        'contest_name': contest,
                        'results': {}
                    }
                # Initialize result for this geo unit
                if geo_key not in results_by_year[year][contest_key]['results']:
                    results_by_year[year][contest_key]['results'][geo_key] = {
                        'geo_id': geo_id,
                        'name': name,
                        'year': year,
                        'contest': contest,
                        'dem_votes': 0,
                        'rep_votes': 0,
                        'total_votes': 0,
                        'all_parties': {'DEM': 0, 'REP': 0}
                    }
                # Add votes
                val = str(row[col]).strip()
                votes = int(val) if val.isdigit() else 0
                if party == 'Dem':
                    results_by_year[year][contest_key]['results'][geo_key]['dem_votes'] += votes
                    results_by_year[year][contest_key]['results'][geo_key]['all_parties']['DEM'] += votes
                elif party == 'Rep':
                    results_by_year[year][contest_key]['results'][geo_key]['rep_votes'] += votes
                    results_by_year[year][contest_key]['results'][geo_key]['all_parties']['REP'] += votes
                results_by_year[year][contest_key]['results'][geo_key]['total_votes'] += votes
                total_results += 1

# Build summary
summary = {
    'total_years': len(all_years),
    'total_contests': len(all_contests),
    'total_geo_results': total_results,
    'years_covered': sorted(list(all_years))
}

# Metadata (customize as needed)
metadata = {
    'title': 'South Carolina Statewide Historic Election Results',
    'description': 'Historic election results from multiple sources, formatted in the NC JSON structure.',
    'years_covered': sorted(list(all_years)),
    'processed_date': str(date.today()),
    'source_files': csv_files
}

output = {
    'metadata': metadata,
    'summary': summary,
    'results_by_year': results_by_year
}

# Add dem_pct and rep_pct to each result
for year in results_by_year:
    for contest_key in results_by_year[year]:
        for geo_key, result in results_by_year[year][contest_key]['results'].items():
            total = result['total_votes']
            dem = result['dem_votes']
            rep = result['rep_votes']
            result['dem_pct'] = round((dem / total) * 100, 2) if total else 0.00
            result['rep_pct'] = round((rep / total) * 100, 2) if total else 0.00

# Convert defaultdicts to dicts for JSON serialization
def dictify(obj):
    if isinstance(obj, defaultdict):
        obj = {k: dictify(v) for k, v in obj.items()}
    elif isinstance(obj, dict):
        obj = {k: dictify(v) for k, v in obj.items()}
    return obj

output['results_by_year'] = dictify(output['results_by_year'])

with open(json_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f'Historic election results saved to {json_path}')
