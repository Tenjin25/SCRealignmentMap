# South Carolina Political Realignment Map

An interactive visualization of South Carolina's electoral evolution from 2006-2024, featuring comprehensive county-level results for presidential, gubernatorial, U.S. Senate, and statewide constitutional office elections.

## 🗺️ Overview

This project provides an in-depth look at South Carolina's political landscape through interactive maps that display county-level voting patterns, margins, and competitiveness across nearly two decades of elections. The map uses a sophisticated 15-category competitiveness scale to visualize electoral dynamics from landslide victories to razor-thin margins.

**Live Demo**: [View the interactive map](https://tenjin25.github.io/SCRealignmentMap/)

## ✨ Features

### Interactive Map Visualization
- **County-level color coding** based on a 15-tier competitiveness scale
- **Dynamic contest selection** organized by office type
- **Detailed tooltips** showing county results, margins, and vote totals
- **Responsive design** optimized for desktop and mobile viewing
- **Smooth transitions** between different elections

### Comprehensive Election Coverage

**Presidential Elections** (5 cycles)
- 2008, 2012, 2016, 2020, 2024

**U.S. Senate Elections** (5 cycles)
- 2008, 2014, 2016, 2020, 2022

**Gubernatorial Elections** (5 cycles)
- 2006, 2010, 2014, 2018, 2022
- Includes separately-elected Lieutenant Governor races (2006, 2010, 2014)

**Statewide Constitutional Officers** (6 offices × multiple cycles)
- Attorney General
- State Superintendent of Education  
- Secretary of State
- State Treasurer
- Comptroller General
- Commissioner of Agriculture
- Adjutant General (2006, 2014 only)

### Advanced Competitiveness Scale

Results are categorized into 15 precision tiers:
- **Republican**: Annihilation (+40%+), Dominant (+30-40%), Stronghold (+20-30%), Safe (+15-20%), Likely (+10-15%), Lean (+5-10%), Tilt (+2.5-5%)
- **Tossup**: ±2.5%
- **Democratic**: Tilt (+2.5-5%), Lean (+5-10%), Likely (+10-15%), Safe (+15-20%), Stronghold (+20-30%), Dominant (+30-40%), Annihilation (+40%+)

## 📊 Data Sources

All election data is sourced from official South Carolina state records:

- **2006-2022 Elections**: South Carolina State Election Commission (ENR system)
- **2024 Election**: Official precinct-level results
- **Geographic Data**: U.S. Census Bureau TIGER/Line shapefiles (2020)

## 🛠️ Technical Architecture

### Data Pipeline

The project includes robust Python scripts for data extraction and processing:

1. **ENR Scrapers** (`extract_2010_all.py`, etc.)
   - Automated extraction from SC Election Commission ENR JSON API
   - County-level aggregation across all 46 SC counties
   - Multi-office batch processing

2. **Data Structuring** (`fix_json_structure.py`)
   - Adds competitiveness scale metadata
   - Calculates margins and competitive categories
   - Adds party labels and candidate designations
   - Normalizes office names across years

3. **Quality Assurance**
   - Automated vote total validation
   - Cross-referencing with official sources
   - FIPS code accuracy verification

### Web Application

- **Frontend**: Vanilla JavaScript with Mapbox GL JS
- **Styling**: Custom CSS with responsive design
- **Data Format**: Structured JSON with competitiveness metadata
- **Performance**: Optimized for fast loading and smooth interactions

## 📁 Project Structure

```
SCRealignments/
├── index.html                 # Main map interface
├── Data/                      # Election result JSON files
│   ├── county_results_2024_president_fips_accurate.json
│   ├── county_results_2022_*.json
│   └── ... (50+ contest files)
├── workspace_files/
│   └── enr_scraped/          # Raw ENR data backups
├── extract_2010_all.py       # ENR scraper for 2010
├── fix_json_structure.py     # JSON processor and validator
└── README.md                 # This file
```

## 🚀 Getting Started

### Viewing the Map

1. **Online**: Visit the [live demo](https://tenjin25.github.io/SCRealignmentMap/)
2. **Local**: Clone the repository and open `index.html` in your browser

```bash
git clone https://github.com/Tenjin25/SCRealignmentMap.git
cd SCRealignmentMap
# Open index.html in your browser
```

### Working with the Data

All contest data is available in the `Data/` directory as structured JSON files. Each file contains:

```json
{
  "competitiveness_scale": {
    "Republican": [...],
    "Tossup": [...],
    "Democratic": [...]
  },
  "county_fips_code": {
    "county": "Charleston",
    "contest": "President",
    "year": 2024,
    "dem_candidate": "Kamala Harris (D)",
    "rep_candidate": "Donald Trump (R)",
    "dem_votes": 123456,
    "rep_votes": 98765,
    "margin_pct": 12.34,
    "winner": "DEM",
    "competitiveness": {
      "category": "Likely Democratic",
      "party": "Democratic",
      "color": "#4575b4"
    }
  }
}
```

### Adding New Elections

1. Extract data using the ENR scraper or manual CSV processing
2. Run `fix_json_structure.py` to add competitiveness metadata
3. Add entries to `index.html` in the `elections` and `contestMetadata` objects
4. Test the new contest in the dropdown

## 📈 Data Quality

- ✅ All 46 SC counties covered for every contest
- ✅ Vote totals validated against official sources
- ✅ FIPS codes verified for accurate geographic mapping
- ✅ Party labels and candidate names standardized
- ✅ Only competitive races included (both parties >5% statewide)

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- Adding precinct-level visualization
- Expanding to earlier election years
- Adding demographic overlays
- Implementing comparison tools between years
- Mobile app development

Please open an issue to discuss major changes before submitting a pull request.

## 📝 License

MIT License - see LICENSE file for details

Data is sourced from public government records and is in the public domain.

## 🙏 Acknowledgments

- **South Carolina State Election Commission** for comprehensive ENR data
- **Mapbox** for the mapping platform
- **U.S. Census Bureau** for geographic shapefiles
- **OpenElections Project** for data standards inspiration

## 📧 Contact

For questions, suggestions, or data requests:
- Open an issue on GitHub
- Visit the repository: [github.com/Tenjin25/SCRealignmentMap](https://github.com/Tenjin25/SCRealignmentMap)

---

*Last updated: November 2025*
