"""
Configuration Module
====================
Configuration settings for LSTM stock prediction model.
"""

from dataclasses import dataclass
from typing import List, Optional
import json
from pathlib import Path


@dataclass
class DataConfig:
    """Data-related configuration."""
    raw_data_path: str = "data/processed/lstm_ready_data.csv"
    processed_data_path: str = "data/processed/processed_stock_data.csv"
    date_column: str = "Date"
    target_column: str = "Close"
    feature_columns: List[str] = None
    
    def __post_init__(self):
        if self.feature_columns is None:
            self.feature_columns = ["Open", "High", "Low", "Close", "Volume"]


@dataclass
class PreprocessingConfig:
    """Preprocessing configuration."""
    sequence_length: int = 12  # Number of months to look back
    train_ratio: float = 0.8
    validation_ratio: float = 0.1
    test_ratio: float = 0.1
    missing_value_method: str = "ffill"  # 'ffill', 'bfill', 'interpolate'
    add_technical_indicators: bool = True
    normalize: bool = True


@dataclass
class ModelConfig:
    """Model architecture configuration."""
    model_type: str = "stacked_lstm"  # 'simple_lstm', 'stacked_lstm', 'bidirectional_lstm', 'attention_lstm'
    lstm_units: List[int] = None
    dropout_rate: float = 0.2
    learning_rate: float = 0.001
    optimizer: str = "adam"  # 'adam', 'rmsprop', 'sgd'
    
    def __post_init__(self):
        if self.lstm_units is None:
            self.lstm_units = [50, 50]


@dataclass
class TrainingConfig:
    """Training configuration."""
    epochs: int = 100
    batch_size: int = 32
    early_stopping_patience: int = 15
    reduce_lr_patience: int = 10
    validation_split: float = 0.1
    shuffle: bool = False  # Don't shuffle time series data
    verbose: int = 1


@dataclass
class PathConfig:
    """Path configuration."""
    project_root: str = "backend/lstm_stock_prediction"
    data_dir: str = "data"
    model_dir: str = "models"
    log_dir: str = "logs"
    results_dir: str = "results"
    checkpoint_dir: str = "models/checkpoints"
    saved_models_dir: str = "models/saved_models"
    
    def get_absolute_paths(self, base_path: Optional[Path] = None) -> dict:
        """Get absolute paths for all directories."""
        if base_path is None:
            base_path = Path(self.project_root)
        
        return {
            'data_dir': base_path / self.data_dir,
            'model_dir': base_path / self.model_dir,
            'log_dir': base_path / self.log_dir,
            'results_dir': base_path / self.results_dir,
            'checkpoint_dir': base_path / self.checkpoint_dir,
            'saved_models_dir': base_path / self.saved_models_dir
        }


class Config:
    """Main configuration class combining all configs."""
    
    def __init__(self):
        self.data = DataConfig()
        self.preprocessing = PreprocessingConfig()
        self.model = ModelConfig()
        self.training = TrainingConfig()
        self.paths = PathConfig()
    
    def save_to_json(self, filepath: str) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            filepath: Path to save the config file
        """
        config_dict = {
            'data': self.data.__dict__,
            'preprocessing': self.preprocessing.__dict__,
            'model': self.model.__dict__,
            'training': self.training.__dict__,
            'paths': self.paths.__dict__
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=4)
        
        print(f"Configuration saved to {filepath}")
    
    @classmethod
    def load_from_json(cls, filepath: str) -> 'Config':
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to the config file
            
        Returns:
            Config object
        """
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        
        config = cls()
        
        # Update each config section
        for key, value in config_dict.get('data', {}).items():
            setattr(config.data, key, value)
        
        for key, value in config_dict.get('preprocessing', {}).items():
            setattr(config.preprocessing, key, value)
        
        for key, value in config_dict.get('model', {}).items():
            setattr(config.model, key, value)
        
        for key, value in config_dict.get('training', {}).items():
            setattr(config.training, key, value)
        
        for key, value in config_dict.get('paths', {}).items():
            setattr(config.paths, key, value)
        
        print(f"Configuration loaded from {filepath}")
        return config
    
    def print_config(self) -> None:
        """Print current configuration."""
        print("\n" + "="*50)
        print("LSTM Stock Prediction Configuration")
        print("="*50)
        
        print("\nData Config:")
        for key, value in self.data.__dict__.items():
            print(f"  {key}: {value}")
        
        print("\nPreprocessing Config:")
        for key, value in self.preprocessing.__dict__.items():
            print(f"  {key}: {value}")
        
        print("\nModel Config:")
        for key, value in self.model.__dict__.items():
            print(f"  {key}: {value}")
        
        print("\nTraining Config:")
        for key, value in self.training.__dict__.items():
            print(f"  {key}: {value}")
        
        print("\nPath Config:")
        for key, value in self.paths.__dict__.items():
            print(f"  {key}: {value}")
        
        print("="*50 + "\n")


# Default configuration
def get_default_config() -> Config:
    """Get default configuration."""
    return Config()
