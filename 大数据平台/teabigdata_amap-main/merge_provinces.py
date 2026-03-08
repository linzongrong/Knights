import json
import os
import glob

# Paths
INPUT_DIR = 'src/assets/external_geojson/province'
OUTPUT_FILE = 'src/assets/geojson/country.json'

def merge_provinces():
    if not os.path.exists(INPUT_DIR):
        print(f"Error: {INPUT_DIR} does not exist.")
        return

    features = []
    
    # Iterate over all JSON files in the province directory
    files = glob.glob(os.path.join(INPUT_DIR, '*.json'))
    print(f"Found {len(files)} province files.")

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Each file is a FeatureCollection. We take its features.
                # Usually there is ONE feature (the province) or multiple (islands etc).
                # We want to add them to our master list.
                if 'features' in data:
                    features.extend(data['features'])
                elif 'type' in data and data['type'] == 'Feature':
                    features.append(data)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # Create the master FeatureCollection
    master_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    # Write to output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_collection, f, ensure_ascii=False)
    
    print(f"Successfully created {OUTPUT_FILE} with {len(features)} features.")

if __name__ == "__main__":
    merge_provinces()
