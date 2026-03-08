"""
LSTM Prediction Routes
======================
API routes for stock price predictions using LSTM models.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
import httpx
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# LSTM Service URL (from docker-compose)
LSTM_SERVICE_URL = "http://lstm-predictor:8002"


class StockPredictionRequest(BaseModel):
    """Request model for stock predictions."""
    symbol: str
    historical_data: List[List[float]]
    method: Optional[str] = "weighted_average"
    include_details: Optional[bool] = False


class StockQueryRequest(BaseModel):
    """Request model for natural language queries."""
    query: str
    symbol: str
    historical_data: Optional[List[List[float]]] = None
    context: Optional[Dict] = None


@router.get("/lstm/health")
async def check_lstm_health():
    """Check if LSTM service is healthy."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{LSTM_SERVICE_URL}/health")
            return response.json()
    except Exception as e:
        logger.error(f"LSTM service health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"LSTM service unavailable: {str(e)}"
        )


@router.get("/lstm/models")
async def get_available_models():
    """Get list of available LSTM models."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{LSTM_SERVICE_URL}/ensemble/models")
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to retrieve models"
                )
    except httpx.RequestError as e:
        logger.error(f"Error fetching models: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="LSTM service unavailable"
        )


@router.get("/lstm/ensemble/info")
async def get_ensemble_info():
    """Get information about the model ensemble."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{LSTM_SERVICE_URL}/ensemble/info")
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to retrieve ensemble info"
                )
    except httpx.RequestError as e:
        logger.error(f"Error fetching ensemble info: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="LSTM service unavailable"
        )


@router.post("/lstm/predict")
async def predict_stock_price(request: StockPredictionRequest):
    """
    Predict stock prices using ensemble of LSTM models.
    
    Args:
        request: Stock prediction request with historical data
        
    Returns:
        Ensemble predictions with confidence intervals
    """
    try:
        # Prepare request for LSTM service
        lstm_request = {
            "symbol": request.symbol,
            "data": request.historical_data,
            "method": request.method,
            "include_individual": request.include_details
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{LSTM_SERVICE_URL}/predict/ensemble",
                json=lstm_request
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Add backend metadata
                result['service'] = 'LSTM Ensemble'
                result['backend_timestamp'] = datetime.now().isoformat()
                
                return result
            else:
                error_detail = response.json().get('detail', 'Prediction failed')
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
                
    except httpx.RequestError as e:
        logger.error(f"LSTM prediction  request error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="LSTM service unavailable"
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/lstm/query")
async def query_prediction(request: StockQueryRequest):
    """
    Answer user queries about stock predictions using natural language.
    
    This endpoint translates natural language queries into predictions
    and returns user-friendly responses.
    
    Args:
        request: Query request with user's question
        
    Returns:
        Natural language response with predictions
    """
    try:
        # Prepare query parameters
        params = {
            "query": request.query,
            "symbol": request.symbol,
            "method": "weighted_average"
        }
        
        # Prepare request body if historical data provided
        request_body = None
        if request.historical_data:
            request_body = request.historical_data
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Send query to LSTM service
            if request_body:
                response = await client.post(
                    f"{LSTM_SERVICE_URL}/query/predict",
                    params=params,
                    json={"data": request_body}
                )
            else:
                response = await client.post(
                    f"{LSTM_SERVICE_URL}/query/predict",
                    params=params
                )
            
            if response.status_code == 200:
                result = response.json()
                
                # Enhance response with additional context if provided
                if request.context:
                    result['context'] = request.context
                
                result['query_timestamp'] = datetime.now().isoformat()
                
                return result
            else:
                error_detail = response.json().get('detail', 'Query processing failed')
                return {
                    "answer": f"I encountered an issue processing your query: {error_detail}",
                    "status": "error",
                    "timestamp": datetime.now().isoformat()
                }
                
    except httpx.RequestError as e:
        logger.error(f"LSTM query request error: {str(e)}")
        return {
            "answer": "I apologize, but I'm unable to connect to the prediction service at the moment. Please try again later.",
            "status": "service_unavailable",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        return {
            "answer": f"An error occurred while processing your query: {str(e)}",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }


@router.post("/lstm/predict/single")
async def predict_single_model(
    symbol: str,
    data: List[List[float]],
    model_name: Optional[str] = None
):
    """
    Get prediction from a single model (fallback endpoint).
    
    Args:
        symbol: Stock symbol
        data: Historical data
        model_name: Optional specific model name
        
    Returns:
        Single model prediction
    """
    try:
        lstm_request = {
            "symbol": symbol,
            "data": data
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{LSTM_SERVICE_URL}/predict",
                json=lstm_request
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Single model prediction failed"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Single model prediction error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="LSTM service unavailable"
        )


@router.get("/lstm/status")
async def get_lstm_status():
    """
    Get comprehensive status of LSTM service and models.
    
    Returns:
        Status information including health, loaded models, and metrics
    """
    status = {
        "service": "LSTM Stock Prediction",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check health
            health_response = await client.get(f"{LSTM_SERVICE_URL}/health")
            status['health'] = health_response.json() if health_response.status_code == 200 else {"status": "unhealthy"}
            
            # Get ensemble info
            try:
                ensemble_response = await client.get(f"{LSTM_SERVICE_URL}/ensemble/info")
                if ensemble_response.status_code == 200:
                    status['ensemble'] = ensemble_response.json()
            except:
                status['ensemble'] = {"status": "not_loaded"}
            
            # Get models list
            try:
                models_response = await client.get(f"{LSTM_SERVICE_URL}/ensemble/models")
                if models_response.status_code == 200:
                    status['models'] = models_response.json()
            except:
                status['models'] = {"status": "not_available"}
            
            status['overall_status'] = 'operational'
            
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        status['overall_status'] = 'unavailable'
        status['error'] = str(e)
    
    return status
