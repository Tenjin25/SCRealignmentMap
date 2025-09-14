"""
automate_county_level_aggregation_and_join.py

Aggregates all OpenElections precinct-level CSVs to county-level for each year, computes competitiveness, and merges with the appropriate county GeoJSON. Outputs a merged GeoJSON for each year.

Assumes:
- Precinct-level CSVs are in Data/{year}/counties/
- County GeoJSONs are in Data/ (e.g., tl_2008_45_county00.geojson)
- Output files will be named sc_{year}_county_election_merged_competitiveness.geojson
"""
import os
import glob
import pandas as pd
import geopandas as gpd
from collections import defaultdict

# Load FIPS lookup once
fips_path = 'sc_county_fips.csv'
fips_df = pd.read_csv(fips_path, dtype=str)
fips_df['county_name'] = fips_df['county_name'].str.strip().str.upper()

# --- Competitiveness scale and function (copied from join_county_geojson_with_competitiveness.py) ---
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
    return {"category": "Tossup", "range": "±0.5%", "party": "Tossup", "color": "#f7f7f7"}

def margin_str(row):
    if row['winner'] == 'REP':
        return f"R+{abs(row['margin_pct']):.2f}"
    elif row['winner'] == 'DEM':
        return f"D+{abs(row['margin_pct']):.2f}"
    else:
        return "Tied"

def party_group(party):
    if isinstance(party, str):
        p = party.upper()
        if p.startswith('DEM'): return 'dem_votes'
        if p.startswith('REP'): return 'rep_votes'
        return 'other_votes'
    return 'other_votes'

def aggregate_precincts_to_county(precinct_files):
    # Aggregate all precincts for a county into a single DataFrame
    dfs = []
    for f in precinct_files:
        df = pd.read_csv(f, dtype=str)
        dfs.append(df)
    results = pd.concat(dfs, ignore_index=True)
    results['votes'] = pd.to_numeric(results['votes'], errors='coerce').fillna(0).astype(int)
    results['county_name'] = results['county'].str.strip().str.upper()
    results['vote_type'] = results['party'].apply(party_group)
    county_agg = results.pivot_table(index='county_name', columns='vote_type', values='votes', aggfunc='sum', fill_value=0).reset_index()
    for col in ['dem_votes', 'rep_votes', 'other_votes']:
        if col not in county_agg.columns:
            county_agg[col] = 0
    county_agg['total_votes'] = county_agg['dem_votes'] + county_agg['rep_votes'] + county_agg['other_votes']
    county_agg['margin'] = county_agg['rep_votes'] - county_agg['dem_votes']
    county_agg['margin_pct'] = ((county_agg['rep_votes'] - county_agg['dem_votes']) / county_agg['total_votes'] * 100).round(2)
    county_agg['winner'] = county_agg.apply(lambda row: 'REP' if row['margin'] > 0 else ('DEM' if row['margin'] < 0 else 'TIE'), axis=1)
    county_agg['competitiveness'] = county_agg['margin_pct'].apply(assign_competitiveness)
    county_agg['category'] = county_agg['competitiveness'].apply(lambda x: x['category'])
    county_agg['comp_party'] = county_agg['competitiveness'].apply(lambda x: x['party'])
    county_agg['comp_color'] = county_agg['competitiveness'].apply(lambda x: x['color'])
    county_agg['comp_range'] = county_agg['competitiveness'].apply(lambda x: x['range'])
    county_agg['margin_str'] = county_agg.apply(margin_str, axis=1)
    # Merge in FIPS code
    merged = county_agg.merge(fips_df, on='county_name', how='left')
    # Reorder columns for clarity
    cols = ['county_fips', 'county_name', 'dem_votes', 'rep_votes', 'other_votes', 'total_votes', 'margin', 'margin_pct', 'winner', 'category', 'comp_party', 'comp_color', 'comp_range', 'margin_str']
    merged = merged[cols]
    return merged

def main():
    data_dir = 'Data'
    geojsons = {
        '2008': 'Data/tl_2008_45_county00.geojson',
        '2012': 'Data/tl_2012_45_county10.geojson',
        '2014': 'Data/tl_2012_45_county10.geojson',
        '2018': 'Data/tl_2012_45_county10.geojson',
        '2022': 'Data/tl_2012_45_county10.geojson',
        '2024': 'Data/tl_2012_45_county10.geojson',
    }
    for year in ['2008', '2012', '2014', '2018', '2022', '2024']:
        counties_dir = os.path.join(data_dir, year, 'counties')
        if not os.path.isdir(counties_dir):
            print(f"Skipping {year}: no counties directory found.")
            continue
        precinct_files = glob.glob(os.path.join(counties_dir, f'*precinct.csv'))
        if not precinct_files:
            print(f"Skipping {year}: no precinct CSVs found.")
            continue
        print(f"Aggregating {len(precinct_files)} precinct files for {year}...")
        county_agg = aggregate_precincts_to_county(precinct_files)
        # Load county GeoJSON
        geojson_path = geojsons.get(year)
        if not geojson_path or not os.path.isfile(geojson_path):
            print(f"Skipping {year}: no county GeoJSON found.")
            continue
        counties = gpd.read_file(geojson_path)
        # Dynamically detect the county name field
        possible_name_fields = ['NAME00', 'NAME10', 'NAME', 'NAMELSAD', 'county_name']
        name_field = None
        for field in possible_name_fields:
            if field in counties.columns:
                name_field = field
                break
        if not name_field:
            print(f"Skipping {year}: no recognized county name field in GeoJSON.")
            continue
        counties['county_name'] = counties[name_field].str.strip().str.upper()
        # Merge in FIPS code to counties GeoDataFrame
        counties = counties.merge(fips_df, on='county_name', how='left')
        # Now join on county_fips
        merged = counties.merge(county_agg, on=['county_fips', 'county_name'], how='left', suffixes=('', '_agg'))
        out_path = f'sc_{year}_county_election_merged_competitiveness.geojson'
        merged.to_file(out_path, driver='GeoJSON')
        print(f"Saved {out_path}")

if __name__ == '__main__':
    main()
