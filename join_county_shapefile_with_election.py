# join_county_shapefile_with_election.py
"""
Joins the 2008 SC county shapefile (tl_2008_45_county00) with county-level election results CSV (e.g., OpenElections).
Outputs a merged GeoJSON for mapping/analysis.

Dependencies: geopandas, pandas
"""
import geopandas as gpd
import pandas as pd
import os

# Paths (update as needed)
county_shp = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\tl_2008_45_county00.shp'
election_csv = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\20061107__sc__general__county.csv'
output_geojson = 'sc_2008_county_election_merged.geojson'

# Load shapefile
counties = gpd.read_file(county_shp)

# Load election results
results = pd.read_csv(election_csv, dtype=str)

# Normalize FIPS columns for join
if 'CNTYIDFP' in counties.columns:
    counties['county_fips'] = counties['CNTYIDFP'].astype(str).str.zfill(5)
else:
    counties['county_fips'] = counties['GEOID'].astype(str).str.zfill(5)

# Try to find FIPS in results
fips_col = None
for col in results.columns:
    if 'fips' in col.lower():
        fips_col = col
        break
if not fips_col:
    # Try to build FIPS from county number
    if 'county' in results.columns:
        # This assumes county is a FIPS code or can be mapped
        results['county_fips'] = results['county'].astype(str).str.zfill(5)
        fips_col = 'county_fips'
    else:
        raise Exception('No FIPS or county code column found in election CSV.')

# Aggregate election results by county FIPS (sum votes by party, etc.)
agg_cols = [col for col in results.columns if col not in ['county_fips', fips_col, 'county', 'county_name']]
agg_dict = {col: 'first' for col in agg_cols}
agg_dict['county_fips'] = 'first'
results_agg = results.groupby('county_fips', as_index=False).agg(agg_dict)

# Merge
merged = counties.merge(results_agg, on='county_fips', how='left')

# Save
merged.to_file(output_geojson, driver='GeoJSON')
print(f'Merged county shapefile and election results saved as {output_geojson}')
