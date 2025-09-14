import os
import pandas as pd
import json

data_dir = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data"
output_json = "sc_precinct_results_structured.json"
scan_paths = [
    r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\20161108__sc__general__precinct.csv",
    r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\20181106__sc__general__precinct.csv",
    r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\20201103__sc__general__precinct.csv",
    r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\2012",
    r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\2014",
    r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\2018",
    r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\2022",
    r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\2024",
    r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\20061107__sc__general__county.csv",
    r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\20061107__sc__general__precinct.csv",
    r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\20081104__sc__general__precinct.csv"
]
def get_competitiveness(margin_pct):
    abs_margin = abs(margin_pct)
    if margin_pct >= 40:
        return {"category": "Annihilation", "party": "Republican" if margin_pct > 0 else "Democratic", "color": "#67000d" if margin_pct > 0 else "#08306b"}
    elif abs_margin >= 30:
        return {"category": "Dominant", "party": "Republican" if margin_pct > 0 else "Democratic", "color": "#a50f15" if margin_pct > 0 else "#08519c"}
    elif abs_margin >= 20:
        return {"category": "Stronghold", "party": "Republican" if margin_pct > 0 else "Democratic", "color": "#cb181d" if margin_pct > 0 else "#3182bd"}
    elif abs_margin >= 10:
        return {"category": "Safe", "party": "Republican" if margin_pct > 0 else "Democratic", "color": "#ef3b2c" if margin_pct > 0 else "#6baed6"}
    elif abs_margin >= 5.5:
        return {"category": "Likely", "party": "Republican" if margin_pct > 0 else "Democratic", "color": "#fb6a4a" if margin_pct > 0 else "#9ecae1"}
    elif abs_margin >= 1:
        return {"category": "Lean", "party": "Republican" if margin_pct > 0 else "Democratic", "color": "#fcae91" if margin_pct > 0 else "#c6dbef"}
    elif abs_margin >= 0.5:
        return {"category": "Tilt", "party": "Republican" if margin_pct > 0 else "Democratic", "color": "#fee8c8" if margin_pct > 0 else "#e1f5fe"}
    else:
        return {"category": "Tossup", "party": "Tossup", "color": "#f7f7f7"}

# Helper to collect all CSVs from files and directories
def get_all_csvs(paths):
    csv_files = []
    for path in paths:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.csv'):
                        csv_files.append(os.path.join(root, file))
        elif os.path.isfile(path) and path.endswith('.csv'):
            csv_files.append(path)
    return csv_files


# New structure: results_by_year[year][contest_slug][contest_key]['results'][county_precinct]
results_by_year = {}
office_slug_map = {
    'president': 'president',
    'u.s. senate': 'us_senate',
    'governor': 'governor',
    'lieutenant governor': 'lieutenant_governor',
    'superintendent of education': 'superintendent_of_education',
    'attorney general': 'attorney_general',
    'treasurer': 'state_treasurer',
    'secretary of state': 'secretary_of_state',
    'comptroller': 'comptroller',
    'agriculture': 'agriculture_commissioner',
    'adjutant general': 'adjutant_general',
    'commissioner of agriculture': 'agriculture_commissioner',
    'comptroller general': 'comptroller_general'
}
for csv_path in get_all_csvs(scan_paths):
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Skipping {csv_path}: {e}")
        continue

    # Find year from filename
    year = None
    file = os.path.basename(csv_path)
    for y in range(2000, 2030):
        if str(y) in file:
            year = str(y)
            break
    if not year:
        continue

    base_required = {'office', 'county', 'party', 'votes'}
    has_precinct = 'precinct' in df.columns
    if not base_required.issubset(df.columns):
        print(f"Skipping {csv_path}: missing required columns {base_required - set(df.columns)}")
        continue

    # Exclude 'Straight Party' rows
    df = df[~df['office'].str.contains('Straight Party', case=False, na=False)]

    for office_kw, contest_slug in office_slug_map.items():
        contest_df = df[df['office'].str.lower().str.contains(office_kw, na=False)]
        if contest_df.empty:
            continue
        contest_key = f"{contest_slug}_{year}"
        if year not in results_by_year:
            results_by_year[year] = {}
        if contest_slug not in results_by_year[year]:
            results_by_year[year][contest_slug] = {}
        if contest_key not in results_by_year[year][contest_slug]:
            results_by_year[year][contest_slug][contest_key] = {
                "contest_name": contest_df['office'].iloc[0].upper(),
                "results": {}
            }
        if has_precinct:
            grouped = contest_df.groupby(['county', 'precinct'])
            for group_key, group in grouped:
                # group_key is (county, precinct)
                county = group_key[0] if isinstance(group_key, tuple) else group_key
                precinct = group_key[1] if isinstance(group_key, tuple) else None
                # Robust party matching
                party_series = group['party'].fillna('').str.upper()
                dem_votes = group[party_series.str.startswith('DEM')]['votes'].sum()
                rep_votes = group[party_series.str.startswith('REP')]['votes'].sum()
                other_votes = group[~party_series.str.startswith(('DEM', 'REP'))]['votes'].sum()
                total_votes = group['votes'].sum()
                two_party_total = dem_votes + rep_votes
                margin = rep_votes - dem_votes
                margin_pct = 100 * (rep_votes - dem_votes) / two_party_total if two_party_total else 0
                winner = "REP" if margin > 0 else ("DEM" if margin < 0 else "TIE")
                competitiveness = get_competitiveness(margin_pct)
                all_parties = group.groupby('party')['votes'].sum().to_dict()

                precinct_key = f"{county}_{precinct}".replace(" ", "_").upper()
                # Find DEM and REP candidate names
                dem_candidates = group[party_series.str.startswith('DEM')]['candidate'].dropna().unique()
                rep_candidates = group[party_series.str.startswith('REP')]['candidate'].dropna().unique()
                dem_candidate = '/'.join(dem_candidates) if len(dem_candidates) > 0 else None
                rep_candidate = '/'.join(rep_candidates) if len(rep_candidates) > 0 else None

                results_by_year[year][contest_slug][contest_key]["results"][precinct_key] = {
                    "county": str(county),
                    "precinct": precinct,
                    "contest": contest_df['office'].iloc[0],
                    "year": year,
                    "dem_candidate": dem_candidate,
                    "rep_candidate": rep_candidate,
                    "dem_votes": int(dem_votes),
                    "rep_votes": int(rep_votes),
                    "other_votes": int(other_votes),
                    "total_votes": int(total_votes),
                    "two_party_total": int(two_party_total),
                    "margin": int(margin),
                    "margin_pct": round(margin_pct, 2),
                    "winner": winner,
                    "competitiveness": competitiveness,
                    "all_parties": {k: int(v) for k, v in all_parties.items()}
                }
        else:
            grouped = contest_df.groupby(['county'])
            for group_key, group in grouped:
                # group_key is county (may be tuple)
                county = group_key[0] if isinstance(group_key, tuple) else group_key
                party_series = group['party'].fillna('').str.upper()
                dem_votes = group[party_series.str.startswith('DEM')]['votes'].sum()
                rep_votes = group[party_series.str.startswith('REP')]['votes'].sum()
                other_votes = group[~party_series.str.startswith(('DEM', 'REP'))]['votes'].sum()
                total_votes = group['votes'].sum()
                two_party_total = dem_votes + rep_votes
                margin = rep_votes - dem_votes
                margin_pct = 100 * (rep_votes - dem_votes) / two_party_total if two_party_total else 0
                winner = "REP" if margin > 0 else ("DEM" if margin < 0 else "TIE")
                competitiveness = get_competitiveness(margin_pct)
                all_parties = group.groupby('party')['votes'].sum().to_dict()

                county_key = f"{county}".replace(" ", "_").upper()
                # Find DEM and REP candidate names
                dem_candidates = group[party_series.str.startswith('DEM')]['candidate'].dropna().unique()
                rep_candidates = group[party_series.str.startswith('REP')]['candidate'].dropna().unique()
                dem_candidate = '/'.join(dem_candidates) if len(dem_candidates) > 0 else None
                rep_candidate = '/'.join(rep_candidates) if len(rep_candidates) > 0 else None

                results_by_year[year][contest_slug][contest_key]["results"][county_key] = {
                    "county": str(county),
                    "precinct": None,
                    "contest": contest_df['office'].iloc[0],
                    "year": year,
                    "dem_candidate": dem_candidate,
                    "rep_candidate": rep_candidate,
                    "dem_votes": int(dem_votes),
                    "rep_votes": int(rep_votes),
                    "other_votes": int(other_votes),
                    "total_votes": int(total_votes),
                    "two_party_total": int(two_party_total),
                    "margin": int(margin),
                    "margin_pct": round(margin_pct, 2),
                    "winner": winner,
                    "competitiveness": competitiveness,
                    "all_parties": {k: int(v) for k, v in all_parties.items()}
                }

# Write output to JSON file, sorted by year
sorted_results = {k: results_by_year[k] for k in sorted(results_by_year, key=lambda x: int(x))}
final_output = {"results_by_year": sorted_results}
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(final_output, f, indent=2, ensure_ascii=False)
print(f"Saved structured results to {output_json}")
