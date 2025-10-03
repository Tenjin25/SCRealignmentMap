import json

# Check if Greenwood County data is corrupted
with open('workspace_files/county_results_2020_fips.json', 'r') as f:
    data = json.load(f)

greenwood = data['45047']
print("Greenwood County 2020 Presidential Results:")
print(f"  Democratic: {greenwood['dem_votes']:,} votes")
print(f"  Republican: {greenwood['rep_votes']:,} votes")
print(f"  Total: {greenwood['total_votes']:,} votes")
print(f"  Winner in data: {greenwood['winner']}")
print()
print("This shows Biden winning Greenwood County, which is historically inaccurate.")
print("Greenwood County should be strongly Republican.")
print()

# Check actual typical results for reference
print("For comparison, here's what we'd expect:")
print("  Trump should have ~65-70% in Greenwood County")
print("  Biden should have ~30-35% in Greenwood County")
print()
print("The data appears to have the vote counts swapped or corrupted.")