import csv
import sys
import json
import os

# Increase CSV limit
csv.field_size_limit(sys.maxsize)

INPUT_FILE = 'src/utils/ok_geo.csv'
OUTPUT_DIR = 'src/assets/geojson'

def parse_polygon(polygon_str):
    """
    Parses a polygon string "lng lat,lng lat;..." or similar format.
    The provided samples look like "lng lat,lng lat,..." (comma separated points).
    Need to ensure it forms a valid closed Loop for GeoJSON Polygon.
    GeoJSON Polygon: [[[lng, lat], [lng, lat], ...]] (must adhere to winding order, but we'll trust input mostly)
    """
    if not polygon_str:
        return []
    
    # Split by comma to get "lng lat" pairs
    points = polygon_str.split(',')
    coordinates = []
    
    for p in points:
        parts = p.strip().split()
        if len(parts) >= 2:
            try:
                lng = float(parts[0])
                lat = float(parts[1])
                coordinates.append([lng, lat])
            except ValueError:
                continue
                
    # Ensure closed loop
    if coordinates and coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])
        
    return [coordinates] if coordinates else []

def create_feature(item, level):
    poly_coords = parse_polygon(item['polygon'])
    if not poly_coords:
        return None
        
    return {
        "type": "Feature",
        "properties": {
            "adcode": item['id'],
            "name": item['name'],
            "level": level,
            "center": [0,0] # Center calculation if needed, defaulting for now
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": poly_coords
        }
    }

def generate_geojsons():
    print(f"Reading {INPUT_FILE}...")
    
    rows_by_pid = {}
    rows_by_id = {}
    
    provinces = [] # deep 0
    cities = []    # deep 1
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row['pid']
                deep = row['deep']
                
                if deep == '0':
                    provinces.append(row)
                elif deep == '1':
                    cities.append(row)
                
                if pid not in rows_by_pid:
                    rows_by_pid[pid] = []
                rows_by_pid[pid].append(row)
                
                rows_by_id[row['id']] = row
                
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Found {len(provinces)} provinces and {len(cities)} cities. Generating files...")

    # 1. Generate country.json (contains all Provinces)
    country_features = []
    for prov in provinces:
        feat = create_feature(prov, "province")
        if feat:
            country_features.append(feat)
            
    with open(os.path.join(OUTPUT_DIR, "country.json"), 'w', encoding='utf-8') as f:
        json.dump({"type": "FeatureCollection", "features": country_features}, f, ensure_ascii=False)

    # 2. Generate Province files (contains Cities)
    for prov in provinces:
        prov_id = prov['id']
        children = rows_by_pid.get(prov_id, [])
        features = []
        for child in children:
            feat = create_feature(child, "city")
            if feat:
                features.append(feat)
                
        with open(os.path.join(OUTPUT_DIR, f"{prov_id}.json"), 'w', encoding='utf-8') as f:
            json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False)

    # 3. Generate City files (contains Counties/Districts)
    for city in cities:
        city_id = city['id']
        children = rows_by_pid.get(city_id, [])
        
        # Some cities might not have children in the csv? 
        # Only generate file if requested or valid.
        # But for 3-level logic we need them if they have children.
        if children:
            features = []
            for child in children:
                feat = create_feature(child, "district")
                if feat:
                    features.append(feat)
            
            with open(os.path.join(OUTPUT_DIR, f"{city_id}.json"), 'w', encoding='utf-8') as f:
                 json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False)
            
    print(f"Done. Generated files in {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_geojsons()
