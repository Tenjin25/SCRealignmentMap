import geopandas as gpd
import pandas as pd

# Paths
county_geojson = 'tl_2020_45_county20.geojson'
elstats_csv = 'elstats_search_b48bcf59c9eb3184_cleaned_aggregated.csv'
output_geojson = 'tl_2020_45_county20_merged.geojson'

# Load county GeoJSON
print('Loading county GeoJSON...')
gdf = gpd.read_file(county_geojson)

# Load election stats CSV
print('Loading election stats CSV...')
df = pd.read_csv(elstats_csv, dtype=str)

# Clean whitespace from column names
cols = [c.strip() for c in df.columns]
df.columns = cols


# --- Build wide-format election results table matching v04.csv ---
# Define the columns to match the sample
columns = [
	'GEOID20', 'Name',
	'E_16_PRES_Total', 'E_16_PRES_Dem', 'E_16_PRES_Rep',
	'E_16_SEN_Total', 'E_16_SEN_Dem', 'E_16_SEN_Rep',
	'E_18_GOV_Total', 'E_18_GOV_Dem', 'E_18_GOV_Rep',
	'E_18_AG_Total', 'E_18_AG_Dem', 'E_18_AG_Rep',
	'E_16-20_COMP_Total', 'E_16-20_COMP_Dem', 'E_16-20_COMP_Rep',
	'E_20_PRES_Total', 'E_20_PRES_Dem', 'E_20_PRES_Rep',
	'E_20_SEN_Total', 'E_20_SEN_Dem', 'E_20_SEN_Rep'
]

# Helper: get county/precinct name and GEOID from geojson
geo_lookup = gdf[['GEOID20', 'NAME20']].set_index('NAME20').to_dict('index')

# Prepare a results dict for each geo unit
results = {}
for name, row in gdf.iterrows():
	results[row['NAME20']] = {
		'GEOID20': row['GEOID20'],
		'Name': row['NAME20']
	}
	# Initialize all columns to 0
	for col in columns[2:]:
		results[row['NAME20']][col] = 0

# Map from office/year to column names
office_map = {
	('2016', 'President'): ('E_16_PRES_Dem', 'E_16_PRES_Rep', 'E_16_PRES_Total'),
	('2016', 'Senate'): ('E_16_SEN_Dem', 'E_16_SEN_Rep', 'E_16_SEN_Total'),
	('2018', 'Governor'): ('E_18_GOV_Dem', 'E_18_GOV_Rep', 'E_18_GOV_Total'),
	('2018', 'Attorney General'): ('E_18_AG_Dem', 'E_18_AG_Rep', 'E_18_AG_Total'),
	('2020', 'President'): ('E_20_PRES_Dem', 'E_20_PRES_Rep', 'E_20_PRES_Total'),
	('2020', 'Senate'): ('E_20_SEN_Dem', 'E_20_SEN_Rep', 'E_20_SEN_Total'),
}

# Fill in results from the CSV
for _, row in df.iterrows():
	year = str(row['election_date'])[:4]
	office = row['office_name']
	county = row['division_name']
	party = row['candidate_party_name']
	votes = int(row['votes']) if row['votes'].isdigit() else 0
	# Map office name to simplified
	if 'President' in office:
		office_key = 'President'
	elif 'Senate' in office:
		office_key = 'Senate'
	elif 'Governor' in office:
		office_key = 'Governor'
	elif 'Attorney General' in office:
		office_key = 'Attorney General'
	else:
		continue
	key = (year, office_key)
	if key not in office_map:
		continue
	dem_col, rep_col, total_col = office_map[key]
	if county in results:
		if party == 'Democratic':
			results[county][dem_col] += votes
		elif party == 'Republican':
			results[county][rep_col] += votes
		results[county][total_col] += votes

# Optionally, compute composite columns (e.g., E_16-20_COMP_*)
for county in results:
	# Composite: sum of all totals/dem/rep for 2016-2020
	results[county]['E_16-20_COMP_Total'] = (
		results[county]['E_16_PRES_Total'] + results[county]['E_16_SEN_Total'] +
		results[county]['E_18_GOV_Total'] + results[county]['E_18_AG_Total'] +
		results[county]['E_20_PRES_Total'] + results[county]['E_20_SEN_Total']
	)
	results[county]['E_16-20_COMP_Dem'] = (
		results[county]['E_16_PRES_Dem'] + results[county]['E_16_SEN_Dem'] +
		results[county]['E_18_GOV_Dem'] + results[county]['E_18_AG_Dem'] +
		results[county]['E_20_PRES_Dem'] + results[county]['E_20_SEN_Dem']
	)
	results[county]['E_16-20_COMP_Rep'] = (
		results[county]['E_16_PRES_Rep'] + results[county]['E_16_SEN_Rep'] +
		results[county]['E_18_GOV_Rep'] + results[county]['E_18_AG_Rep'] +
		results[county]['E_20_PRES_Rep'] + results[county]['E_20_SEN_Rep']
	)

# Build DataFrame and save as CSV
out_df = pd.DataFrame(list(results.values()))
out_df = out_df[columns]  # Ensure column order
out_df.to_csv('election_data_SC.v07.csv', index=False)
print('CSV exported as election_data_SC.v07.csv')

# Merge with county GeoJSON on county name (as before)
agg = df[(df['election_date'].str.startswith('2024')) & (df['office_name'].str.contains('President'))]
agg = agg.groupby(['division_name','candidate_party_name'])['votes'].sum().unstack(fill_value=0).reset_index()
merged = gdf.merge(agg, left_on='NAME20', right_on='division_name', how='left')
merged.to_file(output_geojson, driver='GeoJSON')
print(f'Merged county GeoJSON saved to {output_geojson}')
