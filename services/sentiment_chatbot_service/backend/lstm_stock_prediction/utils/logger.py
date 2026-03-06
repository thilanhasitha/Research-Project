"""
Logger Utilities
================
Utilities for logging and monitoring.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(name: str = 'lstm_stock_prediction',
                log_dir: str = 'logs',
                log_file: Optional[str] = None,
                level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_dir: Directory to save log files
        log_file: Log filename (auto-generated if None)
        level: Logging level
        
    Returns:
        Configured logger
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler
    if log_file is None:
        log_file = f"lstm_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    file_handler = logging.FileHandler(log_path / log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    logger.info(f"Logger initialized. Log file: {log_path / log_file}")
    
    return logger


class ProgressTracker:
    """Track and log training progress."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize progress tracker.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.start_time = None
        self.epoch_times = []
    
    def start(self) -> None:
        """Start tracking."""
        self.start_time = datetime.now()
        self.logger.info("="*60)
        self.logger.info("Training started")
        self.logger.info("="*60)
    
    def log_epoch(self, epoch: int, total_epochs: int, 
                  metrics: dict) -> None:
        """
        Log epoch information.
        
        Args:
            epoch: Current epoch number
            total_epochs: Total number of epochs
            metrics: Dictionary of metrics
        """
        epoch_start = datetime.now()
        
        metrics_str = " - ".join([f"{k}: {v:.6f}" for k, v in metrics.items()])
        self.logger.info(f"Epoch {epoch}/{total_epochs} - {metrics_str}")
        
        self.epoch_times.append((datetime.now() - epoch_start).total_seconds())
    
    def finish(self) -> None:
        """Finish tracking and log summary."""
        if self.start_time is None:
            return
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        avg_epoch_time = sum(self.epoch_times) / len(self.epoch_times) if self.epoch_times else 0
        
        self.logger.info("="*60)
        self.logger.info("Training completed")
        self.logger.info(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        self.logger.info(f"Average epoch time: {avg_epoch_time:.2f} seconds")
        self.logger.info("="*60)
