"""
LSTM Stock Prediction API
=========================
FastAPI application for serving LSTM stock predictions with ensemble support.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import numpy as np
import pandas as pd
from pathlib import Path
from tensorflow import keras
import logging
from datetime import datetime

from src.data_loader import StockDataLoader
from src.data_preprocessor import StockDataPreprocessor
from utils.helpers import load_scaler
from utils.logger import setup_logger
from ensemble import ModelEnsemble, PredictionAggregator
from prediction_visualizer import PredictionVisualizer

# Setup logging
logger = setup_logger(name='lstm_api', log_dir='logs')

app = FastAPI(
    title="LSTM Stock Prediction API",
    description="API for stock price predictions using LSTM models",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and scaler
model = None
scaler = None
model_loaded = False
ensemble = None
ensemble_loaded = False
visualizer = None

# Request/Response Models
class PredictionRequest(BaseModel):
    symbol: str
    data: List[List[float]]  # Historical data as list of feature vectors
    sequence_length: Optional[int] = 12
    n_future_steps: Optional[int] = 1

class EnsemblePredictionRequest(BaseModel):
    symbol: str
    data: List[List[float]]
    method: Optional[str] = "weighted_average"  # average, weighted_average, median, best, voting
    include_individual: Optional[bool] = True

class PredictionResponse(BaseModel):
    symbol: str
    predictions: List[float]
    timestamp: str
    model_name: str

class EnsemblePredictionResponse(BaseModel):
    symbol: str
    ensemble_prediction: List[float]
    confidence_intervals: List[float]
    confidence_level: str
    num_models: int
    individual_models: Optional[Dict] = None
    recommendation: str
    timestamp: str
    visualizations: Optional[Dict[str, str]] = None
    data_files: Optional[Dict[str, str]] = None
    prediction_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: str

class ModelInfo(BaseModel):
    model_path: str
    model_loaded: bool
    input_shape: Optional[List[int]] = None
    output_shape: Optional[List[int]] = None


# Mount static files for serving visualizations
results_dir = Path("results")
results_dir.mkdir(exist_ok=True)
app.mount("/results", StaticFiles(directory="results"), name="results")


def load_model_and_scaler(model_path: str, scaler_path: str):
    """Load the trained model and scaler."""
    global model, scaler, model_loaded
    
    try:
        logger.info(f"Loading model from {model_path}")
        model = keras.models.load_model(model_path)
        
        logger.info(f"Loading scaler from {scaler_path}")
        scaler = load_scaler(scaler_path)
        
        model_loaded = True
        logger.info("Model and scaler loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        model_loaded = False
        return False, visualizer
    
    # Initialize visualizer
    visualizer = PredictionVisualizer(results_dir='results')
    logger.info("Prediction visualizer initialized")


@app.on_event("startup")
async def startup_event():
    """Load models on startup."""
    global ensemble, ensemble_loaded
    
    # Try to load ensemble models
    try:
        metadata_path = Path("models/models_metadata.json")
        if metadata_path.exists():
            ensemble = ModelEnsemble()
            ensemble.load_models()
            ensemble_loaded = True
            logger.info("Ensemble models loaded successfully")
        else:
            logger.warning("Ensemble metadata not found. Run train_multi_models.py first.")
    except Exception as e:
        logger.error(f"Failed to load ensemble: {str(e)}")
        ensemble_loaded = False
    
    # Fallback: Try to load single model
    model_path = Path("models/lstm_model.h5")
    scaler_path = Path("models/scaler.pkl")
    
    if model_path.exists() and scaler_path.exists():
        load_model_and_scaler(str(model_path), str(scaler_path))
    else:
        logger.warning("Single model not found. Please train a model first.")


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return {
        "status": "running",
        "model_loaded": model_loaded or ensemble_loaded,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    status = "healthy"
    if not model_loaded and not ensemble_loaded:
        status = "no_models_loaded"
    
    return {
        "status": status,
        "model_loaded": model_loaded or ensemble_loaded,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/model/info", response_model=ModelInfo)
async def get_model_info():
    """Get information about the loaded model."""
    if not model_loaded or model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_path": "models/lstm_model.h5",
        "model_loaded": model_loaded,
        "input_shape": list(model.input_shape),
        "output_shape": list(model.output_shape)
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make predictions using the loaded LSTM model.
    
    Args:
        request: PredictionRequest containing symbol and historical data
        
    Returns:
        PredictionResponse with predictions
    """
    if not model_loaded or model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        logger.info(f"Making prediction for symbol: {request.symbol}")
        
        # Convert input data to numpy array
        data = np.array(request.data)
        
        # Ensure data has correct shape
        if len(data.shape) == 2:
            # Reshape to (1, sequence_length, n_features)
            data = data.reshape(1, data.shape[0], data.shape[1])
        
        # Make prediction
        predictions = model.predict(data, verbose=0)
        
        # Convert predictions to list
        pred_list = predictions.flatten().tolist()
        
        logger.info(f"Prediction successful for {request.symbol}: {pred_list}")
        
        return {
            "symbol": request.symbol,
            "predictions": pred_list,
            "timestamp": datetime.now().isoformat(),
            "model_name": "LSTM"
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch")
async def predict_batch(requests: List[PredictionRequest]):
    """
    Make batch predictions for multiple symbols.
    
    Args:
        requests: List of PredictionRequest objects
        
    Returns:
        List of PredictionResponse objects
    """
    if not model_loaded or model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    results = []
    for req in requests:
        try:
            result = await predict(req)
            results.append(result)
        except Exception as e:
            logger.error(f"Error in batch prediction for {req.symbol}: {str(e)}")
            results.append({
                "symbol": req.symbol,
                "predictions": [],
                "timestamp": datetime.now().isoformat(),
                "model_name": "LSTM",
                "error": str(e)
            })
    
    return results


@app.post("/model/load")
async def load_model_endpoint(model_path: str, scaler_path: str):
    """
    Load or reload the model and scaler.
    
    Args:
        model_path: Path to the model file
        scaler_path: Path to the scaler file
    """
    success = load_model_and_scaler(model_path, scaler_path)
    
    if success:
        return {
            "status": "success",
            "message": "Model and scaler loaded successfully",
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to load model and scaler")


@app.post("/predict/ensemble", response_model=EnsemblePredictionResponse)
async def predict_ensemble(request: EnsemblePredictionRequest):
    """
    Make ensemble predictions using multiple models.
    
    Args:
        request: EnsemblePredictionRequest with data and ensemble method
        
    Returns:
        EnsemblePredictionResponse with combined predictions
    """
    if not ensemble_loaded or ensemble is None:
        raise HTTPException(
            status_code=503, 
            detail="Ensemble not loaded. Run train_multi_models.py to train models."
        )
    
    try:
        logger.info(f"Making ensemble prediction for {request.symbol} using {request.method}")
        
        # Convert input data to numpy array
        data = np.array(request.data)
        
        # Ensure data has correct shape
        if len(data.shape) == 2:
            data = data.reshape(1, data.shape[0], data.shape[1])
        
        # Get ensemble predictions with confidence
        predictions, confidence, all_preds = ensemble.predict_with_confidence(
            data, 
            method=request.method
        )
        
        # Get ensemble info
        ensemble_info = ensemble.get_ensemble_info()
        
        # Format response
        aggregator = PredictionAggregator()
        formatted_response = aggregator.format_prediction_response(
            predictions=predictions,
            confidence=confidence,
            model_predictions=all_preds if request.include_individual else {},
            ensemble_info=ensemble_info,
            symbol=request.symbol
        )
        
        formatted_response['timestamp'] = datetime.now().isoformat()
        
        if not request.include_individual:
            formatted_response['individual_models'] = None
        
        # Generate visualizations if visualizer is available
        if visualizer:
            try:
                prediction_id = visualizer.generate_prediction_id()
                formatted_response['prediction_id'] = prediction_id
                
                logger.info(f"Generating visualizations for prediction {prediction_id}")
                
                # Generate plots
                plot_paths = visualizer.plot_ensemble_predictions(
                    symbol=request.symbol,
                    historical_data=data,
                    ensemble_prediction=formatted_response['ensemble_prediction'],
                    individual_predictions=all_preds if request.include_individual else {},
                    confidence_intervals=formatted_response['confidence_intervals'],
                    save_id=prediction_id
                )
                
                # Make paths accessible via web
                formatted_response['visualizations'] = {
                    key: f"/results/{value}" for key, value in plot_paths.items()
                }
                
                # Save prediction data
                data_path = visualizer.save_prediction_data(
                    symbol=request.symbol,
                    ensemble_prediction=formatted_response['ensemble_prediction'],
                    individual_predictions=all_preds if request.include_individual else {},
                    confidence_intervals=formatted_response['confidence_intervals'],
                    metadata={
                        'method': request.method,
                        'confidence_level': formatted_response['confidence_level'],
                        'num_models': formatted_response['num_models']
                    },
                    save_id=prediction_id
                )
                
                formatted_response['data_files'] = {
                    'json': f"/results/{data_path}",
                    'csv': f"/results/{data_path.replace('.json', '.csv')}"
                }
                
                # Generate HTML report
                report_path = visualizer.create_summary_report(
                    symbol=request.symbol,
                    prediction_data=formatted_response,
                    plots=plot_paths,
                    save_id=prediction_id
                )
                
                formatted_response['report'] = f"/results/{report_path}"
                
                logger.info(f"Visualizations and report generated successfully: {prediction_id}")
                
            except Exception as viz_error:
                logger.error(f"Visualization error: {str(viz_error)}")
                # Continue even if visualization fails
                formatted_response['visualizations'] = None
                formatted_response['data_files'] = None
        
        logger.info(f"Ensemble prediction successful: {formatted_response['ensemble_prediction']}")
        
        return formatted_response
        
    except Exception as e:
        logger.error(f"Ensemble prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ensemble prediction failed: {str(e)}")


@app.get("/ensemble/info")
async def get_ensemble_info():
    """Get information about the ensemble models."""
    if not ensemble_loaded or ensemble is None:
        raise HTTPException(status_code=503, detail="Ensemble not loaded")
    
    info = ensemble.get_ensemble_info()
    info['timestamp'] = datetime.now().isoformat()
    
    return info


@app.get("/ensemble/models")
async def list_ensemble_models():
    """List all available models in the ensemble."""
    if not ensemble_loaded or ensemble is None:
        raise HTTPException(status_code=503, detail="Ensemble not loaded")
    
    models_info = []
    for model_name, metadata in ensemble.metadata.items():
        models_info.append({
            'name': model_name,
            'dataset': metadata['dataset'],
            'metrics': metadata['metrics'],
            'features': metadata['feature_columns']
        })
    
    return {
        'models': models_info,
        'total': len(models_info),
        'timestamp': datetime.now().isoformat()
    }


@app.post("/query/predict")
async def query_based_prediction(
    query: str = Query(..., description="Natural language query about stock prediction"),
    symbol: str = Query("STOCK", description="Stock symbol"),
    data: List[List[float]] = None,
    method: str = Query("weighted_average", description="Ensemble method")
):
    """
    Answer user queries with ensemble predictions.
    
    This endpoint accepts natural language queries and returns predictions
    with explanations suitable for end-user consumption.
    
    Args:
        query: User's question (e.g., "What's the forecast for next month?")
        symbol: Stock symbol
        data: Historical data
        method: Ensemble method
        
    Returns:
        User-friendly response with predictions and explanation
    """
    if not ensemble_loaded or ensemble is None:
        return {
            "answer": "I apologize, but the prediction models are not currently loaded. Please train the models first using train_multi_models.py",
            "status": "error"
        }
    
    if data is None:
        return {
            "answer": f"To predict the stock price for {symbol}, please provide historical price data.",
            "status": "missing_data"
        }
    
    try:
        # Convert data
        data_array = np.array(data)
        if len(data_array.shape) == 2:
            data_array = data_array.reshape(1, data_array.shape[0], data_array.shape[1])
        
        # Get predictions
        predictions, confidence, all_preds = ensemble.predict_with_confidence(
            data_array, 
            method=method
        )
        
        # Format user-friendly response
        pred_value = float(predictions.flatten()[0])
        conf_value = float(confidence.flatten()[0])
        
        # Determine confidence level
        if conf_value < 0.1:
            conf_text = "high confidence"
        elif conf_value < 0.3:
            conf_text = "moderate confidence"
        else:
            conf_text = "low confidence"
        
        # Generate natural language answer
        answer = f"Based on analysis from {len(all_preds)} trained models, "
        answer += f"the predicted value for {symbol} is {pred_value:.2f} with {conf_text}. "
        
        # Add model agreement info
        pred_values = [float(p.flatten()[0]) for p in all_preds.values()]
        agreement = 1.0 - (np.std(pred_values) / (np.mean(pred_values) + 1e-10))
        
        if agreement > 0.8:
            answer += "The models show strong agreement on this prediction. "
        elif agreement > 0.5:
            answer += "The models show moderate agreement on this prediction. "
        else:
            answer += "The models show some variation in their predictions. "
        
        # Add interpretation
        if len(data) > 0:
            recent_price = float(data[-1][3])  # Assuming close price is at index 3
            change_pct = ((pred_value - recent_price) / recent_price) * 100
            
            if abs(change_pct) < 2:
                answer += f"The prediction suggests relatively stable prices (change: {change_pct:+.2f}%)."
            elif change_pct > 0:
                answer += f"The prediction indicates an upward trend (expected increase: {change_pct:+.2f}%)."
            else:
                answer += f"The prediction indicates a downward trend (expected decrease: {change_pct:+.2f}%)."
        
        return {
            "answer": answer,
            "predicted_value": pred_value,
            "confidence": conf_text,
            "confidence_score": float(1.0 - conf_value),
            "num_models": len(all_preds),
            "model_agreement": float(agreement),
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Query prediction error: {str(e)}")
        return {
            "answer": f"I encountered an error while making the prediction: {str(e)}",
            "status": "error"
        }


@app.get("/predictions/history")
async def list_saved_predictions(limit: int = Query(20, ge=1, le=100)):
    """
    List recently saved predictions.
    
    Args:
        limit: Maximum number of predictions to return
        
    Returns:
        List of saved predictions with metadata
    """
    try:
        data_dir = Path("results/data")
        
        if not data_dir.exists():
            return {"predictions": [], "total": 0}
        
        # Find all JSON prediction files
        json_files = sorted(
            data_dir.glob("*_prediction.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]
        
        predictions = []
        for json_file in json_files:
            try:
                import json
                with open(json_file, 'r') as f:
                    pred_data = json.load(f)
                    predictions.append({
                        'prediction_id': pred_data.get('prediction_id'),
                        'symbol': pred_data.get('symbol'),
                        'timestamp': pred_data.get('timestamp'),
                        'ensemble_value': pred_data.get('ensemble_prediction', [None])[0],
                        'file': str(json_file.relative_to(Path("results")))
                    })
            except Exception as e:
                logger.error(f"Error reading {json_file}: {str(e)}")
                continue
        
        return {
            "predictions": predictions,
            "total": len(predictions)
        }
        
    except Exception as e:
        logger.error(f"Error listing predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predictions/{prediction_id}")
async def get_prediction(prediction_id: str):
    """
    Retrieve a specific saved prediction.
    
    Args:
        prediction_id: Unique prediction identifier
        
    Returns:
        Prediction data with visualization links
    """
    try:
        data_dir = Path("results/data")
        
        # Find the JSON file
        json_files = list(data_dir.glob(f"*_{prediction_id}_prediction.json"))
        
        if not json_files:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        import json
        with open(json_files[0], 'r') as f:
            pred_data = json.load(f)
        
        # Add visualization links
        symbol = pred_data.get('symbol', 'UNKNOWN')
        plots_dir = Path("results/plots")
        
        visualizations = {}
        for plot_type in ['ensemble_full', 'individual_models', 'trend']:
            plot_file = plots_dir / f"{symbol}_{prediction_id}_{plot_type}.png"
            if plot_file.exists():
                visualizations[plot_type] = f"/results/plots/{plot_file.name}"
        
        # Add report link
        report_file = Path("results") / f"{symbol}_{prediction_id}_report.html"
        if report_file.exists():
            pred_data['report_url'] = f"/results/{report_file.name}"
        
        pred_data['visualizations'] = visualizations
        
        return pred_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predictions/{prediction_id}/report")
async def get_prediction_report(prediction_id: str):
    """
    Get HTML report for a specific prediction.
    
    Args:
        prediction_id: Unique prediction identifier
        
    Returns:
        HTML report file
    """
    try:
        results_dir = Path("results")
        
        # Find the HTML report
        report_files = list(results_dir.glob(f"*_{prediction_id}_report.html"))
        
        if not report_files:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            report_files[0],
            media_type="text/html",
            filename=report_files[0].name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/predictions/{prediction_id}")
async def delete_prediction(prediction_id: str):
    """
    Delete a saved prediction and its associated files.
    
    Args:
        prediction_id: Unique prediction identifier
        
    Returns:
        Deletion status
    """
    try:
        deleted_files = []
        
        # Delete data files
        data_dir = Path("results/data")
        for pattern in [f"*_{prediction_id}_prediction.json", f"*_{prediction_id}_prediction.csv"]:
            for file in data_dir.glob(pattern):
                file.unlink()
                deleted_files.append(str(file))
        
        # Delete plot files
        plots_dir = Path("results/plots")
        for file in plots_dir.glob(f"*_{prediction_id}_*.png"):
            file.unlink()
            deleted_files.append(str(file))
        
        # Delete report
        results_dir = Path("results")
        for file in results_dir.glob(f"*_{prediction_id}_report.html"):
            file.unlink()
            deleted_files.append(str(file))
        
        if not deleted_files:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        logger.info(f"Deleted prediction {prediction_id}: {len(deleted_files)} files")
        
        return {
            "status": "deleted",
            "prediction_id": prediction_id,
            "files_deleted": len(deleted_files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results/stats")
async def get_results_stats():
    """Get statistics about saved results."""
    try:
        results_dir = Path("results")
        data_dir = results_dir / "data"
        plots_dir = results_dir / "plots"
        
        # Count files
        json_count = len(list(data_dir.glob("*.json"))) if data_dir.exists() else 0
        csv_count = len(list(data_dir.glob("*.csv"))) if data_dir.exists() else 0
        plot_count = len(list(plots_dir.glob("*.png"))) if plots_dir.exists() else 0
        report_count = len(list(results_dir.glob("*_report.html")))
        
        # Calculate disk usage
        def get_dir_size(path):
            if not path.exists():
                return 0
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        
        total_size_bytes = get_dir_size(results_dir)
        total_size_mb = total_size_bytes / (1024 * 1024)
        
        return {
            "predictions_saved": json_count,
            "csv_files": csv_count,
            "visualizations": plot_count,
            "reports": report_count,
            "total_size_mb": round(total_size_mb, 2),
            "storage_location": str(results_dir.absolute())
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
