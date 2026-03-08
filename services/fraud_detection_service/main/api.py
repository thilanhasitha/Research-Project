import os
import time
import json
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
from fastapi.middleware.cors import CORSMiddleware
# Import Model 1 Logic
from src.models.model_1.pd_logic import engineer_features, get_explanations, TICKER_COL, DATE_COL
from src.db.db import db  # MongoDB client from db.py

app = FastAPI(title="Unified CSE Forensic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. DIRECTORY CONFIGURATION ---
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR  = os.path.join(BASE_DIR, "static")
REPORTS_DIR = os.path.join(STATIC_DIR, "reports")
REPORT2_DIR = os.path.join(STATIC_DIR, "report2")
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(REPORT2_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- 2. LOAD ALL ASSETS ---
# Model 1 Assets
M1_PATH = os.path.join(BASE_DIR, "..", "src", "models", "model_1", "isolation_forest_model.joblib")
S1_PATH = os.path.join(BASE_DIR, "..", "src", "models", "model_1", "robust_scaler.joblib")

# Model 2 Assets
M2_PATH = os.path.join(BASE_DIR, "..", "src", "models", "model_2", "app", "assets", "fraud_model_attention.h5")
S2_PATH = os.path.join(BASE_DIR, "..", "src", "models", "model_2", "app", "assets", "scaler.joblib")
T2_PATH = os.path.join(BASE_DIR, "..", "src", "models", "model_2", "app", "assets", "thresholds.json")

MODEL_1  = joblib.load(M1_PATH)
SCALER_1 = joblib.load(S1_PATH)
MODEL_2  = load_model(M2_PATH, compile=False)
SCALER_2 = joblib.load(S2_PATH)

# Load thresholds saved during training — fallback to percentile if file missing
if os.path.exists(T2_PATH):
    with open(T2_PATH) as f:
        THRESHOLDS = json.load(f)
else:
    THRESHOLDS = None

# UPDATED: 5 features and window=10 to match new improved model
M2_FEATURES  = ['Intraday_Return', 'Vol_Spike', 'Price_Impact',
                 'Log_Volatility', 'Trade_Density']
M2_WINDOW    = 10
M2_NUM_HEADS = 4   # must match num_heads used in model_trainer.py


# --- 3. HELPER FUNCTIONS ---

def sanitize_for_json(obj):
    """Replace NaN/Inf floats with None so JSON serialization doesn't crash."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    elif isinstance(obj, np.floating):
        val = float(obj)
        return None if (np.isnan(val) or np.isinf(val)) else val
    elif isinstance(obj, np.integer):
        return int(obj)
    return obj


def get_detailed_forensic_analysis(row, dtw_dist, threshold):
    evidence = []
    f_type, f_level, confidence = None, "LOW", 0

    # Logic 1: Pump and Dump
    if row['Vol_Spike'] > 2.0 and row['Intraday_Return'] > 0.03:
        f_type, f_level, confidence = "CRITICAL: PUMP & DUMP", "CRITICAL", 95
        evidence.append(f"Price surged {round(row['Intraday_Return']*100, 2)}% on extreme volume spike.")

    # Logic 2: Wash Trading
    elif row['Vol_Spike'] > 5.0 and abs(row['Intraday_Return']) < 0.0001:
        f_type, f_level, confidence = "WASH TRADING", "HIGH", 85
        evidence.append("Circular trading detected: High volume but zero price impact.")

    # Logic 3: Market Ramping
    elif abs(row['Price_Impact']) > 10.0:
        f_type, f_level, confidence = "MARKET RAMPING", "HIGH", 80
        evidence.append(f"Artificial price movement. Price Impact Score: {round(row['Price_Impact'], 2)}")

    # Logic 4: Bot Signature
   # Logic 4: Bot Signature — only flag if there's meaningful trading activity
    elif dtw_dist > threshold and row.get('Vol_Spike', 0) > 0.5 and row.get('trade_count', 0) > 5:
        f_type, f_level, confidence = "BOT SIGNATURE", "MEDIUM", 70
        evidence.append(f"Non-human rhythm (DTW: {round(dtw_dist, 3)})")

    if f_type:
        return f_type, f_level, " | ".join(evidence), f"{confidence}%"
    return None, None, None, None


def generate_master_plot(df_feat, filename):
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


def _compute_dtw(seq, pred):
    """Module-level helper so joblib can pickle it on all platforms."""
    dist, _ = fastdtw(seq, pred, dist=euclidean)
    return dist


# --- 4. ENDPOINTS ---

@app.post("/api/v1/detect/pump-dump")
async def detect_fraud(file: UploadFile = File(...)):
    raw_df = pd.read_csv(file.file)
    total_rows = len(raw_df)
    total_companies_scanned = raw_df[TICKER_COL].nunique() if TICKER_COL in raw_df.columns else 0

    df_feat, feature_cols = engineer_features(raw_df)

    X_input  = df_feat[feature_cols]
    X_scaled = SCALER_1.transform(X_input)
    scores   = -MODEL_1.score_samples(X_scaled)
    df_feat["anomaly_score"] = scores

    is_anomaly = (scores > 0.65) & \
                 (df_feat['gap_return'] > 0.15) & \
                 (df_feat['vol_surge_ratio'] > 5.0)

    df_feat["anomaly_label"] = 1
    df_feat.loc[is_anomaly, "anomaly_label"] = -1

    total_found    = int(np.sum(is_anomaly))
    unique_tickers = df_feat.loc[is_anomaly, TICKER_COL].nunique() if total_found > 0 else 0

    report_filename = f"fraud_report_{int(time.time())}.png"
    image_created   = generate_master_plot(df_feat, report_filename)

    results = []
    if total_found > 0:
        fraud_indices = np.where(is_anomaly)[0]
        reasons  = get_explanations(MODEL_1, X_scaled[fraud_indices], feature_cols)
        fraud_df = df_feat[is_anomaly].copy()

        for i, (_, row) in enumerate(fraud_df.iterrows()):
            results.append({
                "ticker":         row[TICKER_COL],
                "date":           str(row[DATE_COL]),
                "pump_intensity": f"{row['gap_return']*100:.1f}%",
                "anomaly_score":  round(float(row["anomaly_score"]), 4),
                "volume_surge":   f"{row['vol_surge_ratio']:.1f}x",
                "reason":         reasons[i]
            })

    history_entry = {
        "timestamp":    datetime.now(),
        "type":         "PUMP_DUMP",
        "scan_summary": {"total_rows": len(raw_df), "frauds_detected": total_found},
        "detections":   results,
        "report_url":   f"/static/reports/{report_filename}" if image_created else None
    }
    await db.pump_dump_history.insert_one(history_entry)

    return {
        "status": "Success",
        "scan_summary": {
            "total_rows_processed":     total_rows,
            "total_companies_scanned":  total_companies_scanned,
            "frauds_detected":          total_found,
            "unique_companies_flagged": unique_tickers
        },
        "detections": results,
        "report_url": f"/static/reports/{report_filename}" if image_created else None
    }


@app.post("/api/v1/detect/forensic-lstm")
async def detect_m2(file: UploadFile = File(...)):
    """Model 2: Attention-Augmented LSTM + DTW — 5 features, window=10"""
    df = pd.read_csv(file.file)

    # Validate required columns exist
    missing = [f for f in M2_FEATURES if f not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns in uploaded CSV: {missing}")

    total_rows = len(df)
    companies  = df['Symbol'].nunique()

    # Sort by company then date — matches training sequence creation
    df = df.sort_values(['Symbol', 'Date']).reset_index(drop=True)
    scaled_data = SCALER_2.transform(df[M2_FEATURES].values)

    # Build sequences per company (no cross-company contamination)
    # Uses numpy sliding_window_view for zero-copy slice — much faster than appending
    sequences       = []
    seq_row_indices = []
    for symbol, group in df.groupby('Symbol', sort=False):
        idxs     = group.index.to_numpy()
        grp_data = scaled_data[idxs]
        if len(idxs) < M2_WINDOW:
            continue
        windows = np.lib.stride_tricks.sliding_window_view(
            grp_data, window_shape=(M2_WINDOW, grp_data.shape[1])
        ).squeeze(axis=1)
        sequences.append(windows)
        seq_row_indices.extend(idxs[M2_WINDOW - 1:].tolist())
    X_reshaped = np.concatenate(sequences, axis=0) if sequences else np.empty((0, M2_WINDOW, len(M2_FEATURES)))

    # Inference — Model 2 returns [reconstruction, attention_weights]
    # batch_size=256 is ~8x faster than the default batch_size=32
    predictions, attn_weights = MODEL_2.predict(X_reshaped, batch_size=256, verbose=0)

    # DTW Scoring — parallelised across all CPU threads for a large speedup
    dtw_distances = joblib.Parallel(n_jobs=-1, prefer="threads")(
        joblib.delayed(_compute_dtw)(X_reshaped[i], predictions[i])
        for i in range(len(X_reshaped))
    )

    # Use 95% threshold — catches meaningful anomalies without being too strict
    strict_threshold = float(np.percentile(dtw_distances, 99))

    # Build Report — use seq_row_indices to get the correct row per sequence
    final_alerts = []
    for i in range(len(seq_row_indices)):
        row_data = df.iloc[seq_row_indices[i]].to_dict()
        f_type, f_level, f_ev, f_conf = get_detailed_forensic_analysis(
            row_data, dtw_distances[i], strict_threshold
        )

        if f_type:
            focus_day_idx = int(np.argmax(attn_weights[i].mean(axis=0).mean(axis=0)))
            row_data.update({
                "fraud_type":          f_type,
                "risk_level":          f_level,
                "forensic_evidence":   f_ev,
                "attention_focus_day": focus_day_idx + 1,
                "confidence_score":    f_conf,
                "dtw_score":           round(dtw_distances[i], 4)
            })
            final_alerts.append(sanitize_for_json(row_data))

    # Generate Chart
    timestamp      = datetime.now().strftime("%Y%m%d_%H%M%S")
    chart_filename = f"fraud_chart_{timestamp}.png"
    chart_path     = os.path.join(REPORT2_DIR, chart_filename)

    plt.figure(figsize=(12, 6))
    plt.plot(dtw_distances, label='Anomaly Score (DTW)', color='#1f77b4', alpha=0.7)
    plt.axhline(y=strict_threshold, color='red', linestyle='--', label='95% Fraud Threshold')

    anomalies_idx = [i for i, d in enumerate(dtw_distances) if d > strict_threshold]
    if anomalies_idx:
        plt.scatter(
            anomalies_idx,
            [dtw_distances[i] for i in anomalies_idx],
            color='red', s=30, label='Alert Points'
        )

    plt.title(f"Forensic Analysis Report - {timestamp}")
    plt.xlabel("Sequence Index")
    plt.ylabel("Neural Reconstruction Error")
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()

    # Save slim version to MongoDB to avoid 16MB BSON limit
    slim_alerts = [
        {
            "Symbol":              a.get("Symbol"),
            "Date":                str(a.get("Date")),
            "fraud_type":          a.get("fraud_type"),
            "risk_level":          a.get("risk_level"),
            "forensic_evidence":   a.get("forensic_evidence"),
            "attention_focus_day": a.get("attention_focus_day"),
            "confidence_score":    a.get("confidence_score"),
            "dtw_score":           a.get("dtw_score"),
        }
        for a in final_alerts
    ]
    history_entry = {
        "timestamp":           datetime.now(),
        "type":                "FORENSIC_LSTM",
        "scan_summary":        {"total_rows": total_rows, "high_risk_alerts": len(final_alerts)},
        "alerts":              slim_alerts,
        "visual_evidence_url": f"/static/report2/{chart_filename}"
    }
    await db.forensic_history.insert_one(history_entry)

    report_df = pd.DataFrame(final_alerts)
    if not report_df.empty:
        report_df = report_df.sort_values('dtw_score', ascending=False)
        summary = {
            "total_rows_scanned":     total_rows,
            "total_companies":        companies,
            "high_risk_alerts_found": len(report_df),
            "fraud_breakdown":        report_df['fraud_type'].value_counts().to_dict()
        }
    else:
        summary = {
            "total_rows_scanned":     total_rows,
            "total_companies":        companies,
            "high_risk_alerts_found": 0,
            "fraud_breakdown":        {}
        }

    return {
        "status":              "Success",
        "scan_summary":        summary,
        "alerts":              final_alerts,
        "visual_evidence_url": f"/static/report2/{chart_filename}"
    }


@app.get("/api/v1/history/pump-dump")
async def get_pd_history():
    cursor  = db.pump_dump_history.find({"type": "PUMP_DUMP"}).sort("timestamp", -1)
    history = await cursor.to_list(length=100)
    for item in history:
        item["_id"]       = str(item["_id"])
        item["timestamp"] = item["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    return {"status": "Success", "data": history}


@app.get("/api/v1/history/forensic")
async def get_forensic_history():
    cursor  = db.forensic_history.find({"type": "FORENSIC_LSTM"}).sort("timestamp", -1)
    history = await cursor.to_list(length=100)
    for item in history:
        item["_id"]       = str(item["_id"])
        item["timestamp"] = item["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        item["alerts"]    = sanitize_for_json(item.get("alerts", []))
    return {"status": "Success", "data": history}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)