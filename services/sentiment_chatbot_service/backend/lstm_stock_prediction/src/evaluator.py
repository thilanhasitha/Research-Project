"""
Model Evaluator Module
=======================
Handles evaluation and prediction of LSTM models.
"""

import numpy as np
import pandas as pd
from tensorflow import keras
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from typing import Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate and make predictions with LSTM models."""
    
    def __init__(self, model: keras.Model):
        """
        Initialize the evaluator.
        
        Args:
            model: Trained Keras model
        """
        self.model = model
        self.predictions = None
        self.metrics = {}
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input features
            
        Returns:
            Predictions array
        """
        self.predictions = self.model.predict(X, verbose=0)
        logger.info(f"Generated {len(self.predictions)} predictions")
        return self.predictions
    
    def evaluate(self, X: np.ndarray, y_true: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Args:
            X: Input features
            y_true: True target values
            
        Returns:
            Dictionary of evaluation metrics
        """
        # Make predictions
        y_pred = self.predict(X)
        
        # Calculate metrics
        self.metrics = {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'mape': self.calculate_mape(y_true, y_pred)
        }
        
        logger.info("Evaluation metrics:")
        for metric, value in self.metrics.items():
            logger.info(f"  {metric.upper()}: {value:.6f}")
        
        return self.metrics
    
    @staticmethod
    def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate Mean Absolute Percentage Error.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            MAPE value
        """
        # Avoid division by zero
        mask = y_true != 0
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    def calculate_directional_accuracy(self, y_true: np.ndarray, 
                                      y_pred: np.ndarray) -> float:
        """
        Calculate directional accuracy (percentage of correct trend predictions).
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Directional accuracy percentage
        """
        if len(y_true) < 2:
            return 0.0
        
        true_direction = np.sign(np.diff(y_true.flatten()))
        pred_direction = np.sign(np.diff(y_pred.flatten()))
        
        correct = np.sum(true_direction == pred_direction)
        total = len(true_direction)
        
        accuracy = (correct / total) * 100
        logger.info(f"Directional Accuracy: {accuracy:.2f}%")
        return accuracy
    
    def get_prediction_errors(self, y_true: np.ndarray, 
                             y_pred: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Calculate prediction errors.
        
        Args:
            y_true: True values
            y_pred: Predicted values (uses stored predictions if None)
            
        Returns:
            Array of errors
        """
        if y_pred is None:
            if self.predictions is None:
                raise ValueError("No predictions available")
            y_pred = self.predictions
        
        errors = y_true - y_pred.flatten()
        return errors
    
    def create_results_dataframe(self, y_true: np.ndarray, 
                                y_pred: Optional[np.ndarray] = None,
                                dates: Optional[pd.DatetimeIndex] = None) -> pd.DataFrame:
        """
        Create a DataFrame with actual and predicted values.
        
        Args:
            y_true: True values
            y_pred: Predicted values (uses stored predictions if None)
            dates: Optional date index
            
        Returns:
            DataFrame with results
        """
        if y_pred is None:
            if self.predictions is None:
                raise ValueError("No predictions available")
            y_pred = self.predictions
        
        results_df = pd.DataFrame({
            'Actual': y_true.flatten(),
            'Predicted': y_pred.flatten(),
            'Error': self.get_prediction_errors(y_true, y_pred),
            'Absolute_Error': np.abs(self.get_prediction_errors(y_true, y_pred)),
            'Percentage_Error': (self.get_prediction_errors(y_true, y_pred) / y_true.flatten()) * 100
        })
        
        if dates is not None:
            results_df.index = dates
        
        logger.info(f"Created results DataFrame with {len(results_df)} rows")
        return results_df
    
    def get_metrics_summary(self) -> pd.DataFrame:
        """
        Get a summary of evaluation metrics.
        
        Returns:
            DataFrame with metrics summary
        """
        if not self.metrics:
            logger.warning("No metrics available. Run evaluate() first.")
            return pd.DataFrame()
        
        summary = pd.DataFrame([self.metrics])
        return summary
    
    def predict_future(self, last_sequence: np.ndarray, 
                      n_steps: int = 1) -> np.ndarray:
        """
        Make future predictions.
        
        Args:
            last_sequence: Last sequence of data
            n_steps: Number of steps to predict into the future
            
        Returns:
            Array of future predictions
        """
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(n_steps):
            # Predict next value
            next_pred = self.model.predict(
                current_sequence.reshape(1, *current_sequence.shape),
                verbose=0
            )
            predictions.append(next_pred[0, 0])
            
            # Update sequence (assuming single feature prediction)
            # For multi-feature, you'd need to handle this differently
            current_sequence = np.roll(current_sequence, -1, axis=0)
            current_sequence[-1, 0] = next_pred[0, 0]
        
        predictions = np.array(predictions)
        logger.info(f"Generated {n_steps} future predictions")
        return predictions
