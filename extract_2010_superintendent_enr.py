"""
Extract 2010 State Superintendent of Education data from SC ENR
Uses the same county structure as extract_2010_all.py
"""

import requests
import json
import time
from pathlib import Path

# SC County FIPS mapping
FIPS_MAP = {
    'Abbeville': '45001', 'Aiken': '45003', 'Allendale': '45005', 'Anderson': '45007',
    'Bamberg': '45009', 'Barnwell': '45011', 'Beaufort': '45013', 'Berkeley': '45015',
    'Calhoun': '45017', 'Charleston': '45019', 'Cherokee': '45021', 'Chester': '45023',
    'Chesterfield': '45025', 'Clarendon': '45027', 'Colleton': '45029', 'Darlington': '45031',
    'Dillon': '45033', 'Dorchester': '45035', 'Edgefield': '45037', 'Fairfield': '45039',
    'Florence': '45041', 'Georgetown': '45043', 'Greenville': '45045', 'Greenwood': '45047',
    'Hampton': '45049', 'Horry': '45051', 'Jasper': '45053', 'Kershaw': '45055',
    'Lancaster': '45057', 'Laurens': '45059', 'Lee': '45061', 'Lexington': '45063',
    'McCormick': '45065', 'Marion': '45067', 'Marlboro': '45069', 'Newberry': '45071',
    'Oconee': '45073', 'Orangeburg': '45075', 'Pickens': '45077', 'Richland': '45079',
    'Saluda': '45081', 'Spartanburg': '45083', 'Sumter': '45085', 'Union': '45087',
    'Williamsburg': '45089', 'York': '45091'
}

# County ENR IDs for 2010
COUNTY_IDS = {
    'Abbeville': '40479', 'Aiken': '40481', 'Allendale': '40483', 'Anderson': '40485',
    'Bamberg': '40487', 'Barnwell': '40489', 'Beaufort': '40491', 'Berkeley': '40493',
    'Calhoun': '40495', 'Charleston': '40497', 'Cherokee': '40499', 'Chester': '40501',
    'Chesterfield': '40503', 'Clarendon': '40505', 'Colleton': '40507', 'Darlington': '40509',
    'Dillon': '40511', 'Dorchester': '40513', 'Edgefield': '40515', 'Fairfield': '40517',
    'Florence': '40519', 'Georgetown': '40521', 'Greenville': '40523', 'Greenwood': '40525',
    'Hampton': '40527', 'Horry': '40529', 'Jasper': '40531', 'Kershaw': '40533',
    'Lancaster': '40535', 'Laurens': '40537', 'Lee': '40539', 'Lexington': '40541',
    'McCormick': '40543', 'Marion': '40545', 'Marlboro': '40547', 'Newberry': '40549',
    'Oconee': '40551', 'Orangeburg': '40553', 'Pickens': '40555', 'Richland': '40557',
    'Saluda': '40559', 'Spartanburg': '40561', 'Sumter': '40563', 'Union': '40565',
    'Williamsburg': '40567', 'York': '40569'
}

def fetch_county_superintendent(county_name, county_id):
    """Fetch superintendent data for a county from ENR JSON API"""
    fips = FIPS_MAP[county_name]
    
    # Build the JSON URL following the pattern: 
    # https://www.enr-scvotes.org/SC/{CountyName}/{election_id}/{county_id}/json/sum.json
    # For 2010, election_id is 19078 (different from the select page which was 19077)
    json_url = f"https://www.enr-scvotes.org/SC/{county_name}/19078/{county_id}/json/sum.json"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(json_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract superintendent contest
            for contest in data.get('Contests', []):
                if 'Superintendent' in contest.get('C', ''):
                    candidates = contest['CH']
                    parties = contest['P']
                    votes = contest['V']
                    
                    # Find DEM and REP
                    dem_votes = 0
                    rep_votes = 0
                    dem_candidate = ""
                    rep_candidate = ""
                    other_votes = 0
                    all_parties = {}
                    
                    for i, party in enumerate(parties):
                        vote_count = votes[i]
                        candidate_name = candidates[i]
                        all_parties[party] = vote_count
                        
                        if party == 'DEM':
                            dem_votes = vote_count
                            dem_candidate = candidate_name
                        elif party == 'REP':
                            rep_votes = vote_count
                            rep_candidate = candidate_name
                        elif party not in ['DEM', 'REP']:
                            other_votes += vote_count
                    
                    if dem_votes > 0 and rep_votes > 0:
                        two_party_total = dem_votes + rep_votes
                        margin = rep_votes - dem_votes
                        margin_pct = round((margin / two_party_total * 100), 2)
                        
                        return {
                            fips: {
                                'dem_votes': dem_votes,
                                'rep_votes': rep_votes,
                                'other_votes': other_votes,
                                'total_votes': sum(votes),
                                'all_parties': all_parties,
                                'margin': margin,
                                'margin_pct': margin_pct,
                                'winner': 'REP' if margin > 0 else 'DEM',
                                'dem_candidate': dem_candidate,
                                'rep_candidate': rep_candidate
                            }
                        }
            
            print(f"  ⚠ {county_name}: No superintendent data found")
            return None
            
        else:
            print(f"  ✗ {county_name}: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ✗ {county_name}: {e}")
        return None

def main():
    results = {}
    
    print("Extracting 2010 Superintendent of Education data...")
    print("=" * 60)
    
    for county_name in sorted(FIPS_MAP.keys()):
        county_id = COUNTY_IDS[county_name]
        fips = FIPS_MAP[county_name]
        
        print(f"Fetching {county_name} ({fips})...", end=" ")
        
        county_data = fetch_county_superintendent(county_name, county_id)
        
        if county_data:
            results.update(county_data)
            data = county_data[fips]
            print(f"✓ {data['dem_candidate'][:20]} {data['dem_votes']:,} vs {data['rep_candidate'][:20]} {data['rep_votes']:,}")
        
        time.sleep(0.3)  # Rate limiting
    
    # Save raw results
    output_file = 'Data/county_results_2010_superintendent_raw.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✓ Extracted {len(results)}/46 counties")
    print(f"✓ Saved to {output_file}")
    
    # Calculate statewide totals
    if results:
        total_dem = sum(c['dem_votes'] for c in results.values())
        total_rep = sum(c['rep_votes'] for c in results.values())
        total_other = sum(c['other_votes'] for c in results.values())
        total_votes = sum(c['total_votes'] for c in results.values())
        
        print(f"\nStatewide totals:")
        print(f"  DEM ({list(results.values())[0]['dem_candidate']}): {total_dem:,} ({total_dem/total_votes*100:.1f}%)")
        print(f"  REP ({list(results.values())[0]['rep_candidate']}): {total_rep:,} ({total_rep/total_votes*100:.1f}%)")
        print(f"  Other: {total_other:,}")
        print(f"  Margin: R+{(total_rep - total_dem):,} ({((total_rep - total_dem) / (total_dem + total_rep) * 100):.2f}%)")

if __name__ == "__main__":
    main()
