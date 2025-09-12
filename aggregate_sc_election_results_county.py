#!/usr/bin/env python3
"""
Aggregate SC election results by county, office, candidate, and party,
summing across all vote channels and only using rows where division_type == 'County'.
"""

import pandas as pd
from pathlib import Path

def aggregate_by_county(input_file, output_file=None):
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ File not found: {input_file}")
        return False

    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_county_agg{input_path.suffix}"
    output_path = Path(output_file)

    print(f"📊 Loading file: {input_path}")
    df = pd.read_csv(input_path)
    # Strip whitespace from all column headers
    df.columns = [col.strip() for col in df.columns]

    # Filter to only county-level rows
    if 'division_type' not in df.columns:
        print("❌ 'division_type' column not found after stripping headers!")
        print(f"Available columns: {list(df.columns)}")
        return False
    df_county = df[df['division_type'].str.strip().str.lower() == 'county']
    print(f"🔎 Filtered to {len(df_county)} county-level rows.")

    group_cols = [
        'division_name', 'division_id', 'office_name', 'office_id',
        'candidate_name', 'candidate_id', 'candidate_party_name', 'candidate_party_id'
    ]
    if 'votes' not in df_county.columns:
        print("❌ 'votes' column not found!")
        return False

    print(f"🔗 Grouping by: {group_cols}")
    agg = df_county.groupby(group_cols, dropna=False)['votes'].sum().reset_index()

    print(f"💾 Saving county-level aggregated results to: {output_path}")
    agg.to_csv(output_path, index=False)
    print(f"✅ County-level aggregation complete! {len(agg)} rows written.")
    return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Enter path to aggregated SC election results CSV: ").strip()
    aggregate_by_county(input_file)
