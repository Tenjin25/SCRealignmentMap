import os
import csv
import json
from collections import defaultdict

DATA_DIR = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data"
OUTPUT_DIR = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\workspace_files"

def extract_year(fname):
    import re
    m = re.match(r"(\d{4})", fname)
    return m.group(1) if m else None

def aggregate_precinct_votes():
    csv_files = []
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))

    year_aggs = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
        'precinct': None,
        'county': None,
        'contest': None,
        'year': None,
        'dem_candidate': None,
        'rep_candidate': None,
        'dem_votes': 0,
        'rep_votes': 0,
        'other_votes': 0,
        'total_votes': 0,
        'two_party_total': 0,
        'margin': 0,
        'margin_pct': 0.0,
        'winner': None,
        'competitiveness': {},
        'all_parties': {}
    })))
    for fpath in csv_files:
        fname = os.path.basename(fpath)
        year = extract_year(fname)
        if not year:
            continue
        with open(fpath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            include_offices = [
                'PRESIDENT',
                'US SENATE', 'UNITED STATES SENATE', 'U.S. SENATE',
                'GOVERNOR', 'LIEUTENANT GOVERNOR', 'ATTORNEY GENERAL',
                'SECRETARY OF STATE', 'TREASURER', 'STATE TREASURER', 'TREASURER OF STATE',
                'COMPTROLLER GENERAL', 'SUPERINTENDENT OF EDUCATION',
                'COMMISSIONER OF AGRICULTURE'
            ]
            vote_type_cols = ['votes', 'early_voting', 'absentee_by_mail', 'provisional', 'failsafe_provisional', 'failsafe', 'election_day']
            for row in reader:
                office = str(row.get('office', '')).strip().upper()
                if ('HOUSE' in office and ('STATE' in office or 'US' in office)) or ('SENATE' in office and 'STATE' in office):
                    continue
                matched = False
                for inc in include_offices:
                    if inc in office:
                        matched = True
                        break
                if not matched:
                    continue
                county_raw = row.get('county', '')
                county = str(county_raw).strip().upper()
                precinct_raw = row.get('precinct', '')
                precinct = str(precinct_raw).strip().upper()
                if not precinct:
                    continue
                contest = office
                party = str(row.get('party', '')).strip().upper()
                candidate = str(row.get('candidate', '')).strip()
                total_candidate_votes = 0
                for col in vote_type_cols:
                    v = row.get(col)
                    try:
                        total_candidate_votes += int(v) if v is not None and v != '' else 0
                    except (TypeError, ValueError):
                        continue
                result = year_aggs[year][precinct][contest]
                result['precinct'] = precinct
                result['county'] = county
                result['contest'] = contest
                result['year'] = year
                if party in ('DEM', 'DEMOCRAT'):
                    result['dem_candidate'] = candidate
                    result['dem_votes'] += total_candidate_votes
                elif party in ('REP', 'REPUBLICAN'):
                    result['rep_candidate'] = candidate
                    result['rep_votes'] += total_candidate_votes
                else:
                    result['other_votes'] += total_candidate_votes
                result['total_votes'] += total_candidate_votes
                if party:
                    result['all_parties'][party] = result['all_parties'].get(party, 0) + total_candidate_votes
    def get_competitiveness(winner, margin_pct):
        if winner == 'REP':
            if margin_pct >= 40:
                return {'category': 'Annihilation', 'party': 'Republican', 'color': '#67000d'}
            elif margin_pct >= 30:
                return {'category': 'Dominant', 'party': 'Republican', 'color': '#a50f15'}
            elif margin_pct >= 20:
                return {'category': 'Stronghold', 'party': 'Republican', 'color': '#cb181d'}
            elif margin_pct >= 10:
                return {'category': 'Safe', 'party': 'Republican', 'color': '#ef3b2c'}
            elif margin_pct >= 5.5:
                return {'category': 'Likely', 'party': 'Republican', 'color': '#fb6a4a'}
            elif margin_pct >= 1:
                return {'category': 'Lean', 'party': 'Republican', 'color': '#fcae91'}
            elif margin_pct >= 0.5:
                return {'category': 'Tilt', 'party': 'Republican', 'color': '#fee8c8'}
            else:
                return {'category': 'Tossup', 'party': 'Tossup', 'color': '#f7f7f7'}
        elif winner == 'DEM':
            if margin_pct >= 40:
                return {'category': 'Annihilation', 'party': 'Democratic', 'color': '#08306b'}
            elif margin_pct >= 30:
                return {'category': 'Dominant', 'party': 'Democratic', 'color': '#08519c'}
            elif margin_pct >= 20:
                return {'category': 'Stronghold', 'party': 'Democratic', 'color': '#3182bd'}
            elif margin_pct >= 10:
                return {'category': 'Safe', 'party': 'Democratic', 'color': '#6baed6'}
            elif margin_pct >= 5.5:
                return {'category': 'Likely', 'party': 'Democratic', 'color': '#9ecae1'}
            elif margin_pct >= 1:
                return {'category': 'Lean', 'party': 'Democratic', 'color': '#c6dbef'}
            elif margin_pct >= 0.5:
                return {'category': 'Tilt', 'party': 'Democratic', 'color': '#e1f5fe'}
            else:
                return {'category': 'Tossup', 'party': 'Tossup', 'color': '#f7f7f7'}
        else:
            return {'category': 'Tossup', 'party': 'Tossup', 'color': '#f7f7f7'}
    # Sort years for output
    sorted_years = sorted(year_aggs.keys())
    # Option 1: Write separate files per year (sorted)
    for year in sorted_years:
        output = {}
        for precinct in year_aggs[year]:
            output[precinct] = {}
            for contest in year_aggs[year][precinct]:
                result = year_aggs[year][precinct][contest]
                result['two_party_total'] = result['dem_votes'] + result['rep_votes']
                result['margin'] = abs(result['dem_votes'] - result['rep_votes'])
                # Exclude unopposed races
                nonzero_parties = sum([result['dem_votes'] > 0, result['rep_votes'] > 0, result['other_votes'] > 0])
                if nonzero_parties <= 1:
                    continue
                if result['two_party_total'] > 0:
                    result['margin_pct'] = round(100.0 * result['margin'] / result['two_party_total'], 2)
                if result['dem_votes'] > result['rep_votes']:
                    result['winner'] = 'DEM'
                elif result['rep_votes'] > result['dem_votes']:
                    result['winner'] = 'REP'
                else:
                    result['winner'] = 'TIE'
                result['competitiveness'] = get_competitiveness(result['winner'], result['margin_pct'])
                output[precinct][contest] = result
        out_path = os.path.join(OUTPUT_DIR, f"precinct_results_{year}.json")
        with open(out_path, 'w', encoding='utf-8') as out:
            json.dump(output, out, indent=2)
        print(f"Aggregated precinct results for {year} -> {out_path}")

    # Option 2: Write merged file with all years sorted and metadata/summary
    merged_output = {
        "metadata": {
            "title": "South Carolina Statewide Precinct Election Results (Standardized)",
            "description": "Comprehensive precinct-level results for non-gerrymandered races with enhanced categorization",
            "processed_date": "2025-09-23",
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
                    "Competitiveness categorization for each precinct",
                    "Contest type classification (Federal/State/Judicial)",
                    "Office ranking system for analysis prioritization",
                    "Color coding compatible with political geography visualization"
                ]
            }
        },
        "summary": {
            "total_years": len(sorted_years),
            "total_contests": 0,
            "total_precinct_results": 0,
            "years_covered": sorted_years
        },
        "results_by_year": {}
    }
    contest_count = 0
    precinct_result_count = 0
    for year in sorted_years:
        merged_output["results_by_year"][year] = {}
        for precinct in year_aggs[year]:
            merged_output["results_by_year"][year][precinct] = {}
            for contest in year_aggs[year][precinct]:
                result = year_aggs[year][precinct][contest]
                result['two_party_total'] = result['dem_votes'] + result['rep_votes']
                result['margin'] = abs(result['dem_votes'] - result['rep_votes'])
                nonzero_parties = sum([result['dem_votes'] > 0, result['rep_votes'] > 0, result['other_votes'] > 0])
                if nonzero_parties <= 1:
                    continue
                if result['two_party_total'] > 0:
                    result['margin_pct'] = round(100.0 * result['margin'] / result['two_party_total'], 2)
                if result['dem_votes'] > result['rep_votes']:
                    result['winner'] = 'DEM'
                elif result['rep_votes'] > result['dem_votes']:
                    result['winner'] = 'REP'
                else:
                    result['winner'] = 'TIE'
                result['competitiveness'] = get_competitiveness(result['winner'], result['margin_pct'])
                merged_output["results_by_year"][year][precinct][contest] = result
                contest_count += 1
                precinct_result_count += 1
    merged_output["summary"]["total_contests"] = contest_count
    merged_output["summary"]["total_precinct_results"] = precinct_result_count
    merged_path = os.path.join(OUTPUT_DIR, "all_precinct_results.json")
    with open(merged_path, 'w', encoding='utf-8') as out:
        json.dump(merged_output, out, indent=2)
    print(f"Aggregated merged precinct results for all years -> {merged_path}")

if __name__ == "__main__":
    aggregate_precinct_votes()
