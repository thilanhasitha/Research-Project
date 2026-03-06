"""
Generate Visualization Plots for RAG Integration
================================================
This script generates stock market visualization plots and saves them
with metadata for the plot retrieval service.
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.plot_manager import PlotManager

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_stock_data():
    """Load stock data from processed CSV."""
    data_path = project_root / "data" / "processed" / "stock_data_scaled.csv"
    
    if not data_path.exists():
        # Try alternative path
        data_path = project_root / "data" / "raw" / "stock_data.csv"
    
    if not data_path.exists():
        print(f"⚠ Warning: No stock data found at {data_path}")
        return None
    
    print(f"📊 Loading stock data from {data_path}")
    df = pd.read_csv(data_path)
    
    # Ensure Date column exists and is parsed
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    elif 'date' in df.columns:
        df['Date'] = pd.to_datetime(df['date'])
        
    return df

def generate_price_plot(df, plot_manager):
    """Generate stock closing price over time plot."""
    print("\n📈 Generating Stock Price Plot...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if 'Date' in df.columns and 'Close' in df.columns:
        ax.plot(df['Date'], df['Close'], linewidth=2, color='#2E86AB')
        ax.set_title('Stock Closing Price Over Time', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Closing Price (LKR)', fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plot_manager.save_plot(
            plot_id="stock_price_time_series",
            title="Stock Closing Price Over Time",
            description="Historical closing price trend showing the stock's performance over time. This visualization helps identify long-term trends, support/resistance levels, and overall market sentiment.",
            keywords=["stock", "price", "closing", "time series", "trend", "historical", "chart"],
            category="price",
            fig=fig
        )
        
        plt.close()
        print("✓ Stock Price Plot saved")
    else:
        print("⚠ Skipping: Required columns (Date, Close) not found")
        plt.close()

def generate_volume_plot(df, plot_manager):
    """Generate trading volume plot."""
    print("\n📊 Generating Trading Volume Plot...")
    
    if 'Date' not in df.columns or 'Volume' not in df.columns:
        print("⚠ Skipping: Required columns (Date, Volume) not found")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.bar(df['Date'], df['Volume'], color='#A23B72', alpha=0.7)
    ax.set_title('Trading Volume Over Time', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Volume', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plot_manager.save_plot(
        plot_id="trading_volume_time_series",
        title="Trading Volume Over Time",
        description="Daily trading volume showing market activity and liquidity. High volume often indicates strong investor interest and can confirm price trends. Volume spikes may signal important market events.",
        keywords=["volume", "trading", "liquidity", "market activity", "time series"],
        category="volume",
        fig=fig
    )
    
    plt.close()
    print("✓ Trading Volume Plot saved")

def generate_ohlc_plot(df, plot_manager):
    """Generate OHLC candlestick-style plot."""
    print("\n🕯 Generating OHLC Plot...")
    
    required_cols = ['Date', 'Open', 'High', 'Low', 'Close']
    if not all(col in df.columns for col in required_cols):
        print("⚠ Skipping: Required OHLC columns not found")
        return
    
    # Use last 60 days for better visibility
    df_recent = df.tail(60).copy()
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Create candlestick-style plot
    for idx, row in df_recent.iterrows():
        color = '#2ECC71' if row['Close'] >= row['Open'] else '#E74C3C'
        
        # High-Low line
        ax.plot([idx, idx], [row['Low'], row['High']], color=color, linewidth=1)
        
        # Open-Close box
        height = abs(row['Close'] - row['Open'])
        bottom = min(row['Open'], row['Close'])
        ax.add_patch(plt.Rectangle((idx - 0.3, bottom), 0.6, height, 
                                   facecolor=color, edgecolor=color))
    
    ax.set_title('OHLC Price Chart (Last 60 Days)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Trading Days', fontsize=12)
    ax.set_ylabel('Price (LKR)', fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plot_manager.save_plot(
        plot_id="ohlc_candlestick_chart",
        title="OHLC Candlestick Chart",
        description="Open-High-Low-Close chart showing detailed price action for each trading day. Green candles indicate days where price closed higher than it opened (bullish), while red candles show the opposite (bearish). This chart helps identify patterns and market momentum.",
        keywords=["OHLC", "candlestick", "price action", "open", "high", "low", "close", "technical analysis"],
        category="price",
        fig=fig
    )
    
    plt.close()
    print("✓ OHLC Plot saved")

def generate_returns_distribution(df, plot_manager):
    """Generate daily returns distribution plot."""
    print("\n📉 Generating Returns Distribution...")
    
    if 'Close' not in df.columns:
        print("⚠ Skipping: Close column not found")
        return
    
    # Calculate daily returns
    returns = df['Close'].pct_change().dropna() * 100
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(returns, bins=50, color='#6C5B7B', alpha=0.7, edgecolor='black')
    ax.axvline(returns.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {returns.mean():.2f}%')
    ax.axvline(returns.median(), color='green', linestyle='--', linewidth=2, label=f'Median: {returns.median():.2f}%')
    
    ax.set_title('Distribution of Daily Returns', fontsize=16, fontweight='bold')
    ax.set_xlabel('Daily Return (%)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plot_manager.save_plot(
        plot_id="daily_returns_distribution",
        title="Daily Returns Distribution",
        description=f"Histogram showing the distribution of daily percentage returns. Mean return: {returns.mean():.2f}%, Median: {returns.median():.2f}%. This helps understand return volatility and risk characteristics of the stock.",
        keywords=["returns", "distribution", "volatility", "risk", "histogram", "statistics"],
        category="analysis",
        fig=fig
    )
    
    plt.close()
    print("✓ Returns Distribution Plot saved")

def generate_moving_averages_plot(df, plot_manager):
    """Generate moving averages plot."""
    print("\n📊 Generating Moving Averages Plot...")
    
    if 'Date' not in df.columns or 'Close' not in df.columns:
        print("⚠ Skipping: Required columns not found")
        return
    
    # Calculate moving averages
    df = df.copy()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.plot(df['Date'], df['Close'], label='Close Price', linewidth=2, color='#34495E')
    ax.plot(df['Date'], df['MA20'], label='20-Day MA', linewidth=2, color='#3498DB', linestyle='--')
    ax.plot(df['Date'], df['MA50'], label='50-Day MA', linewidth=2, color='#E74C3C', linestyle='--')
    
    ax.set_title('Stock Price with Moving Averages', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price (LKR)', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plot_manager.save_plot(
        plot_id="moving_averages_chart",
        title="Stock Price with Moving Averages",
        description="Stock price with 20-day and 50-day moving averages. Moving averages smooth out price data to identify trends. When shorter MA crosses above longer MA (golden cross), it's a bullish signal. The opposite (death cross) is bearish.",
        keywords=["moving average", "MA", "trend", "technical indicator", "golden cross", "death cross"],
        category="technical",
        fig=fig
    )
    
    plt.close()
    print("✓ Moving Averages Plot saved")

def generate_volatility_plot(df, plot_manager):
    """Generate rolling volatility plot."""
    print("\n📈 Generating Volatility Plot...")
    
    if 'Close' not in df.columns or 'Date' not in df.columns:
        print("⚠ Skipping: Required columns not found")
        return
    
    # Calculate rolling volatility (standard deviation of returns)
    returns = df['Close'].pct_change()
    rolling_vol = returns.rolling(window=20).std() * np.sqrt(252) * 100  # Annualized volatility
    
    df = df.copy()
    df['Volatility'] = rolling_vol
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(df['Date'], df['Volatility'], linewidth=2, color='#E67E22')
    ax.fill_between(df['Date'], df['Volatility'], alpha=0.3, color='#E67E22')
    ax.set_title('Rolling 20-Day Volatility (Annualized)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Volatility (%)', fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plot_manager.save_plot(
        plot_id="rolling_volatility_chart",
        title="Rolling 20-Day Volatility",
        description="Annualized volatility calculated from 20-day rolling standard deviation of returns. Higher volatility indicates greater price fluctuations and higher risk. Volatility spikes often coincide with market uncertainty or significant events.",
        keywords=["volatility", "risk", "standard deviation", "rolling", "annualized"],
        category="analysis",
        fig=fig
    )
    
    plt.close()
    print("✓ Volatility Plot saved")

def generate_correlation_heatmap(df, plot_manager):
    """Generate correlation heatmap of features."""
    print("\n🔥 Generating Correlation Heatmap...")
    
    # Select numeric columns
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    available_cols = [col for col in numeric_cols if col in df.columns]
    
    if len(available_cols) < 2:
        print("⚠ Skipping: Not enough numeric columns for correlation")
        return
    
    correlation = df[available_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title('Feature Correlation Heatmap', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    plot_manager.save_plot(
        plot_id="feature_correlation_heatmap",
        title="Feature Correlation Heatmap",
        description="Correlation matrix showing relationships between different stock features (Open, High, Low, Close, Volume). Values range from -1 (negative correlation) to +1 (positive correlation). Strong correlations indicate features that move together.",
        keywords=["correlation", "heatmap", "features", "relationship", "matrix"],
        category="analysis",
        fig=fig
    )
    
    plt.close()
    print("✓ Correlation Heatmap saved")

def main():
    """Main function to generate all plots."""
    print("=" * 60)
    print("Plot Generation for RAG Integration")
    print("=" * 60)
    
    # Initialize plot manager
    plot_manager = PlotManager(
        plots_dir=str(project_root / "data" / "plots"),
        index_file=str(project_root / "data" / "plots" / "plot_index.json")
    )
    
    # Load data
    df = load_stock_data()
    
    if df is None:
        print("\n❌ Cannot generate plots: No data available")
        print("Please ensure stock data is available in:")
        print("  - data/processed/stock_data_scaled.csv")
        print("  - OR data/raw/stock_data.csv")
        return
    
    print(f"\n✓ Loaded {len(df)} rows of data")
    print(f"  Columns: {', '.join(df.columns[:10])}")
    
    # Generate all plots
    try:
        generate_price_plot(df, plot_manager)
        generate_volume_plot(df, plot_manager)
        generate_ohlc_plot(df, plot_manager)
        generate_returns_distribution(df, plot_manager)
        generate_moving_averages_plot(df, plot_manager)
        generate_volatility_plot(df, plot_manager)
        generate_correlation_heatmap(df, plot_manager)
        
        # Print statistics
        stats = plot_manager.get_stats()
        print("\n" + "=" * 60)
        print("✓ Plot Generation Complete!")
        print("=" * 60)
        print(f"  Total Plots: {stats['total_plots']}")
        print(f"  Categories: {', '.join(stats['categories'])}")
        print(f"  Storage: {stats['total_size_mb']:.2f} MB")
        print(f"  Location: {plot_manager.plots_dir}")
        print("\nPlots are ready for RAG integration!")
        
    except Exception as e:
        print(f"\n❌ Error generating plots: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
