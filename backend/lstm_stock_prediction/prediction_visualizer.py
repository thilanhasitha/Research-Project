"""
Prediction Visualization Module
================================
Visualizations specifically for API predictions and ensemble results.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class PredictionVisualizer:
    """Visualizer for prediction results and ensemble outputs."""
    
    def __init__(self, results_dir: str = 'results'):
        """
        Initialize prediction visualizer.
        
        Args:
            results_dir: Base directory for results
        """
        self.results_dir = Path(results_dir)
        self.plots_dir = self.results_dir / 'plots'
        self.data_dir = self.results_dir / 'data'
        
        # Create directories
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_prediction_id(self) -> str:
        """Generate unique prediction ID based on timestamp."""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    def plot_ensemble_predictions(
        self,
        symbol: str,
        historical_data: np.ndarray,
        ensemble_prediction: List[float],
        individual_predictions: Dict[str, Dict],
        confidence_intervals: List[float],
        save_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create comprehensive visualization of ensemble predictions.
        
        Args:
            symbol: Stock symbol
            historical_data: Historical price data
            ensemble_prediction: Ensemble prediction values
            individual_predictions: Dictionary of individual model predictions
            confidence_intervals: Confidence intervals (std dev)
            save_id: Optional prediction ID
            
        Returns:
            Dictionary with paths to saved plots
        """
        if save_id is None:
            save_id = self.generate_prediction_id()
        
        plots = {}
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.25)
        
        # 1. Main prediction plot with confidence bands
        ax1 = fig.add_subplot(gs[0, :])
        plots['main'] = self._plot_main_prediction(
            ax1, symbol, historical_data, ensemble_prediction, 
            confidence_intervals, individual_predictions
        )
        
        # 2. Individual model predictions comparison
        ax2 = fig.add_subplot(gs[1, 0])
        self._plot_model_comparison(ax2, individual_predictions, ensemble_prediction)
        
        # 3. Model weights pie chart
        ax3 = fig.add_subplot(gs[1, 1])
        self._plot_model_weights(ax3, individual_predictions)
        
        # 4. Confidence level bar chart
        ax4 = fig.add_subplot(gs[2, 0])
        self._plot_confidence_levels(ax4, confidence_intervals, ensemble_prediction)
        
        # 5. Prediction summary table
        ax5 = fig.add_subplot(gs[2, 1])
        self._plot_summary_table(ax5, symbol, ensemble_prediction, individual_predictions)
        
        # Save comprehensive plot
        plot_filename = f"{symbol}_{save_id}_ensemble_full.png"
        plot_path = self.plots_dir / plot_filename
        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        plots['full'] = str(plot_path.relative_to(self.results_dir))
        
        # Create individual focused plots
        plots['individual'] = self._create_individual_plot(
            symbol, ensemble_prediction, individual_predictions, save_id
        )
        
        plots['trend'] = self._create_trend_plot(
            symbol, historical_data, ensemble_prediction, save_id
        )
        
        logger.info(f"Generated ensemble visualizations: {save_id}")
        return plots
    
    def _plot_main_prediction(
        self,
        ax,
        symbol: str,
        historical_data: np.ndarray,
        ensemble_prediction: List[float],
        confidence_intervals: List[float],
        individual_predictions: Dict
    ) -> str:
        """Plot main prediction with confidence bands."""
        # Extract close prices (assuming index 3)
        if len(historical_data.shape) == 3:
            historical_prices = historical_data[0, :, 3]  # Close price
        else:
            historical_prices = historical_data[:, 3]
        
        n_hist = len(historical_prices)
        n_pred = len(ensemble_prediction)
        
        # X-axis
        hist_x = np.arange(n_hist)
        pred_x = np.arange(n_hist, n_hist + n_pred)
        
        # Plot historical data
        ax.plot(hist_x, historical_prices, 'o-', label='Historical', 
                linewidth=2, markersize=4, color='#2E86AB')
        
        # Plot ensemble prediction
        ax.plot(pred_x, ensemble_prediction, 'o-', label='Ensemble Prediction',
                linewidth=2.5, markersize=6, color='#A23B72')
        
        # Plot confidence bands
        ensemble_arr = np.array(ensemble_prediction)
        confidence_arr = np.array(confidence_intervals)
        
        ax.fill_between(
            pred_x,
            ensemble_arr - confidence_arr,
            ensemble_arr + confidence_arr,
            alpha=0.2,
            color='#A23B72',
            label='Confidence Interval (±1σ)'
        )
        
        # Plot individual model predictions (lighter)
        for model_name, model_data in individual_predictions.items():
            model_preds = model_data['predictions']
            ax.plot(pred_x, model_preds, '--', alpha=0.3, linewidth=1)
        
        ax.set_xlabel('Time Steps', fontsize=11, fontweight='bold')
        ax.set_ylabel('Price', fontsize=11, fontweight='bold')
        ax.set_title(f'{symbol} - Ensemble Prediction with Confidence Bands', 
                    fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        return "main_prediction"
    
    def _plot_model_comparison(self, ax, individual_predictions: Dict, ensemble_prediction: List[float]):
        """Plot bar chart comparing individual model predictions."""
        if not individual_predictions:
            ax.text(0.5, 0.5, 'No individual model data', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        models = list(individual_predictions.keys())
        # Get first prediction value from each model
        pred_values = [individual_predictions[m]['predictions'][0] for m in models]
        ensemble_val = ensemble_prediction[0]
        
        colors = ['#3498db' if abs(v - ensemble_val) < 0.5 else '#e74c3c' 
                 for v in pred_values]
        
        bars = ax.barh(models, pred_values, color=colors, alpha=0.7)
        ax.axvline(ensemble_val, color='#A23B72', linestyle='--', 
                  linewidth=2, label='Ensemble')
        
        ax.set_xlabel('Predicted Value', fontsize=10, fontweight='bold')
        ax.set_title('Individual Model Predictions', fontsize=11, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, axis='x')
    
    def _plot_model_weights(self, ax, individual_predictions: Dict):
        """Plot pie chart of model weights."""
        if not individual_predictions:
            ax.text(0.5, 0.5, 'No weight data', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        models = list(individual_predictions.keys())
        weights = [individual_predictions[m]['weight'] for m in models]
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(models)))
        
        wedges, texts, autotexts = ax.pie(
            weights,
            labels=models,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        for text in texts:
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)
        
        ax.set_title('Model Weights in Ensemble', fontsize=11, fontweight='bold')
    
    def _plot_confidence_levels(self, ax, confidence_intervals: List[float], 
                                ensemble_prediction: List[float]):
        """Plot confidence levels for each prediction step."""
        steps = range(1, len(confidence_intervals) + 1)
        
        # Calculate confidence as percentage (lower std = higher confidence)
        max_std = max(confidence_intervals) if confidence_intervals else 1
        confidence_pct = [100 * (1 - (ci / (max_std + 0.01))) for ci in confidence_intervals]
        
        colors = ['#27AE60' if c > 70 else '#F39C12' if c > 40 else '#E74C3C' 
                 for c in confidence_pct]
        
        bars = ax.bar(steps, confidence_pct, color=colors, alpha=0.7)
        
        # Add threshold lines
        ax.axhline(70, color='green', linestyle='--', alpha=0.5, linewidth=1)
        ax.axhline(40, color='orange', linestyle='--', alpha=0.5, linewidth=1)
        
        ax.set_xlabel('Prediction Step', fontsize=10, fontweight='bold')
        ax.set_ylabel('Confidence (%)', fontsize=10, fontweight='bold')
        ax.set_title('Prediction Confidence Levels', fontsize=11, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3, axis='y')
    
    def _plot_summary_table(self, ax, symbol: str, ensemble_prediction: List[float],
                           individual_predictions: Dict):
        """Display summary statistics as a table."""
        ax.axis('tight')
        ax.axis('off')
        
        # Prepare data
        pred_val = ensemble_prediction[0] if ensemble_prediction else 0
        n_models = len(individual_predictions)
        
        if individual_predictions:
            avg_rmse = np.mean([m['rmse'] for m in individual_predictions.values()])
            best_model = min(individual_predictions.items(), 
                           key=lambda x: x[1]['rmse'])[0]
        else:
            avg_rmse = 0
            best_model = "N/A"
        
        table_data = [
            ['Metric', 'Value'],
            ['Symbol', symbol],
            ['Ensemble Prediction', f'{pred_val:.4f}'],
            ['Number of Models', str(n_models)],
            ['Average RMSE', f'{avg_rmse:.4f}'],
            ['Best Model', best_model],
            ['Timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        table = ax.table(
            cellText=table_data,
            cellLoc='left',
            loc='center',
            colWidths=[0.4, 0.6]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Style header row
        for i in range(2):
            table[(0, i)].set_facecolor('#34495E')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Alternate row colors
        for i in range(1, len(table_data)):
            for j in range(2):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#ECF0F1')
        
        ax.set_title('Prediction Summary', fontsize=11, fontweight='bold', pad=20)
    
    def _create_individual_plot(
        self,
        symbol: str,
        ensemble_prediction: List[float],
        individual_predictions: Dict,
        save_id: str
    ) -> str:
        """Create focused plot of individual model predictions."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if not individual_predictions:
            ax.text(0.5, 0.5, 'No individual model data available',
                   ha='center', va='center', fontsize=12)
        else:
            x = range(len(ensemble_prediction))
            
            # Plot each model
            for model_name, model_data in individual_predictions.items():
                preds = model_data['predictions']
                weight = model_data['weight']
                ax.plot(x, preds, 'o-', label=f"{model_name} (w={weight:.2f})",
                       alpha=0.7, linewidth=2, markersize=5)
            
            # Plot ensemble
            ax.plot(x, ensemble_prediction, 'o-', label='Ensemble',
                   linewidth=3, markersize=7, color='#A23B72')
            
            ax.set_xlabel('Prediction Step', fontsize=11, fontweight='bold')
            ax.set_ylabel('Predicted Value', fontsize=11, fontweight='bold')
            ax.set_title(f'{symbol} - Individual Model Predictions vs Ensemble',
                        fontsize=13, fontweight='bold')
            ax.legend(loc='best', fontsize=9)
            ax.grid(True, alpha=0.3)
        
        plot_filename = f"{symbol}_{save_id}_individual_models.png"
        plot_path = self.plots_dir / plot_filename
        plt.savefig(plot_path, dpi=200, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(plot_path.relative_to(self.results_dir))
    
    def _create_trend_plot(
        self,
        symbol: str,
        historical_data: np.ndarray,
        ensemble_prediction: List[float],
        save_id: str
    ) -> str:
        """Create trend visualization."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Extract close prices
        if len(historical_data.shape) == 3:
            historical_prices = historical_data[0, :, 3]
        else:
            historical_prices = historical_data[:, 3]
        
        # Combine historical and predicted
        all_prices = np.concatenate([historical_prices, ensemble_prediction])
        x_all = range(len(all_prices))
        
        # Split into historical and prediction
        n_hist = len(historical_prices)
        
        ax.plot(x_all[:n_hist], all_prices[:n_hist], 'o-',
               label='Historical', linewidth=2.5, color='#2E86AB', markersize=5)
        ax.plot(x_all[n_hist-1:], all_prices[n_hist-1:], 'o-',
               label='Predicted', linewidth=2.5, color='#E63946', markersize=6)
        
        # Add vertical line separator
        ax.axvline(n_hist - 0.5, color='gray', linestyle='--', 
                  alpha=0.5, linewidth=2, label='Prediction Start')
        
        # Calculate and show trend
        if len(ensemble_prediction) > 0:
            trend_pct = ((ensemble_prediction[-1] - historical_prices[-1]) / 
                        historical_prices[-1] * 100)
            trend_text = f"Predicted Change: {trend_pct:+.2f}%"
            ax.text(0.02, 0.98, trend_text, transform=ax.transAxes,
                   fontsize=11, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                   verticalalignment='top')
        
        ax.set_xlabel('Time Steps', fontsize=11, fontweight='bold')
        ax.set_ylabel('Price', fontsize=11, fontweight='bold')
        ax.set_title(f'{symbol} - Price Trend and Forecast',
                    fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plot_filename = f"{symbol}_{save_id}_trend.png"
        plot_path = self.plots_dir / plot_filename
        plt.savefig(plot_path, dpi=200, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(plot_path.relative_to(self.results_dir))
    
    def save_prediction_data(
        self,
        symbol: str,
        ensemble_prediction: List[float],
        individual_predictions: Dict,
        confidence_intervals: List[float],
        metadata: Dict,
        save_id: Optional[str] = None
    ) -> str:
        """
        Save prediction data as JSON and CSV.
        
        Args:
            symbol: Stock symbol
            ensemble_prediction: Ensemble predictions
            individual_predictions: Individual model predictions
            confidence_intervals: Confidence intervals
            metadata: Additional metadata
            save_id: Optional prediction ID
            
        Returns:
            Path to saved JSON file
        """
        if save_id is None:
            save_id = self.generate_prediction_id()
        
        # Prepare data structure
        data = {
            'prediction_id': save_id,
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'ensemble_prediction': ensemble_prediction,
            'confidence_intervals': confidence_intervals,
            'individual_models': individual_predictions,
            'metadata': metadata
        }
        
        # Save as JSON
        json_filename = f"{symbol}_{save_id}_prediction.json"
        json_path = self.data_dir / json_filename
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Save as CSV (simplified)
        csv_filename = f"{symbol}_{save_id}_prediction.csv"
        csv_path = self.data_dir / csv_filename
        
        df_data = {
            'step': range(len(ensemble_prediction)),
            'ensemble_prediction': ensemble_prediction,
            'confidence_interval': confidence_intervals
        }
        
        # Add individual models
        for model_name, model_data in individual_predictions.items():
            df_data[f'model_{model_name}'] = model_data['predictions']
        
        df = pd.DataFrame(df_data)
        df.to_csv(csv_path, index=False)
        
        logger.info(f"Saved prediction data: {save_id}")
        
        return str(json_path.relative_to(self.results_dir))
    
    def create_summary_report(
        self,
        symbol: str,
        prediction_data: Dict,
        plots: Dict[str, str],
        save_id: str
    ) -> str:
        """
        Create a summary report in HTML format.
        
        Args:
            symbol: Stock symbol
            prediction_data: Prediction data dictionary
            plots: Dictionary of plot paths
            save_id: Prediction ID
            
        Returns:
            Path to HTML report
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prediction Report - {symbol}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .metadata {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .metadata p {{ margin: 5px 0; }}
                .plot {{ margin: 30px 0; text-align: center; }}
                .plot img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }}
                .prediction-value {{ font-size: 24px; font-weight: bold; color: #e74c3c; }}
                .confidence {{ font-size: 18px; color: #27ae60; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #34495e; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>LSTM Stock Prediction Report</h1>
                
                <div class="metadata">
                    <p><strong>Symbol:</strong> {symbol}</p>
                    <p><strong>Prediction ID:</strong> {save_id}</p>
                    <p><strong>Timestamp:</strong> {prediction_data.get('timestamp', 'N/A')}</p>
                    <p><strong>Number of Models:</strong> {prediction_data.get('num_models', 'N/A')}</p>
                </div>
                
                <h2>Prediction Results</h2>
                <p class="prediction-value">Predicted Value: {prediction_data.get('ensemble_prediction', ['N/A'])[0]}</p>
                <p class="confidence">Confidence Level: {prediction_data.get('confidence_level', 'N/A')}</p>
                <p>{prediction_data.get('recommendation', '')}</p>
                
                <h2>Visualizations</h2>
                
                <div class="plot">
                    <h3>Full Ensemble Analysis</h3>
                    <img src="{plots.get('full', '')}" alt="Full Ensemble Plot">
                </div>
                
                <div class=" plot">
                    <h3>Individual Model Predictions</h3>
                    <img src="{plots.get('individual', '')}" alt="Individual Models Plot">
                </div>
                
                <div class="plot">
                    <h3>Price Trend</h3>
                    <img src="{plots.get('trend', '')}" alt="Trend Plot">
                </div>
                
                <h2>Model Performance</h2>
                <table>
                    <tr>
                        <th>Model Name</th>
                        <th>Prediction</th>
                        <th>Weight</th>
                        <th>RMSE</th>
                    </tr>
        """
        
        # Add individual model rows
        for model_name, model_data in prediction_data.get('individual_models', {}).items():
            pred_val = model_data['predictions'][0] if model_data['predictions'] else 'N/A'
            html_content += f"""
                    <tr>
                        <td>{model_name}</td>
                        <td>{pred_val}</td>
                        <td>{model_data.get('weight', 'N/A'):.4f}</td>
                        <td>{model_data.get('rmse', 'N/A'):.4f}</td>
                    </tr>
            """
        
        html_content += """
                </table>
                
                <p style="margin-top: 40px; text-align: center; color: #7f8c8d; font-size: 12px;">
                    Generated by LSTM Stock Prediction System
                </p>
            </div>
        </body>
        </html>
        """
        
        # Save HTML report
        report_filename = f"{symbol}_{save_id}_report.html"
        report_path = self.results_dir / report_filename
        
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML report: {save_id}")
        
        return str(report_path.relative_to(self.results_dir))
