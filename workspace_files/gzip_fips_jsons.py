import os
import gzip

# Directory containing FIPS-keyed JSON files
results_dir = 'workspace_files'

for fname in os.listdir(results_dir):
    if fname.endswith('_fips.json'):
        json_path = os.path.join(results_dir, fname)
        gz_path = json_path + '.gz'
        with open(json_path, 'rb') as f_in, gzip.open(gz_path, 'wb') as f_out:
            f_out.writelines(f_in)
        print(f'Compressed {json_path} -> {gz_path}')
