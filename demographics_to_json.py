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

input_csv = 'SC/Data/demographic_data_SC.v04_with_county.csv'
output_json = 'sc_demographics_structured.json'

df = pd.read_csv(input_csv, dtype=str)
df.columns = [c.strip() for c in df.columns]

results_by_year = defaultdict(lambda: defaultdict(dict))
all_years = set()
all_vars = set()
total_results = 0

for _, row in df.iterrows():
    county_fips = str(row['county_fips']).strip()
    county_name = str(row['county_name']).strip()
    for col in df.columns:
        if '_' in col and col not in ['GEOID20', 'Name', 'county_fips', 'county_name']:
            parts = col.split('_')
            year = None
            for p in parts:
                if p.isdigit() and len(p) == 2:
                    year = '20' + p
            if year:
                var = col.replace(f'_{parts[1]}_', '_', 1)
                all_years.add(year)
                all_vars.add(var)
                if county_fips not in results_by_year[year][var]:
                    results_by_year[year][var][county_fips] = {
                        'county_fips': county_fips,
                        'county_name': county_name,
                        'value': row[col]
                    }
                total_results += 1

summary = {
    'total_years': len(all_years),
    'total_variables': len(all_vars),
    'total_geo_results': total_results,
    'years_covered': sorted(list(all_years))
}
metadata = {
    'title': 'South Carolina Demographic Data Structured',
    'description': 'Demographic data from multiple years, formatted in the NC JSON structure.',
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

print(f'Demographic data saved to {output_json}')
