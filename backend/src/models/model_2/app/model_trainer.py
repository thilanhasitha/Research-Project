import pandas as pd
import numpy as np
import joblib
import os
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import (LSTM, Dense, RepeatVector, TimeDistributed, 
                                     Input, MultiHeadAttention, LayerNormalization, Add)
from tensorflow.keras.models import Model

# 1. LOAD & SCALE
# Using the same features you defined
df = pd.read_csv('C:/Reserch_campus/Research-Project/backend/src/models/model_2/data/processed/cse_standardized_features.csv')
features_list = ['Intraday_Return', 'Vol_Spike', 'Price_Impact']
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df[features_list])

# 2. SAVE SCALER
joblib.dump(scaler, 'scaler.joblib')

# 3. CREATE SEQUENCES
def create_sequences(data, window=5):
    X = []
    for i in range(len(data) - window + 1):
        X.append(data[i:i+window])
    return np.array(X)

X_train = create_sequences(scaled_data)

# 4. UPDATED ARCHITECTURE: ATTENTION-AUGMENTED LSTM AUTOENCODER
def build_attention_autoencoder(window=5, n_features=3):
    # Input
    inputs = Input(shape=(window, n_features))

    # --- ENCODER ---
    # We must set return_sequences=True so the Attention layer can see the whole history
    encoder_lstm = LSTM(64, activation='relu', return_sequences=True)(inputs)
    
    # Self-Attention Layer (The Novel Part)
    # This allows the model to weigh which of the 5 days are most important
    attention_out, attention_weights = MultiHeadAttention(
        num_heads=2, key_dim=64, name="attention_layer"
    )(encoder_lstm, encoder_lstm, return_attention_scores=True)
    
    # Residual Connection & Normalization (Standard in Transformers)
    x = Add()([encoder_lstm, attention_out])
    x = LayerNormalization()(x)
    
    # Bottleneck (Reduce to a single vector)
    bottleneck = LSTM(32, activation='relu', return_sequences=False)(x)

    # --- DECODER ---
    x = RepeatVector(window)(bottleneck)
    x = LSTM(64, activation='relu', return_sequences=True)(x)
    
    # Final Output Reconstruction
    outputs = TimeDistributed(Dense(n_features))(x)

    # Define Model
    # We include attention_weights in outputs so we can extract them during prediction
    model = Model(inputs=inputs, outputs=[outputs, attention_weights])
    model.compile(optimizer='adam', loss='mse')
    
    return model

model = build_attention_autoencoder(window=5, n_features=3)

# 5. TRAIN
print("Training Attention-Augmented Model...")
# Note: We pass X_train twice because it's an autoencoder (input == target)
# We ignore the second output (attention_weights) during training loss calculation
model.fit(X_train, [X_train, np.zeros((len(X_train), 2, 5, 5))], epochs=50, batch_size=32)

# 6. SAVE MODEL
model.save('fraud_model_attention.h5')
print("Model Saved successfully with Attention Layer!")