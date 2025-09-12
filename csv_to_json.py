import pandas as pd
import json

# Replace with your actual CSV filename
csv_file = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\elstats_search_b48bcf59c9eb3184.csv'
json_file = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\SC\sc_election_results.json'

# Read the CSV
df = pd.read_csv(csv_file, dtype={'fips': str})

# Group by county and FIPS
counties = []
for (fips, name), group in df.groupby(['fips', 'county']):
    results = group[['year', 'contest', 'dem', 'gop', 'other', 'margin']].to_dict(orient='records')
    counties.append({
        'fips': fips,
        'name': name,
        'results': results
    })

# Output to JSON
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump({'counties': counties}, f, indent=2)

print(f"Election data written to {json_file}")