"""
Model Trainer Module
====================
Handles training of LSTM models with callbacks and monitoring.
"""

import numpy as np
from tensorflow import keras
from tensorflow.keras import callbacks
from pathlib import Path
from typing import Optional, Tuple
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train LSTM models with proper monitoring and checkpointing."""
    
    def __init__(self, model: keras.Model, save_dir: str = 'models/saved_models'):
        """
        Initialize the trainer.
        
        Args:
            model: Compiled Keras model
            save_dir: Directory to save models and checkpoints
        """
        self.model = model
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.history = None
        
    def get_callbacks(self, checkpoint_path: str, 
                     early_stopping_patience: int = 15,
                     reduce_lr_patience: int = 10) -> list:
        """
        Get training callbacks.
        
        Args:
            checkpoint_path: Path to save model checkpoints
            early_stopping_patience: Patience for early stopping
            reduce_lr_patience: Patience for learning rate reduction
            
        Returns:
            List of Keras callbacks
        """
        callback_list = [
            # Model checkpoint
            callbacks.ModelCheckpoint(
                filepath=checkpoint_path,
                monitor='val_loss',
                save_best_only=True,
                save_weights_only=False,
                mode='min',
                verbose=1
            ),
            
            # Early stopping
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=early_stopping_patience,
                restore_best_weights=True,
                verbose=1
            ),
            
            # Reduce learning rate on plateau
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=reduce_lr_patience,
                min_lr=1e-7,
                verbose=1
            ),
            
            # TensorBoard logging
            callbacks.TensorBoard(
                log_dir=f'logs/tensorboard/{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                histogram_freq=1
            )
        ]
        
        return callback_list
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
             X_val: np.ndarray, y_val: np.ndarray,
             epochs: int = 100, batch_size: int = 32,
             early_stopping_patience: int = 15,
             reduce_lr_patience: int = 10) -> dict:
        """
        Train the model.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            epochs: Number of training epochs
            batch_size: Batch size
            early_stopping_patience: Patience for early stopping
            reduce_lr_patience: Patience for learning rate reduction
            
        Returns:
            Training history dictionary
        """
        logger.info("Starting model training...")
        
        # Create checkpoint path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_path = self.save_dir / f"model_checkpoint_{timestamp}.h5"
        
        # Get callbacks
        callback_list = self.get_callbacks(
            str(checkpoint_path),
            early_stopping_patience,
            reduce_lr_patience
        )
        
        # Train model
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callback_list,
            verbose=1
        )
        
        logger.info("Training completed!")
        
        # Save final model
        final_model_path = self.save_dir / f"final_model_{timestamp}.h5"
        self.model.save(str(final_model_path))
        logger.info(f"Final model saved to {final_model_path}")
        
        # Save training history
        self.save_training_history(timestamp)
        
        return self.history.history
    
    def save_training_history(self, timestamp: str) -> None:
        """
        Save training history to JSON file.
        
        Args:
            timestamp: Timestamp for filename
        """
        if self.history is None:
            logger.warning("No training history to save")
            return
        
        history_path = self.save_dir / f"training_history_{timestamp}.json"
        
        # Convert numpy values to Python types
        history_dict = {}
        for key, values in self.history.history.items():
            history_dict[key] = [float(v) for v in values]
        
        with open(history_path, 'w') as f:
            json.dump(history_dict, f, indent=4)
        
        logger.info(f"Training history saved to {history_path}")
    
    def get_best_epoch(self) -> Tuple[int, float]:
        """
        Get the best epoch based on validation loss.
        
        Returns:
            Tuple of (best_epoch, best_val_loss)
        """
        if self.history is None:
            raise ValueError("No training history available")
        
        val_losses = self.history.history['val_loss']
        best_epoch = np.argmin(val_losses)
        best_val_loss = val_losses[best_epoch]
        
        logger.info(f"Best epoch: {best_epoch + 1} with val_loss: {best_val_loss:.6f}")
        return best_epoch + 1, best_val_loss
