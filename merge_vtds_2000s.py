# merge_vtds_2000s.py
"""
Merges all South Carolina county-level VTD shapefiles from the 2000s (e.g., 2008 TIGER/Line) into a single statewide GeoJSON or Shapefile.

- Place all extracted county VTD shapefiles in a directory (one subfolder per county, each containing a .shp file)
- Script will find all `tl_2008_*_vtd00.shp` files and merge them
- Output: `sc_2000s_vtds_merged.geojson` and `sc_2000s_vtds_merged.shp`

Dependencies: geopandas, pandas
"""
import geopandas as gpd
import pandas as pd
import glob
import os


# Path to the folder with all extracted county VTD shapefiles
shapefile_dir = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\VTDs'
shapefiles = glob.glob(os.path.join(shapefile_dir, '**', 'tl_2008_*_vtd00.shp'), recursive=True)

if not shapefiles:
    print('No VTD shapefiles found. Check your directory and file pattern.')
    exit(1)

print(f'Found {len(shapefiles)} county VTD shapefiles.')

gdfs = [gpd.read_file(shp) for shp in shapefiles]
all_vtds = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)

# Save merged output
all_vtds.to_file('sc_2000s_vtds_merged.shp')
all_vtds.to_file('sc_2000s_vtds_merged.geojson', driver='GeoJSON')
print('Merged VTDs saved as sc_2000s_vtds_merged.shp and sc_2000s_vtds_merged.geojson')
