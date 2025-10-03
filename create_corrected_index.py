import json
import copy

# Load the current index
with open('sc_results_index.json', 'r') as f:
    index = json.load(f)

# Create a copy for the corrected version
corrected_index = copy.deepcopy(index)

# Update specific entries to use corrected files
corrections_mapping = {
    'county_results_2020_fips.json': 'county_results_2020_fips_corrected.json',
    'county_results_2018_fips.json': 'county_results_2018_fips_corrected.json'
}

# Update the index to point to corrected files
for year, contests in corrected_index['county']['contests_by_year'].items():
    for contest in contests:
        if contest['file'] in corrections_mapping:
            old_file = contest['file']
            new_file = corrections_mapping[old_file]
            contest['file'] = new_file
            print(f"Updated {year} {contest['name']}: {old_file} -> {new_file}")

# Save the corrected index
with open('sc_results_index_corrected.json', 'w') as f:
    json.dump(corrected_index, f, indent=2)

print("\nCreated corrected index: sc_results_index_corrected.json")
print("This index points to data files with accurate Greenwood County results.")