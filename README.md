# South Carolina Political Realignment Map (2008–2024)

This project visualizes South Carolina's county-level and precinct-level election results from 2008 to 2024, with a focus on the 2024 presidential election. It includes a robust data pipeline, interactive Mapbox GL JS web map, and automated cross-referencing with official results.

## Features
- Interactive map of SC elections (2008–2024)
- County-level and precinct-level results
- Sidebar with detailed county data, trends, and competitiveness
- Data pipeline in Python for cleaning, aggregating, and structuring results
- Automated script to cross-check and correct 2024 results with official Wikipedia data
- All data and code versioned and published on GitHub

## Data Sources
- `sc_election_results_v06_structured_corrected.json`: Official, cross-checked 2024 results (used by the map)
- `sc_election_results_v06_structured.json`: Original structured results
- `cross_reference_2024_results.py`: Script to automate cross-checking and correction
- Source CSVs and shapefiles (see `/SC/Data/` and project history)

## Usage
1. **View the Map**: Open `index.html` in your browser. The map loads the corrected 2024 results by default.
2. **Update Data**: Run `cross_reference_2024_results.py` to check/correct your results against Wikipedia.
3. **Customize**: Edit the Python scripts or web UI as needed for new years, contests, or data sources.

## How the Cross-Check Works
- The script loads your 2024 results and compares them to the official Wikipedia county table.
- Any discrepancies in vote counts or percentages are corrected.
- A summary of changes is printed, and a new JSON file is saved for the map.

## Contributing
Pull requests and issues are welcome! Please cite your data sources and describe any changes clearly.

## License
MIT License. Data is public domain or as cited in the source files.

## Credits
- Data: South Carolina Election Commission, Wikipedia, U.S. Census
- Map: Mapbox GL JS
- Code: Tenjin25 and contributors

---
For questions or suggestions, open an issue or contact the maintainer via GitHub.
