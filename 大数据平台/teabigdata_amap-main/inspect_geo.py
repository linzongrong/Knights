import csv
import sys

csv.field_size_limit(sys.maxsize)

with open('src/utils/ok_geo.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    print("Headers:", reader.fieldnames)
    
    counts = {}
    samples = []
    
    for i, row in enumerate(reader):
        d = row['deep']
        counts[d] = counts.get(d, 0) + 1
        if d not in [s['deep'] for s in samples]:
            samples.append(row)
        
        if i > 1000 and len(samples) > 3: # Stop early if we have enough info
            break
            
    print("Counts by deep:", counts)
    for s in samples:
        print(f"Deep: {s['deep']}, Name: {s['name']}, ID: {s['id']}, PID: {s['pid']}")
        print(f"Polygon sample (first 100 chars): {s['polygon'][:100]}")
