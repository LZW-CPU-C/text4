import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def load_data(file_path):
    """加载并预处理数据"""
    try:
        df = pd.read_csv(file_path)
        
        # 数据清洗
        df = df.dropna(subset=['lng', 'lat'])
        df = df[df['lng'] > 0]  # 过滤无效经纬度
        
        # 确保必要的特征列存在
        required_columns = ['lng', 'lat', 'rating', 'price_level', 'surrounding_population', 'competitors', 'transport']
        for col in required_columns:
            if col not in df.columns:
                # 添加模拟特征（实际项目中应使用真实特征）
                print(f"警告: 缺少列 '{col}'，使用模拟数据")
                if col == 'rating':
                    df['rating'] = np.round(np.random.uniform(3.5, 5.0, len(df)), 1)
                elif col == 'price_level':
                    df['price_level'] = np.random.randint(1, 5, len(df))
                elif col == 'surrounding_population':
                    df['surrounding_population'] = np.random.randint(5000, 50000, len(df))
                elif col == 'competitors':
                    df['competitors'] = np.random.randint(0, 15, len(df))
                elif col == 'transport':
                    df['transport'] = np.round(np.random.uniform(0.5, 1.0, len(df)), 2)
        
        return df
    except Exception as e:
        print(f"加载数据失败: {str(e)}")
        return pd.DataFrame()  # 返回空DataFrame