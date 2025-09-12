#!/usr/bin/env python3
"""
Aggregate SC election results by county, office, candidate, and party.
Sums votes for each group and outputs a new CSV.
"""

import pandas as pd
from pathlib import Path

def aggregate_sc_election_results(input_file, output_file=None):
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ File not found: {input_file}")
        return False

    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_aggregated{input_path.suffix}"
    output_path = Path(output_file)

    print(f"📊 Loading cleaned file: {input_path}")
    df = pd.read_csv(input_path)

    # Group by county (division_name, division_id), office, candidate, and party
    group_cols = []
    for col in [
        'division_name', 'division_id', 'office_name', 'office_id',
        'candidate_name', 'candidate_id', 'candidate_party_name', 'candidate_party_id'
    ]:
        if col in df.columns:
            group_cols.append(col)
    # Ensure county columns are first
    county_cols = [col for col in ['division_name', 'division_id'] if col in group_cols]
    other_cols = [col for col in group_cols if col not in county_cols]
    group_cols = county_cols + other_cols
    if 'votes' not in df.columns:
        print("❌ 'votes' column not found!")
        return False
    print(f"🔗 Grouping by: {group_cols}")
    agg = df.groupby(group_cols, dropna=False)['votes'].sum().reset_index()
    print(f"💾 Saving aggregated results to: {output_path}")
    agg.to_csv(output_path, index=False)
    print(f"✅ Aggregation complete! {len(agg)} rows written.")
    return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Enter path to cleaned SC election results CSV: ").strip()
    aggregate_sc_election_results(input_file)
