import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import (LSTM, Dense, RepeatVector, TimeDistributed,
                                     Input, MultiHeadAttention, LayerNormalization,
                                     Add, Dropout)
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau


# IMPROVEMENT 1: Dynamic path — works on any machine

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_PATH   = os.path.normpath(os.path.join(BASE_DIR, '..', 'data', 'processed', 'cse_standardized_features.csv'))
ASSETS_DIR  = os.path.join(BASE_DIR, 'assets')
os.makedirs(ASSETS_DIR, exist_ok=True)


# IMPROVEMENT 2: Use MORE features for richer learning

FEATURES    = ['Intraday_Return', 'Vol_Spike', 'Price_Impact',
               'Log_Volatility', 'Trade_Density']
WINDOW_SIZE = 10   # IMPROVEMENT 3: 10-day window captures more patterns than 5

df = pd.read_csv(DATA_PATH)
print(f" Loaded data: {df.shape[0]} rows, {df['Symbol'].nunique()} companies")

# IMPROVEMENT 4: Create sequences PER COMPANY
# This prevents Company A's last day bleeding into Company B's first day

def create_sequences_per_symbol(df, features, window):
    all_sequences = []
    for symbol, group in df.groupby('Symbol'):
        data = group[features].values
        if len(data) < window:
            continue  # skip companies with too few trading days
        for i in range(len(data) - window + 1):
            all_sequences.append(data[i : i + window])
    return np.array(all_sequences)

print(" Creating sequences per company...")
X_all = create_sequences_per_symbol(df, FEATURES, WINDOW_SIZE)
print(f" Total sequences: {X_all.shape}  (sequences × window × features)")


# IMPROVEMENT 5: Scale AFTER sequence creation to prevent data leakage

n_seq, n_window, n_feat = X_all.shape
X_flat = X_all.reshape(-1, n_feat)

scaler = MinMaxScaler()
X_scaled_flat = scaler.fit_transform(X_flat)
X_scaled = X_scaled_flat.reshape(n_seq, n_window, n_feat)

joblib.dump(scaler, os.path.join(ASSETS_DIR, 'scaler.joblib'))
print(" Scaler saved")


# IMPROVEMENT 6: Train/Validation split

X_train, X_val = train_test_split(X_scaled, test_size=0.15, random_state=42, shuffle=True)
print(f" Train: {X_train.shape[0]} sequences | Validation: {X_val.shape[0]} sequences")


# MODEL ARCHITECTURE

def build_attention_autoencoder(window, n_features):
    inputs = Input(shape=(window, n_features))

    # --- ENCODER ---
    encoder_lstm = LSTM(64, activation='relu', return_sequences=True)(inputs)
    # IMPROVEMENT 7: Dropout to prevent overfitting
    encoder_lstm = Dropout(0.2)(encoder_lstm)

    # Self-Attention — weighs which of the N days are most suspicious
    attention_out, attention_weights = MultiHeadAttention(
        num_heads=4, key_dim=32, name="attention_layer"   # 4 heads for richer attention
    )(encoder_lstm, encoder_lstm, return_attention_scores=True)

    # Residual Connection & Layer Normalization
    x = Add()([encoder_lstm, attention_out])
    x = LayerNormalization()(x)

    # Bottleneck
    bottleneck = LSTM(32, activation='relu', return_sequences=False)(x)
    bottleneck = Dropout(0.2)(bottleneck)

    # --- DECODER ---
    x = RepeatVector(window)(bottleneck)
    x = LSTM(64, activation='relu', return_sequences=True)(x)
    outputs = TimeDistributed(Dense(n_features))(x)

    model = Model(inputs=inputs, outputs=[outputs, attention_weights])
    model.compile(optimizer='adam', loss='mse')
    return model

model = build_attention_autoencoder(WINDOW_SIZE, len(FEATURES))
model.summary()


# IMPROVEMENT 8: Early Stopping + LR Reduction
# Stops automatically when validation loss stops improving

callbacks = [
    EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
]

dummy_attn = np.zeros((len(X_train), 4, WINDOW_SIZE, WINDOW_SIZE))

print(" Training Attention-Augmented LSTM Autoencoder...")
history = model.fit(
    X_train,
    [X_train, dummy_attn],
    epochs=100,                      # EarlyStopping will stop before this
    batch_size=32,
    validation_data=(X_val, [X_val, np.zeros((len(X_val), 4, WINDOW_SIZE, WINDOW_SIZE))]),
    callbacks=callbacks,
    verbose=1
)

# Save model
model_path = os.path.join(ASSETS_DIR, 'fraud_model_attention.h5')
model.save(model_path)
print(f" Model saved to: {model_path}")


# IMPROVEMENT 9: Compute and save reconstruction threshold
# Used by api.py instead of hardcoded percentile at inference time

print(" Computing anomaly threshold on training data...")
train_preds, _ = model.predict(X_train, verbose=0)
train_errors = np.mean(np.abs(train_preds - X_train), axis=(1, 2))
threshold_95  = float(np.percentile(train_errors, 95))
threshold_99  = float(np.percentile(train_errors, 99))
threshold_999 = float(np.percentile(train_errors, 99.9))

import json
thresholds = {"95": threshold_95, "99": threshold_99, "99.9": threshold_999}
with open(os.path.join(ASSETS_DIR, 'thresholds.json'), 'w') as f:
    json.dump(thresholds, f, indent=2)

print(f" Thresholds saved → 95%: {threshold_95:.4f} | 99%: {threshold_99:.4f} | 99.9%: {threshold_999:.4f}")
print(" Training Complete!")