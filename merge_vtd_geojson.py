import geopandas as gpd
import pandas as pd
import glob
import os

# Paths
geojson_path = 'tl_2020_45_vtd20/tl_2020_45_vtd20.geojson'
data_dir = 'SC/Data/'
output_path = 'tl_2020_45_vtd20/vtd20_merged.geojson'

# Load GeoJSON
print('Loading GeoJSON...')
gdf = gpd.read_file(geojson_path)

# Find all CSVs in the data directory
csv_files = glob.glob(os.path.join(data_dir, '*.csv'))

# Merge each CSV that has GEOID20

for csv_file in csv_files:
    print(f'Processing {csv_file}...')
    try:
        df = pd.read_csv(csv_file, dtype=str, encoding_errors="ignore")
    except Exception as e:
        print(f'Error reading {csv_file}: {e}')
        continue
    # Remove whitespace from column names
    df.columns = df.columns.str.strip()
    print(f'Columns in {csv_file}: {list(df.columns)}')
    # Try to find the GEOID20 column (case-insensitive, strip whitespace)
    geoid_col = None
    for col in df.columns:
        if col.strip().upper() == 'GEOID20':
            geoid_col = col
            break
    if geoid_col:
        df[geoid_col] = df[geoid_col].str.strip()
        gdf = gdf.merge(df, left_on='GEOID20', right_on=geoid_col, how='left', suffixes=('', f'_{os.path.basename(csv_file).split(".")[0]}'))
    else:
        print(f'Skipping {csv_file}: no GEOID20 column (after cleaning)')

# Ensure all columns are unique by renaming duplicates
def make_unique_columns(columns):
    seen = {}
    new_cols = []
    for col in columns:
        if col not in seen:
            seen[col] = 0
            new_cols.append(col)
        else:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
    return new_cols

gdf.columns = make_unique_columns(gdf.columns)

# Save merged GeoJSON
gdf.to_file(output_path, driver='GeoJSON')
print(f'Merged GeoJSON saved to {output_path}')
