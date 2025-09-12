import pandas as pd
import json
from collections import defaultdict

fips_path = 'sc_county_fips.csv'

# Input CSV and output JSON
csv_path = 'elstats_search_b48bcf59c9eb3184_cleaned_aggregated.csv'
json_path = 'sc_election_results_structured.json'

# Competitiveness categories (example, adjust as needed)
competitiveness_scale = [
    (40, 'Annihilation', 'R_ANNIHILATION', '#67000d', 'Republican'),
    (30, 'Dominant', 'R_DOMINANT', '#a50f15', 'Republican'),
    (20, 'Stronghold', 'R_STRONGHOLD', '#cb181d', 'Republican'),
    (10, 'Safe', 'R_SAFE', '#ef3b2c', 'Republican'),
    (5.5, 'Likely', 'R_LIKELY', '#fb6a4a', 'Republican'),
    (1, 'Lean', 'R_LEAN', '#fcae91', 'Republican'),
    (0.5, 'Tilt', 'R_TILT', '#fee8c8', 'Republican'),
    (0.5, 'Tossup', 'TOSSUP', '#f7f7f7', 'Tossup'),
    (-0.5, 'Tilt', 'D_TILT', '#e1f5fe', 'Democratic'),
    (-1, 'Lean', 'D_LEAN', '#c6dbef', 'Democratic'),
    (-5.5, 'Likely', 'D_LIKELY', '#9ecae1', 'Democratic'),
    (-10, 'Safe', 'D_SAFE', '#6baed6', 'Democratic'),
    (-20, 'Stronghold', 'D_STRONGHOLD', '#3182bd', 'Democratic'),
    (-30, 'Dominant', 'D_DOMINANT', '#08519c', 'Democratic'),
    (-40, 'Annihilation', 'D_ANNIHILATION', '#08306b', 'Democratic'),
]

def get_competitiveness(margin_pct):
    for threshold, category, code, color, party in competitiveness_scale:
        if margin_pct >= threshold:
            return {'category': category, 'party': party, 'code': code, 'color': color}
        if margin_pct <= threshold:
            return {'category': category, 'party': party, 'code': code, 'color': color}
    return {'category': 'Tossup', 'party': 'Tossup', 'code': 'TOSSUP', 'color': '#f7f7f7'}


# Read CSV
df = pd.read_csv(csv_path, dtype=str)
df.columns = [c.strip() for c in df.columns]
df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)

# Read FIPS mapping
fips_df = pd.read_csv(fips_path, dtype=str)
fips_map = {row['county_name'].strip(): row['county_fips'].zfill(3) for _, row in fips_df.iterrows()}

# Aggregate votes by year, contest, county, candidate (sum across vote channels)

import re
# Add a 'year' column for grouping (extract 4-digit year from election_date)
df['year'] = df['election_date'].apply(lambda x: re.search(r'(20\d{2})', str(x)).group(1) if re.search(r'(20\d{2})', str(x)) else '')
df['contest'] = df['office_name'].str.strip()
df['county'] = df['division_name'].str.strip()
df['candidate'] = df['candidate_name'].str.strip()
df['party'] = df['candidate_party_name'].str.strip()


grouped = df.groupby(['year', 'contest', 'county', 'candidate', 'party'], as_index=False)['votes'].sum()

# Debug: print unique year values
print('DEBUG: unique years in grouped data:', grouped['year'].unique())

data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
import re
for _, row in grouped.iterrows():
    year_raw = str(row['year']).strip()
    match = re.search(r'(20\d{2})', year_raw)
    if match:
        year = match.group(1)
    else:
        # Skip if no valid year
        continue
    contest = row['contest']
    county = row['county']
    candidate = row['candidate']
    party = row['party']
    county_fips = fips_map.get(county, None)
    votes = int(row['votes'])
    entry = data[year][county].setdefault(contest, {
        'county': county,
        'county_fips': county_fips,
        'contest': contest,
        'year': year,
        'results': {},
        'all_parties': defaultdict(int)
    })
    entry['all_parties'][party] += votes
    entry['results'][candidate] = {
        'party': party,
        'votes': votes
    }

 # Calculate margins and competitiveness
for year, counties in data.items():
    for county, contests in counties.items():
        for contest, entry in contests.items():
            parties = entry['all_parties']
            dem = parties.get('Democratic', 0)
            rep = parties.get('Republican', 0)
            total = sum(parties.values())
            margin = rep - dem
            two_party_total = rep + dem
            margin_pct = ((margin) / two_party_total * 100) if two_party_total else 0
            winner = 'REP' if margin > 0 else ('DEM' if margin < 0 else 'TIE')
            entry['dem_votes'] = dem
            entry['rep_votes'] = rep
            entry['total_votes'] = total
            entry['two_party_total'] = two_party_total
            entry['margin'] = margin
            entry['margin_pct'] = round(margin_pct, 2)
            entry['winner'] = winner
            entry['competitiveness'] = get_competitiveness(margin_pct)
            entry['all_parties'] = dict(parties)

# Add metadata and categorization system
metadata = {
    "title": "South Carolina Statewide County Election Results (2008-2024)",
    "description": "Comprehensive county-level results for non-gerrymandered races with enhanced categorization",
    "years_covered": ["2008", "2010", "2012", "2014", "2016", "2018", "2020", "2022", "2024"],
    "exclusions": ["Congressional districts (gerrymandered)"],
    "focus": "Clean geographic political patterns",
    "processed_date": "2025-09-11",
    "categorization_system": {
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
        },
        "office_types": ["Federal", "State", "Judicial", "Other"],
        "enhanced_features": [
            "Competitiveness categorization for each county",
            "Contest type classification (Federal/State/Judicial)",
            "Office ranking system for analysis prioritization",
            "Color coding compatible with political geography visualization"
        ]
    }
}


# --- Build summary ---
all_years = sorted(data.keys())
all_contests = set()
total_results = 0
for year in data:
    for county in data[year]:
        for contest in data[year][county]:
            all_contests.add(contest)
            total_results += 1
summary = {
    "total_years": len(all_years),
    "total_contests": len(all_contests),
    "total_county_results": total_results,
    "years_covered": all_years
}

# --- Restructure results_by_year to match NC format ---
results_by_year = {}
for year in data:
    # Group contests by type (e.g., 'presidential', 'gubernatorial', etc.)
    year_obj = {}
    contest_type_map = defaultdict(dict)
    for county in data[year]:
        for contest in data[year][county]:
            # You may want to improve this logic to classify contest types
            contest_type = 'general'  # Default; customize as needed
            if 'president' in contest.lower():
                contest_type = 'presidential'
            elif 'governor' in contest.lower():
                contest_type = 'gubernatorial'
            elif 'senate' in contest.lower():
                contest_type = 'senate'
            elif 'house' in contest.lower():
                contest_type = 'house'
            # Unique contest key
            contest_key = f"{contest_type}_{year}_{abs(hash(contest))%10000}"
            if contest_key not in contest_type_map[contest_type]:
                contest_type_map[contest_type][contest_key] = {
                    "contest_name": contest,
                    "results": {}
                }
            # Use county name as key (or FIPS if you prefer)
            county_key = county
            contest_type_map[contest_type][contest_key]["results"][county_key] = data[year][county][contest]
    # Flatten contest_type_map into year_obj
    for contest_type in contest_type_map:
        year_obj[contest_type] = contest_type_map[contest_type]
    results_by_year[year] = year_obj

output = {
    "metadata": metadata,
    "summary": summary,
    "results_by_year": results_by_year
}

# Save as JSON
with open(json_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"Structured election results saved to {json_path}")
