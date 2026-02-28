"""
Data Preprocessor Module
=========================
Handles preprocessing, normalization, and sequence creation for LSTM training.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataPreprocessor:
    """Preprocess stock price data for LSTM model training."""
    
    def __init__(self, feature_columns: list, target_column: str = 'Close'):
        """
        Initialize the preprocessor.
        
        Args:
            feature_columns: List of column names to use as features
            target_column: Column name to predict
        """
        self.feature_columns = feature_columns
        self.target_column = target_column
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.scaled_data = None
        
    def handle_missing_values(self, data: pd.DataFrame, 
                             method: str = 'ffill') -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            data: Input DataFrame
            method: Method to handle missing values ('ffill', 'bfill', 'interpolate')
            
        Returns:
            DataFrame with handled missing values
        """
        if method == 'ffill':
            return data.ffill()
        elif method == 'bfill':
            return data.bfill()
        elif method == 'interpolate':
            return data.interpolate(method='linear')
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def normalize_data(self, data: pd.DataFrame) -> np.ndarray:
        """
        Normalize data using MinMaxScaler.
        
        Args:
            data: Input DataFrame
            
        Returns:
            Normalized numpy array
        """
        selected_data = data[self.feature_columns].values
        self.scaled_data = self.scaler.fit_transform(selected_data)
        logger.info(f"Normalized data shape: {self.scaled_data.shape}")
        return self.scaled_data
    
    def inverse_transform(self, scaled_data: np.ndarray) -> np.ndarray:
        """
        Inverse transform scaled data back to original scale.
        
        Args:
            scaled_data: Scaled data array
            
        Returns:
            Original scale data
        """
        return self.scaler.inverse_transform(scaled_data)
    
    def create_sequences(self, data: np.ndarray, 
                        sequence_length: int = 12,
                        target_index: int = 0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training.
        
        Args:
            data: Normalized data array
            sequence_length: Number of time steps to look back
            target_index: Index of the target feature
            
        Returns:
            Tuple of (X, y) where X is sequences and y is targets
        """
        X, y = [], []
        
        for i in range(sequence_length, len(data)):
            X.append(data[i-sequence_length:i])
            y.append(data[i, target_index])
        
        X = np.array(X)
        y = np.array(y)
        
        logger.info(f"Created sequences - X shape: {X.shape}, y shape: {y.shape}")
        return X, y
    
    def split_data(self, X: np.ndarray, y: np.ndarray, 
                   train_ratio: float = 0.8) -> Tuple[np.ndarray, ...]:
        """
        Split data into training and testing sets.
        
        Args:
            X: Feature sequences
            y: Target values
            train_ratio: Ratio of training data
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        split_idx = int(len(X) * train_ratio)
        
        X_train = X[:split_idx]
        X_test = X[split_idx:]
        y_train = y[:split_idx]
        y_test = y[split_idx:]
        
        logger.info(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
        return X_train, X_test, y_train, y_test
    
    def add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to the dataset.
        
        Args:
            data: Input DataFrame with OHLCV data
            
        Returns:
            DataFrame with added technical indicators
        """
        df = data.copy()
        
        # Moving Averages
        df['MA_7'] = df[self.target_column].rolling(window=7).mean()
        df['MA_14'] = df[self.target_column].rolling(window=14).mean()
        df['MA_30'] = df[self.target_column].rolling(window=30).mean()
        
        # Exponential Moving Average
        df['EMA_12'] = df[self.target_column].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df[self.target_column].ewm(span=26, adjust=False).mean()
        
        # Volatility
        df['Volatility'] = df[self.target_column].rolling(window=7).std()
        
        # Price momentum
        df['Momentum'] = df[self.target_column].diff(periods=1)
        
        # Drop NaN values created by indicators
        df = df.dropna()
        
        logger.info(f"Added technical indicators. New shape: {df.shape}")
        return df
