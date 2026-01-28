import os
import time
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from tensorflow.keras.models import load_model
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from datetime import datetime
import uvicorn
from fastapi.middleware.cors import CORSMiddleware # Added CORS
# Import Model 1 Logic
from src.models.model_1.pd_logic import engineer_features, get_explanations, TICKER_COL, DATE_COL

app = FastAPI(title="Unified CSE Forensic API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development; replace with ["http://localhost:5173"] later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- 1. DIRECTORY CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
REPORTS_DIR = os.path.join(STATIC_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)
REPORT2_DIR = os.path.join(STATIC_DIR, "report2")
os.makedirs(REPORT2_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- 2. LOAD ALL ASSETS ---
# Model 1 Assets
M1_PATH = os.path.join(BASE_DIR, "..", "src", "models", "model_1", "isolation_forest_model.joblib")
S1_PATH = os.path.join(BASE_DIR, "..", "src", "models", "model_1", "robust_scaler.joblib")


# Model 2 Assets
M2_PATH = os.path.join(BASE_DIR, "..", "src", "models", "model_2", "app","assets","fraud_model_attention.h5")
S2_PATH = os.path.join(BASE_DIR, "..", "src", "models", "model_2", "app","assets","scaler.joblib")

MODEL_1 = joblib.load(M1_PATH)
SCALER_1 = joblib.load(S1_PATH)
MODEL_2 = load_model(M2_PATH, compile=False)
SCALER_2 = joblib.load(S2_PATH)

# --- 3. HELPER FUNCTIONS ---

def get_detailed_forensic_analysis(row, dtw_dist, threshold):
    evidence = []
    f_type, f_level, confidence = None, "LOW", 0
    
    # Logic 1: Pump and Dump
    if row['Vol_Spike'] > 2.0 and row['Intraday_Return'] > 0.03:
        f_type, f_level, confidence = "CRITICAL: PUMP & DUMP", "CRITICAL", 95
        evidence.append(f"Price surged {round(row['Intraday_Return']*100,2)}% on extreme volume spike.")
    
    # Logic 2: Wash Trading
    elif row['Vol_Spike'] > 5.0 and abs(row['Intraday_Return']) < 0.0001:
        f_type, f_level, confidence = "WASH TRADING", "HIGH", 85
        evidence.append("Circular trading detected: High volume but zero price impact.")
    
    # Logic 3: Market Ramping
    elif abs(row['Price_Impact']) > 10.0:
        f_type = "MARKET RAMPING"
        f_level = "HIGH"
        evidence.append(f"Artificial price movement. Price Impact Score: {round(row['Price_Impact'], 2)}")
        confidence = 80

    elif dtw_dist > threshold:
        f_type, f_level, confidence = "BOT SIGNATURE", "MEDIUM", 70
        evidence.append(f"Non-human rhythm (DTW: {round(dtw_dist, 3)})")

    return f_type, f_level, " | ".join(evidence), f"{confidence}%" if f_type else (None, None, None, None)

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

# --- 4. ENDPOINTS ---

@app.post("/api/v1/detect/pump-dump")
async def detect_fraud(file: UploadFile = File(...)):
    # Load Data
    raw_df = pd.read_csv(file.file)
    total_rows = len(raw_df)
    total_companies_scanned = raw_df[TICKER_COL].nunique() if TICKER_COL in raw_df.columns else 0
    
    # Feature Engineering
    df_feat, feature_cols = engineer_features(raw_df)
    
    # Prediction
    X_input = df_feat[feature_cols]
    X_scaled = SCALER_1.transform(X_input) 
    scores = -MODEL_1.score_samples(X_scaled)
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
        reasons = get_explanations(MODEL_1, X_scaled[fraud_indices], feature_cols)
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
        "report_url": f"/static/reports/{report_filename}" if image_created else None
    }

@app.post("/api/v1/detect/forensic-lstm")
async def detect_m2(file: UploadFile = File(...)):
    """Model 2: Attention-Augmented LSTM + DTW"""
    df = pd.read_csv(file.file)
    features = ['Intraday_Return', 'Vol_Spike', 'Price_Impact']
    scaled_data = SCALER_2.transform(df[features])
    
    total_rows = len(df)
    companies = df['Symbol'].nunique()

    window_size = 5
    sequences = [scaled_data[i : i + window_size] for i in range(len(scaled_data) - window_size + 1)]
    X_reshaped = np.array(sequences)

    # Inference (Model 2 returns [reconstruction, attention_weights])
    predictions, attn_weights = MODEL_2.predict(X_reshaped)

    # 3. DTW Scoring
    dtw_distances = []
    for i in range(len(X_reshaped)):
            dist, _ = fastdtw(X_reshaped[i], predictions[i], dist=euclidean)
            dtw_distances.append(dist)

    strict_threshold = np.percentile(dtw_distances, 99.9)

    # 4. Building the Report
    aligned_df = df.iloc[window_size - 1 :].copy()
    final_alerts = []
    
    for i in range(len(aligned_df)):
        row_data = aligned_df.iloc[i].to_dict()
        f_type, f_level, f_ev, f_conf = get_detailed_forensic_analysis(row_data, dtw_distances[i], strict_threshold)
        
        if f_type:
            # Extract which day the Attention layer focused on (Max weight in the 5-day window)
            focus_day_idx = np.argmax(attn_weights[i].mean(axis=0).mean(axis=0)) 
            
            row_data.update({
                "fraud_type": f_type,
                "risk_level": f_level,
                "forensic_evidence": f_ev,
                "attention_focus_day": int(focus_day_idx + 1),
                "confidence_score": f_conf,
                "dtw_score": round(dtw_distances[i], 4)
            })
            final_alerts.append(row_data)

    # 5. GENERATE AND SAVE CHART FIGURE
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chart_filename = f"fraud_chart_{timestamp}.png"
    chart_path = os.path.join(REPORT2_DIR, chart_filename)

    plt.figure(figsize=(12, 6))
    plt.plot(dtw_distances, label='Anomaly Score (DTW)', color='#1f77b4', alpha=0.7)
    plt.axhline(y=strict_threshold, color='red', linestyle='--', label='99.9% Fraud Threshold')
        
        # Highlight high-risk points
    anomalies_idx = [i for i, d in enumerate(dtw_distances) if d > strict_threshold]
    if anomalies_idx:
            plt.scatter(anomalies_idx, [dtw_distances[i] for i in anomalies_idx], color='red', s=30, label='Alert Points')

    plt.title(f"Forensic Analysis Report - {timestamp}")
    plt.xlabel("Sequence Index")
    plt.ylabel("Neural Reconstruction Error")
    plt.legend()
    plt.grid(True, alpha=0.2)
        
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()

        # 6. RETURN JSON WITH LINK TO IMAGE
    report_df = pd.DataFrame(final_alerts)
    if not report_df.empty:
            report_df = report_df.sort_values('dtw_score', ascending=False)
            
            summary = {
                "total_rows_scanned": total_rows,
                "total_companies": companies,
                "high_risk_alerts_found": len(report_df),
                "fraud_breakdown": report_df['fraud_type'].value_counts().to_dict()
            }

            return {
            "status": "Success",
            "scan_summary": summary,
            "alerts": final_alerts,
            "visual_evidence_url": f"/static/report2/{chart_filename}"
        }

if __name__ == "__main__":
  
    uvicorn.run(app, host="0.0.0.0", port=8003)