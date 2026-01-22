import os
import io
import matplotlib
matplotlib.use('Agg')  # Required for server-side rendering
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify, url_for
from tensorflow.keras.models import load_model
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from datetime import datetime

app = Flask(__name__)

# Ensure static folder exists for saving images
if not os.path.exists('static'):
    os.makedirs('static')

# 1. LOAD ASSETS
MODEL = load_model('fraud_model.h5', compile=False)
SCALER = joblib.load('scaler.joblib')

def get_detailed_fraud_analysis(row, dtw_dist, threshold):
    """
    Forensic Engine: Identifies specific market crimes.
    """
    evidence = []
    confidence = 0
    f_type = None
    f_level = "LOW"

    # Logic 1: Pump and Dump
    if row['Vol_Spike'] > 2.0 and row['Intraday_Return'] > 0.03:
        f_type = "CRITICAL: PUMP & DUMP"
        f_level = "CRITICAL"
        evidence.append(f"Price surged {round(row['Intraday_Return']*100,2)}% on extreme volume spike.")
        confidence = 95
    
    # Logic 2: Wash Trading
    elif row['Vol_Spike'] > 5.0 and abs(row['Intraday_Return']) < 0.0001:
        f_type = "WASH TRADING"
        f_level = "HIGH"
        evidence.append("Circular trading detected: High volume but zero price impact.")
        confidence = 85

    # Logic 3: Market Ramping
    elif abs(row['Price_Impact']) > 10.0:
        f_type = "MARKET RAMPING"
        f_level = "HIGH"
        evidence.append(f"Artificial price movement. Price Impact Score: {round(row['Price_Impact'], 2)}")
        confidence = 80

    # Logic 4: Bot Signature
    elif dtw_dist > threshold:
        f_type = "BOT SIGNATURE"
        f_level = "MEDIUM"
        evidence.append(f"Non-human trading rhythm detected (DTW Score: {round(dtw_dist, 3)})")
        confidence = 70

    if f_type:
        return f_type, f_level, " | ".join(evidence), f"{confidence}%"
    return None, None, None, None

@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['file']
        df = pd.read_csv(file)
        
        # stats for summary
        total_rows = len(df)
        companies = df['Symbol'].nunique()

        # 1. Preprocessing
        features = ['Intraday_Return', 'Vol_Spike', 'Price_Impact']
        scaled_data = SCALER.transform(df[features])
        
        window_size = 5
        sequences = [scaled_data[i : i + window_size] for i in range(len(scaled_data) - window_size + 1)]
        X_reshaped = np.array(sequences)

        # 2. AI Inference
        predictions = MODEL.predict(X_reshaped)

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
            f_type, f_level, f_ev, f_conf = get_detailed_fraud_analysis(row_data, dtw_distances[i], strict_threshold)
            
            if f_type:
                row_data.update({
                    "fraud_type": f_type,
                    "risk_level": f_level,
                    "forensic_evidence": f_ev,
                    "confidence_score": f_conf,
                    "dtw_score": round(dtw_distances[i], 4)
                })
                final_alerts.append(row_data)

        # 5. GENERATE AND SAVE CHART FIGURE
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"fraud_chart_{timestamp}.png"
        chart_path = os.path.join('static', chart_filename)

        

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

            return jsonify({
                "scan_summary": summary,
                "alerts": report_df.to_dict(orient='records'),
                "visual_evidence_url": f"http://127.0.0.1:5005/static/{chart_filename}"
            })
        else:
            return jsonify({
                "message": "No critical fraud detected.",
                "visual_evidence_url": f"http://127.0.0.1:5005/static/{chart_filename}"
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005, debug=False)