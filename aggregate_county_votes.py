import os
import csv
import json
from collections import defaultdict

DATA_DIR = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data"
VTD_DIR = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\VTDs"
OUTPUT_DIR = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\workspace_files"

# Helper to extract year from filename
import re
def extract_year(fname):
    m = re.match(r"(\d{4})", fname)
    return m.group(1) if m else None

def load_vtds():
    vtd_map = defaultdict(list)
    # Assumes VTDs are stored as CSVs with 'county' and 'vtd' columns
    for fname in os.listdir(VTD_DIR):
        if fname.endswith('.csv'):
            with open(os.path.join(VTD_DIR, fname), newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    county = row.get('county')
                    vtd = row.get('vtd')
                    if county and vtd:
                        vtd_map[county.upper()].append(vtd)
    return vtd_map

def aggregate_votes():
    vtd_map = load_vtds()
    # Recursively find all CSV files in DATA_DIR and subfolders
    csv_files = []
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))

    log_path = os.path.join(OUTPUT_DIR, "aggregate_county_votes.log")
    log_file = open(log_path, "w", encoding="utf-8")
    def log(msg):
        print(msg)
        log_file.write(msg + "\n")

    # Aggregate by year across all files
    year_aggs = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
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
                if not county:
                    log(f"Skipped row with missing county: {row}")
                    continue
                log(f"Processing county: {county} in file: {fname}")
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
                result = year_aggs[year][county][contest]
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
    # After all files processed, calculate and write output per year
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
    for year in year_aggs:
        output = {}
        for county in year_aggs[year]:
            for contest in year_aggs[year][county]:
                result = year_aggs[year][county][contest]
                result['two_party_total'] = result['dem_votes'] + result['rep_votes']
                result['margin'] = abs(result['dem_votes'] - result['rep_votes'])
                # Exclude unopposed races: only one party has nonzero votes
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
                if contest not in output:
                    output[contest] = {}
                output[contest][county] = result
        out_path = os.path.join(OUTPUT_DIR, f"county_results_{year}.json")
        with open(out_path, 'w', encoding='utf-8') as out:
            json.dump(output, out, indent=2)
        log(f"Aggregated contest results for {year} -> {out_path}")
    log_file.close()

if __name__ == "__main__":
    aggregate_votes()
