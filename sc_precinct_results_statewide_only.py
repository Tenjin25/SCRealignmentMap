"""
Aggregates SC county-level election CSVs and joins with VTD GeoJSON, outputting NC-style nested JSON for mapping/analysis.
FILTERED VERSION - Only processes major statewide offices.

- Reads all county CSVs in Data/2012
- Joins with tl_2012_45_vtd10.geojson on county/precinct
- Aggregates results by contest and precinct
- Calculates vote totals, margins, winner, competitiveness, and color
- Outputs JSON in NC-style format

Dependencies: pandas, geopandas
"""
import pandas as pd
import geopandas as gpd
import json
import os
import glob

# --- CONFIG ---
base_data_dir = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data'
base_vtd_dir = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\VTDs'
out_json = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\sc_precinct_results_statewide_only.json'

# STATEWIDE OFFICES ONLY
target_contests = [
    "PRESIDENT",
    "U.S. SENATE", 
    "US SENATE",
    "UNITED STATES SENATE",
    "GOVERNOR",
    "LIEUTENANT GOVERNOR",
    "ATTORNEY GENERAL",
    "SECRETARY OF STATE",
    "STATE TREASURER",
    "COMPTROLLER GENERAL",
    "STATE SUPERINTENDENT OF EDUCATION",
    "COMMISSIONER OF AGRICULTURE",
    "ADJUTANT GENERAL"
]

comp_scale = {
    "Republican": [
        (40, 'Annihilation', '#67000d'),
        (30, 'Dominant', '#a50f15'),
        (20, 'Stronghold', '#cb181d'),
        (10, 'Safe', '#ef3b2c'),
        (5.5, 'Likely', '#fb6a4a'),
        (1, 'Lean', '#fcae91'),
        (0.5, 'Tilt', '#fee8c8'),
    ],
    "Tossup": [
        (0.5, 'Tossup', '#f7f7f7'),
    ],
    "Democratic": [
        (0.5, 'Tilt', '#e1f5fe'),
        (1, 'Lean', '#c6dbef'),
        (5.5, 'Likely', '#9ecae1'),
        (10, 'Safe', '#6baed6'),
        (20, 'Stronghold', '#3182bd'),
        (30, 'Dominant', '#08519c'),
        (40, 'Annihilation', '#08306b'),
    ]
}

def get_contest_type(contest_name):
    name = contest_name.upper()
    if "PRESIDENT" in name:
        return "presidential"
    elif "U.S. SENATE" in name or "US SENATE" in name or "UNITED STATES SENATE" in name:
        return "us_senate"
    elif "GOVERNOR" in name and "LIEUTENANT" not in name:
        return "governor"
    elif "LIEUTENANT GOVERNOR" in name:
        return "lt_governor"
    elif "ATTORNEY GENERAL" in name:
        return "attorney_general"
    elif "SECRETARY OF STATE" in name:
        return "secretary_of_state"
    elif "STATE TREASURER" in name:
        return "state_treasurer"
    elif "COMPTROLLER GENERAL" in name:
        return "comptroller_general"
    elif "STATE SUPERINTENDENT OF EDUCATION" in name:
        return "state_superintendent_of_education"
    elif "COMMISSIONER OF AGRICULTURE" in name:
        return "commissioner_of_agriculture"
    elif "ADJUTANT GENERAL" in name:
        return "adjutant_general"
    else:
        # Normalize: lowercase, replace spaces and punctuation with underscores
        import re
        norm = re.sub(r'[^A-Za-z0-9]+', '_', contest_name.strip().lower())
        return norm

def is_statewide_office(office_name):
    """Check if an office is one of our target statewide offices"""
    office_upper = office_name.upper()
    for target in target_contests:
        if target in office_upper:
            return True
    return False

year_csv_map = {}
all_csvs = glob.glob(os.path.join(base_data_dir, '**', '*.csv'), recursive=True)
print(f"Found {len(all_csvs)} CSV files")
for csv_path in all_csvs:
    fname = os.path.basename(csv_path)
    print(f"Processing: {fname}")
    if fname[:4].isdigit():
        year = fname[:4]
        # Only process precinct-level files
        if 'precinct' in fname.lower():
            year_csv_map.setdefault(year, []).append(csv_path)
            print(f"Added {fname} to year {year}")
        else:
            print(f"Skipping non-precinct file: {fname}")
    else:
        print(f"Skipping file without year prefix: {fname}")

print(f"Year-CSV mapping: {year_csv_map}")

output = {}

for year_str in sorted(year_csv_map.keys()):
    print(f"\n=== Processing year {year_str} ===")
    df_list = []
    for csv_path in year_csv_map[year_str]:
        print(f"Reading: {os.path.basename(csv_path)}")
        try:
            df = pd.read_csv(csv_path)
            print(f"  - Shape: {df.shape}")
            print(f"  - Columns: {list(df.columns)}")
            for col in ['county', 'precinct', 'office', 'party', 'candidate', 'votes']:
                if col not in df.columns:
                    print(f"  - Missing column '{col}', adding empty column")
                    df[col] = ''
            df['county'] = df['county'].astype(str).str.upper()
            df['precinct'] = df['precinct'].astype(str).str.upper()
            df['office'] = df['office'].astype(str)
            df['party'] = df['party'].astype(str)
            df['candidate'] = df['candidate'].astype(str)
            df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
            df_list.append(df)
            print(f"  - Successfully processed {len(df)} rows")
        except Exception as e:
            print(f"  - Error reading {csv_path}: {e}")
            continue
    year = int(year_str)
    if 2006 <= year <= 2010:
        vtd_geojson = os.path.join(base_vtd_dir, 'tl_2008_45_vtd00.geojson')
    elif 2012 <= year <= 2018:
        vtd_geojson = os.path.join(base_vtd_dir, 'tl_2012_45_vtd10.geojson')
    elif 2020 <= year <= 2024:
        vtd_geojson = os.path.join(base_vtd_dir, 'tl_2020_45_vtd20.geojson')
    else:
        print(f"No VTD mapping for year {year}, skipping")
        continue

    print(f"Using VTD file: {os.path.basename(vtd_geojson)}")
    
    if not os.path.exists(vtd_geojson):
        print(f"VTD file not found: {vtd_geojson}")
        continue
        
    try:
        vtd_gdf = gpd.read_file(vtd_geojson)
        print(f"VTD GeoJSON loaded: {len(vtd_gdf)} features")
        print(f"VTD columns: {list(vtd_gdf.columns)}")
        
        # Handle different column names across years
        if 'NAME00' in vtd_gdf.columns:
            vtd_gdf['county'] = vtd_gdf['NAME00'].str.upper()
            vtd_gdf['precinct'] = vtd_gdf['NAME00'].str.upper()
        elif 'NAME10' in vtd_gdf.columns:
            vtd_gdf['county'] = vtd_gdf['NAME10'].str.upper()
            vtd_gdf['precinct'] = vtd_gdf['NAME10'].str.upper()
        elif 'NAME20' in vtd_gdf.columns:
            vtd_gdf['county'] = vtd_gdf['NAME20'].str.upper()
            vtd_gdf['precinct'] = vtd_gdf['NAME20'].str.upper()
        else:
            print(f"No NAME column found in VTD file for year {year}")
            vtd_gdf['county'] = ''
            vtd_gdf['precinct'] = ''
    except Exception as e:
        print(f"Error reading VTD file: {e}")
        continue

    if not df_list:
        print(f"No data found for year {year_str}")
        continue
    results_df = pd.concat(df_list, ignore_index=True)
    print(f"Combined data: {len(results_df)} total rows")

    # Filter to only statewide offices
    statewide_df = results_df[results_df['office'].apply(is_statewide_office)]
    print(f"After statewide filter: {len(statewide_df)} rows")

    # Aggregate statewide contests only
    all_contests = statewide_df['office'].dropna().unique()
    print(f"Found statewide contests: {list(all_contests)}")
    
    contests_processed = 0
    for contest_name in all_contests:
        # For pre-2018, treat Lt. Governor as separate contest
        if int(year_str) < 2018 and contest_name.upper() == "LIEUTENANT GOVERNOR":
            contest_type = "lt_governor"
        else:
            contest_type = get_contest_type(contest_name)
        contest_id = f"{contest_type}_{year_str}"
        actual_df = statewide_df[statewide_df['office'].str.upper() == contest_name.upper()]
        if actual_df.empty:
            print(f"  - No data for contest: {contest_name}")
            continue
        candidate_counts = actual_df.groupby('candidate')['votes'].sum()
        candidates_with_votes = candidate_counts[candidate_counts > 0].index.tolist()
        if len(candidates_with_votes) <= 1:
            print(f"  - Skipping {contest_name}: only {len(candidates_with_votes)} candidates with votes")
            continue
            
        print(f"  - Processing {contest_name}: {len(candidates_with_votes)} candidates")
        contests_processed += 1
        contest_obj = {
            'contest_name': contest_name,
            'results': {}
        }
        dem_candidate = rep_candidate = None
        for cand in candidates_with_votes:
            parties = [p.upper() for p in actual_df[actual_df['candidate'] == cand]['party'].unique()]
            if any(p in ['DEM', 'DEMOCRAT'] for p in parties):
                dem_candidate = cand
            elif any(p in ['REP', 'REPUBLICAN'] for p in parties):
                rep_candidate = cand
        contest_obj['dem_candidate'] = dem_candidate
        contest_obj['rep_candidate'] = rep_candidate
        for _, row in actual_df.iterrows():
            key = f"{row['county']}_{row['precinct']}"
            if key not in contest_obj['results']:
                contest_obj['results'][key] = {
                    'county': row['county'],
                    'precinct': row['precinct'],
                    'contest': contest_name,
                    'year': year_str,
                    'dem_candidate': dem_candidate,
                    'rep_candidate': rep_candidate,
                    'results': {},
                    'total_votes': 0,
                    'all_parties': {},
                    'votes_by_method': {}
                }
            party_raw = row['party'] if pd.notnull(row['party']) else ''
            party = party_raw.upper()
            if party in ['DEMOCRAT', 'DEM']:
                party = 'DEM'
            elif party in ['REPUBLICAN', 'REP']:
                party = 'REP'
            candidate = row['candidate'] if pd.notnull(row['candidate']) else ''
            votes = int(round(float(row['votes'])) if pd.notnull(row['votes']) else 0)
            contest_obj['results'][key]['results'][candidate] = votes
            contest_obj['results'][key]['all_parties'][party] = int(round(contest_obj['results'][key]['all_parties'].get(party, 0))) + votes
            if 'voting_method' in actual_df.columns:
                method = row['voting_method'] if pd.notnull(row['voting_method']) else 'UNKNOWN'
                contest_obj['results'][key]['votes_by_method'][method] = contest_obj['results'][key]['votes_by_method'].get(method, 0) + votes
        for precinct in contest_obj['results']:
            if contest_obj['results'][precinct]['votes_by_method']:
                contest_obj['results'][precinct]['total_votes'] = int(round(sum(contest_obj['results'][precinct]['votes_by_method'].values())))
            else:
                contest_obj['results'][precinct]['total_votes'] = int(round(sum(float(v) for v in contest_obj['results'][precinct]['results'].values())))
            parties = contest_obj['results'][precinct]['all_parties']
            dem = int(round(parties.get('DEM', 0)))
            rep = int(round(parties.get('REP', 0)))
            other = int(round(sum(v for k, v in parties.items() if k not in ['DEM', 'REP'])))
            two_party_total = dem + rep
            margin = rep - dem
            margin_pct = (margin / two_party_total * 100.0) if two_party_total else 0.0
            if two_party_total == 0:
                winner = 'Tossup'
                cat = 'Tossup'
                color = '#f7f7f7'
                code = 'TOSSUP'
            elif abs(margin_pct) <= 0.5:
                winner = 'Tossup'
                cat = 'Tossup'
                color = '#f7f7f7'
                code = 'TOSSUP'
            elif margin_pct > 0.5:
                winner = 'Republican'
                for thresh, name, col in comp_scale['Republican']:
                    if abs(margin_pct) >= thresh:
                        cat = name
                        color = col
                        code = f'R_{name.upper()}'
                        break
            elif margin_pct < -0.5:
                winner = 'Democratic'
                for thresh, name, col in reversed(comp_scale['Democratic']):
                    if abs(margin_pct) >= thresh:
                        cat = name
                        color = col
                        code = f'D_{name.upper()}'
                        break
            contest_obj['results'][precinct].update({
                'dem_votes': dem,
                'rep_votes': rep,
                'other_votes': other,
                'two_party_total': two_party_total,
                'margin': margin,
                'margin_pct': f"{margin_pct:.2f}",
                'winner': winner,
                'competitiveness': {
                    'category': cat,
                    'party': winner,
                    'code': code,
                    'color': color
                }
            })
        output.setdefault(year_str, {})[contest_id] = contest_obj
    
    print(f"Year {year_str}: processed {contests_processed} statewide contests")

print(f"\n=== SUMMARY ===")
total_contests = sum(len(contests) for contests in output.values())
print(f"Total years processed: {len(output)}")
print(f"Total statewide contests processed: {total_contests}")
for year, contests in output.items():
    print(f"  {year}: {len(contests)} contests")

# --- OUTPUT ---
with open(out_json, 'w') as f:
    json.dump({'results_by_year': output}, f, indent=2)
print(f'Statewide-only NC-style JSON saved to {out_json}')