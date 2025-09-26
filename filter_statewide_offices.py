import pandas as pd

# Load the office names CSV
input_csv = 'unique_office_names_by_year.csv'
df = pd.read_csv(input_csv)

# List of statewide offices to keep (case-insensitive, excluding President and US Senate)
statewide_offices = [
    'ADJUTANT GENERAL',
    'ATTORNEY GENERAL',
    'COMMISSIONER OF AGRICULTURE',
    'COMPTROLLER GENERAL',
    'GOVERNOR',
    'LIEUTENANT GOVERNOR',
    'SECRETARY OF STATE',
    'STATE SUPERINTENDENT OF EDUCATION',
    'STATE TREASURER',
]

# Exclude President and US Senate (case-insensitive)
exclude = ['PRESIDENT', 'US SENATE', 'UNITED STATES SENATE', 'U.S. SENATE']

def is_statewide(office):
    office_upper = str(office).upper()
    return office_upper in statewide_offices and not any(e in office_upper for e in exclude)

filtered = df[df['office_name'].apply(is_statewide)]
filtered.to_csv('statewide_offices_by_year.csv', index=False)
print(f"Wrote {len(filtered)} statewide offices to statewide_offices_by_year.csv")import pandas as pd

# Load the CSV of all office names by year
input_csv = 'unique_office_names_by_year.csv'
df = pd.read_csv(input_csv)

# Define keywords for statewide offices to keep (excluding President and US Senate)
statewide_keywords = [
    'ADJUTANT GENERAL',
    'ATTORNEY GENERAL',
    'COMMISSIONER OF AGRICULTURE',
    'COMPTROLLER GENERAL',
    'GOVERNOR',
    'LIEUTENANT GOVERNOR',
    'SECRETARY OF STATE',
    'STATE SUPERINTENDENT OF EDUCATION',
    'STATE TREASURER',
]

# Exclude President and US Senate
exclude_keywords = ['PRESIDENT', 'US SENATE', 'UNITED STATES SENATE', 'U.S. SENATE']

def is_statewide(office):
    office_upper = office.upper()
    return (
        any(kw in office_upper for kw in statewide_keywords)
        and not any(ex in office_upper for ex in exclude_keywords)
    )

filtered_df = df[df['office_name'].apply(is_statewide)]
filtered_df.to_csv('statewide_offices_by_year.csv', index=False)
print(f"Wrote {len(filtered_df)} statewide offices to statewide_offices_by_year.csv")
