import os
import time
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Essential for server-side rendering
import matplotlib.pyplot as plt
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles

# Import your custom logic and constants
from src.models.model_1.pd_logic import engineer_features, get_explanations, TICKER_COL, DATE_COL

app = FastAPI()

# --- 1. DIRECTORY & PATH CONFIGURATION ---
API_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(API_DIR) 

STATIC_DIR = os.path.join(BASE_DIR, "static")
REPORTS_DIR = os.path.join(STATIC_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Mount static folder so images are accessible via URL
app.mount("/plots", StaticFiles(directory=REPORTS_DIR), name="plots")

# Build absolute paths to the models
MODEL_PATH = os.path.join(API_DIR, "..", "src", "models", "model_1", "isolation_forest_model.joblib")
SCALER_PATH = os.path.join(API_DIR, "..", "src", "models", "model_1", "robust_scaler.joblib")

# Load AI assets
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Run main.py first.")

MODEL = joblib.load(MODEL_PATH)
SCALER = joblib.load(SCALER_PATH)

# --- 2. HELPER FUNCTIONS ---

def generate_master_plot(df_feat, filename):
    """Generates a fraud map with vertical labels for the API response."""
    anomalies = df_feat[df_feat['anomaly_label'] == -1].copy()
    if anomalies.empty:
        return False

    plt.figure(figsize=(16, 9), dpi=150)
    plt.style.use('bmh')

    scatter = plt.scatter(
        pd.to_datetime(anomalies[DATE_COL]), 
        anomalies['gap_return'], 
        c=anomalies['anomaly_score'], 
        cmap='YlOrRd', 
        s=180, 
        edgecolors='black', 
        alpha=0.9,
        zorder=3
    )
    
    for i in range(len(anomalies)):
        plt.text(
            pd.to_datetime(anomalies[DATE_COL]).iloc[i], 
            anomalies['gap_return'].iloc[i] + 0.015, 
            str(anomalies[TICKER_COL].iloc[i]), 
            fontsize=10, fontweight='bold', ha='center', va='bottom', 
            rotation=90, zorder=4,
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1)
        )

    plt.colorbar(scatter, label='AI Confidence Score')
    plt.title("Detected Pump & Dump Events", fontsize=18)
    plt.xlabel("Date")
    plt.ylabel("Price Jump %")
    plt.tight_layout()
    
    save_path = os.path.join(REPORTS_DIR, filename)
    plt.savefig(save_path)
    plt.close()
    return True

# --- 3. API ENDPOINTS ---

@app.post("/detect")
async def detect_fraud(file: UploadFile = File(...)):
    # Load Data
    raw_df = pd.read_csv(file.file)
    total_rows = len(raw_df)
    total_companies_scanned = raw_df[TICKER_COL].nunique() if TICKER_COL in raw_df.columns else 0
    
    # Feature Engineering
    df_feat, feature_cols = engineer_features(raw_df)
    
    # Prediction
    X_input = df_feat[feature_cols]
    X_scaled = SCALER.transform(X_input) 
    scores = -MODEL.score_samples(X_scaled)
    df_feat["anomaly_score"] = scores
    
    # Strict Filter
    is_anomaly = (scores > 0.65) & \
                 (df_feat['gap_return'] > 0.15) & \
                 (df_feat['vol_surge_ratio'] > 5.0)
    
    df_feat["anomaly_label"] = 1
    df_feat.loc[is_anomaly, "anomaly_label"] = -1
    
    total_found = int(np.sum(is_anomaly))
    unique_tickers = df_feat.loc[is_anomaly, TICKER_COL].nunique() if total_found > 0 else 0

    # Generate Visualization
    report_filename = f"fraud_report_{int(time.time())}.png"
    image_created = generate_master_plot(df_feat, report_filename)
    
    # Formatting Results
    results = []
    if total_found > 0:
        fraud_indices = np.where(is_anomaly)[0]
        reasons = get_explanations(MODEL, X_scaled[fraud_indices], feature_cols)
        fraud_df = df_feat[is_anomaly].copy()
        
        for i, (_, row) in enumerate(fraud_df.iterrows()):
            results.append({
                "ticker": row[TICKER_COL],
                "date": str(row[DATE_COL]),
                "pump_intensity": f"{row['gap_return']*100:.1f}%",
                "anomaly_score": round(float(row["anomaly_score"]), 4),
                "volume_surge": f"{row['vol_surge_ratio']:.1f}x",
                "reason": reasons[i]
            })

    return {
        "status": "Success",
        "scan_summary": {
            "total_rows_processed": total_rows,
            "total_companies_scanned": total_companies_scanned,
            "frauds_detected": total_found,
            "unique_companies_flagged": unique_tickers
        },
        "detections": results,
        "report_url": f"/plots/{report_filename}" if image_created else None
    }