import json

data = json.load(open('workspace_files/enr_downloads/aiken_2008.json'))
senate = [c for c in data['Contests'] if 'Senate' in c['C'] and 'U.S.' in c['C']][0]

print(f"Contest: {senate['C']}")
print(f"Candidates: {senate['CH']}")
print(f"Parties: {senate['P']}")
print(f"Votes: {senate['V']}")
print(f"\nTotal votes: {sum(senate['V'])}")
