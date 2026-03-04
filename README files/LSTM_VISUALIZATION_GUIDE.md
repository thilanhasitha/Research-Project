# LSTM Prediction Visualizations & Results Guide

## Overview

The LSTM prediction API now automatically generates comprehensive visualizations and stores prediction results for every ensemble prediction made.

## What Gets Saved

When you make a prediction, the system automatically creates:

### 1. **Visualizations** (PNG images)
- **Full Ensemble Analysis** - Comprehensive dashboard with:
  - Main prediction plot with confidence bands
  - Individual model comparison chart
  - Model weights pie chart
  - Confidence levels bar chart
  - Summary statistics table

- **Individual Models Plot** - Focused comparison of each model's predictions

- **Trend Forecast** - Historical data + future predictions with trend analysis

### 2. **Data Files**
- **JSON** - Complete prediction data with all metadata
- **CSV** - Tabular format for easy analysis in Excel/Python

### 3. **HTML Report**
- Interactive report combining all visualizations
- Model performance metrics
- Professional format ready for sharing

## API Endpoints

### Make Prediction with Visualizations

```bash
POST /predict/ensemble
```

**Request:**
```json
{
  "symbol": "STOCK.CSE",
  "data": [[100,102,99,101,1500000], [101,103,100,102,1600000]],
  "method": "weighted_average",
  "include_individual": true
}
```

**Response:**
```json
{
  "symbol": "STOCK.CSE",
  "prediction_id": "20260228_143025_123456",
  "ensemble_prediction": [104.2],
  "confidence_level": "high",
  "visualizations": {
    "full": "/results/plots/STOCK.CSE_20260228_143025_123456_ensemble_full.png",
    "individual": "/results/plots/STOCK.CSE_20260228_143025_123456_individual_models.png",
    "trend": "/results/plots/STOCK.CSE_20260228_143025_123456_trend.png"
  },
  "data_files": {
    "json": "/results/data/STOCK.CSE_20260228_143025_123456_prediction.json",
    "csv": "/results/data/STOCK.CSE_20260228_143025_123456_prediction.csv"
  },
  "report": "/results/STOCK.CSE_20260228_143025_123456_report.html",
  "timestamp": "2026-02-28T14:30:25"
}
```

### List Saved Predictions

```bash
GET /predictions/history?limit=20
```

**Response:**
```json
{
  "predictions": [
    {
      "prediction_id": "20260228_143025_123456",
      "symbol": "STOCK.CSE",
      "timestamp": "2026-02-28T14:30:25",
      "ensemble_value": 104.2,
      "file": "data/STOCK.CSE_20260228_143025_123456_prediction.json"
    }
  ],
  "total": 1
}
```

### Get Specific Prediction

```bash
GET /predictions/{prediction_id}
```

Returns complete prediction data with all visualization links.

### View HTML Report

```bash
GET /predictions/{prediction_id}/report
```

Opens the interactive HTML report in your browser.

### Access Visualizations

All visualizations are served as static files:

```bash
# Full ensemble dashboard
GET /results/plots/{symbol}_{prediction_id}_ensemble_full.png

# Individual models comparison
GET /results/plots/{symbol}_{prediction_id}_individual_models.png

# Trend forecast
GET /results/plots/{symbol}_{prediction_id}_trend.png
```

### Delete Prediction

```bash
DELETE /predictions/{prediction_id}
```

Removes all files associated with a prediction (visualizations, data files, report).

### Get Storage Statistics

```bash
GET /results/stats
```

**Response:**
```json
{
  "predictions_saved": 15,
  "csv_files": 15,
  "visualizations": 45,
  "reports": 15,
  "total_size_mb": 12.5,
  "storage_location": "C:/path/to/results"
}
```

## Folder Structure

```
results/
├── plots/
│   ├── STOCK.CSE_20260228_143025_123456_ensemble_full.png
│   ├── STOCK.CSE_20260228_143025_123456_individual_models.png
│   └── STOCK.CSE_20260228_143025_123456_trend.png
├── data/
│   ├── STOCK.CSE_20260228_143025_123456_prediction.json
│   └── STOCK.CSE_20260228_143025_123456_prediction.csv
└── STOCK.CSE_20260228_143025_123456_report.html
```

## Using Visualizations in Your Application

### Frontend Integration

```javascript
// Make prediction
const response = await fetch('http://localhost:8002/predict/ensemble', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    symbol: 'STOCK.CSE',
    data: [[100,102,99,101,1500000]],
    method: 'weighted_average',
    include_individual: true
  })
});

const result = await response.json();

// Display visualizations
const fullChart = result.visualizations.full;
const trendChart = result.visualizations.trend;

// Show images
document.getElementById('chart').src = `http://localhost:8002${fullChart}`;

// Link to report
const reportUrl = `http://localhost:8002${result.report}`;
window.open(reportUrl, '_blank');

// Download CSV
const csvUrl = `http://localhost:8002${result.data_files.csv}`;
window.location.href = csvUrl;
```

### Python Integration

```python
import requests
import pandas as pd

# Make prediction
response = requests.post(
    'http://localhost:8002/predict/ensemble',
    json={
        'symbol': 'STOCK.CSE',
        'data': [[100,102,99,101,1500000]],
        'method': 'weighted_average',
        'include_individual': True
    }
)

result = response.json()

# Download and analyze CSV
csv_url = f"http://localhost:8002{result['data_files']['csv']}"
df = pd.read_csv(csv_url)
print(df)

# Save visualizations locally
import urllib.request

for viz_name, viz_path in result['visualizations'].items():
    url = f"http://localhost:8002{viz_path}"
    filename = f"prediction_{viz_name}.png"
    urllib.request.urlretrieve(url, filename)
    print(f"Saved {filename}")
```

## Visualization Features

### 1. Full Ensemble Dashboard

![Ensemble Dashboard Example](docs/ensemble_full_example.png)

**Includes:**
- **Main Plot**: Historical data → Ensemble prediction with confidence bands and individual model predictions (faded)
- **Model Comparison**: Horizontal bar chart showing each model's prediction vs ensemble
- **Weight Distribution**: Pie chart of model weights in the ensemble
- **Confidence Levels**: Bar chart showing confidence for each prediction step
- **Summary Table**: Key metrics and statistics

### 2. Individual Models Plot

**Features:**
- Shows each model's prediction as a separate line
- Weight value displayed in legend
- Ensemble prediction highlighted
- Easy to see model agreement/disagreement

### 3. Trend Forecast

**Features:**
- Combined view of historical and predicted prices
- Vertical separator marking prediction start
- Trend percentage calculation
- Clear visual of price direction

## Customization

### Change Save Directory

In [main.py](backend/lstm_stock_prediction/main.py):

```python
# Change default results directory
results_dir = Path("custom/path/to/results")
app.mount("/results", StaticFiles(directory="custom/path/to/results"), name="results")
```

### Adjust Plot DPI/Quality

In [prediction_visualizer.py](backend/lstm_stock_prediction/prediction_visualizer.py):

```python
# Change DPI for higher/lower resolution
plt.savefig(plot_path, dpi=300)  # Default: 300
# For web: 150 is usually sufficient
# For print: 300-600 recommended
```

### Custom Color Schemes

In [prediction_visualizer.py](backend/lstm_stock_prediction/prediction_visualizer.py):

```python
# Modify color constants
HISTORICAL_COLOR = '#2E86AB'  # Blue
PREDICTION_COLOR = '#A23B72'  # Purple
CONFIDENCE_COLOR_HIGH = '#27AE60'  # Green
CONFIDENCE_COLOR_LOW = '#E74C3C'  # Red
```

## Best Practices

1. **Regular Cleanup**: Delete old predictions periodically to save disk space
2. **Confidence Threshold**: Only save visualizations for predictions with confidence > 40%
3. **Batch Operations**: Use batch predict endpoint for multiple stocks
4. **Caching**: Cache frequently accessed visualizations
5. **Monitoring**: Track storage usage with `/results/stats`

## Storage Management

### Automatic Cleanup Script

```python
import requests
from datetime import datetime, timedelta

# Get all predictions
response = requests.get('http://localhost:8002/predictions/history?limit=100')
predictions = response.json()['predictions']

# Delete predictions older than 30 days
cutoff_date = datetime.now() - timedelta(days=30)

for pred in predictions:
    pred_date = datetime.fromisoformat(pred['timestamp'])
    if pred_date < cutoff_date:
        requests.delete(f"http://localhost:8002/predictions/{pred['prediction_id']}")
        print(f"Deleted old prediction: {pred['prediction_id']}")
```

### Disk Space Monitoring

```bash
# Check current storage usage
curl http://localhost:8002/results/stats

# Response shows total_size_mb
```

## Access from Backend API

The main backend (`localhost:8001`) can proxy these endpoints:

```bash
# Through main backend
POST http://localhost:8001/api/lstm/predict

# Returns same response with visualizations
# Frontend only needs to hit one API
```

## Docker Volume Mounting

In [docker-compose.yml](docker-compose.yml):

```yaml
lstm-predictor:
  volumes:
    - ./backend/lstm_stock_prediction/results:/app/results
```

This ensures results persist even if container restarts.

## Troubleshooting

### Visualizations Not Appearing

1. Check if matplotlib is installed with Agg backend
2. Verify `results/` directory has write permissions
3. Check logs: `docker logs LSTM_model`

### Large File Sizes

- Reduce DPI in visualizations
- Convert PNG to JPEG for smaller sizes
- Implement automatic cleanup for old predictions

### Static Files Not Serving

- Verify static files mounting in FastAPI
- Check file permissions
- Ensure paths are relative to results directory

## Example Use Cases

### 1. Daily Report Generation

```python
# Generate predictions for portfolio
stocks = ['STOCK1', 'STOCK2', 'STOCK3']

for stock in stocks:
    response = predict_with_visualizations(stock, historical_data[stock])
    report_url = response['report']
    email_report(report_url)  # Send to stakeholders
```

### 2. Model Performance Tracking

```python
# Analyze all saved predictions
predictions = get_all_predictions()

for pred in predictions:
    data = load_prediction_data(pred['prediction_id'])
    analyze_model_performance(data['individual_models'])
```

### 3. Interactive Dashboard

```javascript
// Real-time dashboard showing latest predictions
async function updateDashboard() {
    const history = await fetch('/predictions/history?limit=5');
    const predictions = await history.json();
    
    // Display latest visualizations
    predictions.forEach(pred => {
        displayChart(pred.prediction_id);
    });
}
```

## Summary

✅ **Automatic Visualization Generation** - Every prediction creates comprehensive charts
✅ **Multiple Formats** - PNG, CSV, JSON, HTML
✅ **Easy Access** - Static file serving via web API
✅ **Storage Management** - Track and clean up old predictions
✅ **Frontend Ready** - Direct image URLs for immediate display
✅ **Professional Reports** - HTML reports ready for sharing

All prediction results are automatically saved and can be accessed anytime through the API! 🎨📊
