import pandas as pd
import os

# List of files to process
files = [
    'SC/Data/election_data_SC.v04.csv',
    'SC/Data/election_data_SC.v05.csv',
    'SC/Data/election_data_SC.v06.csv',
    'SC/Data/demographic_data_SC.v04.csv',
    'SC/Data/demographic_data_SC.v06.csv',
]

# County FIPS reference
fips_path = 'sc_county_fips.csv'
fips_df = pd.read_csv(fips_path, dtype=str)

for file in files:
    if not os.path.exists(file):
        print(f"File not found: {file}")
        continue
    df = pd.read_csv(file, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    if 'GEOID20' in df.columns:
        df['county_fips'] = df['GEOID20'].str[:5]
        merged = df.merge(fips_df, on='county_fips', how='left')
        out_path = file.replace('.csv', '_with_county.csv')
        merged.to_csv(out_path, index=False)
        print(f"Merged and saved: {out_path}")
    else:
        print(f"No GEOID20 column in {file}, skipping.")
