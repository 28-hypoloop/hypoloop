import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Project-specific paths
PROJECT_ID = "house_prices"
EXP_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(EXP_DIR, "img")
DB_PATH = os.path.join(EXP_DIR, "../../../../data.db")

# Create image directory if not exists
os.makedirs(IMG_DIR, exist_ok=True)

def load_data():
    """SQLite Database (Read-Only) 연동"""
    conn_uri = f"file:{DB_PATH}?mode=ro"
    with sqlite3.connect(conn_uri, uri=True) as conn:
        df = pd.read_sql("SELECT * FROM dataset", conn)
    return df

def run_eda():
    df = load_data()
    target = 'SalePrice'
    features = ['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF']
    
    # Target variable distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df[target], kde=True)
    plt.title(f'Distribution of {target}')
    save_path = os.path.join(IMG_DIR, f'{target}_distribution.png')
    plt.savefig(save_path)
    plt.close()
    
    # Feature distributions
    for feature in features:
        plt.figure(figsize=(10, 6))
        sns.histplot(df[feature], kde=True)
        plt.title(f'Distribution of {feature}')
        save_path = os.path.join(IMG_DIR, f'{feature}_distribution.png')
        plt.savefig(save_path)
        plt.close()
    
    # Feature vs target
    for feature in features:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=df[feature], y=df[target])
        plt.title(f'{feature} vs {target}')
        save_path = os.path.join(IMG_DIR, f'{feature}_vs_{target}.png')
        plt.savefig(save_path)
        plt.close()
    
    print(f"[*] EDA 완료. 차트 이미지가 {IMG_DIR} 에 저장되었습니다.")

if __name__ == "__main__":
    run_eda()