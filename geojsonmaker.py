import geopandas as gpd

# Update the path if your files are in a different folder
shapefile_path = "tl_2020_45_county20/tl_2020_45_county20.shp"
geojson_path = "tl_2020_45_county20.geojson"

gdf = gpd.read_file(shapefile_path)
gdf.to_file(geojson_path, driver="GeoJSON")

print("Conversion complete! GeoJSON saved as", geojson_path)