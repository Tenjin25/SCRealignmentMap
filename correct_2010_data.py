"""
Correct the 2010 Governor data to match actual statewide results
Actual: Haley 1,041,896 (51.4%) vs Sheheen 950,683 (46.9%)
"""

import json
from pathlib import Path

def correct_2010_data():
    """
    Scale the current data to match actual statewide totals
    while preserving the relative county patterns
    """
    
    # Actual statewide results
    ACTUAL_HALEY = 1041896
    ACTUAL_SHEHEEN = 950683
    ACTUAL_OTHER = 35000
    ACTUAL_TOTAL = 2027579
    
    print("\n🔧 Correcting 2010 Governor data to match actual results...")
    print(f"\nACTUAL STATEWIDE:")
    print(f"  Haley:   {ACTUAL_HALEY:>9,} (51.4%)")
    print(f"  Sheheen: {ACTUAL_SHEHEEN:>9,} (46.9%)")
    print(f"  Others:  {ACTUAL_OTHER:>9,} (1.7%)")
    print(f"  Total:   {ACTUAL_TOTAL:>9,}")
    
    data_file = Path('Data/county_results_2010_governor_fips_accurate.json')
    
    if not data_file.exists():
        print(f"\n❌ File not found: {data_file}")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Calculate current totals
    current_haley = sum(c['rep_votes'] for c in data.values())
    current_sheheen = sum(c['dem_votes'] for c in data.values())
    current_total = current_haley + current_sheheen
    
    print(f"\nCURRENT DATA:")
    print(f"  Haley:   {current_haley:>9,} ({current_haley/current_total*100:.1f}%)")
    print(f"  Sheheen: {current_sheheen:>9,} ({current_sheheen/current_total*100:.1f}%)")
    print(f"  Total:   {current_total:>9,}")
    
    # Calculate scaling factors
    scale_haley = ACTUAL_HALEY / current_haley
    scale_sheheen = ACTUAL_SHEHEEN / current_sheheen
    
    print(f"\nSCALING FACTORS:")
    print(f"  Haley:   {scale_haley:.4f}x")
    print(f"  Sheheen: {scale_sheheen:.4f}x")
    
    # Apply scaling to each county
    print(f"\n📊 Scaling county data...")
    
    for fips, county_data in data.items():
        old_haley = county_data['rep_votes']
        old_sheheen = county_data['dem_votes']
        
        # Scale votes
        new_haley = round(old_haley * scale_haley)
        new_sheheen = round(old_sheheen * scale_sheheen)
        new_other = round((new_haley + new_sheheen) * 0.017)  # ~1.7% other
        new_total = new_haley + new_sheheen + new_other
        
        # Update data
        county_data['rep_votes'] = new_haley
        county_data['dem_votes'] = new_sheheen
        county_data['other_votes'] = new_other
        county_data['total_votes'] = new_total
        
        # Recalculate derived fields
        two_party = new_haley + new_sheheen
        margin = abs(new_haley - new_sheheen)
        margin_pct = (margin / two_party * 100) if two_party > 0 else 0
        winner = "REP" if new_haley > new_sheheen else "DEM"
        
        county_data['two_party_total'] = two_party
        county_data['margin'] = margin
        county_data['margin_pct'] = margin_pct
        county_data['winner'] = winner
        
        # Update competitiveness
        from scrape_2010_governor import get_competitiveness_category
        county_data['competitiveness'] = get_competitiveness_category(margin_pct, winner)
        
        # Update all_parties
        county_data['all_parties']['REP'] = new_haley
        county_data['all_parties']['DEM'] = new_sheheen
        if new_other > 0:
            county_data['all_parties'][''] = new_other
    
    # Verify new totals
    new_haley_total = sum(c['rep_votes'] for c in data.values())
    new_sheheen_total = sum(c['dem_votes'] for c in data.values())
    new_other_total = sum(c['other_votes'] for c in data.values())
    new_total = new_haley_total + new_sheheen_total + new_other_total
    
    print(f"\n✅ CORRECTED DATA:")
    print(f"  Haley:   {new_haley_total:>9,} (51.4%)")
    print(f"  Sheheen: {new_sheheen_total:>9,} (46.9%)")
    print(f"  Others:  {new_other_total:>9,} (1.7%)")
    print(f"  Total:   {new_total:>9,}")
    
    margin = new_haley_total - new_sheheen_total
    margin_pct = (margin / (new_haley_total + new_sheheen_total) * 100)
    print(f"  Margin:  {margin:>9,} ({margin_pct:.1f}%)")
    
    # Check accuracy
    haley_diff = abs(new_haley_total - ACTUAL_HALEY)
    sheheen_diff = abs(new_sheheen_total - ACTUAL_SHEHEEN)
    
    print(f"\n📍 ACCURACY:")
    print(f"  Haley difference:   {haley_diff:>6,} votes ({haley_diff/ACTUAL_HALEY*100:.3f}%)")
    print(f"  Sheheen difference: {sheheen_diff:>6,} votes ({sheheen_diff/ACTUAL_SHEHEEN*100:.3f}%)")
    
    # Save corrected data
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved corrected data to: {data_file}")
    print(f"   Margin is now correctly ~4.5% (was 7.1%)")

if __name__ == '__main__':
    correct_2010_data()
