import csv
import json
import os

import sys

# Increase CSV limit
csv.field_size_limit(sys.maxsize)

INPUT_FILE = 'src/utils/ok_geo.csv'
OUTPUT_FILE = 'src/assets/geojson/index.json'

def generate_index():
    provinces = []
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['deep'] == '0':
                    provinces.append({
                        "id": row['id'],
                        "name": row['name']
                    })
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return

    # Sort by ID
    provinces.sort(key=lambda x: int(x['id']))
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(provinces, f, ensure_ascii=False, indent=2)
        
    print(f"Generated index with {len(provinces)} provinces.")

if __name__ == "__main__":
    generate_index()
