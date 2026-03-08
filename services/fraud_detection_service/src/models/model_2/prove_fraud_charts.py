import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed

def prove_fraud_with_labels(file_path, target_symbol):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    stock_data = df[df['Symbol'] == target_symbol].sort_values('Date').reset_index(drop=True)
    
    if len(stock_data) < 20:
        print(f" Not enough data for {target_symbol}")
        return

    # 1. Prepare Features
    features = ['Intraday_Return', 'Vol_Spike', 'Price_Impact']
    data = stock_data[features].values
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)

    # 2. Sequence Creation
    n_steps = 5
    X = [scaled_data[i:(i + n_steps)] for i in range(len(scaled_data) - n_steps + 1)]
    X = np.array(X)

    # 3. AI Brain (Autoencoder)
    model = Sequential([
        LSTM(32, activation='relu', input_shape=(n_steps, len(features)), return_sequences=False),
        RepeatVector(n_steps),
        LSTM(32, activation='relu', return_sequences=True),
        TimeDistributed(Dense(len(features)))
    ])
    model.compile(optimizer='adam', loss='mae')
    model.fit(X, X, epochs=20, batch_size=16, verbose=0)

    # 4. Identify Fraud Types
    X_pred = model.predict(X)
    error = np.mean(np.abs(X_pred - X), axis=(1, 2))
    threshold = np.percentile(error, 95)
    
    dates = stock_data['Date'].iloc[n_steps-1:].reset_index(drop=True)
    fraud_indices = np.where(error > threshold)[0]

    # --- NEW: THE DETECTIVE LOGIC ---
    print(f"\n--- 🕵️ FORENSIC REPORT FOR {target_symbol} ---")
    for idx in fraud_indices:
        actual_row = stock_data.iloc[idx + n_steps - 1]
        fraud_type = "Pattern Anomaly (Bot Signature)"
        
        # Identification Logic
        if actual_row['Vol_Spike'] > 2:
            fraud_type = "POSSIBLE PUMP & DUMP (Artificial Volume)"
        elif actual_row['Price_Impact'] > 2:
            fraud_type = "POSSIBLE MARKET RAMPING (Price Manipulation)"
        
        print(f"Date: {actual_row['Date'].date()} | Type: {fraud_type} | AI Error: {round(error[idx], 4)}")

    # 5. Visual Chart
    plt.figure(figsize=(14, 7))
    plt.plot(dates, error, label='AI Reconstruction Error', color='blue', alpha=0.6)
    plt.axhline(y=threshold, color='red', linestyle='--', label='Fraud Threshold')
    
    # Label the points on the chart
    for idx in fraud_indices:
        plt.scatter(dates.iloc[idx], error[idx], color='red', s=100)
        plt.annotate("FRAUD DETECTED", (dates.iloc[idx], error[idx]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='red', weight='bold')

    plt.title(f"DETAILED FRAUD ANALYSIS: {target_symbol}", fontsize=14)
    plt.ylabel("AI Reconstruction Error", fontsize=12)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    input_csv = r"C:\Reserch_campus\Research-Project\backend\src\models\model_2\data\processed\cse_standardized_features.csv"
    prove_fraud_with_labels(input_csv, target_symbol='HNB')