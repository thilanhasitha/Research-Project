"""
Multi-Model Training Script
============================
Train separate LSTM models for different datasets in the processed folder.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

import numpy as np
import pandas as pd
import json
from typing import Dict, List
from config.config import Config
from src.data_loader import StockDataLoader
from src.data_preprocessor import StockDataPreprocessor
from src.model import LSTMStockModel
from src.trainer import ModelTrainer
from src.evaluator import ModelEvaluator
from utils.visualization import Visualizer
from utils.logger import setup_logger
from utils.helpers import (
    split_train_val_test,
    save_scaler,
    save_metrics
)


class MultiModelTrainer:
    """Train multiple LSTM models for different datasets."""
    
    def __init__(self, data_dir: str = "data/processed", models_dir: str = "models"):
        """
        Initialize multi-model trainer.
        
        Args:
            data_dir: Directory containing processed datasets
            models_dir: Directory to save trained models
        """
        self.data_dir = Path(data_dir)
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = setup_logger(name='multi_model_training', log_dir='logs')
        self.trained_models = {}
        self.model_metadata = {}
        
    def discover_datasets(self) -> List[Path]:
        """Discover all CSV files in the processed data directory."""
        csv_files = list(self.data_dir.glob("*.csv"))
        self.logger.info(f"Found {len(csv_files)} datasets: {[f.name for f in csv_files]}")
        return csv_files
    
    def train_model_for_dataset(
        self, 
        data_path: Path, 
        model_name: str,
        config: Config = None
    ) -> Dict:
        """
        Train a single LSTM model for a specific dataset.
        
        Args:
            data_path: Path to the dataset CSV file
            model_name: Identifier for the model
            config: Model configuration
            
        Returns:
            Dictionary with training results and metadata
        """
        if config is None:
            config = Config()
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"Training model: {model_name}")
        self.logger.info(f"Dataset: {data_path.name}")
        self.logger.info(f"{'='*80}\n")
        
        try:
            # Load data
            data_loader = StockDataLoader(str(data_path))
            data = data_loader.load_csv(date_column=config.data.date_column)
            
            if not data_loader.validate_data(
                config.data.feature_columns + [config.data.date_column]
            ):
                raise ValueError(f"Data validation failed for {data_path.name}")
            
            self.logger.info(f"Loaded {len(data)} records from {data_path.name}")
            
            # Preprocess data
            preprocessor = StockDataPreprocessor(config.preprocessing)
            X, y, scaler = preprocessor.prepare_sequences(
                data, 
                config.data.feature_columns,
                config.data.target_column
            )
            
            # Split data
            X_train, y_train, X_val, y_val, X_test, y_test = split_train_val_test(
                X, y, 
                train_ratio=config.preprocessing.train_ratio,
                val_ratio=config.preprocessing.validation_ratio
            )
            
            self.logger.info(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
            
            # Build model
            model_builder = LSTMStockModel(config.model)
            model = model_builder.build_model(
                input_shape=(X_train.shape[1], X_train.shape[2])
            )
            
            # Train model
            trainer = ModelTrainer(model, config.training)
            history = trainer.train(
                X_train, y_train,
                X_val, y_val,
                verbose=1
            )
            
            # Evaluate model
            evaluator = ModelEvaluator(model, scaler)
            metrics = evaluator.evaluate(X_test, y_test)
            
            self.logger.info(f"\nModel Performance for {model_name}:")
            self.logger.info(f"  RMSE: {metrics['rmse']:.4f}")
            self.logger.info(f"  MAE: {metrics['mae']:.4f}")
            self.logger.info(f"  R²: {metrics['r2']:.4f}")
            
            # Save model and scaler
            model_path = self.models_dir / f"{model_name}_model.h5"
            scaler_path = self.models_dir / f"{model_name}_scaler.pkl"
            
            model.save(str(model_path))
            save_scaler(scaler, str(scaler_path))
            
            self.logger.info(f"Model saved: {model_path}")
            self.logger.info(f"Scaler saved: {scaler_path}")
            
            # Store metadata
            metadata = {
                'model_name': model_name,
                'dataset': data_path.name,
                'model_path': str(model_path),
                'scaler_path': str(scaler_path),
                'metrics': metrics,
                'data_shape': {
                    'train': X_train.shape,
                    'val': X_val.shape,
                    'test': X_test.shape
                },
                'feature_columns': config.data.feature_columns,
                'target_column': config.data.target_column,
                'sequence_length': config.preprocessing.sequence_length
            }
            
            self.model_metadata[model_name] = metadata
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error training model {model_name}: {str(e)}")
            raise
    
    def train_all_models(self, custom_configs: Dict[str, Config] = None):
        """
        Train models for all discovered datasets.
        
        Args:
            custom_configs: Dictionary mapping dataset names to custom configs
        """
        datasets = self.discover_datasets()
        
        if not datasets:
            self.logger.warning("No datasets found in the processed directory!")
            return
        
        self.logger.info(f"\nStarting multi-model training for {len(datasets)} datasets\n")
        
        for data_path in datasets:
            # Create model name from dataset filename
            model_name = data_path.stem
            
            # Get custom config if provided
            config = None
            if custom_configs and model_name in custom_configs:
                config = custom_configs[model_name]
            
            try:
                metadata = self.train_model_for_dataset(
                    data_path, 
                    model_name,
                    config
                )
                self.trained_models[model_name] = metadata
                
            except Exception as e:
                self.logger.error(f"Failed to train model for {data_path.name}: {str(e)}")
                continue
        
        # Save metadata
        self.save_metadata()
        
        # Print summary
        self.print_training_summary()
    
    def save_metadata(self):
        """Save metadata for all trained models."""
        metadata_path = self.models_dir / "models_metadata.json"
        
        # Convert numpy types to native Python types for JSON serialization
        serializable_metadata = {}
        for model_name, metadata in self.model_metadata.items():
            serializable_metadata[model_name] = {
                'model_name': metadata['model_name'],
                'dataset': metadata['dataset'],
                'model_path': metadata['model_path'],
                'scaler_path': metadata['scaler_path'],
                'metrics': {
                    k: float(v) if isinstance(v, (np.floating, np.integer)) else v
                    for k, v in metadata['metrics'].items()
                },
                'feature_columns': metadata['feature_columns'],
                'target_column': metadata['target_column'],
                'sequence_length': metadata['sequence_length']
            }
        
        with open(metadata_path, 'w') as f:
            json.dump(serializable_metadata, f, indent=2)
        
        self.logger.info(f"\nMetadata saved: {metadata_path}")
    
    def print_training_summary(self):
        """Print summary of all trained models."""
        self.logger.info(f"\n{'='*80}")
        self.logger.info("TRAINING SUMMARY")
        self.logger.info(f"{'='*80}\n")
        
        if not self.trained_models:
            self.logger.info("No models were successfully trained.")
            return
        
        for model_name, metadata in self.trained_models.items():
            self.logger.info(f"Model: {model_name}")
            self.logger.info(f"  Dataset: {metadata['dataset']}")
            self.logger.info(f"  RMSE: {metadata['metrics']['rmse']:.4f}")
            self.logger.info(f"  MAE: {metadata['metrics']['mae']:.4f}")
            self.logger.info(f"  R²: {metadata['metrics']['r2']:.4f}")
            self.logger.info("")
        
        # Best model
        best_model = min(
            self.trained_models.items(),
            key=lambda x: x[1]['metrics']['rmse']
        )
        
        self.logger.info(f"Best performing model (lowest RMSE): {best_model[0]}")
        self.logger.info(f"  RMSE: {best_model[1]['metrics']['rmse']:.4f}\n")


def main():
    """Main execution function."""
    
    # Initialize multi-model trainer
    trainer = MultiModelTrainer(
        data_dir="data/processed",
        models_dir="models"
    )
    
    # Optional: Define custom configurations for specific datasets
    # custom_configs = {
    #     'lstm_ready_data': Config(
    #         model=ModelConfig(lstm_units=[64, 32]),
    #         training=TrainingConfig(epochs=100)
    #     )
    # }
    
    # Train all models
    trainer.train_all_models()
    
    print("\n✅ Multi-model training completed!")
    print("Models and metadata saved in: models/")
    print("Check logs/ directory for detailed training logs")


if __name__ == "__main__":
    main()
