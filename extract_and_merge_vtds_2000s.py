# extract_and_merge_vtds_2000s.py
"""
Recursively finds and extracts all VTD ZIP files in a directory tree, then merges all resulting shapefiles into a single GeoJSON and Shapefile.

- Place all ZIPs (e.g., tl_2008_45001_vtd00.zip) anywhere under the root directory (including subfolders)
- Script will extract each ZIP into its own subfolder (if not already extracted)
- Then merges all .shp files matching tl_2008_*_vtd00.shp in the tree

Dependencies: geopandas, pandas
"""
import geopandas as gpd
import pandas as pd
import glob
import os
import zipfile

# Set this to your VTDs root directory
vtds_root = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data\VTDs'

# 1. Recursively find and extract all ZIPs
zip_files = glob.glob(os.path.join(vtds_root, '**', 'tl_2008_45*_vtd00.zip'), recursive=True)
print(f'Found {len(zip_files)} ZIP files.')

for zip_path in zip_files:
    extract_dir = os.path.splitext(zip_path)[0]
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f'Extracted {zip_path} to {extract_dir}')
    else:
        print(f'Skipping extraction (already exists): {extract_dir}')

# 2. Recursively find all shapefiles and merge
shapefiles = glob.glob(os.path.join(vtds_root, '**', 'tl_2008_*_vtd00.shp'), recursive=True)
print(f'Found {len(shapefiles)} shapefiles to merge.')

if not shapefiles:
    print('No shapefiles found. Check your extraction and directory structure.')
    exit(1)

gdfs = [gpd.read_file(shp) for shp in shapefiles]
all_vtds = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)

# Save merged output
all_vtds.to_file('sc_2000s_vtds_merged.shp')
all_vtds.to_file('sc_2000s_vtds_merged.geojson', driver='GeoJSON')
print('Merged VTDs saved as sc_2000s_vtds_merged.shp and sc_2000s_vtds_merged.geojson')
