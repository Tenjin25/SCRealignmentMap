import json

# Read the Aiken 2010 sample to verify superintendent data format
with open('workspace_files/enr_downloads/aiken_2010.json', 'r') as f:
    aiken_data = json.load(f)

print("Checking Aiken 2010 for superintendent data...")
for contest in aiken_data['Contests']:
    contest_name = contest['C']
    if 'Superintendent' in contest_name:
        print(f"\nFound: {contest_name}")
        print(f"Candidates: {contest['CH']}")
        print(f"Parties: {contest['P']}")
        print(f"Votes: {contest['V']}")
        
        # Find DEM and REP
        for i, party in enumerate(contest['P']):
            if party == 'DEM':
                print(f"  DEM: {contest['CH'][i]} - {contest['V'][i]:,} votes")
            elif party == 'REP':
                print(f"  REP: {contest['CH'][i]} - {contest['V'][i]:,} votes")
