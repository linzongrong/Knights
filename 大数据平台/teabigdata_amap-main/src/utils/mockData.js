/**
 * Generates mock Tree data with administrative hierarchy.
 * 
 * @param {number} count - Number of points to generate.
 * @returns {Array} List of tree objects with properties: lnglat, name, province, city, district, township, dbh, style.
 */
export const generatePoints = (count) => {
    const trees = [];

    // Administrative Hierarchy Configuration
    // Defines the bounds and townships for specific districts to ensure realistic data distribution.
    const hierarchy = {
        '云南省': {
            '昆明市': {
                '五华区': {
                    bounds: { minLng: 102.6, maxLng: 102.75, minLat: 25.0, maxLat: 25.15 }, // Wuhua District Bounds
                    townships: ['华山街道', '护国街道', '大观街道', '龙翔街道', '丰宁街道', '莲华街道', '红云街道', '黑林铺街道', '普吉街道', '西翥街道']
                },
                '盘龙区': {
                    bounds: { minLng: 102.7, maxLng: 102.9, minLat: 25.0, maxLat: 25.25 }, // Panlong District Bounds
                    townships: ['拓东街道', '鼓楼街道', '东华街道', '联盟街道', '金辰街道', '青云街道', '茨坝街道', '龙泉街道', '松华街道', '双龙街道', '滇源街道', '阿子营街道']
                },
                '官渡区': {
                    bounds: { minLng: 102.7, maxLng: 102.85, minLat: 24.9, maxLat: 25.05 },
                    townships: ['关上街道', '太和街道', '吴井街道', '金马街道', '小板桥街道', '官渡街道']
                },
                '西山区': {
                    bounds: { minLng: 102.6, maxLng: 102.7, minLat: 24.9, maxLat: 25.05 },
                    townships: ['西苑街道', '马街街道', '金碧街道', '永昌街道', '前卫街道', '福海街道', '棕树营街道', '碧鸡街道', '海口街道', '团结街道']
                }
            },
            '大理白族自治州': {
                '大理市': {
                    bounds: { minLng: 100.1, maxLng: 100.35, minLat: 25.55, maxLat: 25.75 },
                    townships: ['下关镇', '大理镇', '凤仪镇', '喜洲镇', '海东镇', '挖色镇', '银桥镇', '双廊镇', '上关镇', '太邑彝族乡']
                }
            }
        },
        '贵州省': {
            '贵阳市': {
                '南明区': {
                    bounds: { minLng: 106.65, maxLng: 106.75, minLat: 26.5, maxLat: 26.6 },
                    townships: ['新华路街道', '市府路街道', '河滨街道', '兴关路街道']
                },
                '云岩区': {
                    bounds: { minLng: 106.65, maxLng: 106.75, minLat: 26.6, maxLat: 26.7 },
                    townships: ['大营路街道', '黔灵镇', '普陀路街道']
                }
            }
        }
    };

    let generatedCount = 0;

    while (generatedCount < count) {
        // 1. Randomly select hierarchically down to Township
        const provinces = Object.keys(hierarchy);
        const province = provinces[Math.floor(Math.random() * provinces.length)];

        const cities = Object.keys(hierarchy[province]);
        const city = cities[Math.floor(Math.random() * cities.length)];

        const districts = Object.keys(hierarchy[province][city]);
        const district = districts[Math.floor(Math.random() * districts.length)];
        const districtData = hierarchy[province][city][district];

        const township = districtData.townships[Math.floor(Math.random() * districtData.townships.length)];

        // 2. Generate random coordinate within the specific district's bounds
        const lng = Math.random() * (districtData.bounds.maxLng - districtData.bounds.minLng) + districtData.bounds.minLng;
        const lat = Math.random() * (districtData.bounds.maxLat - districtData.bounds.minLat) + districtData.bounds.minLat;

        // 3. Generate random DBH (Diameter at Breast Height)
        const dbh = Math.floor(Math.random() * (500 - 10 + 1)) + 10; // 10cm - 500cm

        // 4. Determine Style Index based on DBH
        let style = 0;
        if (dbh <= 150) style = 0;      // Small (Green)
        else if (dbh <= 350) style = 1; // Medium (Yellow)
        else style = 2;                 // Large (Brown)

        // Mock River Basin (Lancang vs Other)
        const riverBasin = Math.random() < 0.4 ? '澜沧江流域' : '其他流域';

        // Mock Mountain Range
        const randMtn = Math.random();
        let mountainRange = '其他山脉';
        if (randMtn < 0.3) mountainRange = '哀牢山山脉';
        else if (randMtn < 0.5) mountainRange = '高黎贡山山脉';

        trees.push({
            lnglat: [lng, lat], // AMap 2.0 supports [lng, lat] array
            name: `树木 #${generatedCount + 1}`,
            province: province,
            city: city,
            district: district,
            township: township,
            dbh: dbh,
            style: style,
            riverBasin: riverBasin,
            mountainRange: mountainRange
        });

        generatedCount++;
    }

    return trees;
};
