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
    
    # 1. 扫描所有省级文件（2 位 adcode）
    print("扫描省级文件...")
    province_files = [f for f in GEOJSON_DIR.glob('*.json') 
                      if len(f.stem) == 2 and f.stem.isdigit()]
    
    print(f"找到 {len(province_files)} 个省级文件")
    
    for prov_file in province_files:
        prov_adcode = prov_file.stem
        
        try:
            with open(prov_file, 'r', encoding='utf-8') as f:
                prov_data = json.load(f)
            
            features = prov_data.get('features', [])
            
            # 从文件名获取省份信息
            prov_name = ""
            prov_center = [0, 0]
            prov_centroid = [0, 0]
            
            # 提取这个省下的所有城市
            city_list = []
            for feature in features:
                props = feature.get('properties', {})
                city_adcode = str(props.get('adcode', ''))
                city_name = props.get('name', '')
                city_center = props.get('center', [0, 0])
                city_centroid = props.get('centroid', city_center)
                city_level = props.get('level', 'city')
                
                # 第一个特征通常代表省会/首府
                if not prov_name and city_name:
                    # 使用省会城市的信息作为省的参考点
                    prov_name = city_name.replace('市', '') + '省' if not city_name.endswith('省') else city_name
                    prov_center = city_center
                    prov_centroid = city_centroid
                
                # 只添加城市级别
                if city_adcode != prov_adcode and city_name:
                    city_info = {
                        'name': city_name,
                        'center': city_center,
                        'centroid': city_centroid,
                        'level': city_level,
                        'children': []
                    }
                    
                    # 添加到省级 children
                    city_list.append({
                        'adcode': city_adcode,
                        'name': city_name
                    })
                    
                    # 添加城市本身到 info_data
                    if city_adcode not in info_data:
                        info_data[city_adcode] = city_info
            
            # 添加省份信息
            if prov_adcode:
                info_data[prov_adcode] = {
                    'name': f'{prov_adcode}省',  # 临时名称
                    'center': prov_center,
                    'centroid': prov_centroid,
                    'level': 'province',
                    'children': city_list
                }
        
        except Exception as e:
            print(f"处理 {prov_file.name} 时出错：{e}")
            continue
    
    # 2. 读取市级文件，提取区县级信息
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
    
    # 3. 构建根节点（中国）
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
    
    # 4. 排序并保存
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
