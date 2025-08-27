from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

def train_kmeans(df, n_clusters=5):
    """训练K-Means聚类模型"""
    if df.empty:
        print("数据为空，无法训练模型")
        return None, None
    
    features = ['surrounding_population', 'competitors', 'transport', 'rating', 'price_level']
    
    # 确保所有特征列都存在
    for feature in features:
        if feature not in df.columns:
            print(f"错误: 缺少特征列 '{feature}'")
            return None, None
    
    X = df[features].values
    # 特征标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # 训练模型
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X_scaled)

    return kmeans, scaler

def predict_clusters(df, model, scaler):
    """预测聚类结果"""
    features = ['surrounding_population', 'competitors', 'transport', 'rating', 'price_level']
    X = df[features].values
    X_scaled = scaler.transform(X)
    
    df['cluster'] = model.predict(X_scaled)
    return df

def predict_new_location(features, model, scaler):
    """预测新位置的聚类"""
    features_array = np.array(features).reshape(1, -1)
    features_scaled = scaler.transform(features_array)
    return model.predict(features_scaled)