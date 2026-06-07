import os
import sqlite3
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import math

# Project-specific paths
PROJECT_ID = "house_prices"
EXP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(EXP_DIR, "../../../../data.db")
MLFLOW_URI = "sqlite:///mlruns.db"
EXP_NAME = f"exp_{PROJECT_ID}"

def load_data():
    """SQLite Database (Read-Only) 연동"""
    conn_uri = f"file:{DB_PATH}?mode=ro"
    with sqlite3.connect(conn_uri, uri=True) as conn:
        df = pd.read_sql("SELECT * FROM dataset", conn)
    return df

def run_training():
    df = load_data()
    target = 'SalePrice'
    features = ['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF']
    
    # Data split
    X = df[features]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    
    # MLflow setup
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXP_NAME)
    
    with mlflow.start_run():
        # Model training
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluation
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        # Calculate RMSE manually since sklearn 1.5+ changed the API
        mse = mean_squared_error(y_test, y_pred)
        rmse = math.sqrt(mse)
        
        # Log results
        mlflow.log_params({
            'model': 'RandomForestRegressor',
            'features': str(features),
            'n_estimators': 100,
            'random_state': 42
        })
        mlflow.log_metrics({
            'r2_score': r2,
            'rmse': rmse
        })
        mlflow.sklearn.log_model(model, "model")
    
    print(f"[*] Training 및 MLflow 로깅이 성공적으로 완료되었습니다. R2: {r2:.3f}, RMSE: {rmse:.2f}")

if __name__ == "__main__":
    run_training()