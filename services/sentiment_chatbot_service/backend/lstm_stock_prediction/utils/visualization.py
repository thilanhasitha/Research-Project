"""
Visualization Utilities
=======================
Utilities for visualizing data, training progress, and predictions.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.colors
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
try:
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)
except:
    pass  # Ignore style errors


class Visualizer:
    """Visualization utilities for LSTM stock prediction."""
    
    def __init__(self, save_dir: str = 'results/plots'):
        """
        Initialize the visualizer.
        
        Args:
            save_dir: Directory to save plots
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_stock_data(self, data: pd.DataFrame, 
                       date_column: str = 'Date',
                       price_column: str = 'Close',
                       title: str = 'Stock Price Over Time',
                       save_name: Optional[str] = None) -> None:
        """
        Plot stock price data.
        
        Args:
            data: DataFrame with stock data
            date_column: Name of date column
            price_column: Name of price column
            title: Plot title
            save_name: Filename to save plot
        """
        plt.figure(figsize=(14, 6))
        plt.plot(data[date_column], data[price_column], linewidth=2)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_name:
            save_path = self.save_dir / save_name
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {save_path}")
        
        plt.show()
    
    def plot_training_history(self, history: Dict[str, List[float]],
                             metrics: List[str] = ['loss', 'mae'],
                             save_name: Optional[str] = None) -> None:
        """
        Plot training history.
        
        Args:
            history: Training history dictionary
            metrics: List of metrics to plot
            save_name: Filename to save plot
        """
        n_metrics = len(metrics)
        fig, axes = plt.subplots(1, n_metrics, figsize=(7*n_metrics, 5))
        
        if n_metrics == 1:
            axes = [axes]
        
        for idx, metric in enumerate(metrics):
            if metric in history:
                axes[idx].plot(history[metric], label=f'Train {metric}', linewidth=2)
                
                val_metric = f'val_{metric}'
                if val_metric in history:
                    axes[idx].plot(history[val_metric], 
                                 label=f'Validation {metric}', 
                                 linewidth=2)
                
                axes[idx].set_xlabel('Epoch', fontsize=12)
                axes[idx].set_ylabel(metric.upper(), fontsize=12)
                axes[idx].set_title(f'Model {metric.upper()}', fontsize=14, fontweight='bold')
                axes[idx].legend()
                axes[idx].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_name:
            save_path = self.save_dir / save_name
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Training history plot saved to {save_path}")
        
        plt.show()
    
    def plot_predictions(self, y_true: np.ndarray, 
                        y_pred: np.ndarray,
                        dates: Optional[pd.DatetimeIndex] = None,
                        title: str = 'Actual vs Predicted Stock Prices',
                        save_name: Optional[str] = None) -> None:
        """
        Plot actual vs predicted values.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            dates: Optional date index
            title: Plot title
            save_name: Filename to save plot
        """
        plt.figure(figsize=(14, 6))
        
        x_axis = dates if dates is not None else range(len(y_true))
        
        plt.plot(x_axis, y_true, label='Actual', linewidth=2, alpha=0.8)
        plt.plot(x_axis, y_pred, label='Predicted', linewidth=2, alpha=0.8)
        
        plt.xlabel('Date' if dates is not None else 'Sample', fontsize=12)
        plt.ylabel('Price', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_name:
            save_path = self.save_dir / save_name
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Predictions plot saved to {save_path}")
        
        plt.show()
    
    def plot_prediction_errors(self, errors: np.ndarray,
                              title: str = 'Prediction Errors Distribution',
                              save_name: Optional[str] = None) -> None:
        """
        Plot prediction errors distribution.
        
        Args:
            errors: Prediction errors
            title: Plot title
            save_name: Filename to save plot
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        axes[0].hist(errors, bins=50, edgecolor='black', alpha=0.7)
        axes[0].set_xlabel('Error', fontsize=12)
        axes[0].set_ylabel('Frequency', fontsize=12)
        axes[0].set_title('Error Distribution', fontsize=13, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # Q-Q plot
        from scipy import stats
        stats.probplot(errors.flatten(), dist="norm", plot=axes[1])
        axes[1].set_title('Q-Q Plot', fontsize=13, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_name:
            save_path = self.save_dir / save_name
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Error plot saved to {save_path}")
        
        plt.show()
    
    def plot_feature_correlation(self, data: pd.DataFrame,
                                features: List[str],
                                title: str = 'Feature Correlation Matrix',
                                save_name: Optional[str] = None) -> None:
        """
        Plot feature correlation heatmap.
        
        Args:
            data: DataFrame with features
            features: List of feature column names
            title: Plot title
            save_name: Filename to save plot
        """
        plt.figure(figsize=(10, 8))
        
        correlation = data[features].corr()
        
        sns.heatmap(correlation, annot=True, cmap='coolwarm', 
                   center=0, square=True, linewidths=1,
                   cbar_kws={"shrink": 0.8})
        
        plt.title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save_name:
            save_path = self.save_dir / save_name
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Correlation plot saved to {save_path}")
        
        plt.show()
    
    def plot_residuals(self, y_true: np.ndarray, 
                      y_pred: np.ndarray,
                      dates: Optional[pd.DatetimeIndex] = None,
                      title: str = 'Residual Plot',
                      save_name: Optional[str] = None) -> None:
        """
        Plot residuals over time.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            dates: Optional date index
            title: Plot title
            save_name: Filename to save plot
        """
        residuals = y_true.flatten() - y_pred.flatten()
        x_axis = dates if dates is not None else range(len(residuals))
        
        plt.figure(figsize=(14, 6))
        plt.scatter(x_axis, residuals, alpha=0.6)
        plt.axhline(y=0, color='r', linestyle='--', linewidth=2)
        plt.xlabel('Date' if dates is not None else 'Sample', fontsize=12)
        plt.ylabel('Residuals', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_name:
            save_path = self.save_dir / save_name
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Residual plot saved to {save_path}")
        
        plt.show()
    
    def plot_comparison_metrics(self, metrics_dict: Dict[str, Dict[str, float]],
                               title: str = 'Model Comparison',
                               save_name: Optional[str] = None) -> None:
        """
        Plot comparison of multiple models.
        
        Args:
            metrics_dict: Dictionary of model names to metrics
            title: Plot title
            save_name: Filename to save plot
        """
        df = pd.DataFrame(metrics_dict).T
        
        fig, axes = plt.subplots(1, len(df.columns), figsize=(5*len(df.columns), 5))
        
        if len(df.columns) == 1:
            axes = [axes]
        
        for idx, column in enumerate(df.columns):
            df[column].plot(kind='bar', ax=axes[idx], color='steelblue')
            axes[idx].set_title(f'{column.upper()}', fontsize=13, fontweight='bold')
            axes[idx].set_ylabel('Value', fontsize=11)
            axes[idx].grid(True, alpha=0.3, axis='y')
            axes[idx].tick_params(axis='x', rotation=45)
        
        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_name:
            save_path = self.save_dir / save_name
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Comparison plot saved to {save_path}")
        
        plt.show()
