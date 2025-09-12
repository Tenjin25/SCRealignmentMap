import pandas as pd

# Input and output file paths
input_file = "elstats_search_b48bcf59c9eb3184_cleaned_aggregated_county_agg.csv"
output_file = "elstats_search_b48bcf59c9eb3184_county_party_margins.csv"

# Read the data
# Strip whitespace from headers and relevant columns
with open(input_file, 'r', encoding='utf-8') as f:
    header = f.readline().strip().split(',')
    header = [h.strip() for h in header]
    df = pd.read_csv(f, names=header)
    df.columns = [c.strip() for c in df.columns]


# Remove rows that are not actual candidate results (e.g., Total Ballots Cast, Overvotes/Undervotes, etc.)
exclude_mask = df['candidate_name'].str.contains('Total|Overvotes|Undervotes', case=False, na=False)
df_candidates = df[~exclude_mask].copy()

# Convert votes to numeric, coerce errors to NaN then fill with 0
df_candidates['votes'] = pd.to_numeric(df_candidates['votes'], errors='coerce').fillna(0).astype(int)

# Group by county, office, and party, sum votes
party_votes = df_candidates.groupby([
    'division_name', 'office_name', 'candidate_party_name'
], as_index=False)['votes'].sum()

# For each county/office, find the top two parties and their vote totals
results = []
for (county, office), group in party_votes.groupby(['division_name', 'office_name']):
    group_sorted = group.sort_values('votes', ascending=False)
    if len(group_sorted) == 0:
        continue
    winner = group_sorted.iloc[0]
    runner_up = group_sorted.iloc[1] if len(group_sorted) > 1 else None
    margin = winner['votes'] - (runner_up['votes'] if runner_up is not None else 0)
    results.append({
        'county': county.strip(),
        'office': office.strip(),
        'winning_party': winner['candidate_party_name'].strip(),
        'winning_votes': winner['votes'],
        'runner_up_party': runner_up['candidate_party_name'].strip() if runner_up is not None else '',
        'runner_up_votes': runner_up['votes'] if runner_up is not None else 0,
        'margin': margin
    })

# Output to CSV
results_df = pd.DataFrame(results)
results_df.to_csv(output_file, index=False)

print(f"Output written to {output_file}")
