import json
import os
from pathlib import Path

GEOJSON_DIR = Path('src/assets/geojson')
OUTPUT_FILE = Path('src/assets/external_geojson/info.json')

def extract_info_from_geojson():
    """从 GeoJSON 文件中提取行政区划信息"""
    
    # 确保输出目录存在
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    info_data = {}
    
    # 1. 首先读取 country.json 获取省级信息
    country_file = GEOJSON_DIR / 'country.json'
    if country_file.exists():
        print(f"读取 {country_file}...")
        with open(country_file, 'r', encoding='utf-8') as f:
            country_data = json.load(f)
        
        # 提取省级行政区
        province_features = country_data.get('features', [])
        print(f"找到 {len(province_features)} 个省级行政区")
        
        for feature in province_features:
            props = feature.get('properties', {})
            adcode = str(props.get('adcode', ''))
            name = props.get('name', '')
            center = props.get('center', [0, 0])
            centroid = props.get('centroid', center)
            
            if adcode and name:
                info_data[adcode] = {
                    'name': name,
                    'center': center,
                    'centroid': centroid,
                    'level': props.get('level', 'province'),
                    'children': []
                }
    
    # 2. 读取各个省级文件，提取市级信息
    print("\n扫描省级文件...")
    province_files = [f for f in GEOJSON_DIR.glob('*.json') 
                      if f.name != 'country.json' and f.name != 'index.json']
    
    for prov_file in province_files:
        try:
            # 文件名通常是省级 adcode
            prov_adcode = prov_file.stem
            
            with open(prov_file, 'r', encoding='utf-8') as f:
                prov_data = json.load(f)
            
            features = prov_data.get('features', [])
            
            # 提取这个省下的所有城市
            for feature in features:
                props = feature.get('properties', {})
                city_adcode = str(props.get('adcode', ''))
                city_name = props.get('name', '')
                city_center = props.get('center', [0, 0])
                city_centroid = props.get('centroid', city_center)
                city_level = props.get('level', 'city')
                
                # 只添加城市级别（不是省本身）
                if city_adcode != prov_adcode and city_name:
                    city_info = {
                        'name': city_name,
                        'center': city_center,
                        'centroid': city_centroid,
                        'level': city_level,
                        'children': []
                    }
                    
                    # 添加到省级 children
                    if prov_adcode in info_data:
                        # 检查是否已存在
                        existing = [c for c in info_data[prov_adcode]['children'] 
                                   if c.get('adcode') == city_adcode]
                        if not existing:
                            info_data[prov_adcode]['children'].append({
                                'adcode': city_adcode,
                                'name': city_name
                            })
                    
                    # 添加城市本身到 info_data
                    if city_adcode not in info_data:
                        info_data[city_adcode] = city_info
        
        except Exception as e:
            print(f"处理 {prov_file.name} 时出错：{e}")
            continue
    
    # 3. 读取市级文件，提取区县级信息
    print("\n扫描市级文件...")
    city_files_processed = 0
    for city_file in GEOJSON_DIR.glob('*.json'):
        city_adcode = city_file.stem
        
        # 跳过特殊文件
        if city_file.name in ['country.json', 'index.json']:
            continue
        
        # 只处理 6 位 adcode 的文件（市级或区县级）
        if len(city_adcode) != 6:
            continue
        
        try:
            with open(city_file, 'r', encoding='utf-8') as f:
                city_data = json.load(f)
            
            features = city_data.get('features', [])
            
            # 提取这个市下的所有区县
            for feature in features:
                props = feature.get('properties', {})
                county_adcode = str(props.get('adcode', ''))
                county_name = props.get('name', '')
                county_center = props.get('center', [0, 0])
                county_centroid = props.get('centroid', county_center)
                
                # 只添加区县级别
                if county_adcode != city_adcode and county_name:
                    # 添加到市级 children
                    if city_adcode in info_data:
                        existing = [c for c in info_data[city_adcode]['children'] 
                                   if c.get('adcode') == county_adcode]
                        if not existing:
                            info_data[city_adcode]['children'].append({
                                'adcode': county_adcode,
                                'name': county_name
                            })
            
            city_files_processed += 1
            
        except Exception as e:
            continue
    
    print(f"\n处理了 {city_files_processed} 个市级文件")
    
    # 4. 构建根节点（中国）
    root_children = []
    for adcode, info in info_data.items():
        if info.get('level') == 'province':
            root_children.append({
                'adcode': adcode,
                'name': info['name']
            })
    
    # 按 adcode 排序
    root_children.sort(key=lambda x: int(x['adcode']))
    
    root_info = {
        'name': '中国',
        'center': [116.405285, 39.904989],  # 北京中心
        'centroid': [116.405285, 39.904989],
        'level': 'country',
        'children': root_children
    }
    
    # 添加根节点
    info_data['100000'] = root_info
    
    # 5. 排序并保存
    print(f"\n保存 info.json 到 {OUTPUT_FILE}...")
    
    # 按 adcode 排序所有键
    sorted_info = dict(sorted(info_data.items()))
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted_info, f, ensure_ascii=False, indent=2)
    
    # 统计信息
    provinces = sum(1 for v in info_data.values() if v.get('level') == 'province')
    cities = sum(1 for v in info_data.values() if v.get('level') == 'city')
    total_with_children = sum(1 for v in info_data.values() if v.get('children'))
    
    print(f"\n✅ 生成完成！")
    print(f"   - 总记录数：{len(info_data)}")
    print(f"   - 省级：{provinces}")
    print(f"   - 市级：{cities}")
    print(f"   - 有子区域的：{total_with_children}")
    print(f"\n文件已保存到：{OUTPUT_FILE.absolute()}")

if __name__ == '__main__':
    extract_info_from_geojson()
