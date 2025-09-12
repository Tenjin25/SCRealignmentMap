import csv

input_file = "elstats_search_b48bcf59c9eb3184.csv"      # Change to your actual filename
output_file = "cleaned_results.csv"

# List of columns to keep (in your specified order)
columns = [
    "contest_id","election_id","election_date","election_type","primary_party",
    "question_text","question_type","office_id","office_name","office_modifier",
    "district_id","district_type","district_name","candidate_id","candidate_name",
    "retention_candidate_id","retention_candidate_name","division_id","division_type",
    "division_name","vote_channel","is_winner","candidate_party_id","candidate_party_name","votes"
]

with open(input_file, encoding="utf-8") as f_in, open(output_file, "w", newline="", encoding="utf-8") as f_out:
    reader = csv.DictReader(f_in)
    writer = csv.DictWriter(f_out, fieldnames=columns)
    writer.writeheader()
    for row in reader:
        # Only keep the specified columns, fill missing with empty string
        filtered = {col: row.get(col, "").strip() for col in columns}
        writer.writerow(filtered)

print(f"Cleaned CSV written to {output_file}")