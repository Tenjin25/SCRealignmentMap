from competitiveness_category import get_competitiveness_category
categorization_system = {
    "competitiveness_scale": {
        "Republican": [
            {"category": "Annihilation", "range": "R+40%+", "color": "#67000d"},
            {"category": "Dominant", "range": "R+30-40%", "color": "#a50f15"},
            {"category": "Stronghold", "range": "R+20-30%", "color": "#cb181d"},
            {"category": "Safe", "range": "R+10-20%", "color": "#ef3b2c"},
            {"category": "Likely", "range": "R+5.5-10%", "color": "#fb6a4a"},
            {"category": "Lean", "range": "R+1-5.5%", "color": "#fcae91"},
            {"category": "Tilt", "range": "R+0.5-1%", "color": "#fee8c8"}
        ],
        "Tossup": [
            {"category": "Tossup", "range": "±0.5%", "color": "#f7f7f7"}
        ],
        "Democratic": [
            {"category": "Tilt", "range": "D+0.5-1%", "color": "#e1f5fe"},
            {"category": "Lean", "range": "D+1-5.5%", "color": "#c6dbef"},
            {"category": "Likely", "range": "D+5.5-10%", "color": "#9ecae1"},
            {"category": "Safe", "range": "D+10-20%", "color": "#6baed6"},
            {"category": "Stronghold", "range": "D+20-30%", "color": "#3182bd"},
            {"category": "Dominant", "range": "D+30-40%", "color": "#08519c"},
            {"category": "Annihilation", "range": "D+40%+", "color": "#08306b"}
        ]
    }
}
import pandas as pd
import json
from collections import defaultdict
from datetime import date

input_csv = 'SC/Data/election_data_SC.v06_with_county.csv'
output_json = 'sc_election_results_v06_structured.json'

df = pd.read_csv(input_csv, dtype=str)
df.columns = [c.strip() for c in df.columns]

results_by_year = defaultdict(lambda: defaultdict(dict))
all_years = set()
all_contests = set()
total_results = 0

for _, row in df.iterrows():
    county_fips = str(row['county_fips']).strip()
    county_name = str(row['county_name']).strip()
    for col in df.columns:
        if col.startswith('E_') and ('_Dem' in col or '_Rep' in col):
            parts = col.split('_')
            if len(parts) < 4:
                continue
            year = '20' + parts[1] if parts[1].isdigit() else None
            office = parts[2]
            party = parts[3]
            if not year or not office or not party:
                continue
            contest = office
            contest_key = f'{contest}_{year}'
            all_years.add(year)
            all_contests.add(contest_key)
            geo_key = county_fips
            if contest_key not in results_by_year[year]:
                results_by_year[year][contest_key] = {
                    'contest_name': contest,
                    'results': {}
                }
            if geo_key not in results_by_year[year][contest_key]['results']:
                results_by_year[year][contest_key]['results'][geo_key] = {
                    'county_fips': county_fips,
                    'county_name': county_name,
                    'year': year,
                    'contest': contest,
                    'dem_votes': 0,
                    'rep_votes': 0,
                    'total_votes': 0,
                    'all_parties': {'DEM': 0, 'REP': 0}
                }
            val = str(row[col]).strip()
            votes = int(val) if val.isdigit() else 0
            if party == 'Dem':
                results_by_year[year][contest_key]['results'][geo_key]['dem_votes'] += votes
                results_by_year[year][contest_key]['results'][geo_key]['all_parties']['DEM'] += votes
            elif party == 'Rep':
                results_by_year[year][contest_key]['results'][geo_key]['rep_votes'] += votes
                results_by_year[year][contest_key]['results'][geo_key]['all_parties']['REP'] += votes
            results_by_year[year][contest_key]['results'][geo_key]['total_votes'] += votes
            # Add competitiveness category after updating votes
            dem_votes = results_by_year[year][contest_key]['results'][geo_key]['dem_votes']
            rep_votes = results_by_year[year][contest_key]['results'][geo_key]['rep_votes']
            cat, rng, color, margin = get_competitiveness_category(rep_votes, dem_votes)
            results_by_year[year][contest_key]['results'][geo_key]['competitiveness_category'] = cat
            results_by_year[year][contest_key]['results'][geo_key]['competitiveness_range'] = rng
            results_by_year[year][contest_key]['results'][geo_key]['competitiveness_color'] = color
            results_by_year[year][contest_key]['results'][geo_key]['competitiveness_margin'] = margin
            total_results += 1

summary = {
    'total_years': len(all_years),
    'total_contests': len(all_contests),
    'total_geo_results': total_results,
    'years_covered': sorted(list(all_years))
}
metadata = {
    'title': 'South Carolina Election Results Structured (v06)',
    'description': 'Election results with county info, formatted in the NC JSON structure.',
    'years_covered': sorted(list(all_years)),
    'processed_date': str(date.today()),
    'source_file': input_csv
}


output = {
    'metadata': metadata,
    'summary': summary,
    'results_by_year': {y: dict(v) for y, v in results_by_year.items()},
    'categorization_system': categorization_system
}

with open(output_json, 'w') as f:
    json.dump(output, f, indent=2)

print(f'Election results saved to {output_json}')
