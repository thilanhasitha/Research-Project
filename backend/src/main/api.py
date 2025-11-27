from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import pandas as pd
import joblib
import os
import uuid

from db.db import db  # <--- Import from your db.py

from models.data_preprocessing import engineer_features
from models.model import apply_model
from models.visualization import plot_price_with_anomalies, plot_anomaly_counts

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Load model/scaler once
MODEL_PATH = "../models/pumpdump_local_iforest_model.joblib"
SCALER_PATH = "../models/pumpdump_local_scaler.joblib"
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# Static file serving for charts
CHART_DIR = os.path.abspath("charts")
os.makedirs(CHART_DIR, exist_ok=True)
app.mount("/charts", StaticFiles(directory=CHART_DIR), name="charts")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        df = pd.read_csv(pd.compat.StringIO(contents.decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file format")

    df_feat, X_scaled, feature_cols, _ = engineer_features(df)
    X_scaled = scaler.transform(df_feat[feature_cols].values)
    result_df = apply_model(df_feat, model, X_scaled)

    # Generate unique IDs for chart files
    task_id = str(uuid.uuid4())
    price_chart_path = os.path.join(CHART_DIR, f"{task_id}_price_anomalies.png")
    count_chart_path = os.path.join(CHART_DIR, f"{task_id}_anomaly_counts.png")

    # Generate and save charts to file
    plot_price_with_anomalies(result_df)
    os.rename("pumpdump_local_price_anomalies.png", price_chart_path)
    plot_anomaly_counts(result_df)
    os.rename("pumpdump_local_anomaly_counts.png", count_chart_path)

    # Save results to MongoDB
    doc = {
        "task_id": task_id,
        "results": result_df[["Date", "Company", "Day Close", "anomaly_label", "anomaly_score"]].to_dict(orient="records"),
        "price_chart": f"/charts/{task_id}_price_anomalies.png",
        "count_chart": f"/charts/{task_id}_anomaly_counts.png"
    }
    await db.predictions.insert_one(doc)

    # Return prediction + chart URLs
    return {
        "task_id": task_id,
        "columns": list(result_df.columns),
        "data": doc["results"],
        "chart_urls": [doc["price_chart"], doc["count_chart"]]
    }

# Example endpoint to get a list of previous results (for making UI history page)
@app.get("/history")
async def history():
    cursor = db.predictions.find({}, {"_id": 0, "task_id": 1, "chart_urls": 1})
    tasks = await cursor.to_list(length=100)
    return tasks
