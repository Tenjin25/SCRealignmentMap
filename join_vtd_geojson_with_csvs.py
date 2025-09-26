# join_vtd_geojson_with_csvs.py
"""
Joins election CSVs in the Data folder with VTD GeoJSONs for mapping and analysis.

- For each CSV in the Data folder, attempts to join with the specified VTD GeoJSONs (2008, 2012, 2020).
- Outputs a new GeoJSON for each year with election results merged into the VTD polygons.

Dependencies: geopandas, pandas
"""
import geopandas as gpd
import pandas as pd
import os

data_dir = r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\Data'
vtd_geojsons = {
    '2008': r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\VTDs\tl_2008_45_vtd00.geojson',
    '2012': r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\VTDs\tl_2012_45_vtd10.geojson',
    '2020': r'C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\VTDs\tl_2020_45_vtd20.geojson',
}

# You may need to adjust these column names to match your CSVs and GeoJSONs
vtd_id_columns = {
    '2008': 'VTDIDFP00',
    '2012': 'VTDIDFP10',
    '2020': 'VTDIDFP20',
}

csv_files = [f for f in os.listdir(data_dir) if f.lower().endswith('.csv')]
for year, geojson_path in vtd_geojsons.items():
    print(f'Processing year {year}...')
    vtd_gdf = gpd.read_file(geojson_path)
    vtd_id_col = vtd_id_columns[year]
    for csv_file in csv_files:
        csv_path = os.path.join(data_dir, csv_file)
        print(f'  Joining {csv_file} with {os.path.basename(geojson_path)}...')
        df = pd.read_csv(csv_path)
        # Try to find the VTD ID column in the CSV
        csv_vtd_col = None
        for col in df.columns:
            if col.upper() == vtd_id_col.upper():
                csv_vtd_col = col
                break
        if not csv_vtd_col:
            print(f'    VTD ID column {vtd_id_col} not found in {csv_file}. Skipping.')
            continue
        # Merge election results into VTD polygons
        merged = vtd_gdf.merge(df, left_on=vtd_id_col, right_on=csv_vtd_col, how='left')
        out_path = os.path.join(data_dir, f'{year}_vtds_with_{os.path.splitext(csv_file)[0]}.geojson')
        merged.to_file(out_path, driver='GeoJSON')
        print(f'    Output saved to {out_path}')
print('Done.')
