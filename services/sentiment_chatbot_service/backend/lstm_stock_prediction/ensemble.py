"""
Model Ensemble Module
======================
Combine predictions from multiple LSTM models using various ensemble strategies.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from tensorflow import keras
import json
import logging
from utils.helpers import load_scaler


class ModelEnsemble:
    """Ensemble multiple LSTM models for improved predictions."""
    
    def __init__(self, models_dir: str = "models"):
        """
        Initialize model ensemble.
        
        Args:
            models_dir: Directory containing trained models
        """
        self.models_dir = Path(models_dir)
        self.models = {}
        self.scalers = {}
        self.metadata = {}
        self.logger = logging.getLogger('model_ensemble')
        
    def load_models(self, metadata_path: Optional[str] = None):
        """
        Load all models from metadata file.
        
        Args:
            metadata_path: Path to models_metadata.json file
        """
        if metadata_path is None:
            metadata_path = self.models_dir / "models_metadata.json"
        else:
            metadata_path = Path(metadata_path)
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        
        self.logger.info(f"Loading {len(self.metadata)} models...")
        
        for model_name, metadata in self.metadata.items():
            try:
                # Load model
                model_path = Path(metadata['model_path'])
                if model_path.exists():
                    self.models[model_name] = keras.models.load_model(str(model_path))
                    self.logger.info(f"  ✓ Loaded model: {model_name}")
                else:
                    self.logger.warning(f"  ✗ Model not found: {model_path}")
                    continue
                
                # Load scaler
                scaler_path = Path(metadata['scaler_path'])
                if scaler_path.exists():
                    self.scalers[model_name] = load_scaler(str(scaler_path))
                else:
                    self.logger.warning(f"  ✗ Scaler not found: {scaler_path}")
                    
            except Exception as e:
                self.logger.error(f"  ✗ Error loading {model_name}: {str(e)}")
        
        self.logger.info(f"Successfully loaded {len(self.models)} models")
    
    def predict_single_model(
        self, 
        model_name: str, 
        X: np.ndarray
    ) -> np.ndarray:
        """
        Get prediction from a single model.
        
        Args:
            model_name: Name of the model
            X: Input data
            
        Returns:
            Predictions from the model
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not loaded")
        
        model = self.models[model_name]
        predictions = model.predict(X, verbose=0)
        
        return predictions
    
    def predict_all_models(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Get predictions from all loaded models.
        
        Args:
            X: Input data
            
        Returns:
            Dictionary mapping model names to their predictions
        """
        predictions = {}
        
        for model_name in self.models.keys():
            try:
                pred = self.predict_single_model(model_name, X)
                predictions[model_name] = pred
            except Exception as e:
                self.logger.error(f"Prediction failed for {model_name}: {str(e)}")
        
        return predictions
    
    def ensemble_average(self, predictions: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Simple average ensemble.
        
        Args:
            predictions: Dictionary of model predictions
            
        Returns:
            Averaged predictions
        """
        pred_arrays = list(predictions.values())
        return np.mean(pred_arrays, axis=0)
    
    def ensemble_weighted_average(
        self, 
        predictions: Dict[str, np.ndarray],
        weights: Optional[Dict[str, float]] = None
    ) -> np.ndarray:
        """
        Weighted average ensemble based on model performance.
        
        Args:
            predictions: Dictionary of model predictions
            weights: Optional custom weights. If None, uses inverse RMSE
            
        Returns:
            Weighted averaged predictions
        """
        if weights is None:
            # Use inverse RMSE as weights (better models get higher weight)
            weights = {}
            for model_name in predictions.keys():
                rmse = self.metadata[model_name]['metrics']['rmse']
                weights[model_name] = 1.0 / (rmse + 1e-10)  # Avoid division by zero
            
            # Normalize weights to sum to 1
            total_weight = sum(weights.values())
            weights = {k: v / total_weight for k, v in weights.items()}
        
        # Calculate weighted average
        weighted_sum = np.zeros_like(list(predictions.values())[0])
        for model_name, pred in predictions.items():
            weight = weights.get(model_name, 0.0)
            weighted_sum += pred * weight
        
        return weighted_sum
    
    def ensemble_median(self, predictions: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Median ensemble (robust to outliers).
        
        Args:
            predictions: Dictionary of model predictions
            
        Returns:
            Median predictions
        """
        pred_arrays = list(predictions.values())
        return np.median(pred_arrays, axis=0)
    
    def ensemble_best_model(self, predictions: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Select predictions from the best performing model (lowest RMSE).
        
        Args:
            predictions: Dictionary of model predictions
            
        Returns:
            Predictions from best model
        """
        best_model = min(
            self.metadata.items(),
            key=lambda x: x[1]['metrics']['rmse']
        )[0]
        
        return predictions[best_model]
    
    def ensemble_voting(
        self, 
        predictions: Dict[str, np.ndarray],
        threshold: float = 0.5
    ) -> np.ndarray:
        """
        Voting ensemble for trend prediction (up/down).
        
        Args:
            predictions: Dictionary of model predictions
            threshold: Threshold for determining trend
            
        Returns:
            Ensemble predictions based on majority voting
        """
        pred_arrays = list(predictions.values())
        stacked = np.stack(pred_arrays, axis=0)
        
        # Count votes for "up" trend
        votes_up = np.sum(stacked > threshold, axis=0)
        votes_down = len(pred_arrays) - votes_up
        
        # Return average of models that voted for majority
        result = np.where(
            votes_up >= votes_down,
            np.mean(stacked[stacked > threshold], axis=0),
            np.mean(stacked[stacked <= threshold], axis=0)
        )
        
        return result
    
    def predict_with_confidence(
        self, 
        X: np.ndarray,
        method: str = 'weighted_average'
    ) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Make ensemble predictions with confidence intervals.
        
        Args:
            X: Input data
            method: Ensemble method ('average', 'weighted_average', 'median', 'best', 'voting')
            
        Returns:
            Tuple of (predictions, std_dev, all_predictions)
        """
        # Get predictions from all models
        all_predictions = self.predict_all_models(X)
        
        if not all_predictions:
            raise ValueError("No predictions available from models")
        
        # Calculate ensemble prediction
        if method == 'average':
            ensemble_pred = self.ensemble_average(all_predictions)
        elif method == 'weighted_average':
            ensemble_pred = self.ensemble_weighted_average(all_predictions)
        elif method == 'median':
            ensemble_pred = self.ensemble_median(all_predictions)
        elif method == 'best':
            ensemble_pred = self.ensemble_best_model(all_predictions)
        elif method == 'voting':
            ensemble_pred = self.ensemble_voting(all_predictions)
        else:
            raise ValueError(f"Unknown ensemble method: {method}")
        
        # Calculate standard deviation (uncertainty measure)
        pred_arrays = list(all_predictions.values())
        std_dev = np.std(pred_arrays, axis=0)
        
        return ensemble_pred, std_dev, all_predictions
    
    def get_model_weights(self) -> Dict[str, float]:
        """
        Get weights for each model based on performance.
        
        Returns:
            Dictionary of model weights
        """
        weights = {}
        for model_name, metadata in self.metadata.items():
            rmse = metadata['metrics']['rmse']
            weights[model_name] = 1.0 / (rmse + 1e-10)
        
        # Normalize
        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()}
    
    def get_ensemble_info(self) -> Dict:
        """
        Get information about the ensemble.
        
        Returns:
            Dictionary with ensemble information
        """
        return {
            'num_models': len(self.models),
            'model_names': list(self.models.keys()),
            'model_weights': self.get_model_weights(),
            'model_metrics': {
                name: meta['metrics']
                for name, meta in self.metadata.items()
            }
        }


class PredictionAggregator:
    """Aggregate and format predictions for user-friendly responses."""
    
    @staticmethod
    def format_prediction_response(
        predictions: np.ndarray,
        confidence: np.ndarray,
        model_predictions: Dict[str, np.ndarray],
        ensemble_info: Dict,
        symbol: str = "STOCK"
    ) -> Dict:
        """
        Format predictions into user-friendly response.
        
        Args:
            predictions: Ensemble predictions
            confidence: Standard deviation / confidence measure
            model_predictions: Individual model predictions
            ensemble_info: Information about the ensemble
            symbol: Stock symbol
            
        Returns:
            Formatted response dictionary
        """
        pred_list = predictions.flatten().tolist()
        conf_list = confidence.flatten().tolist()
        
        # Calculate confidence level
        avg_confidence = 1.0 - np.mean(confidence)  # Lower std = higher confidence
        confidence_level = "high" if avg_confidence > 0.7 else "medium" if avg_confidence > 0.4 else "low"
        
        # Format individual model predictions
        individual_predictions = {}
        for model_name, preds in model_predictions.items():
            individual_predictions[model_name] = {
                'predictions': preds.flatten().tolist(),
                'weight': ensemble_info['model_weights'].get(model_name, 0.0),
                'rmse': ensemble_info['model_metrics'][model_name]['rmse']
            }
        
        return {
            'symbol': symbol,
            'ensemble_prediction': pred_list,
            'confidence_intervals': conf_list,
            'confidence_level': confidence_level,
            'num_models': ensemble_info['num_models'],
            'individual_models': individual_predictions,
            'recommendation': PredictionAggregator._generate_recommendation(
                pred_list, confidence_level
            )
        }
    
    @staticmethod
    def _generate_recommendation(predictions: List[float], confidence: str) -> str:
        """Generate trading recommendation based on predictions."""
        if not predictions:
            return "Insufficient data for recommendation"
        
        trend = "upward" if predictions[-1] > predictions[0] else "downward"
        strength = "strong" if confidence == "high" else "moderate" if confidence == "medium" else "weak"
        
        return f"The ensemble models predict a {strength} {trend} trend with {confidence} confidence."


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    ensemble = ModelEnsemble()
    ensemble.load_models()
    
    print("\nEnsemble Info:")
    info = ensemble.get_ensemble_info()
    print(json.dumps(info, indent=2))
