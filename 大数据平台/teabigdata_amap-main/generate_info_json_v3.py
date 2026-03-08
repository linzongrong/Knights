import json
from pathlib import Path

GEOJSON_DIR = Path('src/assets/geojson')
OUTPUT_FILE = Path('src/assets/external_geojson/info.json')

# 省级行政区代码对照表
PROVINCE_NAMES = {
    '11': '北京市', '12': '天津市', '13': '河北省', '14': '山西省', '15': '内蒙古自治区',
    '21': '辽宁省', '22': '吉林省', '23': '黑龙江省',
    '31': '上海市', '32': '江苏省', '33': '浙江省', '34': '安徽省', '35': '福建省', '36': '江西省', '37': '山东省',
    '41': '河南省', '42': '湖北省', '43': '湖南省', '44': '广东省', '45': '广西壮族自治区', '46': '海南省',
    '50': '重庆市', '51': '四川省', '52': '贵州省', '53': '云南省', '54': '西藏自治区',
    '61': '陕西省', '62': '甘肃省', '63': '青海省', '64': '宁夏回族自治区', '65': '新疆维吾尔自治区',
    '71': '台湾省',
    '81': '香港特别行政区', '82': '澳门特别行政区'
}

def extract_info_from_geojson():
    """从 GeoJSON 文件中提取行政区划信息"""
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    info_data = {}
    
    # 1. 扫描所有省级文件
    print("扫描省级文件...")
    province_files = [f for f in GEOJSON_DIR.glob('*.json') 
                      if len(f.stem) == 2 and f.stem.isdigit()]
    
    print(f"找到 {len(province_files)} 个省级文件")
    
    for prov_file in province_files:
        prov_adcode = prov_file.stem
        prov_name = PROVINCE_NAMES.get(prov_adcode, f'{prov_adcode}省')
        
        try:
            with open(prov_file, 'r', encoding='utf-8') as f:
                prov_data = json.load(f)
            
            features = prov_data.get('features', [])
            
            prov_center = [0, 0]
            prov_centroid = [0, 0]
            city_list = []
            
            # 提取这个省下的所有城市
            for feature in features:
                props = feature.get('properties', {})
                city_adcode = str(props.get('adcode', ''))
                city_name = props.get('name', '')
                city_center = props.get('center', [0, 0])
                city_centroid = props.get('centroid', city_center)
                city_level = props.get('level', 'city')
                
                # 使用第一个城市的中心作为省的中心
                if not prov_center or prov_center == [0, 0]:
                    prov_center = city_center
                    prov_centroid = city_centroid
                
                # 添加城市
                if city_adcode != prov_adcode and city_name:
                    city_info = {
                        'name': city_name,
                        'center': city_center,
                        'centroid': city_centroid,
                        'level': city_level,
                        'children': []
                    }
                    
                    city_list.append({
                        'adcode': city_adcode,
                        'name': city_name
                    })
                    
                    if city_adcode not in info_data:
                        info_data[city_adcode] = city_info
            
            # 添加省份信息
            info_data[prov_adcode] = {
                'name': prov_name,
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
        
        if city_file.name in ['country.json', 'index.json']:
            continue
        
        if len(city_adcode) != 6:
            continue
        
        try:
            with open(city_file, 'r', encoding='utf-8') as f:
                city_data = json.load(f)
            
            features = city_data.get('features', [])
            
            for feature in features:
                props = feature.get('properties', {})
                county_adcode = str(props.get('adcode', ''))
                county_name = props.get('name', '')
                county_center = props.get('center', [0, 0])
                county_centroid = props.get('centroid', county_center)
                
                if county_adcode != city_adcode and county_name:
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
    
    root_children.sort(key=lambda x: int(x['adcode']))
    
    root_info = {
        'name': '中国',
        'center': [116.405285, 39.904989],
        'centroid': [116.405285, 39.904989],
        'level': 'country',
        'children': root_children
    }
    
    info_data['100000'] = root_info
    
    # 4. 排序并保存
    print(f"\n保存 info.json 到 {OUTPUT_FILE}...")
    sorted_info = dict(sorted(info_data.items()))
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted_info, f, ensure_ascii=False, indent=2)
    
    # 统计
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
