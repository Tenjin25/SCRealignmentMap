#!/usr/bin/env python3
"""
Clean up messy CSV election results files
Removes extra quotes, fixes column formatting, and handles malformed lines
"""

import pandas as pd
import csv
from pathlib import Path
import re

def clean_csv_file(input_file, output_file=None):
    """Clean up a messy CSV file"""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ File not found: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}"
    
    output_path = Path(output_file)
    
    print(f"🧹 Cleaning CSV file...")
    print(f"📁 Input:  {input_path}")
    print(f"📁 Output: {output_path}")
    
    try:
        # First, try to read with pandas error handling
        print(f"📊 Loading original file...")
        df = pd.read_csv(input_path, on_bad_lines='warn')
        
        print(f"✅ Loaded {len(df)} records")
        print(f"📋 Original columns: {list(df.columns)}")
        
        # Clean column names
        original_columns = list(df.columns)
        cleaned_columns = []
        
        for col in original_columns:
            # Remove extra quotes and whitespace
            cleaned_col = str(col).strip().strip('"').strip()
            # Remove multiple spaces
            cleaned_col = re.sub(r'\s+', ' ', cleaned_col)
            cleaned_columns.append(cleaned_col)
        
        df.columns = cleaned_columns
        
        print(f"📋 Cleaned columns: {list(df.columns)}")
        
        # Clean data in each column
        print(f"🧽 Cleaning data values...")
        
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                # Remove extra quotes and whitespace from string values
                df[col] = df[col].astype(str).apply(lambda x: str(x).strip().strip('"').strip() if pd.notna(x) else x)
        
        # Show sample of cleaned data
        print(f"📊 Sample cleaned data:")
        print(df.head(3))
        
        # Save cleaned file
        df.to_csv(output_path, index=False, quoting=csv.QUOTE_MINIMAL)
        
        print(f"✅ Cleaned CSV saved to: {output_path}")
        print(f"📊 Final file has {len(df)} records and {len(df.columns)} columns")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error cleaning CSV: {e}")
        return False

def clean_2012_results():
    """Prompt user for SC election results file and clean it"""
    import sys
    print("🚀 Cleaning South Carolina Election Results CSV")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Enter path to SC election results CSV: ").strip()
    
    if not input_file:
        print("❌ No input file provided.")
        return None
    
    result = clean_csv_file(input_file)
    
    if result:
        print(f"\n🎯 Success! Use the cleaned file in your scripts:")
        print(f"   results_file = Path('{result}')")
        # Show file size comparison
        input_path = Path(input_file)
        output_path = Path(result)
        if input_path.exists() and output_path.exists():
            input_size = input_path.stat().st_size
            output_size = output_path.stat().st_size
            print(f"\n📏 File size comparison:")
            print(f"   Original: {input_size:,} bytes")
            print(f"   Cleaned:  {output_size:,} bytes")
            print(f"   Change:   {((output_size - input_size) / input_size * 100):+.1f}%")
    else:
        print(f"\n❌ Failed to clean CSV file")
    return result

def verify_cleaned_file(cleaned_file):
    """Verify the cleaned file loads properly"""
    print(f"\n🔍 Verifying cleaned file...")
    try:
        df = pd.read_csv(cleaned_file)
        print(f"✅ Cleaned file loads successfully!")
        print(f"📊 Records: {len(df)}")
        print(f"📋 Columns: {list(df.columns)}")
        # Optionally, check for a contest column and print unique contests
        contest_cols = [col for col in df.columns if 'contest' in col.lower() or 'office' in col.lower()]
        if contest_cols:
            contest_col = contest_cols[0]
            unique_contests = df[contest_col].dropna().unique()
            print(f"🏛️ Found {len(unique_contests)} unique contests/offices:")
            for contest in unique_contests[:10]:
                print(f"   • {contest}")
            if len(unique_contests) > 10:
                print(f"   ...and {len(unique_contests)-10} more.")
        return True
    except Exception as e:
        print(f"❌ Error verifying cleaned file: {e}")
        return False

def main():
    """Main function"""
    cleaned_file = clean_2012_results()
    if cleaned_file:
        verify_cleaned_file(cleaned_file)
        print(f"\n🎯 Next steps:")
        print(f"   1. Use the cleaned file for your SC election data analysis.")
        print(f"   2. The cleaned file should load without errors.")
        print(f"   3. Column names are now standardized.")

if __name__ == "__main__":
    main()
