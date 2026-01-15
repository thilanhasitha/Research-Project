import pandas as pd
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed, Input
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

def run_ai_anomaly_detection(file_path):
    # 1. LOAD DATA
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found")
        return
        
    df = pd.read_csv(file_path)
    
    # We use 'Intraday_Return' and 'Trade_Intensity_Ratio' 
    # These two together show if price moves and volume spikes happen 'mechanically'
    features = ['Intraday_Return', 'Trade_Intensity_Ratio']
    
    fraud_alerts = []
    unique_symbols = df['Symbol'].unique()[:30] # Start with 30 stocks for speed
    
    print(f"🧠 Training AI 'Brain' on {len(unique_symbols)} Sri Lankan Stocks...")

    for symbol in unique_symbols:
        # Filter data for one stock
        data = df[df['Symbol'] == symbol][features].values
        if len(data) < 40: continue # Need at least 40 days of history
        
        # A. SCALE DATA (0 to 1)
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(data)
        
        # B. CREATE SEQUENCES (The AI looks at 5-day windows)
        def create_sequences(values, time_steps=5):
            output = []
            for i in range(len(values) - time_steps + 1):
                output.append(values[i : (i + time_steps)])
            return np.array(output)
        
        X_train = create_sequences(scaled_data)
        
        # C. BUILD THE LSTM-AUTOENCODER
        # The 'Bottleneck' architecture forces the AI to learn the core pattern
        n_steps = X_train.shape[1]
        n_features = X_train.shape[2]
        
        model = Sequential([
            # Encoder: Squeezes the data
            LSTM(32, activation='relu', input_shape=(n_steps, n_features), return_sequences=False),
            RepeatVector(n_steps),
            # Decoder: Tries to reconstruct the original data
            LSTM(32, activation='relu', return_sequences=True),
            TimeDistributed(Dense(n_features))
        ])
        
        model.compile(optimizer='adam', loss='mae')
        
        # D. TRAIN THE AI
        # It trains on its own data to learn what 'Normal' looks like for THIS stock
        model.fit(X_train, X_train, epochs=30, batch_size=16, verbose=0)
        
        # E. CALCULATE RECONSTRUCTION ERROR
        X_pred = model.predict(X_train, verbose=0)
        # Loss = (Original Data - AI's Reconstruction)
        reconstruction_loss = np.mean(np.abs(X_pred - X_train), axis=(1, 2))
        
        # F. DETECT ANOMALIES
        # Threshold: Any error in the top 3% is a 'Robot Signature' alert
        threshold = np.percentile(reconstruction_loss, 97)
        is_anomaly = reconstruction_loss > threshold
        
        total_anomalies = np.sum(is_anomaly)
        if total_anomalies > 0:
            print(f"🚨 {symbol}: AI detected {total_anomalies} mechanical signatures.")
            fraud_alerts.append({
                'Symbol': symbol,
                'Anomaly_Count': total_anomalies,
                'Max_Anomaly_Score': round(np.max(reconstruction_loss), 4)
            })

    # 3. SAVE THE FINAL EVIDENCE
    alert_df = pd.DataFrame(fraud_alerts)
    output_dir = os.path.join(os.path.dirname(file_path))
    save_path = os.path.join(output_dir, 'ai_fraud_evidence.csv')
    alert_df.to_csv(save_path, index=False)
    
    print(f"\n✅ Phase 3 Complete. Fraud evidence saved to: {save_path}")
    return alert_df

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    processed_data = os.path.normpath(os.path.join(current_dir, '..', 'data', 'processed', 'cse_standardized_features.csv'))
    run_ai_anomaly_detection(processed_data)