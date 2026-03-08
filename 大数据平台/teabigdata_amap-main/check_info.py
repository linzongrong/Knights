import json

# 检查 country.json
with open('src/assets/geojson/country.json', 'r', encoding='utf-8') as f:
    country = json.load(f)

print(f"country.json features: {len(country.get('features', []))}")
print("\n前 5 个特征:")
for feat in country.get('features', [])[:5]:
    props = feat.get('properties', {})
    print(f"  - {props.get('name')} (adcode: {props.get('adcode')}, level: {props.get('level')})")

# 检查生成的 info.json
with open('src/assets/external_geojson/info.json', 'r', encoding='utf-8') as f:
    info = json.load(f)

print(f"\ninfo.json 总记录数：{len(info)}")
print(f"中国 (100000) 的 children: {len(info['100000']['children'])}")
print("\n中国 children 前 10 个:")
for child in info['100000']['children'][:10]:
    print(f"  - {child}")

# 检查省级记录
provinces = [k for k, v in info.items() if v.get('level') == 'province']
print(f"\n省级记录数：{len(provinces)}")
print("前 10 个省级:")
for code in provinces[:10]:
    print(f"  - {code}: {info[code]['name']}")
