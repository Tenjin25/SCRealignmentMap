import csv

INPUT_CSV = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\SC\Data\election_data_SC.v05.csv"
FIPS_REF_CSV = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\sc_county_fips.csv"
OUTPUT_CSV = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\SC\Data\election_data_SC.v05_with_county.csv"

# Load FIPS to county name mapping
fips_to_county = {}
with open(FIPS_REF_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fips = row['county_fips'].strip()
        county = row['county_name'].strip()
        fips_to_county[fips] = county

# Read input, assign correct county names, and write output
with open(INPUT_CSV, 'r', encoding='utf-8') as infile, open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile, skipinitialspace=True)
    fieldnames = [fn.strip() for fn in reader.fieldnames]
    print(f"CSV Header: {fieldnames}")
    if 'county' not in fieldnames:
        fieldnames.append('county')
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        # Strip keys to handle extra spaces
        row = {k.strip(): v for k, v in row.items()}
        geoid = row.get('GEOID20', '').strip()
        fips = geoid[:5] if geoid else ''
        county_val = row.get('county', '')
        if county_val is None:
            county_val = ''
        correct_county = fips_to_county.get(fips, county_val.strip())
        row['county'] = correct_county
        print(f"GEOID20: {geoid}, FIPS: {fips}, Assigned County: {correct_county}")
        if not correct_county:
            print(f"WARNING: No county found for FIPS {fips} (GEOID20: {geoid})")
        writer.writerow(row)

print(f"County names assigned and saved to {OUTPUT_CSV}")
