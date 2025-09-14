# join_county_geojson_with_competitiveness.py
"""
Joins a county GeoJSON with county-level election results, computes margin, margin_pct, winner, and assigns competitiveness category and color.

Dependencies: geopandas, pandas
"""
import geopandas as gpd
import pandas as pd


# Detailed competitiveness scale as per user spec
competitiveness_scale = {
    'Republican': [
        {"category": "Annihilation", "range": "R+40%+", "min": 40, "max": 100, "color": "#67000d"},
        {"category": "Dominant", "range": "R+30-40%", "min": 30, "max": 40, "color": "#a50f15"},
        {"category": "Stronghold", "range": "R+20-30%", "min": 20, "max": 30, "color": "#cb181d"},
        {"category": "Safe", "range": "R+10-20%", "min": 10, "max": 20, "color": "#ef3b2c"},
        {"category": "Likely", "range": "R+5.5-10%", "min": 5.5, "max": 10, "color": "#fb6a4a"},
        {"category": "Lean", "range": "R+1-5.5%", "min": 1, "max": 5.5, "color": "#fcae91"},
        {"category": "Tilt", "range": "R+0.5-1%", "min": 0.5, "max": 1, "color": "#fee8c8"}
    ],
    'Tossup': [
        {"category": "Tossup", "range": "±0.5%", "min": 0, "max": 0.5, "color": "#f7f7f7"}
    ],
    'Democratic': [
        {"category": "Tilt", "range": "D+0.5-1%", "min": 0.5, "max": 1, "color": "#e1f5fe"},
        {"category": "Lean", "range": "D+1-5.5%", "min": 1, "max": 5.5, "color": "#c6dbef"},
        {"category": "Likely", "range": "D+5.5-10%", "min": 5.5, "max": 10, "color": "#9ecae1"},
        {"category": "Safe", "range": "D+10-20%", "min": 10, "max": 20, "color": "#6baed6"},
        {"category": "Stronghold", "range": "D+20-30%", "min": 20, "max": 30, "color": "#3182bd"},
        {"category": "Dominant", "range": "D+30-40%", "min": 30, "max": 40, "color": "#08519c"},
        {"category": "Annihilation", "range": "D+40%+", "min": 40, "max": 100, "color": "#08306b"}
    ]
}

def assign_competitiveness(margin_pct):
    abs_margin = abs(margin_pct)
    if margin_pct > 0.5:
        for entry in competitiveness_scale['Republican']:
            if abs_margin >= entry['min'] and abs_margin < entry['max']:
                return {"category": entry['category'], "range": entry['range'], "party": "Republican", "color": entry['color']}
    elif margin_pct < -0.5:
        for entry in competitiveness_scale['Democratic']:
            if abs_margin >= entry['min'] and abs_margin < entry['max']:
                return {"category": entry['category'], "range": entry['range'], "party": "Democratic", "color": entry['color']}
    else:
        entry = competitiveness_scale['Tossup'][0]
        return {"category": entry['category'], "range": entry['range'], "party": "Tossup", "color": entry['color']}
    # Fallback
    return {"category": "Tossup", "range": "±0.5%", "party": "Tossup", "color": "#f7f7f7"}

# Paths (update as needed)
county_geojson = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\tl_2008_45_county00.geojson'
election_csv = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\20061107__sc__general__county.csv'
output_geojson = 'sc_2008_county_election_merged_competitiveness.geojson'

# Load GeoJSON
counties = gpd.read_file(county_geojson)

# Load election results
results = pd.read_csv(election_csv, dtype=str)


# Use county name for join

# --- Standardize county name for join ---
counties['county_name'] = counties['NAME00'].str.strip().str.upper()
if 'county' in results.columns:
    results['county_name'] = results['county'].str.strip().str.upper()
elif 'county_name' in results.columns:
    results['county_name'] = results['county_name'].str.strip().str.upper()
else:
    raise Exception('No county name column found in election CSV.')

# --- Aggregate OpenElections CSV to county-level vote totals ---
results['votes'] = pd.to_numeric(results['votes'], errors='coerce').fillna(0).astype(int)
def party_group(party):
    if isinstance(party, str):
        p = party.upper()
        if p.startswith('DEM'): return 'dem_votes'
        if p.startswith('REP'): return 'rep_votes'
        return 'other_votes'
    return 'other_votes'
results['vote_type'] = results['party'].apply(party_group)
county_agg = results.pivot_table(index='county_name', columns='vote_type', values='votes', aggfunc='sum', fill_value=0).reset_index()
for col in ['dem_votes', 'rep_votes', 'other_votes']:
    if col not in county_agg.columns:
        county_agg[col] = 0

# --- Compute competitiveness fields ---
county_agg['total_votes'] = county_agg['dem_votes'] + county_agg['rep_votes'] + county_agg['other_votes']
county_agg['margin'] = county_agg['rep_votes'] - county_agg['dem_votes']
county_agg['margin_pct'] = ((county_agg['rep_votes'] - county_agg['dem_votes']) / county_agg['total_votes'] * 100).round(2)
county_agg['winner'] = county_agg.apply(lambda row: 'REP' if row['margin'] > 0 else ('DEM' if row['margin'] < 0 else 'TIE'), axis=1)
county_agg['competitiveness'] = county_agg['margin_pct'].apply(assign_competitiveness)
county_agg['category'] = county_agg['competitiveness'].apply(lambda x: x['category'])
county_agg['comp_party'] = county_agg['competitiveness'].apply(lambda x: x['party'])
county_agg['comp_color'] = county_agg['competitiveness'].apply(lambda x: x['color'])
county_agg['comp_range'] = county_agg['competitiveness'].apply(lambda x: x['range'])
def margin_str(row):
    if row['winner'] == 'REP':
        return f"R+{abs(row['margin_pct']):.2f}"
    elif row['winner'] == 'DEM':
        return f"D+{abs(row['margin_pct']):.2f}"
    else:
        return "Tied"
county_agg['margin_str'] = county_agg.apply(margin_str, axis=1)

# --- Merge with GeoJSON ---
merged = counties.merge(county_agg, on='county_name', how='left')

# Save
merged.to_file(output_geojson, driver='GeoJSON')
print(f'Merged county GeoJSON and election results with competitiveness saved as {output_geojson}')
