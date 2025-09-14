# shp_to_geojson.py
"""
Converts a shapefile to GeoJSON for inspection or mapping.

Usage: Set the input and output paths below, then run the script.

Dependencies: geopandas
"""
import geopandas as gpd

# Path to your shapefile
shp_path = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\tl_2008_45_county00\tl_2008_45_county00.shp'
geojson_path = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\tl_2008_45_county00.geojson'

gdf = gpd.read_file(shp_path)
gdf.to_file(geojson_path, driver='GeoJSON')
print(f"GeoJSON saved to {geojson_path}")
