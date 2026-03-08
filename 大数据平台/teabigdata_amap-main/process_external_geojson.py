import json
import os
import shutil

EXTERNAL_DIR = 'src/assets/external_geojson'
OUTPUT_DIR = 'src/assets/geojson'

def load_info_map():
    info_path = os.path.join(EXTERNAL_DIR, 'info.json')
    if not os.path.exists(info_path):
        print("info.json not found")
        return {}
    
    with open(info_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Build name -> adcode map
    # Note: Names might be duplicated (e.g. distincts), so this simple map might be risky for counties.
    # However, for Province and City files (which are usually unique or qualified), it works.
    # For counties, we might need to be careful.
    
    # A safer approach:
    # 1. Iterate through the info.json hierarchy. (It seems flat or nested?)
    # The snippet showed "100000": {... children: [...] ...}
    # It seems to be a flat map of adcode -> info object.
    
    name_map = {}
    for adcode, info in data.items():
        name = info.get('name')
        if name:
            name_map[name] = adcode
            
    return name_map

def process():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    name_to_adcode = load_info_map()
    print(f"Loaded {len(name_to_adcode)} regions from info.json")

    # 1. Country
    src_country = os.path.join(EXTERNAL_DIR, 'china.json')
    if os.path.exists(src_country):
        shutil.copy2(src_country, os.path.join(OUTPUT_DIR, 'country.json'))
        print("Copied country.json")
    else:
        print("china.json not found!")

    # 2. Provinces
    prov_dir = os.path.join(EXTERNAL_DIR, 'province')
    if os.path.exists(prov_dir):
        for fname in os.listdir(prov_dir):
            if not fname.endswith('.json'): continue
            name = fname.replace('.json', '')
            adcode = name_to_adcode.get(name)
            
            if adcode:
                shutil.copy2(os.path.join(prov_dir, fname), os.path.join(OUTPUT_DIR, f"{adcode}.json"))
            else:
                print(f"Warning: No adcode for province file {fname}")

    # 3. Cities
    city_dir = os.path.join(EXTERNAL_DIR, 'citys') # note 'citys' typo in repo
    if os.path.exists(city_dir):
        for fname in os.listdir(city_dir):
            if not fname.endswith('.json'): continue
            name = fname.replace('.json', '')
            adcode = name_to_adcode.get(name)
            
            if adcode:
                shutil.copy2(os.path.join(city_dir, fname), os.path.join(OUTPUT_DIR, f"{adcode}.json"))
            else:
                # Some files might be named differently?
                print(f"Warning: No adcode for city file {fname}")
                
    # 4. Counties?
    # Verified: Province files contain City features. City files contain County features.
    # We just need to ensure the County files (if any exist in `county/`) are also copied if we want to zoom into them?
    # Actually, the Cascade "Drill Down" works by loading the parent's file to see children.
    # To see the "Township" level (which we don't have), we would need County maps containing Townships.
    # Since we don't have Township data, we don't strictly need detailed maps for individual Counties 
    # UNLESS the user wants to see the shape of the county in isolation or we have township data.
    # However, for completeness and standard naming, let's copy them if available, though they might be leaf nodes.
    
    county_dir = os.path.join(EXTERNAL_DIR, 'county')
    if os.path.exists(county_dir):
        for fname in os.listdir(county_dir):
            if not fname.endswith('.json'): continue
            name = fname.replace('.json', '')
            adcode = name_to_adcode.get(name)
            
            if adcode:
                shutil.copy2(os.path.join(county_dir, fname), os.path.join(OUTPUT_DIR, f"{adcode}.json"))

    # Also update index.json?
    # CustomMap uses `country.json` to populate the first level.
    # Then it loads children dynamically.
    # We don't strictly *need* an index.json if we rely on `country.json` as the source of truth for Top Level.
    # But `CustomMap.vue` in previous iteration used `provinceList`.
    # My NEW CustomMap uses `loadCountryData` fetching `country.json`.
    # So `index.json` is not strictly required anymore.
    
    print(f"Done. Processed files to {OUTPUT_DIR}")


if __name__ == "__main__":
    process()
