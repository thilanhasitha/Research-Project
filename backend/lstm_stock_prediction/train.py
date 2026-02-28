"""
Main Training Script
====================
Main script to train LSTM model on stock price data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

import numpy as np
import pandas as pd
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
    print_data_info,
    save_scaler,
    save_metrics,
    get_model_parameter_count
)


def main():
    """Main training pipeline."""
    
    # Initialize configuration
    config = Config()
    config.print_config()
    
    # Setup logger
    logger = setup_logger(
        name='lstm_training',
        log_dir=config.paths.log_dir
    )
    
    logger.info("Starting LSTM Stock Prediction Training Pipeline")
    
    # ========== Data Loading ==========
    logger.info("Step 1: Loading data...")
    data_loader = StockDataLoader(config.data.raw_data_path)
    
    try:
        # Detect file type and load accordingly
        file_path = Path(config.data.raw_data_path)
        if file_path.suffix.lower() in ['.xls', '.xlsx']:
            logger.info(f"Loading Excel file: {config.data.raw_data_path}")
            data = data_loader.load_excel(date_column=config.data.date_column)
        else:
            logger.info(f"Loading CSV file: {config.data.raw_data_path}")
            data = data_loader.load_csv(date_column=config.data.date_column)
    except FileNotFoundError:
        logger.error(f"Data file not found: {config.data.raw_data_path}")
        logger.info("Please place your stock data (CSV or Excel) in data/raw/ directory")
        logger.info("Expected columns: Date, Open, High, Low, Close, Volume")
        return
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        logger.info("Please check your data file format and columns")
        return
    
    # Validate data
    required_columns = config.data.feature_columns + [config.data.date_column]
    if not data_loader.validate_data(required_columns):
        logger.error("Data validation failed")
        return
    
    logger.info(f"Loaded {len(data)} records")
    logger.info(f"Date range: {data[config.data.date_column].min()} to {data[config.data.date_column].max()}")
    
    # ========== Data Preprocessing ==========
    logger.info("Step 2: Preprocessing data...")
    preprocessor = StockDataPreprocessor(
        feature_columns=config.data.feature_columns,
        target_column=config.data.target_column
    )
    
    # Handle missing values
    data = preprocessor.handle_missing_values(
        data,
        method=config.preprocessing.missing_value_method
    )
    
    # Add technical indicators if configured
    if config.preprocessing.add_technical_indicators:
        logger.info("Adding technical indicators...")
        data = preprocessor.add_technical_indicators(data)
        # Update feature columns to include technical indicators
        config.data.feature_columns = [col for col in data.columns 
                                      if col != config.data.date_column]
    
    # Normalize data
    scaled_data = preprocessor.normalize_data(data)
    
    # Create sequences
    target_idx = config.data.feature_columns.index(config.data.target_column)
    X, y = preprocessor.create_sequences(
        scaled_data,
        sequence_length=config.preprocessing.sequence_length,
        target_index=target_idx
    )
    
    # Split data
    X_train, X_val, X_test, y_train, y_val, y_test = split_train_val_test(
        X, y,
        train_ratio=config.preprocessing.train_ratio,
        val_ratio=config.preprocessing.validation_ratio,
        test_ratio=config.preprocessing.test_ratio
    )
    
    print_data_info(X_train, X_val, X_test, y_train, y_val, y_test)
    
    # Save scaler for later use
    scaler_path = Path(config.paths.model_dir) / 'scaler.pkl'
    save_scaler(preprocessor.scaler, str(scaler_path))
    
    # ========== Model Building ==========
    logger.info("Step 3: Building model...")
    input_shape = (X_train.shape[1], X_train.shape[2])
    model_builder = LSTMStockModel(input_shape)
    
    # Build model based on configuration
    if config.model.model_type == 'simple_lstm':
        model = model_builder.build_simple_lstm(
            units=config.model.lstm_units[0],
            dropout=config.model.dropout_rate
        )
    elif config.model.model_type == 'stacked_lstm':
        model = model_builder.build_stacked_lstm(
            units=config.model.lstm_units,
            dropout=config.model.dropout_rate
        )
    elif config.model.model_type == 'bidirectional_lstm':
        model = model_builder.build_bidirectional_lstm(
            units=config.model.lstm_units,
            dropout=config.model.dropout_rate
        )
    elif config.model.model_type == 'attention_lstm':
        model = model_builder.build_attention_lstm(
            units=config.model.lstm_units[0],
            dropout=config.model.dropout_rate
        )
    else:
        logger.error(f"Unknown model type: {config.model.model_type}")
        return
    
    # Compile model
    model_builder.compile_model(
        learning_rate=config.model.learning_rate,
        optimizer=config.model.optimizer
    )
    
    logger.info("Model architecture:")
    model_builder.get_model_summary()
    
    params = get_model_parameter_count(model)
    logger.info(f"Model parameters: {params}")
    
    # ========== Model Training ==========
    logger.info("Step 4: Training model...")
    trainer = ModelTrainer(model, save_dir=config.paths.saved_models_dir)
    
    history = trainer.train(
        X_train, y_train,
        X_val, y_val,
        epochs=config.training.epochs,
        batch_size=config.training.batch_size,
        early_stopping_patience=config.training.early_stopping_patience,
        reduce_lr_patience=config.training.reduce_lr_patience
    )
    
    best_epoch, best_val_loss = trainer.get_best_epoch()
    logger.info(f"Best model at epoch {best_epoch} with validation loss: {best_val_loss:.6f}")
    
    # ========== Model Evaluation ==========
    logger.info("Step 5: Evaluating model...")
    evaluator = ModelEvaluator(model)
    
    # Evaluate on test set
    logger.info("Test set evaluation:")
    test_metrics = evaluator.evaluate(X_test, y_test)
    
    # Calculate directional accuracy
    y_test_pred = evaluator.predictions
    dir_accuracy = evaluator.calculate_directional_accuracy(y_test, y_test_pred)
    test_metrics['directional_accuracy'] = dir_accuracy
    
    # Save metrics
    metrics_path = Path(config.paths.results_dir) / 'metrics' / 'test_metrics.json'
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    save_metrics(test_metrics, str(metrics_path))
    
    # ========== Visualization ==========
    logger.info("Step 6: Creating visualizations...")
    visualizer = Visualizer(save_dir=config.paths.results_dir + '/plots')
    
    # Plot training history
    visualizer.plot_training_history(
        history,
        metrics=['loss', 'mae'],
        save_name='training_history.png'
    )
    
    # Plot predictions
    y_test_pred_unscaled = preprocessor.scaler.inverse_transform(
        np.concatenate([y_test_pred, 
                       np.zeros((len(y_test_pred), len(config.data.feature_columns)-1))], 
                       axis=1)
    )[:, 0]
    
    y_test_unscaled = preprocessor.scaler.inverse_transform(
        np.concatenate([y_test.reshape(-1, 1), 
                       np.zeros((len(y_test), len(config.data.feature_columns)-1))], 
                       axis=1)
    )[:, 0]
    
    visualizer.plot_predictions(
        y_test_unscaled,
        y_test_pred_unscaled,
        title='Test Set: Actual vs Predicted Prices',
        save_name='test_predictions.png'
    )
    
    # Plot prediction errors
    errors = evaluator.get_prediction_errors(y_test, y_test_pred)
    visualizer.plot_prediction_errors(
        errors,
        save_name='prediction_errors.png'
    )
    
    # Plot residuals
    visualizer.plot_residuals(
        y_test,
        y_test_pred,
        save_name='residuals.png'
    )
    
    logger.info("="*60)
    logger.info("Training pipeline completed successfully!")
    logger.info(f"Models saved in: {config.paths.saved_models_dir}")
    logger.info(f"Results saved in: {config.paths.results_dir}")
    logger.info("="*60)


if __name__ == "__main__":
    main()
