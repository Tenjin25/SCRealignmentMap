def get_competitiveness_category(rep_votes, dem_votes):
    if rep_votes is None or dem_votes is None:
        return None, None, None, None
    try:
        rep_votes = int(rep_votes)
        dem_votes = int(dem_votes)
    except Exception:
        return None, None, None, None
    total = rep_votes + dem_votes
    if total == 0:
        return None, None, None, None
    rep_pct = rep_votes / total * 100
    dem_pct = dem_votes / total * 100
    margin = rep_pct - dem_pct
    abs_margin = abs(margin)
    if margin > 0:
        margin_str = f"R+{abs(margin):.1f}%"
    elif margin < 0:
        margin_str = f"D+{abs(margin):.1f}%"
    else:
        margin_str = "0.0%"
    if abs_margin <= 0.5:
        return 'Tossup', '±0.5%', '#f7f7f7', margin_str
    if margin > 0:
        # Republican lead
        if abs_margin > 40:
            return 'Annihilation', 'R+40%+', '#67000d', margin_str
        elif abs_margin > 30:
            return 'Dominant', 'R+30-40%', '#a50f15', margin_str
        elif abs_margin > 20:
            return 'Stronghold', 'R+20-30%', '#cb181d', margin_str
        elif abs_margin > 10:
            return 'Safe', 'R+10-20%', '#ef3b2c', margin_str
        elif abs_margin > 5.5:
            return 'Likely', 'R+5.5-10%', '#fb6a4a', margin_str
        elif abs_margin > 1:
            return 'Lean', 'R+1-5.5%', '#fcae91', margin_str
        else:
            return 'Tilt', 'R+0.5-1%', '#fee8c8', margin_str
    else:
        # Democratic lead
        if abs_margin > 40:
            return 'Annihilation', 'D+40%+', '#08306b', margin_str
        elif abs_margin > 30:
            return 'Dominant', 'D+30-40%', '#08519c', margin_str
        elif abs_margin > 20:
            return 'Stronghold', 'D+20-30%', '#3182bd', margin_str
        elif abs_margin > 10:
            return 'Safe', 'D+10-20%', '#6baed6', margin_str
        elif abs_margin > 5.5:
            return 'Likely', 'D+5.5-10%', '#9ecae1', margin_str
        elif abs_margin > 1:
            return 'Lean', 'D+1-5.5%', '#c6dbef', margin_str
        else:
            return 'Tilt', 'D+0.5-1%', '#e1f5fe', margin_str

# Example usage:
# cat, rng, color = get_competitiveness_category(600, 400)
# print(cat, rng, color)  # Output: Stronghold R+20-30% #cb181d
