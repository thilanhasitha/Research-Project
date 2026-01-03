import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from .config import RANDOM_STATE, N_ESTIMATORS, CONTAMINATION_FRACTION

def train_isolation_forest(X_scaled):
    model = IsolationForest(
        n_estimators=N_ESTIMATORS,
        contamination="auto", 
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_scaled)
    return model

def apply_model(df: pd.DataFrame, model, X_scaled):
    df = df.copy()
    # Higher score = more anomalous
    df["anomaly_score"] = -model.score_samples(X_scaled) 
    
    # Calculate threshold based on top X% of outliers
    threshold = np.percentile(df["anomaly_score"], 100 * (1 - CONTAMINATION_FRACTION))
    
    # LOGIC: Must be a statistical outlier AND have a price increase > 5%
    # This filters out "Dumps" (crashes) or neutral glitches.
    mask = (df["anomaly_score"] >= threshold) & (df["change_pct"] > 0.05)
    
    df["anomaly_label"] = 1 # Normal
    df.loc[mask, "anomaly_label"] = -1 # Fraud Candidate
    
    print(f"[INFO] Applied Dynamic Threshold: {threshold:.4f}")
    return df

def summarise_anomalies(df: pd.DataFrame):
    total = len(df)
    anom_count = int((df["anomaly_label"] == -1).sum())
    return {
        "total_rows": total,
        "anomaly_count": anom_count,
        "anomaly_percentage": (anom_count / total * 100) if total > 0 else 0
    }