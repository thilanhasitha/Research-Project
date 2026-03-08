"""
Helper Utilities
================
General helper functions for the LSTM stock prediction project.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional
import pickle
import json


def save_scaler(scaler, filepath: str) -> None:
    """
    Save scaler to disk.
    
    Args:
        scaler: Fitted scaler object
        filepath: Path to save the scaler
    """
    with open(filepath, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"Scaler saved to {filepath}")


def load_scaler(filepath: str):
    """
    Load scaler from disk.
    
    Args:
        filepath: Path to the saved scaler
        
    Returns:
        Loaded scaler object
    """
    with open(filepath, 'rb') as f:
        scaler = pickle.load(f)
    print(f"Scaler loaded from {filepath}")
    return scaler


def save_metrics(metrics: dict, filepath: str) -> None:
    """
    Save metrics to JSON file.
    
    Args:
        metrics: Dictionary of metrics
        filepath: Path to save the metrics
    """
    with open(filepath, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Metrics saved to {filepath}")


def load_metrics(filepath: str) -> dict:
    """
    Load metrics from JSON file.
    
    Args:
        filepath: Path to the metrics file
        
    Returns:
        Dictionary of metrics
    """
    with open(filepath, 'r') as f:
        metrics = json.load(f)
    print(f"Metrics loaded from {filepath}")
    return metrics


def create_project_directories(base_path: str = 'backend/lstm_stock_prediction') -> None:
    """
    Create all necessary project directories.
    
    Args:
        base_path: Base project path
    """
    directories = [
        'data/raw',
        'data/processed',
        'models/saved_models',
        'models/checkpoints',
        'logs',
        'results/plots',
        'results/metrics',
        'notebooks'
    ]
    
    base = Path(base_path)
    for directory in directories:
        (base / directory).mkdir(parents=True, exist_ok=True)
    
    print(f"Created project directories in {base_path}")


def calculate_returns(prices: np.ndarray) -> np.ndarray:
    """
    Calculate returns from prices.
    
    Args:
        prices: Array of prices
        
    Returns:
        Array of returns
    """
    returns = np.diff(prices) / prices[:-1]
    return returns


def calculate_volatility(returns: np.ndarray, window: int = 30) -> np.ndarray:
    """
    Calculate rolling volatility.
    
    Args:
        returns: Array of returns
        window: Rolling window size
        
    Returns:
        Array of volatility values
    """
    df = pd.DataFrame({'returns': returns})
    volatility = df['returns'].rolling(window=window).std()
    return volatility.values


def split_train_val_test(X: np.ndarray, y: np.ndarray,
                         train_ratio: float = 0.7,
                         val_ratio: float = 0.15,
                         test_ratio: float = 0.15) -> Tuple[np.ndarray, ...]:
    """
    Split data into train, validation, and test sets.
    
    Args:
        X: Features
        y: Targets
        train_ratio: Training data ratio
        val_ratio: Validation data ratio
        test_ratio: Test data ratio
        
    Returns:
        Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "Ratios must sum to 1.0"
    
    n = len(X)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    X_train = X[:train_end]
    X_val = X[train_end:val_end]
    X_test = X[val_end:]
    
    y_train = y[:train_end]
    y_val = y[train_end:val_end]
    y_test = y[val_end:]
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def print_data_info(X_train: np.ndarray, X_val: np.ndarray, 
                   X_test: np.ndarray, y_train: np.ndarray,
                   y_val: np.ndarray, y_test: np.ndarray) -> None:
    """
    Print information about data splits.
    
    Args:
        X_train, X_val, X_test: Feature arrays
        y_train, y_val, y_test: Target arrays
    """
    print("\n" + "="*50)
    print("Data Split Information")
    print("="*50)
    print(f"Training set:   X={X_train.shape}, y={y_train.shape}")
    print(f"Validation set: X={X_val.shape}, y={y_val.shape}")
    print(f"Test set:       X={X_test.shape}, y={y_test.shape}")
    print(f"Total samples:  {len(X_train) + len(X_val) + len(X_test)}")
    print("="*50 + "\n")


def get_model_parameter_count(model) -> dict:
    """
    Get model parameter count.
    
    Args:
        model: Keras model
        
    Returns:
        Dictionary with parameter counts
    """
    trainable_params = sum([np.prod(var.shape) for var in model.trainable_variables])
    non_trainable_params = sum([np.prod(var.shape) for var in model.non_trainable_variables])
    
    return {
        'trainable': int(trainable_params),
        'non_trainable': int(non_trainable_params),
        'total': int(trainable_params + non_trainable_params)
    }
