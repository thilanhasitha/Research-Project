# LSTM Stock Price Prediction Model

This guide explains how to train and use the LSTM model for stock price prediction using monthly stock market data.

## Overview

The LSTM (Long Short-Term Memory) model is designed to predict future stock prices based on historical monthly data. The model uses a sliding window approach with a lookback period of 12 months to forecast the next month's price.

## Files

- **`train_lstm_stock_model.py`** - Main training script
- **`predict_stock_prices.py`** - Prediction/inference script
- **Data Input** - `backend/data/raw/34Monthly Highest,Lowest & Closing Share Prices.xls`
- **Model Output** - `backend/data/proceed/lstm_stock_model.h5`
- **Results** - `backend/data/proceed/training_results.json`
- **Plots** - `backend/data/proceed/training_plots.png`

## Setup

### 1. Install Dependencies

First, install the required machine learning libraries:

```bash
pip install -r backend/requirements.txt
```

Key ML libraries installed:
- TensorFlow (LSTM model)
- Scikit-learn (data preprocessing)
- Matplotlib (visualization)
- Openpyxl (Excel file reading)

### 2. Prepare Your Data

Ensure your monthly stock price data is in the correct location:
```
backend/data/raw/34Monthly Highest,Lowest & Closing Share Prices.xls
```

The script expects columns such as:
- Date/Month/Year column
- High, Low, Close prices (or similar numeric columns)

## Training the Model

### Basic Usage

Run the training script:

```bash
python backend/train_lstm_stock_model.py
```

### Configuration

You can modify hyperparameters at the top of `train_lstm_stock_model.py`:

```python
# Hyperparameters
LOOKBACK_PERIOD = 12      # Number of months to look back
EPOCHS = 100              # Training epochs
BATCH_SIZE = 32           # Batch size
LSTM_UNITS = 50           # LSTM layer units
DROPOUT_RATE = 0.2        # Dropout rate for regularization
LEARNING_RATE = 0.001     # Learning rate
TEST_SIZE = 0.2           # Test set size (20%)
VALIDATION_SPLIT = 0.2    # Validation split (20%)
```

### What Happens During Training

1. **Data Loading**: Reads the Excel file and displays dataset info
2. **Preprocessing**: 
   - Handles missing values
   - Sorts by date
   - Normalizes data (Min-Max scaling to 0-1 range)
3. **Sequence Creation**: Creates sliding windows of 12 months
4. **Train/Test Split**: 80% training, 20% testing
5. **Model Building**: 2-layer LSTM with dropout
6. **Training**: Uses early stopping to prevent overfitting
7. **Evaluation**: Calculates RMSE, MAE, MAPE metrics
8. **Visualization**: Generates training plots

### Output Files

After training, you'll get:

- **`lstm_stock_model.h5`** - Trained model weights
- **`scaler_params.json`** - Normalization parameters (needed for predictions)
- **`training_results.json`** - Performance metrics
- **`training_plots.png`** - 4 visualization plots:
  - Training/validation loss curve
  - Training predictions vs actual
  - Test predictions vs actual
  - Prediction error distribution

## Making Predictions

### Basic Prediction

Run the prediction script:

```bash
python backend/predict_stock_prices.py
```

This will:
1. Load the trained model
2. Load recent stock prices
3. Predict the next month's price
4. Predict the next 6 months
5. Provide confidence intervals

### Using the Predictor Programmatically

```python
from predict_stock_prices import StockPricePredictor

# Initialize
predictor = StockPricePredictor(
    model_path="backend/data/proceed/lstm_stock_model.h5",
    scaler_path="backend/data/proceed/scaler_params.json",
    lookback_period=12
)

# Load model and scaler
predictor.load_model()
predictor.load_scaler()

# Your recent 12 months of prices
recent_prices = [100, 105, 102, 108, 112, 110, 115, 118, 120, 122, 119, 125]

# Predict next month
next_price = predictor.predict_next_price(recent_prices)
print(f"Next month prediction: ${next_price:.2f}")

# Predict next 6 months
future_prices = predictor.predict_multiple_steps(recent_prices, n_steps=6)
print("Next 6 months:", future_prices)

# Get confidence intervals
confidence = predictor.predict_with_confidence(recent_prices)
print(f"95% CI: [{confidence['lower_95']:.2f}, {confidence['upper_95']:.2f}]")
```

## Model Architecture

```
Layer (type)                Output Shape              Param #   
=================================================================
LSTM (1st layer)           (None, 12, 50)            10,400    
Dropout                    (None, 12, 50)            0         
LSTM (2nd layer)           (None, 50)                20,200    
Dropout                    (None, 50)                0         
Dense                      (None, 25)                1,275     
Dense (output)             (None, 1)                 26        
=================================================================
Total params: 31,901
```

## Performance Metrics

The model reports several metrics:

- **RMSE** (Root Mean Square Error): Average prediction error in price units
- **MAE** (Mean Absolute Error): Average absolute difference
- **MAPE** (Mean Absolute Percentage Error): Error as a percentage
- **Loss**: Training loss value

Example output:
```
Test RMSE: 2.45
Train RMSE: 1.89
Test MAPE: 3.21%
Train MAPE: 2.15%
```

## Tips for Better Performance

### 1. Data Quality
- Ensure no missing dates
- Handle outliers appropriately
- Use consistent data sources

### 2. Hyperparameter Tuning
- Increase `LSTM_UNITS` (50, 100, 128) for more complex patterns
- Adjust `LOOKBACK_PERIOD` (6, 12, 24) based on seasonality
- Increase `EPOCHS` if loss is still decreasing
- Adjust `DROPOUT_RATE` (0.1 to 0.5) to prevent overfitting

### 3. Feature Engineering
- Add more features (volume, technical indicators)
- Include external factors (economic indicators)
- Normalize by market index

### 4. Model Improvements
- Try bidirectional LSTM
- Add attention mechanisms
- Ensemble multiple models
- Use GRU instead of LSTM

## Troubleshooting

### Issue: Model Underfitting (High Loss)
**Solutions:**
- Increase model complexity (more LSTM units)
- Increase training epochs
- Reduce dropout rate
- Add more features

### Issue: Model Overfitting (Train loss << Test loss)
**Solutions:**
- Increase dropout rate
- Add L2 regularization
- Reduce model complexity
- Get more training data
- Use early stopping (already implemented)

### Issue: Poor Predictions
**Solutions:**
- Check data quality (missing values, outliers)
- Verify date ordering
- Try different lookback periods
- Normalize data differently (StandardScaler)
- Check if trend is too volatile

### Issue: ValueError during prediction
**Error:** "Need at least 12 data points"
**Solution:** Ensure you provide at least `LOOKBACK_PERIOD` recent prices

## Integration with Project

To integrate this model with your existing RAG chatbot:

1. **Create API Endpoint** in `backend/app/routes/`:

```python
# stock_prediction_routes.py
from fastapi import APIRouter
from predict_stock_prices import StockPricePredictor

router = APIRouter()
predictor = StockPricePredictor(...)
predictor.load_model()
predictor.load_scaler()

@router.post("/predict-stock")
async def predict_stock(recent_prices: list[float]):
    prediction = predictor.predict_next_price(recent_prices)
    return {"predicted_price": prediction}
```

2. **Add to MongoDB** - Store predictions with timestamps
3. **Connect to LLM** - Let users ask "What's the predicted stock price?"
4. **Create Dashboard** - Visualize predictions in frontend

## Next Steps

1. ✅ Train initial model
2. ✅ Evaluate performance metrics
3. ⬜ Fine-tune hyperparameters
4. ⬜ Add more features (if available)
5. ⬜ Create API endpoints
6. ⬜ Integrate with chatbot
7. ⬜ Deploy to production
8. ⬜ Set up automated retraining

## References

- [Understanding LSTM Networks](http://colah.github.io/posts/2015-08-Understanding-LSTMs/)
- [TensorFlow Documentation](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM)
- [Time Series Forecasting](https://www.tensorflow.org/tutorials/structured_data/time_series)

---

**Created:** February 27, 2026  
**Author:** Research Project Team  
**Branch:** feature-Thilan-model-Training
