"""
Data Preparation Script
=======================
Prepares monthly_stock_prices_cleaned.csv for LSTM training by cleaning and restructuring the data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_stock_csv(file_path: str) -> pd.DataFrame:
    """
    Parse the complex CSV file with multiple companies and extract clean stock data.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Clean DataFrame with columns: Date, Open, High, Low, Close, Volume
    """
    logger.info(f"Reading CSV file: {file_path}")
    
    # Read the raw file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    all_data = []
    current_company = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is a company name line (all caps, contains "PLC" or similar)
        if line and not line.startswith('Month') and not line.startswith('2'):
            parts = line.split(',')
            if len(parts) > 0 and parts[0] and len(parts[0]) > 5:
                potential_company = parts[0]
                # Check if it looks like a company name
                if any(keyword in potential_company.upper() for keyword in ['PLC', 'LTD', 'LIMITED', 'FINANCE', 'BANK', 'COMPANY']):
                    current_company = potential_company
                    logger.debug(f"Found company: {current_company}")
        
        # Check if this is a header row
        if 'Month' in line and 'High' in line and 'Low' in line and 'Closing' in line:
            i += 1  # Move to data rows
            # Read data rows until we hit empty lines or next company
            while i < len(lines):
                data_line = lines[i].strip()
                if not data_line or ',' not in data_line:
                    break
                
                parts = [p.strip() for p in data_line.split(',')]
                
                # Check if this looks like a data row (starts with year-month format)
                if len(parts) >= 6 and parts[0] and '-' in parts[0]:
                    try:
                        # Extract data: Month, Date High, High (Rs.), Date Low, Low (Rs.), Closing (Rs.), Trades, Shares, Turnover, Last Traded Date, Days Traded
                        month = parts[0]
                        
                        # Find the closing price (usually around index 5)
                        high_price = None
                        low_price = None
                        close_price = None
                        volume = None
                        
                        # Try to parse numeric values
                        for idx, val in enumerate(parts[1:7]):
                            if val:
                                try:
                                    num_val = float(val.replace(',', ''))
                                    if high_price is None and num_val > 0 and idx in [1, 2]:
                                        high_price = num_val
                                    elif low_price is None and num_val > 0 and idx in [3, 4]:
                                        low_price = num_val
                                    elif close_price is None and num_val > 0 and idx == 5:
                                        close_price = num_val
                                except (ValueError, AttributeError):
                                    continue
                        
                        # Try to get volume (trades or shares)
                        if len(parts) > 6:
                            try:
                                volume = float(parts[6].replace(',', ''))
                            except (ValueError, AttributeError):
                                if len(parts) > 7:
                                    try:
                                        volume = float(parts[7].replace(',', ''))
                                    except:
                                        volume = 0
                        
                        if close_price is not None:
                            all_data.append({
                                'Date': month,
                                'Company': current_company,
                                'High': high_price if high_price else close_price,
                                'Low': low_price if low_price else close_price,
                                'Close': close_price,
                                'Volume': volume if volume else 0
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing line: {data_line[:50]}... Error: {e}")
                
                i += 1
                continue
        
        i += 1
    
    logger.info(f"Extracted {len(all_data)} records")
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    if df.empty:
        logger.error("No data extracted from CSV file")
        return df
    
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m', errors='coerce')
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['Date'])
    
    # Sort by date
    df = df.sort_values('Date')
    
    # Add Open column (approximate as Close of previous month)
    df['Open'] = df.groupby('Company')['Close'].shift(1)
    df['Open'] = df['Open'].fillna(df['Close'])
    
    # Reorder columns
    df = df[['Date', 'Company', 'Open', 'High', 'Low', 'Close', 'Volume']]
    
    logger.info(f"Cleaned data shape: {df.shape}")
    logger.info(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    logger.info(f"Number of companies: {df['Company'].nunique()}")
    logger.info(f"Companies: {df['Company'].unique()[:10].tolist()}...")
    
    return df


def prepare_single_company_data(df: pd.DataFrame, company_name: str = None) -> pd.DataFrame:
    """
    Extract data for a single company, or aggregate all companies.
    
    Args:
        df: DataFrame with all companies
        company_name: Name of company to extract, or None for aggregated data
        
    Returns:
        DataFrame with single company or aggregated data
    """
    if company_name:
        logger.info(f"Extracting data for company: {company_name}")
        company_data = df[df['Company'] == company_name].copy()
        company_data = company_data.drop('Company', axis=1)
        return company_data
    else:
        logger.info("Aggregating data across all companies")
        # Aggregate by taking mean of all companies per month
        agg_data = df.groupby('Date').agg({
            'Open': 'mean',
            'High': 'mean',
            'Low': 'mean',
            'Close': 'mean',
            'Volume': 'sum'
        }).reset_index()
        return agg_data


def main():
    """Main execution function."""
    
    # File paths
    input_file = Path("data/processed/monthly_stock_prices_cleaned.csv")
    output_file = Path("data/processed/lstm_ready_data.csv")
    
    # Create output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Parse the CSV
    df = parse_stock_csv(str(input_file))
    
    if df.empty:
        logger.error("Failed to parse data. Exiting.")
        return
    
    # Save raw parsed data
    raw_output = Path("data/processed/all_companies_parsed.csv")
    df.to_csv(raw_output, index=False)
    logger.info(f"Saved parsed data to: {raw_output}")
    
    # Prepare aggregated data for LSTM
    lstm_data = prepare_single_company_data(df, company_name=None)
    
    # Save LSTM-ready data
    lstm_data.to_csv(output_file, index=False)
    logger.info(f"Saved LSTM-ready data to: {output_file}")
    logger.info(f"Final data shape: {lstm_data.shape}")
    logger.info("\nFirst few rows:")
    print(lstm_data.head(10))
    logger.info("\nData statistics:")
    print(lstm_data.describe())
    
    # Check for missing values
    missing = lstm_data.isnull().sum()
    if missing.any():
        logger.warning(f"Missing values:\n{missing[missing > 0]}")
    else:
        logger.info("No missing values found")
    
    logger.info("\n" + "="*60)
    logger.info("Data preparation complete!")
    logger.info(f"You can now train the LSTM model using: {output_file}")
    logger.info("="*60)


if __name__ == "__main__":
    main()
