import requests
import pandas as pd
import time
import os

# 替换为你的高德API Key
API_KEY = "a64ecd58acdf0289474c6e6d0da4dc43"

def get_poi_data(keywords, city, api_key=API_KEY):
    """获取POI数据"""
    all_dfs = []
    
    for keyword in keywords:
        base_url = "https://restapi.amap.com/v3/place/text"
        pois = []
        page = 1
        
        print(f"开始获取'{keyword}'的数据...")
        
        while True:
            params = {
                "keywords": keyword,
                "city": city,
                "offset": 20,  # 每页20条
                "page": page,
                "key": api_key,
                "extensions": "all"  # 获取所有信息
            }
            try:
                response = requests.get(base_url, params=params, timeout=10)
                data = response.json()
                
                if data["status"] != "1":
                    print(f"请求失败: {data.get('info', '未知错误')}")
                    break
                    
                pois_page = data.get("pois", [])
                if not pois_page:
                    break
                    
                pois.extend(pois_page)
                print(f"已获取第{page}页，共{len(pois_page)}条数据")
                page += 1
                time.sleep(0.2)  # 控制请求频率
                
            except Exception as e:
                print(f"请求异常: {e}")
                break
        
        if pois:
            # 转换为DataFrame并提取关键字段
            df = pd.DataFrame(pois)[
                ['id', 'name', 'type', 'typecode', 'address', 'location', 'tel', 
                 'pname', 'cityname', 'adname', 'business_area', 'photos']
            ]
            # 拆分经纬度
            df[['lng', 'lat']] = df['location'].str.split(',', expand=True).astype(float)
            
            # 添加模拟特征（实际项目中应使用真实特征）
            print("添加模拟特征...")
            df['rating'] = round(pd.Series([round(x, 1) for x in [4.0, 4.2, 4.5, 4.7, 4.9, 3.8] * (len(df)//6 + 1)]), 1)[:len(df)]
            df['price_level'] = pd.Series([1, 2, 2, 3, 3, 4] * (len(df)//6 + 1))[:len(df)]
            df['popularity'] = pd.Series([x for x in range(50, 200, 10)] * (len(df)//15 + 1))[:len(df)]
            df['surrounding_population'] = pd.Series([x for x in range(5000, 50000, 3000)] * (len(df)//15 + 1))[:len(df)]
            df['competitors'] = pd.Series([x for x in range(0, 15, 1)] * (len(df)//15 + 1))[:len(df)]
            df['transport'] = round(pd.Series([round(x, 2) for x in [0.5, 0.6, 0.7, 0.8, 0.9] * (len(df)//5 + 1)]), 2)[:len(df)]
            
            all_dfs.append(df)
    
    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

def geocode(address, api_key=API_KEY):
    """地理编码（地址转经纬度）"""
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {"address": address, "key": api_key}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data["status"] == "1" and data["geocodes"]:
            return data["geocodes"][0]["location"]  # 格式："经度,纬度"
        return None
    except Exception as e:
        print(f"地理编码失败: {str(e)}")
        return None

def reverse_geocode(lng, lat, api_key=API_KEY):
    """逆地理编码（经纬度转地址）"""
    url = "https://restapi.amap.com/v3/geocode/regeo"
    params = {"location": f"{lng},{lat}", "key": api_key}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data["status"] == "1":
            return data["regeocode"]["formatted_address"]
        return None
    except Exception as e:
        print(f"逆地理编码失败: {str(e)}")
        return None

if __name__ == "__main__":
    # 测试获取数据
    df = get_poi_data(["餐厅"], "北京")
    if not df.empty:
        print(f"获取到{len(df)}条数据")
        print(df.head())
        # 保存数据
        df.to_csv("data/restaurants.csv", index=False, encoding="utf_8_sig")
    else:
        print("未获取到数据")