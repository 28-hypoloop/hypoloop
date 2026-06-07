import os
import sqlite3
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import math

EXP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ID = "house_prices"
DB_PATH = os.path.abspath(os.path.join(EXP_DIR, "..", "..", "..", "..", "data.db"))

def load_data():
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    df = pd.read_sql("SELECT * FROM dataset", conn)
    conn.close()
    return df

def train_model():
    df = load_data()
    
    features = ["OverallQual", "GrLivArea", "GarageCars", "TotalBsmtSF", "Neighborhood", "ExterQual", "BldgType"]
    target = "SalePrice"
    
    # Drop rows with missing values in selected features or target
    df = df.dropna(subset=features + [target])
    
    X = df[features]
    y = df[target]
    
    # Identify categorical and numerical columns
    categorical_cols = ["Neighborhood", "ExterQual", "BldgType"]
    numerical_cols = ["OverallQual", "GrLivArea", "GarageCars", "TotalBsmtSF"]
    
    # Create preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', numerical_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
        ])
    
    # Create the full pipeline with RandomForestRegressor
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    mlflow.set_tracking_uri(f"sqlite:///{os.path.join(EXP_DIR, 'mlflow.db')}")
    mlflow.set_experiment(f"exp_{PROJECT_ID}")
    
    with mlflow.start_run():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        
        r2 = r2_score(y_test, preds)
        rmse = math.sqrt(mean_squared_error(y_test, preds))
        
        mlflow.log_params({"n_estimators": 100, "random_state": 42, "features": str(features)})
        mlflow.log_metrics({"r2": r2, "rmse": rmse})
        mlflow.sklearn.log_model(model, "model")
        
        print(f"[*] Training 및 MLflow 로깅이 성공적으로 완료되었습니다. R2: {r2:.3f}, RMSE: {rmse:.2f}")
        return r2, rmse

if __name__ == "__main__":
    train_model()
