import pandas as pd
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
from sklearn.preprocessing import MinMaxScaler

def run_ai_anomaly_detection(file_path):
    # 1. LOAD DATA
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {file_path}")
        return
        
    df = pd.read_csv(file_path)
    print(f"✅ Data Loaded! Columns found: {list(df.columns)}")

    # 2. SELECT FEATURES (Safety Check)
    # We will look for common column names used in CSE data
    possible_features = ['Intraday_Return', 'Trade_Intensity_Ratio', 'Volume', 'Close']
    features = [f for f in possible_features if f in df.columns]
    
    if len(features) < 1:
        print("❌ Error: None of the required features were found in the CSV!")
        return
    
    print(f"📊 Using features for AI: {features}")

    fraud_alerts = []
    unique_symbols = df['Symbol'].unique()[:30] 
    
    for symbol in unique_symbols:
        data = df[df['Symbol'] == symbol][features].values
        if len(data) < 20: continue 
        
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(data)
        
        # Sequence creation
        n_steps = 5
        X = []
        for i in range(len(scaled_data) - n_steps + 1):
            X.append(scaled_data[i : (i + n_steps)])
        X_train = np.array(X)
        
        # Build Model
        model = Sequential([
            LSTM(32, activation='relu', input_shape=(n_steps, len(features)), return_sequences=False),
            RepeatVector(n_steps),
            LSTM(32, activation='relu', return_sequences=True),
            TimeDistributed(Dense(len(features)))
        ])
        model.compile(optimizer='adam', loss='mae')
        model.fit(X_train, X_train, epochs=10, batch_size=16, verbose=0)
        
        # Detect
        X_pred = model.predict(X_train, verbose=0)
        loss = np.mean(np.abs(X_pred - X_train), axis=(1, 2))
        threshold = np.percentile(loss, 95)
        
        anomalies = np.sum(loss > threshold)
        if anomalies > 0:
            print(f"🚨 {symbol}: Found {anomalies} suspicious patterns.")
            fraud_alerts.append({'Symbol': symbol, 'Alerts': anomalies})

    # Save results
    alert_df = pd.DataFrame(fraud_alerts)
    save_path = file_path.replace('.csv', '_ai_alerts.csv')
    alert_df.to_csv(save_path, index=False)
    print(f"🏁 Done! Alerts saved to: {save_path}")

if __name__ == "__main__":
    # MANUALLY SET THE PATH TO YOUR ACTUAL FILE LOCATION
    # This path matches exactly where you said your file is!
    input_path = r"C:\Reserch_campus\Research-Project\backend\src\models\model_2\data\processed\cse_standardized_features.csv"
    
    run_ai_anomaly_detection(input_path)