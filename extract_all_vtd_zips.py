# extract_all_vtd_zips.py
"""
Extracts all county VTD ZIP files for South Carolina from a directory into subfolders (one per county).

- Place all `tl_2008_45*_vtd00.zip` files in a directory (e.g., 'vtd_zips/')
- Script will extract each ZIP into its own subfolder (named after the ZIP file)
- After extraction, you can run merge_vtds_2000s.py to merge all shapefiles

Dependencies: Python standard library (zipfile, os)
"""
import zipfile
import os
import glob

zip_dir = r'c:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\vtd_zips'  # <-- Set to your actual ZIP files directory
extract_dir = r'c:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\SCRealignments\extracted_vtds'  # <-- Set to your desired extraction directory

os.makedirs(extract_dir, exist_ok=True)


# Debug: print all files found in the directory tree
print('Files found in directory:')
for root, dirs, files in os.walk(zip_dir):
    for file in files:
        print(os.path.join(root, file))

zip_files = glob.glob(os.path.join(zip_dir, '**', 'tl_2008_45*_vtd00.zip'), recursive=True)

if not zip_files:
    print('No VTD ZIP files found. Check your directory and file pattern.')
    exit(1)

print(f'Found {len(zip_files)} county VTD ZIP files.')

for zip_path in zip_files:
    county_name = os.path.splitext(os.path.basename(zip_path))[0]
    county_extract_path = os.path.join(extract_dir, county_name)
    os.makedirs(county_extract_path, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(county_extract_path)
    print(f'Extracted {zip_path} to {county_extract_path}')

print('All VTD ZIPs extracted.')
