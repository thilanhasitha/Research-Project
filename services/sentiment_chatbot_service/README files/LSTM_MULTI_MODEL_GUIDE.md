# LSTM Multi-Model Training & Prediction Guide

## Overview

This guide explains how to train multiple LSTM models on different datasets and combine their predictions to respond to user queries through the Trading Sentiment Bot API.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Query                               │
│         "What's the stock forecast for next month?"         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend API (Port 8001)                         │
│                  /api/lstm/query                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         LSTM Service (Port 8002)                             │
│              Container: LSTM_model                           │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │           Model Ensemble System               │          │
│  │                                                │          │
│  │  Model 1   Model 2   Model 3   Model N       │          │
│  │  (Dataset  (Dataset  (Dataset  (Dataset       │          │
│  │   A)        B)        C)        N)            │          │
│  │    │         │         │         │             │          │
│  │    └─────────┴─────────┴─────────┘            │          │
│  │              │                                 │          │
│  │    ┌─────────▼────────────┐                   │          │
│  │    │  Ensemble Strategy   │                   │          │
│  │    │  - Weighted Average  │                   │          │
│  │    │  - Simple Average    │                   │          │
│  │    │  - Median           │                   │          │
│  │    │  - Best Model       │                   │          │
│  │    │  - Voting           │                   │          │
│  │    └──────────────────────┘                   │          │
│  └──────────────────────────────────────────────┘          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            User-Friendly Response                            │
│   "Based on analysis from 3 models, predicted value         │
│    is 125.50 with high confidence..."                       │
└─────────────────────────────────────────────────────────────┘
```

## Step 1: Prepare Your Datasets

Place your CSV datasets in the `data/processed` folder. Each dataset should have:

- **Date column**: Timestamp for each record
- **Feature columns**: Open, High, Low, Close, Volume
- **Clean data**: No missing values or outliers

Example datasets:
```
backend/lstm_stock_prediction/data/processed/
├── lstm_ready_data.csv
├── monthly_stock_prices_cleaned.csv
└── all_companies_parsed.csv
```

## Step 2: Train Multiple Models

Run the multi-model training script:

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Navigate to LSTM directory
cd backend\lstm_stock_prediction

# Train all models
python train_multi_models.py
```

This will:
1. Discover all CSV files in `data/processed/`
2. Train a separate LSTM model for each dataset
3. Evaluate each model and save metrics
4. Save models and scalers in `models/` directory
5. Generate `models/models_metadata.json` with all model information

### Output Files

After training:
```
models/
├── lstm_ready_data_model.h5
├── lstm_ready_data_scaler.pkl
├── monthly_stock_prices_cleaned_model.h5
├── monthly_stock_prices_cleaned_scaler.pkl
├── all_companies_parsed_model.h5
├── all_companies_parsed_scaler.pkl
└── models_metadata.json
```

### Training Configuration

To customize training for specific datasets, edit `train_multi_models.py`:

```python
from config.config import Config, ModelConfig, TrainingConfig

# Define custom configurations
custom_configs = {
    'lstm_ready_data': Config(
        model=ModelConfig(lstm_units=[64, 32], dropout_rate=0.3),
        training=TrainingConfig(epochs=100, batch_size=32)
    ),
    'monthly_stock_prices': Config(
        model=ModelConfig(lstm_units=[128, 64, 32]),
        training=TrainingConfig(epochs=150)
    )
}

# Train with custom configs
trainer.train_all_models(custom_configs=custom_configs)
```

## Step 3: Start the LSTM Docker Service

Build and start the LSTM prediction service:

```bash
# From project root
docker-compose up lstm-predictor --build -d
```

The service will:
- Load all trained models from `models/` directory
- Initialize the model ensemble
- Start the FastAPI server on port 8002

Check service health:
```bash
curl http://localhost:8002/health
```

## Step 4: Use the API

### A. Direct LSTM Service Endpoints

#### 1. Get Ensemble Info
```bash
GET http://localhost:8002/ensemble/info
```

Response:
```json
{
  "num_models": 3,
  "model_names": ["lstm_ready_data", "monthly_stock_prices_cleaned", "all_companies_parsed"],
  "model_weights": {
    "lstm_ready_data": 0.35,
    "monthly_stock_prices_cleaned": 0.40,
    "all_companies_parsed": 0.25
  },
  "model_metrics": {
    "lstm_ready_data": {
      "rmse": 2.45,
      "mae": 1.82,
      "r2": 0.89
    }
  }
}
```

#### 2. Ensemble Prediction
```bash
POST http://localhost:8002/predict/ensemble
```

Request:
```json
{
  "symbol": "STOCK.CSE",
  "data": [
    [100.5, 102.3, 99.8, 101.2, 1500000],
    [101.2, 103.5, 100.9, 102.8, 1600000],
    [102.8, 104.1, 102.0, 103.5, 1700000]
  ],
  "method": "weighted_average",
  "include_individual": true
}
```

Response:
```json
{
  "symbol": "STOCK.CSE",
  "ensemble_prediction": [104.2, 105.1],
  "confidence_intervals": [0.15, 0.18],
  "confidence_level": "high",
  "num_models": 3,
  "individual_models": {
    "lstm_ready_data": {
      "predictions": [104.1, 104.9],
      "weight": 0.35,
      "rmse": 2.45
    },
    "monthly_stock_prices_cleaned": {
      "predictions": [104.3, 105.3],
      "weight": 0.40,
      "rmse": 2.18
    },
    "all_companies_parsed": {
      "predictions": [104.0, 105.0],
      "weight": 0.25,
      "rmse": 3.12
    }
  },
  "recommendation": "The ensemble models predict a strong upward trend with high confidence.",
  "timestamp": "2026-02-28T10:30:00"
}
```

#### 3. Natural Language Query
```bash
POST http://localhost:8002/query/predict?query=What%20is%20the%20forecast%20for%20next%20month&symbol=STOCK.CSE
```

Response:
```json
{
  "answer": "Based on analysis from 3 trained models, the predicted value for STOCK.CSE is 104.20 with high confidence. The models show strong agreement on this prediction. The prediction indicates an upward trend (expected increase: +3.15%).",
  "predicted_value": 104.2,
  "confidence": "high",
  "confidence_score": 0.85,
  "num_models": 3,
  "model_agreement": 0.92,
  "status": "success",
  "timestamp": "2026-02-28T10:30:00"
}
```

### B. Backend API Integration (Recommended)

#### 1. Check LSTM Service Health
```bash
GET http://localhost:8001/api/lstm/health
```

#### 2. Get Available Models
```bash
GET http://localhost:8001/api/lstm/models
```

#### 3. Stock Prediction
```bash
POST http://localhost:8001/api/lstm/predict
```

Request:
```json
{
  "symbol": "STOCK.CSE",
  "historical_data": [
    [100.5, 102.3, 99.8, 101.2, 1500000],
    [101.2, 103.5, 100.9, 102.8, 1600000],
    [102.8, 104.1, 102.0, 103.5, 1700000]
  ],
  "method": "weighted_average",
  "include_details": true
}
```

#### 4. Natural Language Query (User-Facing)
```bash
POST http://localhost:8001/api/lstm/query
```

Request:
```json
{
  "query": "What will the stock price be next month?",
  "symbol": "STOCK.CSE",
  "historical_data": [
    [100.5, 102.3, 99.8, 101.2, 1500000],
    [101.2, 103.5, 100.9, 102.8, 1600000],
    [102.8, 104.1, 102.0, 103.5, 1700000]
  ],
  "context": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

## Ensemble Methods

### 1. Weighted Average (Recommended)
- Uses inverse RMSE as weights
- Better models have more influence
- Best for balanced predictions

```python
method = "weighted_average"
```

### 2. Simple Average
- Equal weight to all models
- Good when model performance is similar

```python
method = "average"
```

### 3. Median
- Robust to outliers
- Good when some models may be unreliable

```python
method = "median"
```

### 4. Best Model
- Uses only the best performing model
- Good when one model is clearly superior

```python
method = "best"
```

### 5. Voting
- Majority voting for trend direction
- Good for classification tasks

```python
method = "voting"
```

## How Predictions are Combined

The ensemble system combines predictions intelligently:

1. **Load All Models**: Each trained model is loaded with its scaler
2. **Generate Predictions**: All models predict on the same input
3. **Apply Ensemble Strategy**: Combine predictions using selected method
4. **Calculate Confidence**: Standard deviation across models indicates uncertainty
5. **Format Response**: Generate user-friendly explanation

### Example: Weighted Average

```
Model 1 (Weight: 0.35, RMSE: 2.45): Predicts 104.1
Model 2 (Weight: 0.40, RMSE: 2.18): Predicts 104.3
Model 3 (Weight: 0.25, RMSE: 3.12): Predicts 104.0

Ensemble = (104.1 × 0.35) + (104.3 × 0.40) + (104.0 × 0.25)
         = 36.435 + 41.72 + 26.0
         = 104.155 ≈ 104.2

Std Dev = 0.15 → High confidence
```

## User Query Flow

When a user asks: **"What's the stock forecast for next month?"**

1. **Frontend** → Sends query to backend API
2. **Backend** → Forwards to LSTM service `/query/predict`
3. **LSTM Service** → 
   - Processes historical data
   - Gets predictions from all models
   - Applies weighted average ensemble
   - Calculates confidence
4. **Response Generation** →
   - Formats prediction with confidence level
   - Adds recommendation
   - Provides model agreement score
5. **User Receives** → Natural language answer with prediction

## Integration Example: Chat Interface

```python
# In your chat service
async def handle_stock_prediction_query(user_query: str, symbol: str, historical_data: list):
    """Handle stock prediction queries from chat."""
    
    # Call LSTM service through backend API
    response = await httpx.post(
        "http://backend:8001/api/lstm/query",
        json={
            "query": user_query,
            "symbol": symbol,
            "historical_data": historical_data,
            "context": {
                "user_id": current_user.id,
                "session_id": session.id
            }
        }
    )
    
    result = response.json()
    
    # Display to user
    return {
        "message": result["answer"],
        "prediction": result["predicted_value"],
        "confidence": result["confidence"],
        "models_used": result["num_models"]
    }
```

## Monitoring & Metrics

### Check Service Status
```bash
GET http://localhost:8001/api/lstm/status
```

### Model Performance Comparison
```bash
GET http://localhost:8002/ensemble/models
```

Response shows metrics for each model:
```json
{
  "models": [
    {
      "name": "lstm_ready_data",
      "metrics": {
        "rmse": 2.45,
        "mae": 1.82,
        "r2": 0.89
      }
    }
  ]
}
```

## Best Practices

1. **Data Quality**: Ensure all datasets are properly cleaned and normalized
2. **Regular Retraining**: Retrain models periodically with new data
3. **Model Selection**: Remove poorly performing models from ensemble
4. **Confidence Thresholds**: Only show predictions with high confidence to users
5. **Fallback**: Have a single best model as fallback if ensemble fails
6. **Monitoring**: Track prediction accuracy over time

## Troubleshooting

### Models Not Loading
```bash
# Check if metadata exists
cat backend/lstm_stock_prediction/models/models_metadata.json

# Retrain if needed
python backend/lstm_stock_prediction/train_multi_models.py
```

### Service Unavailable
```bash
# Check container status
docker ps | grep LSTM_model

# View logs
docker logs LSTM_model

# Restart service
docker-compose restart lstm-predictor
```

### Poor Predictions
1. Check model metrics in metadata
2. Retrain with more data
3. Adjust model architecture
4. Use different ensemble method

## Example: Complete Workflow

```bash
# 1. Prepare datasets
cp your_data.csv backend/lstm_stock_prediction/data/processed/

# 2. Train models
cd backend/lstm_stock_prediction
python train_multi_models.py

# 3. Start services
cd ../..
docker-compose up -d

# 4. Test prediction
curl -X POST http://localhost:8001/api/lstm/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the stock forecast?",
    "symbol": "STOCK.CSE",
    "historical_data": [[100,102,99,101,1500000]]
  }'

# 5. View result
# User receives: "Based on analysis from 3 models, predicted value is 104.20..."
```

## Summary

✅ **Multi-Model Training**: Train separate models for each dataset
✅ **Ensemble Predictions**: Combine predictions intelligently
✅ **Confidence Scoring**: Provide uncertainty estimates
✅ **Natural Language**: User-friendly query interface
✅ **Docker Integration**: Seamless microservice architecture
✅ **Backend API**: Easy integration with existing systems

The system provides robust, reliable stock predictions by leveraging multiple models and presenting results in a user-friendly format suitable for chatbot responses.
