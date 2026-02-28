"""
Prediction Script
=================
Script to make predictions using trained LSTM model.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

import numpy as np
import pandas as pd
import argparse
from tensorflow import keras
from src.data_loader import StockDataLoader
from src.data_preprocessor import StockDataPreprocessor
from src.evaluator import ModelEvaluator
from utils.visualization import Visualizer
from utils.helpers import load_scaler
from utils.logger import setup_logger


def main():
    """Main prediction pipeline."""
    
    parser = argparse.ArgumentParser(description='Make predictions using trained LSTM model')
    parser.add_argument('--model_path', type=str, required=True,
                       help='Path to trained model')
    parser.add_argument('--data_path', type=str, required=True,
                       help='Path to data CSV file')
    parser.add_argument('--scaler_path', type=str, required=True,
                       help='Path to saved scaler')
    parser.add_argument('--output_path', type=str, default='results/predictions.csv',
                       help='Path to save predictions')
    parser.add_argument('--sequence_length', type=int, default=12,
                       help='Sequence length used during training')
    parser.add_argument('--n_future_steps', type=int, default=0,
                       help='Number of future steps to predict')
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger(name='lstm_prediction', log_dir='logs')
    
    logger.info("Starting LSTM Stock Prediction Pipeline")
    logger.info(f"Model: {args.model_path}")
    logger.info(f"Data: {args.data_path}")
    
    # Load model
    logger.info("Loading trained model...")
    model = keras.models.load_model(args.model_path)
    logger.info("Model loaded successfully")
    
    # Load scaler
    logger.info("Loading scaler...")
    scaler = load_scaler(args.scaler_path)
    
    # Load data
    logger.info("Loading data...")
    data_loader = StockDataLoader(args.data_path)
    data = data_loader.load_csv()
    
    # Preprocess data
    logger.info("Preprocessing data...")
    feature_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    preprocessor = StockDataPreprocessor(
        feature_columns=feature_columns,
        target_column='Close'
    )
    preprocessor.scaler = scaler
    
    # Handle missing values
    data = preprocessor.handle_missing_values(data)
    
    # Normalize data
    scaled_data = scaler.transform(data[feature_columns].values)
    
    # Create sequences
    X, y = preprocessor.create_sequences(
        scaled_data,
        sequence_length=args.sequence_length,
        target_index=feature_columns.index('Close')
    )
    
    # Make predictions
    logger.info("Making predictions...")
    evaluator = ModelEvaluator(model)
    predictions = evaluator.predict(X)
    
    # Inverse transform predictions
    predictions_unscaled = scaler.inverse_transform(
        np.concatenate([predictions, 
                       np.zeros((len(predictions), len(feature_columns)-1))], 
                       axis=1)
    )[:, 0]
    
    y_unscaled = scaler.inverse_transform(
        np.concatenate([y.reshape(-1, 1), 
                       np.zeros((len(y), len(feature_columns)-1))], 
                       axis=1)
    )[:, 0]
    
    # Create results DataFrame
    dates = data['Date'].iloc[args.sequence_length:].reset_index(drop=True)
    results_df = evaluator.create_results_dataframe(
        y_unscaled,
        predictions_unscaled,
        dates=dates
    )
    
    # Save predictions
    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)
    logger.info(f"Predictions saved to {output_path}")
    
    # Evaluate if we have true values
    metrics = evaluator.evaluate(X, y)
    logger.info("Performance Metrics:")
    for metric, value in metrics.items():
        logger.info(f"  {metric.upper()}: {value:.6f}")
    
    # Future predictions
    if args.n_future_steps > 0:
        logger.info(f"Making {args.n_future_steps} future predictions...")
        last_sequence = X[-1]
        future_predictions = evaluator.predict_future(last_sequence, args.n_future_steps)
        
        # Inverse transform
        future_predictions_unscaled = scaler.inverse_transform(
            np.concatenate([future_predictions.reshape(-1, 1), 
                           np.zeros((len(future_predictions), len(feature_columns)-1))], 
                           axis=1)
        )[:, 0]
        
        logger.info("Future predictions:")
        for i, pred in enumerate(future_predictions_unscaled, 1):
            logger.info(f"  Step {i}: {pred:.2f}")
    
    # Visualize
    logger.info("Creating visualizations...")
    visualizer = Visualizer(save_dir='results/plots')
    
    visualizer.plot_predictions(
        y_unscaled,
        predictions_unscaled,
        dates=dates,
        title='Actual vs Predicted Stock Prices',
        save_name='predictions.png'
    )
    
    logger.info("Prediction pipeline completed successfully!")


if __name__ == "__main__":
    main()
