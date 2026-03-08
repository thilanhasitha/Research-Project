"""
Data Loader Module
==================
Handles loading and initial validation of stock price datasets.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataLoader:
    """Load and validate stock price data from various formats."""
    
    def __init__(self, data_path: str):
        """
        Initialize the data loader.
        
        Args:
            data_path: Path to the stock data file (CSV, Excel, etc.)
        """
        self.data_path = Path(data_path)
        self.data = None
        
    def load_csv(self, date_column: str = 'Date', 
                 parse_dates: bool = True) -> pd.DataFrame:
        """
        Load stock data from CSV file.
        
        Args:
            date_column: Name of the date column
            parse_dates: Whether to parse dates automatically
            
        Returns:
            DataFrame with stock data
        """
        try:
            self.data = pd.read_csv(
                self.data_path,
                parse_dates=[date_column] if parse_dates else False
            )
            logger.info(f"Loaded {len(self.data)} records from {self.data_path}")
            return self.data
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def load_excel(self, sheet_name: str = 0, 
                   date_column: str = 'Date') -> pd.DataFrame:
        """
        Load stock data from Excel file.
        
        Args:
            sheet_name: Name or index of the sheet to load
            date_column: Name of the date column
            
        Returns:
            DataFrame with stock data
        """
        try:
            self.data = pd.read_excel(
                self.data_path,
                sheet_name=sheet_name,
                parse_dates=[date_column]
            )
            logger.info(f"Loaded {len(self.data)} records from {self.data_path}")
            return self.data
        except Exception as e:
            logger.error(f"Error loading Excel: {e}")
            raise
    
    def validate_data(self, required_columns: list = None) -> bool:
        """
        Validate the loaded data.
        
        Args:
            required_columns: List of required column names
            
        Returns:
            True if validation passes
        """
        if self.data is None:
            logger.error("No data loaded")
            return False
        
        if required_columns:
            missing_cols = set(required_columns) - set(self.data.columns)
            if missing_cols:
                logger.error(f"Missing required columns: {missing_cols}")
                return False
        
        logger.info("Data validation passed")
        return True
    
    def get_data_info(self) -> dict:
        """
        Get information about the loaded data.
        
        Returns:
            Dictionary with data statistics
        """
        if self.data is None:
            return {}
        
        return {
            'rows': len(self.data),
            'columns': list(self.data.columns),
            'date_range': (self.data.iloc[0, 0], self.data.iloc[-1, 0]),
            'missing_values': self.data.isnull().sum().to_dict()
        }
