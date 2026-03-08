
import json
from shapely.geometry import Point, shape
from shapely.ops import unary_union
from shapely.prepared import prep
import os

POINTS_FILE = 'src/assets/tea_points.json'
BASIN_DIR = 'src/assets/riverbasin'

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def get_merged_geom(geojson_path):
    data = load_json(geojson_path)
    if not data: return None
    
    geoms = []
    for feature in data.get('features', []):
        try:
            geoms.append(shape(feature['geometry']))
        except: pass
        
    if not geoms: return None
    return unary_union(geoms) # Handle multi-polygon or multiple features

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("Loading geometries...")
    # Load Real Geometries
    lancang = get_merged_geom(os.path.join(BASIN_DIR, 'lcjly.json'))
    gaoligong = get_merged_geom(os.path.join(BASIN_DIR, 'glgs.json'))
    ailao = get_merged_geom(os.path.join(BASIN_DIR, 'als.json'))
    
    prep_lancang = prep(lancang) if lancang else None
    prep_gaoligong = prep(gaoligong) if gaoligong else None
    prep_ailao = prep(ailao) if ailao else None

    print("Loading points...")
    data = load_json(POINTS_FILE)
    
    updated_basin = 0
    updated_mountain = 0
    
    for pt in data:
        lnglat = pt.get('lnglat')
        if not lnglat or len(lnglat) < 2 or not lnglat[0]:
            continue
            
        point = Point(lnglat[0], lnglat[1])
        
        # Default
        basin_val = ''
        
        # Check Lancang (Broadest)
        if prep_lancang and prep_lancang.contains(point):
            basin_val = '澜沧江流域'
            
        # Check Gaoligong (Override if inside)
        if prep_gaoligong and prep_gaoligong.contains(point):
            basin_val = '高黎贡山山脉'
            
        # Check Ailao (Override if inside)
        if prep_ailao and prep_ailao.contains(point):
            basin_val = '哀牢山流域'
            
        pt['riverBasin'] = basin_val
        
        # Count stats
        if basin_val == '澜沧江流域': updated_basin += 1
        elif basin_val: updated_mountain += 1
        
        # Remove mountainRange field as requested
        if 'mountainRange' in pt:
            del pt['mountainRange']
            
    print(f"Updates: {updated_basin} in Lancang. Removed mountainRange field.")
    save_json(data, POINTS_FILE)
    print("Done.")

if __name__ == '__main__':
    main()
