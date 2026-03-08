"""
LSTM Model Architecture
========================
Defines LSTM model architectures for stock price prediction.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from typing import Tuple, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LSTMStockModel:
    """Build and compile LSTM models for stock price prediction."""
    
    def __init__(self, input_shape: Tuple[int, int]):
        """
        Initialize the LSTM model builder.
        
        Args:
            input_shape: Shape of input sequences (sequence_length, n_features)
        """
        self.input_shape = input_shape
        self.model = None
        
    def build_simple_lstm(self, units: int = 50, dropout: float = 0.2) -> keras.Model:
        """
        Build a simple LSTM model.
        
        Args:
            units: Number of LSTM units
            dropout: Dropout rate
            
        Returns:
            Compiled Keras model
        """
        model = models.Sequential([
            layers.LSTM(units, return_sequences=False, input_shape=self.input_shape),
            layers.Dropout(dropout),
            layers.Dense(1)
        ])
        
        logger.info(f"Built simple LSTM model with {units} units")
        self.model = model
        return model
    
    def build_stacked_lstm(self, units: List[int] = [50, 50], 
                          dropout: float = 0.2) -> keras.Model:
        """
        Build a stacked LSTM model with multiple layers.
        
        Args:
            units: List of units for each LSTM layer
            dropout: Dropout rate
            
        Returns:
            Compiled Keras model
        """
        model = models.Sequential()
        
        # Add first LSTM layer
        model.add(layers.LSTM(
            units[0], 
            return_sequences=True if len(units) > 1 else False,
            input_shape=self.input_shape
        ))
        model.add(layers.Dropout(dropout))
        
        # Add middle LSTM layers
        for i in range(1, len(units) - 1):
            model.add(layers.LSTM(units[i], return_sequences=True))
            model.add(layers.Dropout(dropout))
        
        # Add last LSTM layer if more than one layer
        if len(units) > 1:
            model.add(layers.LSTM(units[-1], return_sequences=False))
            model.add(layers.Dropout(dropout))
        
        # Output layer
        model.add(layers.Dense(1))
        
        logger.info(f"Built stacked LSTM model with layers: {units}")
        self.model = model
        return model
    
    def build_bidirectional_lstm(self, units: List[int] = [50, 50], 
                                dropout: float = 0.2) -> keras.Model:
        """
        Build a bidirectional LSTM model.
        
        Args:
            units: List of units for each LSTM layer
            dropout: Dropout rate
            
        Returns:
            Compiled Keras model
        """
        model = models.Sequential()
        
        # Add first Bidirectional LSTM layer
        model.add(layers.Bidirectional(
            layers.LSTM(
                units[0], 
                return_sequences=True if len(units) > 1 else False
            ),
            input_shape=self.input_shape
        ))
        model.add(layers.Dropout(dropout))
        
        # Add middle Bidirectional LSTM layers
        for i in range(1, len(units) - 1):
            model.add(layers.Bidirectional(
                layers.LSTM(units[i], return_sequences=True)
            ))
            model.add(layers.Dropout(dropout))
        
        # Add last Bidirectional LSTM layer if more than one layer
        if len(units) > 1:
            model.add(layers.Bidirectional(
                layers.LSTM(units[-1], return_sequences=False)
            ))
            model.add(layers.Dropout(dropout))
        
        # Output layer
        model.add(layers.Dense(1))
        
        logger.info(f"Built bidirectional LSTM model with layers: {units}")
        self.model = model
        return model
    
    def build_attention_lstm(self, units: int = 50, 
                           dropout: float = 0.2) -> keras.Model:
        """
        Build an LSTM model with attention mechanism.
        
        Args:
            units: Number of LSTM units
            dropout: Dropout rate
            
        Returns:
            Compiled Keras model
        """
        inputs = layers.Input(shape=self.input_shape)
        
        # LSTM layer
        lstm_out = layers.LSTM(units, return_sequences=True)(inputs)
        lstm_out = layers.Dropout(dropout)(lstm_out)
        
        # Attention mechanism
        attention = layers.Dense(1, activation='tanh')(lstm_out)
        attention = layers.Flatten()(attention)
        attention = layers.Activation('softmax')(attention)
        attention = layers.RepeatVector(units)(attention)
        attention = layers.Permute([2, 1])(attention)
        
        # Apply attention
        sent_representation = layers.multiply([lstm_out, attention])
        sent_representation = layers.Lambda(
            lambda xin: tf.reduce_sum(xin, axis=1)
        )(sent_representation)
        
        # Output layer
        output = layers.Dense(1)(sent_representation)
        
        model = models.Model(inputs=inputs, outputs=output)
        
        logger.info(f"Built attention LSTM model with {units} units")
        self.model = model
        return model
    
    def build_deep_lstm(self, units: List[int] = [128, 128, 64, 32], 
                       dropout: float = 0.3) -> keras.Model:
        """
        Build a deep LSTM model with batch normalization for better performance.
        
        Args:
            units: List of units for each LSTM layer
            dropout: Dropout rate
            
        Returns:
            Compiled Keras model
        """
        model = models.Sequential()
        
        # First LSTM layer with BatchNormalization
        model.add(layers.LSTM(
            units[0], 
            return_sequences=True,
            input_shape=self.input_shape,
            kernel_regularizer=keras.regularizers.l2(0.001)
        ))
        model.add(layers.BatchNormalization())
        model.add(layers.Dropout(dropout))
        
        # Middle LSTM layers
        for i in range(1, len(units) - 1):
            model.add(layers.LSTM(
                units[i], 
                return_sequences=True,
                kernel_regularizer=keras.regularizers.l2(0.001)
            ))
            model.add(layers.BatchNormalization())
            model.add(layers.Dropout(dropout))
        
        # Last LSTM layer
        if len(units) > 1:
            model.add(layers.LSTM(
                units[-1], 
                return_sequences=False,
                kernel_regularizer=keras.regularizers.l2(0.001)
            ))
            model.add(layers.BatchNormalization())
            model.add(layers.Dropout(dropout))
        
        # Dense layers for better learning
        model.add(layers.Dense(32, activation='relu'))
        model.add(layers.Dropout(dropout * 0.5))
        model.add(layers.Dense(16, activation='relu'))
        
        # Output layer
        model.add(layers.Dense(1))
        
        logger.info(f"Built deep LSTM model with layers: {units}")
        self.model = model
        return model
    
    def build_hybrid_cnn_lstm(self, lstm_units: List[int] = [100, 50], 
                             dropout: float = 0.3) -> keras.Model:
        """
        Build a hybrid CNN-LSTM model for feature extraction and time-series learning.
        
        Args:
            lstm_units: List of units for LSTM layers
            dropout: Dropout rate
            
        Returns:
            Compiled Keras model
        """
        model = models.Sequential()
        
        # CNN layers for feature extraction
        model.add(layers.Conv1D(
            filters=64, 
            kernel_size=3, 
            activation='relu',
            input_shape=self.input_shape
        ))
        model.add(layers.MaxPooling1D(pool_size=2))
        model.add(layers.Dropout(dropout * 0.5))
        
        model.add(layers.Conv1D(filters=64, kernel_size=3, activation='relu'))
        model.add(layers.Dropout(dropout * 0.5))
        
        # LSTM layers
        for i, units in enumerate(lstm_units):
            return_seq = i < len(lstm_units) - 1
            model.add(layers.LSTM(units, return_sequences=return_seq))
            model.add(layers.Dropout(dropout))
        
        # Dense layers
        model.add(layers.Dense(25, activation='relu'))
        model.add(layers.Dense(1))
        
        logger.info(f"Built hybrid CNN-LSTM model")
        self.model = model
        return model
    
    def compile_model(self, learning_rate: float = 0.001, 
                     optimizer: str = 'adam') -> None:
        """
        Compile the model.
        
        Args:
            learning_rate: Learning rate for optimizer
            optimizer: Optimizer name ('adam', 'rmsprop', 'sgd')
        """
        if self.model is None:
            raise ValueError("Model not built yet. Build a model first.")
        
        if optimizer == 'adam':
            opt = keras.optimizers.Adam(learning_rate=learning_rate)
        elif optimizer == 'rmsprop':
            opt = keras.optimizers.RMSprop(learning_rate=learning_rate)
        elif optimizer == 'sgd':
            opt = keras.optimizers.SGD(learning_rate=learning_rate)
        else:
            raise ValueError(f"Unknown optimizer: {optimizer}")
        
        self.model.compile(
            optimizer=opt,
            loss='mean_squared_error',
            metrics=['mae', 'mse']
        )
        
        logger.info(f"Compiled model with {optimizer} optimizer (lr={learning_rate})")
    
    def get_model_summary(self) -> None:
        """Print model summary."""
        if self.model is None:
            logger.error("Model not built yet")
            return
        
        self.model.summary()
    
    def save_model(self, filepath: str) -> None:
        """
        Save the model to disk.
        
        Args:
            filepath: Path to save the model
        """
        if self.model is None:
            raise ValueError("Model not built yet")
        
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        Load a model from disk.
        
        Args:
            filepath: Path to the saved model
        """
        self.model = keras.models.load_model(filepath)
        logger.info(f"Model loaded from {filepath}")
