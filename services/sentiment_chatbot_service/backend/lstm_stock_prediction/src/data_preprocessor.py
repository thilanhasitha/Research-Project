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
        Add comprehensive technical indicators to the dataset.
        
        Args:
            data: Input DataFrame with OHLCV data
            
        Returns:
            DataFrame with added technical indicators
        """
        df = data.copy()
        
        # Moving Averages
        df['MA_7'] = df[self.target_column].rolling(window=7).mean()
        df['MA_14'] = df[self.target_column].rolling(window=14).mean()
        df['MA_21'] = df[self.target_column].rolling(window=21).mean()
        df['MA_30'] = df[self.target_column].rolling(window=30).mean()
        
        # Exponential Moving Averages
        df['EMA_12'] = df[self.target_column].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df[self.target_column].ewm(span=26, adjust=False).mean()
        
        # MACD (Moving Average Convergence Divergence)
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # RSI (Relative Strength Index)
        delta = df[self.target_column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df[self.target_column].rolling(window=20).mean()
        bb_std = df[self.target_column].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df[self.target_column] - df['BB_Lower']) / df['BB_Width']
        
        # Volatility Indicators
        df['Volatility_7'] = df[self.target_column].rolling(window=7).std()
        df['Volatility_14'] = df[self.target_column].rolling(window=14).std()
        df['Volatility_30'] = df[self.target_column].rolling(window=30).std()
        
        # Price Momentum
        df['Momentum_1'] = df[self.target_column].diff(periods=1)
        df['Momentum_5'] = df[self.target_column].diff(periods=5)
        df['Momentum_10'] = df[self.target_column].diff(periods=10)
        
        # Rate of Change (ROC)
        df['ROC_5'] = ((df[self.target_column] - df[self.target_column].shift(5)) / df[self.target_column].shift(5)) * 100
        df['ROC_10'] = ((df[self.target_column] - df[self.target_column].shift(10)) / df[self.target_column].shift(10)) * 100
        
        # Average True Range (ATR)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df[self.target_column].shift())
        low_close = np.abs(df['Low'] - df[self.target_column].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = pd.Series(true_range).rolling(window=14).mean().values
        
        # Volume indicators (if volume is available)
        if 'Volume' in df.columns:
            df['Volume_MA_7'] = df['Volume'].rolling(window=7).mean()
            df['Volume_MA_14'] = df['Volume'].rolling(window=14).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_MA_14']
            
            # On-Balance Volume (OBV)
            df['OBV'] = (np.sign(df[self.target_column].diff()) * df['Volume']).fillna(0).cumsum()
        
        # Price percentage change
        df['Pct_Change_1'] = df[self.target_column].pct_change(periods=1)
        df['Pct_Change_5'] = df[self.target_column].pct_change(periods=5)
        
        # Lag features
        for lag in [1, 2, 3, 5, 7]:
            df[f'Close_Lag_{lag}'] = df[self.target_column].shift(lag)
        
        # Drop NaN values created by indicators
        df = df.dropna()
        
        logger.info(f"Added comprehensive technical indicators. New shape: {df.shape}")
        logger.info(f"Total features: {len(df.columns)}")
        return df
