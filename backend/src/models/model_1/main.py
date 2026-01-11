import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
from pd_logic import load_and_clean, engineer_features, DATE_COL, TICKER_COL

# Configuration
from config import DATA_PATH, OUT_PREFIX, CONTAMINATION_FRACTION, N_ESTIMATORS, RANDOM_STATE

def save_master_fraud_map(df_feat):
    anomalies = df_feat[df_feat['anomaly_label'] == -1].copy()
    if anomalies.empty: return

    plt.figure(figsize=(16, 9))
    plt.style.use('bmh')
    
    scatter = plt.scatter(anomalies[DATE_COL], anomalies['gap_return'], 
                          c=anomalies['anomaly_score'], cmap='YlOrRd', 
                          s=150, edgecolors='black', alpha=0.8)
    
    for i in range(len(anomalies)):
        plt.text(anomalies[DATE_COL].iloc[i], anomalies['gap_return'].iloc[i] + 0.015, 
                 anomalies[TICKER_COL].iloc[i], fontsize=9, fontweight='bold', rotation=90)

    plt.colorbar(scatter, label='AI Confidence Score')
    plt.title("Master Fraud Map: Detected Pump Events (No Look-Ahead)", fontsize=16)
    plt.xlabel("Date")
    plt.ylabel("Price Jump %")
    plt.tight_layout()
    plt.savefig(f"{OUT_PREFIX}_master_report.png")
    plt.close()

def main():
    print("--- Training Pump & Dump Detection Model ---")
    
    # 1. Load and Process
    df = load_and_clean(DATA_PATH)
    df_feat, feat_cols = engineer_features(df)
    
    # 2. Scaling (Crucial for Isolation Forest)
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(df_feat[feat_cols])
    
    # 3. Train Model
    model = IsolationForest(n_estimators=N_ESTIMATORS, 
                            contamination=CONTAMINATION_FRACTION, 
                            random_state=RANDOM_STATE)
    model.fit(X_scaled)
    
    # 4. Save Assets for the API
    joblib.dump(model, "isolation_forest_model.joblib")
    joblib.dump(scaler, "robust_scaler.joblib")
    
    # 5. Detection Logic (Labeling)
    df_feat["anomaly_score"] = -model.score_samples(X_scaled)
    threshold = np.percentile(df_feat["anomaly_score"], 100 * (1 - CONTAMINATION_FRACTION))
    
    # Rules: AI thinks it's weird AND significant price jump
    mask = (df_feat["anomaly_score"] >= threshold) & (df_feat["gap_return"] > 0.10)
    df_feat["anomaly_label"] = 1
    df_feat.loc[mask, "anomaly_label"] = -1
    
    # 6. Export Results
    save_master_fraud_map(df_feat)
    df_feat[df_feat['anomaly_label'] == -1].to_csv("all_fraud_cases.csv", index=False)
    print(f"✓ Training Complete. Assets saved.")

if __name__ == "__main__":
    main()