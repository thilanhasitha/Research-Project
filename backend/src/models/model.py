# model.py

import pandas as pd
from sklearn.ensemble import IsolationForest
from src.models.config import CONTAMINATION, RANDOM_STATE, N_ESTIMATORS


def train_isolation_forest(X_scaled):
    model = IsolationForest(
        n_estimators=N_ESTIMATORS,
        contamination=CONTAMINATION,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_scaled)
    
    return model


def apply_model(df: pd.DataFrame, model, X_scaled):
    
    df = df.copy()
    df["anomaly_label"] = model.predict(X_scaled)          # 1 normal, -1 anomaly
    df["anomaly_score"] = -model.score_samples(X_scaled)   # higher = more anomalous
    return df


def summarise_anomalies(df: pd.DataFrame):
    total_rows = len(df)
    anomaly_count = int((df["anomaly_label"] == -1).sum())
    anomaly_percentage = (anomaly_count / total_rows * 100) if total_rows > 0 else 0.0

    return {
        "total_rows": total_rows,
        "anomaly_count": anomaly_count,
        "anomaly_percentage": anomaly_percentage,
    }
