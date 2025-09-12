import pandas as pd

# Input and output file paths
input_file = "elstats_search_b48bcf59c9eb3184.xls"
output_file = "elstats_search_b48bcf59c9eb3184_cleaned.csv"

# Read the Excel file (first sheet by default), explicitly using xlrd engine for .xls
df = pd.read_excel(input_file, engine='xlrd')

# Strip whitespace from headers and all string columns
df.columns = [col.strip() for col in df.columns]
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].astype(str).str.strip().str.replace('"', '')

# Drop completely empty rows and columns
df = df.dropna(how='all').dropna(axis=1, how='all')

# Save to CSV
# Use UTF-8 encoding and do not write row numbers
# Use quoting=csv.QUOTE_MINIMAL for clean output
df.to_csv(output_file, index=False, encoding='utf-8')

print(f"Cleaned CSV written to {output_file}")
