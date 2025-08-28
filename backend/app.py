from flask import Flask, jsonify, request
from flask_cors import CORS
import data_processing as dp
import modeling as ml
import os
import threading
from amap_api import get_poi_data, geocode, reverse_geocode
import time
import hashlib
import json
import traceback
app = Flask(__name__)
CORS(app)
from pathlib import Path
from filelock import FileLock
# 缓存目录
# CACHE_DIR = 'backend/cache'
# os.makedirs(CACHE_DIR, exist_ok=True)
# 缓存配置（替换原有的CACHE_DIR定义）
CACHE_DIR = Path("data/cache")
CACHE_EXPIRE_SECONDS = 3600  # 1小时有效期
MAX_CACHE_SIZE = 1024 * 1024 * 1024  # 1GB上限
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在的目录
DATA_FILE = os.path.join(BASE_DIR, 'data', 'restaurants.csv')


# 加载数据
df = dp.load_data(DATA_FILE)

# 训练模型
if not df.empty:
    kmeans_model, scaler = ml.train_kmeans(df, n_clusters=5)
    print("模型训练完成")
else:
    kmeans_model, scaler = None, None
    print("数据为空，无法训练模型")

def get_cache_key(city, keywords):
    """生成缓存键"""
    key_str = f"{city}_{'_'.join(keywords)}"
    return hashlib.md5(key_str.encode()).hexdigest()

# def get_cached_data(cache_key):
#     """获取缓存数据"""
#     cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
#     if os.path.exists(cache_file):
#         # 检查缓存是否过期（1小时）
#         if time.time() - os.path.getmtime(cache_file) < 3600:
#             with open(cache_file, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#     return None
# 优化后的读取缓存函数（替代原逻辑）
def get_cached_data(cache_key: str) -> dict | None:
    cache_file = _get_cache_path(cache_key)
    if not cache_file.exists():
        return None
    # 检查过期
    if time.time() - cache_file.stat().st_mtime > CACHE_EXPIRE_SECONDS:
        return None
    # 加锁读取
    lock_file = Path(f"{cache_file}.lock")
    with FileLock(lock_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, EOFError):
            cache_file.unlink(missing_ok=True)  # 删除损坏文件
            return None
# def save_data_to_cache(cache_key, data):
#     """保存数据到缓存"""
#     cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
#     with open(cache_file, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)
# 优化后的写入缓存函数（替代原save_data_to_cache）
def save_data_to_cache(cache_key: str, data: dict) -> None:
    cache_file = _get_cache_path(cache_key)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)  # 确保目录存在
    lock_file = Path(f"{cache_file}.lock")
    with FileLock(lock_file):
        # 原子写入（先写临时文件）
        temp_file = cache_file.with_suffix(".tmp.json")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        temp_file.rename(cache_file)  # 原子替换
    # 检查并清理缓存
    clean_cache_if_needed()
# ... 其他API端点保持不变 ...
@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    """获取所有餐厅的聚类结果"""
    try:
        if kmeans_model is None:
            return jsonify({"error": "模型未初始化"}), 500
            
        clustered_data = ml.predict_clusters(df, kmeans_model, scaler)
        # 转换为前端需要的格式（只取部分字段）
        result = clustered_data[['name', 'address', 'lng', 'lat', 'rating', 'price_level', 'cluster']].to_dict(orient='records')
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"获取聚类数据失败: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "服务器内部错误"}), 500
@app.route('/api/predict', methods=['POST'])
def predict_location():
    """预测新位置的分类"""
    try:
        if kmeans_model is None:
            return jsonify({"error": "模型未初始化"}), 500
            
        data = request.json
        features = [
            data['population'],
            data['competitors'],
            data['transport'],
            data['rating'],
            data['price_level']
        ]
        prediction = ml.predict_new_location(features, kmeans_model, scaler)
        return jsonify({"cluster": int(prediction[0])})
    except Exception as e:
        app.logger.error(f"预测位置失败: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "预测失败，请检查输入参数"}), 400

@app.route('/api/get_data', methods=['POST'])
def get_data():
    """从高德API获取数据"""
    data = request.json
    city = data.get('city', '北京')
    keywords = data.get('keywords', ['餐厅'])
    
    # 检查缓存
    cache_key = get_cache_key(city, keywords)
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        # 保存到数据文件
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(cached_data, f, ensure_ascii=False)
        print(f"使用缓存数据: {cache_key}")
        return jsonify({"status": "cached", "message": "使用缓存数据"})
    
    # 在新线程中获取数据
    threading.Thread(target=fetch_data, args=(city, keywords, cache_key)).start()
    
    return jsonify({"status": "started", "message": "数据获取已开始，请稍后刷新页面"})

def fetch_data(city, keywords, cache_key):
    """获取数据并保存"""
    try:
        # 获取POI数据
        poi_df = get_poi_data(keywords, city)
        
        if poi_df.empty:
            print("未获取到数据")
            return
        
        # 转换为JSON可序列化格式
        data = poi_df.to_dict(orient='records')
        
        # 保存到缓存
        save_data_to_cache(cache_key, data)
        
        # 保存到数据文件
        poi_df.to_csv(DATA_FILE, index=False, encoding='utf_8_sig')
        print(f"数据已保存至: {DATA_FILE}")
        
        # 重新加载数据并训练模型
        global df, kmeans_model, scaler
        df = dp.load_data(DATA_FILE)
        if not df.empty:
            kmeans_model, scaler = ml.train_kmeans(df, n_clusters=5)
            print("模型重新训练完成")
        
    except Exception as e:
        print(f"获取数据失败: {str(e)}")

# ... 其他API端点保持不变 ...
@app.route('/api/geocode', methods=['POST'])
def get_geocode():
    """地理编码（地址转经纬度）"""
    data = request.json
    address = data.get('address')
    if not address:
        return jsonify({"error": "地址不能为空"}), 400
    
    try:
        location = geocode(address)
        if location:
            lng, lat = location.split(',')
            return jsonify({"lng": float(lng), "lat": float(lat)})
        return jsonify({"error": "地理编码失败"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.after_request
def set_charset(response):
    """设置字符编码为 UTF-8"""
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response
@app.route('/api/reverse_geocode', methods=['POST'])
def get_reverse_geocode():
    """逆地理编码（经纬度转地址）"""
    data = request.json
    lng = data.get('lng')
    lat = data.get('lat')
    if lng is None or lat is None:
        return jsonify({"error": "经纬度不能为空"}), 400
    
    try:
        address = reverse_geocode(lng, lat)
        return jsonify({"address": address}) if address else jsonify({"error": "逆地理编码失败"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# 新增：生成缓存路径（处理长键名）
def _get_cache_path(cache_key: str) -> Path:
    if len(cache_key) > 64:
        cache_key = hashlib.sha256(cache_key.encode()).hexdigest()
    return CACHE_DIR / f"{cache_key}.json"
# 新增：清理过期缓存
def clean_expired_cache() -> None:
    if not CACHE_DIR.exists():
        return
    for cache_file in CACHE_DIR.glob("*.json"):
        if time.time() - cache_file.stat().st_mtime > CACHE_EXPIRE_SECONDS:
            cache_file.unlink(missing_ok=True)
            Path(f"{cache_file}.lock").unlink(missing_ok=True)
# 新增：缓存大小超限清理
def clean_cache_if_needed() -> None:
    if not CACHE_DIR.exists():
        return
    total_size = sum(f.stat().st_size for f in CACHE_DIR.glob("*.json"))
    if total_size <= MAX_CACHE_SIZE:
        return
    # 按修改时间排序，清理最早的文件
    cache_files = sorted(CACHE_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime)
    current_size = total_size
    for f in cache_files:
        current_size -= f.stat().st_size
        f.unlink(missing_ok=True)
        Path(f"{f}.lock").unlink(missing_ok=True)
        if current_size <= MAX_CACHE_SIZE * 0.8:
            break
if __name__ == '__main__':
    app.run(debug=True, port=5000)
    # 初始化时清理一次过期缓存
    clean_expired_cache()