from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import pandas as pd
import joblib
import os
import uuid

from src.db.db import db  # <--- Import from your db.py 

from src.models.config import DATA_PATH,DATE_COL,TICKER_COL, PREV_CLOSE_COL, DAY_CLOSE_COL, CHANGE_PCT_COL, TURNOVER_COL

from src.models.data_preprocessing import engineer_features
from src.models.model import apply_model
from src.models.visualization import plot_price_with_anomalies, plot_anomaly_counts

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Load model/scaler once
MODEL_PATH = "src/models/pumpdump_local_iforest_model.joblib"
SCALER_PATH = "src/models/pumpdump_local_scaler.joblib"
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# Static file serving for charts
CHART_DIR = os.path.abspath("charts")
os.makedirs(CHART_DIR, exist_ok=True)
app.mount("/charts", StaticFiles(directory=CHART_DIR), name="charts")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Load CSV (comma-separated)
    df = pd.read_csv(file.file)

    # Clean numeric columns
    numeric_cols = ["Prev Close", "Day Close", "Change (%)", "Change (Rs.)", "Turnover"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "")
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.fillna(0)

    print("DEBUG Columns:", df.columns.tolist())

    # PROCESS FEATURES
    df_feat, X_scaled, feature_cols, _ = engineer_features(df)
    X_scaled = scaler.transform(df_feat[feature_cols].values)
    result_df = apply_model(df_feat, model, X_scaled)

    # ----- DETECT ANOMALIES -----
    anomalies = result_df[result_df["anomaly_label"] == -1]
    anomaly_records = anomalies.to_dict(orient="records")

    # create task ID
    task_id = str(uuid.uuid4())

    # Save charts
    price_chart = os.path.join(CHART_DIR, f"{task_id}_price_anomalies.png")
    count_chart = os.path.join(CHART_DIR, f"{task_id}_anomaly_counts.png")
    plot_price_with_anomalies(result_df)
    os.rename("pumpdump_local_price_anomalies.png", price_chart)
    plot_anomaly_counts(result_df)
    os.rename("pumpdump_local_anomaly_counts.png", count_chart)

    # ----- SAVE PREDICTION SUMMARY -----
    prediction_doc = {
        "task_id": task_id,
        "results": result_df.to_dict(orient="records"),
        "price_chart": f"/charts/{task_id}_price_anomalies.png",
        "count_chart": f"/charts/{task_id}_anomaly_counts.png",
        "anomaly_count": len(anomaly_records)
    }
    await db.predictions.insert_one(prediction_doc)

    # ----- SAVE ANOMALIES ONLY -----
    await db.anomalies.insert_one({
        "task_id": task_id,
        "count": len(anomaly_records),
        "records": anomaly_records
    })

    # ---- GRAPH DATA PREPARATION ----

    # Price chart raw data
    price_chart_data = result_df[[
        DATE_COL, 
        DAY_CLOSE_COL, 
        "anomaly_label", 
        "anomaly_score"
    ]].to_dict(orient="records")

    # Anomaly count chart data
    count_chart_data = {
        "normal_count": int((result_df["anomaly_label"] == 1).sum()),
        "anomaly_count": int((result_df["anomaly_label"] == -1).sum())
    }

    # ----- STORE GRAPH DATA -----
    await db.graph_price_data.insert_one({
        "task_id": task_id,
        "data": price_chart_data
    })

    await db.graph_count_data.insert_one({
        "task_id": task_id,
        "data": count_chart_data
    })


    # API response to frontend
    return {
        "task_id": task_id,
        "columns": list(result_df.columns),
        "total_rows": len(result_df),
        "anomaly_count": len(anomaly_records),
        "anomalies": anomaly_records,
        "chart_urls": [
            prediction_doc["price_chart"],
            prediction_doc["count_chart"]
        ]
    }

# Example endpoint to get a list of previous results (for making UI history page)
@app.get("/history")
async def history():
    cursor = db.predictions.find({}, {"_id": 0, "task_id": 1, "chart_urls": 1})
    tasks = await cursor.to_list(length=100)
    return tasks
