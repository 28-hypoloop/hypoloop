import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 경로 설정
PROJECT_ROOT = '/Users/a1234/Desktop/agn'
DB_PATH = os.path.join(PROJECT_ROOT, 'data/projects/house_prices/data.db')
EXP_DIR = '/Users/a1234/Desktop/agn/data/projects/house_prices/hypotheses/hyp02/experiments/exp_4bead2'
IMG_DIR = os.path.join(EXP_DIR, 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def load_data():
    """SQLite Database (Read-Only) 연동"""
    conn_uri = f"file:{DB_PATH}?mode=ro"
    with sqlite3.connect(conn_uri, uri=True) as conn:
        df = pd.read_sql("SELECT * FROM dataset", conn)
    return df

def run_eda():
    df = load_data()
    features = ['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF', 'Neighborhood', 'ExterQual', 'BldgType']
    target = 'SalePrice'
    
    # 수치형 변수 분포
    numeric_features = ['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF']
    for feature in numeric_features:
        plt.figure(figsize=(10, 6))
        sns.histplot(df[feature], kde=True)
        plt.title(f'{feature} Distribution')
        plt.savefig(os.path.join(IMG_DIR, f'{feature}_dist.png'))
        plt.close()
        
        plt.figure(figsize=(8, 6))
        sns.boxplot(x=df[feature])
        plt.title(f'{feature} Outliers')
        plt.savefig(os.path.join(IMG_DIR, f'{feature}_outliers.png'))
        plt.close()
        
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x=df[feature], y=df[target])
        plt.title(f'{feature} vs SalePrice')
        plt.savefig(os.path.join(IMG_DIR, f'{feature}_vs_target.png'))
        plt.close()
    
    # 범주형 변수 분포
    categorical_features = ['Neighborhood', 'ExterQual', 'BldgType']
    for feature in categorical_features:
        plt.figure(figsize=(12, 6))
        sns.countplot(y=df[feature], order=df[feature].value_counts().index[:10])
        plt.title(f'Top 10 {feature} Counts')
        plt.savefig(os.path.join(IMG_DIR, f'{feature}_counts.png'))
        plt.close()
        
        plt.figure(figsize=(12, 6))
        sns.boxplot(x=df[feature], y=df[target])
        plt.title(f'{feature} vs SalePrice')
        plt.savefig(os.path.join(IMG_DIR, f'{feature}_vs_target.png'))
        plt.close()
    
    print(f"[*] EDA 완료. 차트 이미지가 {IMG_DIR} 에 저장되었습니다.")

if __name__ == "__main__":
    run_eda()