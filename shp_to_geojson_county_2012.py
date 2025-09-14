"""
shp_to_geojson_county_2012.py

Converts the 2012 county shapefile to GeoJSON for use in county-level joins.
"""
import geopandas as gpd
import os

shp_path = r"Data/tl_2012_45_vtd10/tl_2012_45_vtd10.shp"
geojson_path = r"Data/tl_2012_45_county10.geojson"

gdf = gpd.read_file(shp_path)

# If this is a VTD shapefile, we need to dissolve to county boundaries using COUNTYFP10
if 'COUNTYFP10' in gdf.columns:
    gdf['county_name'] = gdf['NAME10'].str.strip().str.upper()
    county_gdf = gdf.dissolve(by='COUNTYFP10', as_index=False)
    # Keep representative columns
    keep_cols = ['COUNTYFP10', 'county_name']
    for col in keep_cols:
        if col not in county_gdf.columns and col in gdf.columns:
            county_gdf[col] = gdf.groupby('COUNTYFP10')[col].first().values
    county_gdf.to_file(geojson_path, driver='GeoJSON')
    print(f"Saved dissolved county GeoJSON: {geojson_path}")
else:
    gdf.to_file(geojson_path, driver='GeoJSON')
    print(f"Saved county GeoJSON: {geojson_path}")
