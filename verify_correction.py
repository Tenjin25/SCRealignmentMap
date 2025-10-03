import json

# Verify corrected data
with open('workspace_files/county_results_2020_fips_corrected.json', 'r') as f:
    data = json.load(f)

greenwood = data['45047']
print("Corrected 2020 Greenwood County Results:")
print(f"  Trump: {greenwood['rep_votes']:,} votes ({greenwood['rep_pct']}%)")
print(f"  Biden: {greenwood['dem_votes']:,} votes ({greenwood['dem_pct']}%)")
print(f"  Winner: {greenwood['winner']}")
print(f"  Competitiveness: {greenwood['competitiveness']['category']} {greenwood['competitiveness']['party']}")
print(f"  Color: {greenwood['competitiveness']['color']}")
print()
print("This now shows the historically accurate Republican victory!")