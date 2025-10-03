import json

# Check Greenwood County data in 2022 US Senate
with open('workspace_files/county_results_2022_us_senate_fips.json', 'r') as f:
    data = json.load(f)

greenwood = data.get('45047')
if greenwood:
    print(f"Greenwood County (FIPS 45047):")
    print(f"  County: {greenwood['county']}")
    print(f"  Rep %: {greenwood['rep_pct']}")
    print(f"  Dem %: {greenwood['dem_pct']}")
    print(f"  Margin: {greenwood['rep_pct'] - greenwood['dem_pct']:.1f}% Republican")
    print(f"  Competitiveness:")
    print(f"    Category: {greenwood['competitiveness']['category']}")
    print(f"    Party: {greenwood['competitiveness']['party']}")
    print(f"    Color: {greenwood['competitiveness']['color']}")
else:
    print("Greenwood County not found!")

# Also check a few other counties for comparison
print("\nOther counties for comparison:")
for fips in ['45001', '45003', '45049']:  # Abbeville, Aiken, Hampton
    county = data.get(fips)
    if county:
        margin = county['rep_pct'] - county['dem_pct']
        print(f"{county['county']}: {margin:.1f}% margin → {county['competitiveness']['category']} → {county['competitiveness']['color']}")