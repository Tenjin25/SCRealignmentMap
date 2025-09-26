# tl_2012_45_vtd10_to_geojson.py
"""
Converts the 2012 statewide VTD shapefile to GeoJSON for mapping/analysis.

Dependencies: geopandas
"""
import geopandas as gpd
import os

# Path to the 2012 VTD shapefile
shp_path = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\VTDs\tl_2012_45_vtd10'
geojson_path = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\VTDs\tl_2012_45_vtd10.geojson'

gdf = gpd.read_file(shp_path)
# Select VTD-relevant columns if present
vtd_cols = ['COUNTYFP10', 'VTDIDFP10', 'NAME10', 'geometry']
missing = [col for col in vtd_cols if col not in gdf.columns]
if missing:
    print(f"Columns {missing} not found in {shp_path}. All columns will be included.")
else:
    gdf = gdf[vtd_cols]
gdf.to_file(geojson_path, driver='GeoJSON')
print(f"GeoJSON saved to {geojson_path}")
