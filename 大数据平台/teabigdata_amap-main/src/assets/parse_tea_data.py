
import pandas as pd
import json
import sys

# Install dependencies if missing: pip install pandas xlrd

excel_path = 'src/assets/attmanager_tea_tree.xls'
json_path = 'src/assets/tea_points.json'

try:
    print(f"Reading {excel_path}...")
    df = pd.read_excel(excel_path)
    
    print("Columns found:", df.columns.tolist())
    
    # Needs inspection of columns to map correctly
    # Assuming columns like '纬度' (Lat), '经度' (Lng), '名称' (Name) or similar
    # I will dump the first few rows to see content first if needed
    
    # Define column mappings (prioritize valid names)
    # Check what actually exists
    cols = df.columns.tolist()
    
    # Coordinate columns strategy
    lat_keys = ['LATITUDE', 'LATIN', 'lat', 'Latitude']
    lng_keys = ['LONGITUDE', 'long', 'lng', 'Longitude']
    
    found_lat = next((c for c in lat_keys if c in cols), None)
    found_lng = next((c for c in lng_keys if c in cols), None)
    
    records = df.to_dict(orient='records')
    valid_records = []
    
    print(f"Using Coords: {found_lat}, {found_lng}")

    print(f"Total records to process: {len(records)}")
    processed_count = 0

    for r in records:
        try:
            # 1. Coordinates
            lat_val = r.get(found_lat)
            lng_val = r.get(found_lng)
            
            lat = pd.to_numeric(lat_val, errors='coerce')
            lng = pd.to_numeric(lng_val, errors='coerce')
            
            # If coordinates are missing, we skip for MAP purposes, or include with null?
            # User said "generate all data", but points need coords.
            # If invalid, maybe default to center of China or specific null handling?
            # CustomMap expects valid points. I'll skip if absolutely no coords.
            if pd.isna(lat) or pd.isna(lng):
                # Try fallback: maybe fields like LAT_DEGREE exist?
                # For now, skip.
                continue

            # 2. Name
            # User request: TREE_CODE is the name
            name = str(r.get('TREE_CODE', r.get('CNAME', r.get('USER_NAME', r.get('Name', 'Unknown')))))
            if name == 'nan': name = 'Unknown Tea Tree'

            # 3. Region split (Format: Province/City/District)
            region_str = str(r.get('REGION', ''))
            parts = region_str.split('/')
            province = parts[0] if len(parts) > 0 else ''
            city = parts[1] if len(parts) > 1 else ''
            district = parts[2] if len(parts) > 2 else ''
            
            # 4. DBH
            # User request: dbh corresponds to JIJING field
            dbh_val = r.get('JIJING', r.get('DBH'))
            dbh = pd.to_numeric(dbh_val, errors='coerce')
            if pd.isna(dbh): dbh = 10 # Default
            
            # 5. Style
            style = 0
            if dbh <= 150: style = 0
            elif dbh <= 350: style = 1
            else: style = 2
            
            # 6. Mock Fields for compatibility
            # Randomly assign basin/mountain if missing
            
            # Format TREE_ID: Remove .0 if present
            raw_tree_id = str(r.get('TREE_ID', ''))
            if raw_tree_id.endswith('.0'):
                raw_tree_id = raw_tree_id[:-2]
                
            valid_records.append({
                "id": str(r.get('ID', '')),
                "tree_id": raw_tree_id,
                "lnglat": [float(lng), float(lat)],
                "name": name,
                "province": province,
                "city": city,
                "district": district,
                "township": str(r.get('ADDRESS', '')), # Use ADDRESS as township fallback
                "dbh": float(dbh),
                "style": style,
                "riverBasin": "" # Default
            })
            
            if processed_count % 100 == 0:
                print(f"Processed {processed_count} rows...")
            processed_count += 1
            
        except Exception as ex:
            print(f"Row error: {ex}")
            continue
            
    # Clean NaNs to None for valid JSON
    import math
    def clean_nan(v):
        if isinstance(v, float) and math.isnan(v): return None
        return v
        
    final_records = []
    for r in valid_records:
        r['dbh'] = clean_nan(r['dbh'])
        r['lnglat'] = [clean_nan(x) for x in r['lnglat']]
        final_records.append(r)

    print(f"Writing {len(final_records)} records to {json_path}...")
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(final_records, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved {len(final_records)} points to {json_path}")
    except Exception as e:
        print(f"JSON Dump Failed: {e}")

except Exception as e:
    print(f"Error: {e}")
