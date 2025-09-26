from collections import Counter

log_path = "workspace_files/aggregate_county_votes.log"
county_counter = Counter()

with open(log_path, encoding="utf-8") as f:
    for line in f:
        if line.startswith("Processing county:"):
            parts = line.split()
            county = parts[2]
            county_counter[county] += 1

print("County processing summary:")
for county, count in county_counter.most_common():
    print(f"{county}: {count} times")
