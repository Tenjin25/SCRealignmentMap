import csv

input_file = "elstats_search_b48bcf59c9eb3184.csv"      # Change to your actual filename
output_file = "aligned_output.csv"

with open(input_file, encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
num_cols = len(header)
bad_rows = []
good_rows = [header]

for i, row in enumerate(rows[1:], start=2):
    if len(row) != num_cols:
        print(f"Row {i} has {len(row)} columns (expected {num_cols}): {row}")
        bad_rows.append((i, row))
    else:
        good_rows.append(row)

if bad_rows:
    print(f"\nFound {len(bad_rows)} problematic rows. See above for details.")
else:
    print("All rows are correctly aligned!")

# Write only the good rows to a new file
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(good_rows)

print(f"\nAligned CSV written to {output_file} (only rows with correct columns).")