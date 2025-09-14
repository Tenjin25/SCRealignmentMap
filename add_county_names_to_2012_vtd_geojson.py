import geopandas as gpd
import pandas as pd

# Load the 2012 VTD GeoJSON
vtd_geojson = r"VTDs/tl_2012_45_county10.geojson"
gdf = gpd.read_file(vtd_geojson)


# Load the FIPS lookup
fips_csv = r"SC/sc_county_fips.csv"
fips_df = pd.read_csv(fips_csv, dtype=str)
fips_df['fips'] = fips_df['fips'].astype(str).str.zfill(5)

# Create a mapping from FIPS to county name
fips_to_name = dict(zip(fips_df['fips'], fips_df['county']))

# Combine STATEFP10 and COUNTYFP10 to get full FIPS
# (ensure zero-padding for both fields)
gdf['county_fips'] = gdf['STATEFP10'].astype(str).str.zfill(2) + gdf['COUNTYFP10'].astype(str).str.zfill(3)
gdf['county_name'] = gdf['county_fips'].map(fips_to_name)

# Save the updated GeoJSON
output_geojson = r"VTDs/tl_2012_45_county10_with_county_names.geojson"
gdf.to_file(output_geojson, driver="GeoJSON")

print(f"Saved: {output_geojson}")
