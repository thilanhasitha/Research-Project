import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed

# 1. LOAD & SCALE (The Fix for High Loss)
df = pd.read_csv('../data/processed/cse_standardized_features.csv')
features = ['Intraday_Return', 'Vol_Spike', 'Price_Impact']
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df[features])

# 2. SAVE SCALER IMMEDIATELY (For Frontend use later)
joblib.dump(scaler, 'scaler.joblib')

# 3. CREATE SEQUENCES
def create_sequences(data, window=5):
    X = []
    for i in range(len(data) - window):
        X.append(data[i:i+window])
    return np.array(X)

X_train = create_sequences(scaled_data)

# 4. MODEL ARCHITECTURE
model = Sequential([
    LSTM(64, activation='relu', input_shape=(5, 3), return_sequences=False),
    RepeatVector(5),
    LSTM(64, activation='relu', return_sequences=True),
    TimeDistributed(Dense(3))
])

# Use 'adam' optimizer and 'mse' loss
model.compile(optimizer='adam', loss='mse')

# 5. TRAIN
print(" Training starting...")
model.fit(X_train, X_train, epochs=50, batch_size=32)

# 6. SAVE MODEL
model.save('fraud_model.h5')
print(" Model Saved successfully!")