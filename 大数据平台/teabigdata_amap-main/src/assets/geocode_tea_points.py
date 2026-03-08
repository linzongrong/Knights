
import json
import os
import glob
from shapely.geometry import Point, shape
from shapely.prepared import prep

# Paths
POINTS_FILE = 'src/assets/tea_points.json'
GEOJSON_DIR = 'src/assets/external_geojson'

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("Loading points...")
    points_data = load_json(POINTS_FILE)
    if not points_data:
        return

    # 1. Load All Provinces Geometries once (Optimization)
    print("Loading Province geometries...")
    provinces = [] # List of (name, shapely_geom)
    prov_files = glob.glob(os.path.join(GEOJSON_DIR, 'province', '*.json'))
    
    for p_file in prov_files:
        p_name = os.path.splitext(os.path.basename(p_file))[0]
        p_data = load_json(p_file)
        if not p_data: continue
        
        # Merge all features into one polygon for the province? 
        # Usually province json has multiple features (cities), combining them makes the province shape.
        # But actually checking against the detailed city features inside province.json is accurate for City Level.
        # But for Province Level check, we can just check if it hits ANY feature in the province file.
        
        # Strategy:
        # Load features. create (city_name, polygon, province_name) tuples.
        for feature in p_data.get('features', []):
            try:
                geom = shape(feature['geometry'])
                city_name = feature['properties']['name']
                provinces.append({
                    'prov': p_name,
                    'city': city_name,
                    'geom': prep(geom), # Prepared geometry for faster checks
                    'raw_geom': geom
                })
            except Exception as e:
                pass
                
    print(f"Loaded {len(provinces)} province/city regions.")

    # Cache for lower level data to avoid re-loading files repeatedly
    # Map: CityName -> List of (CountyName, Geom)
    city_cache = {} 

    updated_count = 0
    
    for i, pt in enumerate(points_data):
        lnglat = pt.get('lnglat')
        if not lnglat or len(lnglat) < 2 or not lnglat[0]:
            continue
            
        point = Point(lnglat[0], lnglat[1])
        
        # 1. Find Province & City (from Province file features)
        matched_prov = None
        matched_city = None
        
        # current values
        curr_prov = pt.get('province')
        
        # Optimization: If we have many points, spatial index (RTree) is better. 
        # But for ~2000 points and linear scan of ~34 provinces * ~10 cities ~ 300 polygons, it's okay-ish.
        # Let's just scan.
        
        found_base = False
        for entry in provinces:
            if entry['geom'].contains(point):
                matched_prov = entry['prov']
                matched_city = entry['city']
                found_base = True
                break
        
        if found_base:
            pt['province'] = matched_prov
            pt['city'] = matched_city
            
            # 2. Find District (from City file)
            # We need to load src/assets/external_geojson/citys/{matched_city}.json
            # Note: filename might mismatch if city name differs (e.g. '市' suffix).
            # Usually strict match from previous step properties works.
            
            # Check cache
            if matched_city not in city_cache:
                city_file = os.path.join(GEOJSON_DIR, 'citys', f"{matched_city}.json")
                if not os.path.exists(city_file):
                    # Try removing strict suffix? Or checking info.json?
                    # Fallback: keep district empty
                    city_cache[matched_city] = []
                else:
                    c_data = load_json(city_file)
                    counties = []
                    if c_data:
                        for feature in c_data.get('features', []):
                            try:
                                g = shape(feature['geometry'])
                                c_name = feature['properties']['name']
                                counties.append({'name': c_name, 'geom': prep(g)})
                            except: pass
                    city_cache[matched_city] = counties
            
            # Check counties
            matched_district = ''
            for county in city_cache[matched_city]:
                if county['geom'].contains(point):
                    matched_district = county['name']
                    break
            
            pt['district'] = matched_district
            updated_count += 1
        
        else:
            # print(f"Point {i} not in any known province: {lnglat}")
            pass

        if i % 100 == 0:
            print(f"Processed {i} points...")

    print(f"Updated regions for {updated_count} points.")
    save_json(points_data, POINTS_FILE)
    print("Done.")

if __name__ == '__main__':
    main()
