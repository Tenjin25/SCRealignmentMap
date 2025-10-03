import os
import json
import csv
import sys
from collections import defaultdict
import geojson

def load_vtd_mapping(geojson_path):
    """
    Returns a dict mapping precinct name/code to county name (or FIPS)
    """
    with open(geojson_path, 'r', encoding='utf-8') as f:
        gj = geojson.load(f)
    mapping = {}
    # Detect year from filename
    year = None
    if '2008' in geojson_path:
        year = '2008'
    elif '2012' in geojson_path:
        year = '2012'
    elif '2020' in geojson_path:
        year = '2020'
    # Set property keys by year
    if year == '2008':
        vtd_key = 'NAME00'
        county_key = 'COUNTYFP00'
    elif year == '2020':
        vtd_key = 'NAME20'
        county_key = 'COUNTYFP20'
    elif year == '2012':
        vtd_key = 'NAME10'
        county_key = 'COUNTYFP10'
    else:
        vtd_key = 'VTDNAME'
        county_key = 'COUNTYFP'
    if gj['features']:
        print('Sample VTD GeoJSON property keys:', list(gj['features'][0]['properties'].keys()))
    for feat in gj['features']:
        props = feat['properties']
        vtd = props.get(vtd_key)
        county = props.get(county_key)
        if vtd and county:
            mapping[str(vtd).strip().upper()] = str(county).strip()
    print(f'Loaded VTD mapping: {len(mapping)} entries. Sample:', list(mapping.items())[:5])
    return mapping

def aggregate_election_csv(csv_path, vtd_mapping, offices_to_include):
    """
    Aggregates votes by county for selected offices
    """
    county_results = defaultdict(lambda: defaultdict(int))
    unmatched_precincts = set()
    included_offices = set()
    all_offices = set()
    all_precincts_csv = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            precinct = row.get('precinct') or row.get('PRECINCT') or row.get('VTD') or row.get('VTDNAME') or row.get('NAME')
            office = row.get('office') or row.get('OFFICE')
            candidate = row.get('candidate') or row.get('CANDIDATE')
            party = row.get('party') or row.get('PARTY')
            votes = row.get('votes') or row.get('VOTES')
            county_direct = row.get('county') or row.get('COUNTY')
            if not precinct or not office or not votes:
                continue
            precinct_key = str(precinct).strip().upper()
            all_precincts_csv.add(precinct_key)
            all_offices.add(office)
            county = vtd_mapping.get(precinct_key)
            # Fallback: use county from row if mapping fails
            if not county:
                if county_direct:
                    county = str(county_direct).strip()
                else:
                    unmatched_precincts.add(precinct_key)
                    continue
            # Improved office filter: match if any keyword is in office name
            if not any(o in office.lower() for o in offices_to_include):
                continue
            included_offices.add(office)
            try:
                votes = int(votes)
            except:
                continue
            # Aggregate by county, office, candidate, party
            county_results[county][f'{office}|{candidate}|{party}'] += votes
    # Debug output
    print(f'Unmatched precincts ({len(unmatched_precincts)}):', list(unmatched_precincts)[:10], '...')
    print(f'Included offices: {sorted(list(included_offices))}')
    print(f'Sample office names in CSV: {sorted(list(all_offices))[:10]} ...')
    print(f'Sample precinct names in CSV: {sorted(list(all_precincts_csv))[:10]} ...')
    print(f'Sample precinct names in VTD mapping: {sorted(list(vtd_mapping.keys()))[:10]} ...')
    return county_results

def main():
    # Map years to file paths
    vtd_files = {
        '2008': 'VTDs/tl_2008_45_vtd00.geojson',
        '2012': 'VTDs/tl_2012_45_vtd10.geojson',
        '2020': 'VTDs/tl_2020_45_vtd20.geojson',
    }
    election_files = {
        '2008': 'Data/20081104__sc__general__precinct.csv',
        '2012': 'Data/20121106__sc__general__precinct.csv',
        '2020': 'Data/20201103__sc__general__precinct.csv',
        '2022': 'Data/20221108__sc__general__precinct.csv',
        '2024': 'Data/20241105__sc__general__precinct.csv',
    }
    offices_to_include = [
        'president', 'us senate', 'governor', 'secretary of state', 'attorney general',
        'treasurer', 'comptroller', 'superintendent', 'agriculture', 'lieutenant governor',
        'pres', 'senate', 'gov', 'sec', 'att', 'treas', 'comp', 'super', 'agri', 'lt gov'
    ]
    # Remove legislative offices
    exclude_keywords = ['state house', 'us house', 'state senate', 'house', 'senate district']
    offices_to_include = [o for o in offices_to_include if not any(x in o for x in exclude_keywords)]
    for year, csv_path in election_files.items():
        vtd_path = vtd_files.get(year)
        if not vtd_path or not os.path.exists(vtd_path) or not os.path.exists(csv_path):
            continue
        vtd_mapping = load_vtd_mapping(vtd_path)
        results = aggregate_election_csv(csv_path, vtd_mapping, offices_to_include)
        out_path = f'county_aggregates_{year}.json'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f'Aggregated county results for {year} saved to {out_path}')

if __name__ == '__main__':
    main()
