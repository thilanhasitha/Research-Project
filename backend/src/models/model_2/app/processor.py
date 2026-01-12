import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

def build_cse_forensic_architecture(file_path):
    # 1. LOAD DATA
    df = pd.read_csv(file_path)
    
    # --- STEP A: CLEAN HEADERS ---
    # Strip spaces and move to UPPERCASE to be safe
    df.columns = df.columns.str.strip().str.upper()

    # --- STEP B: MAPPING (Matching your exact CSV) ---
    column_mapping = {
        'SYMBOL': 'Symbol',
        'DATE': 'Date',
        'OPEN': 'Open',
        'HIGH': 'High',
        'LOW': 'Low',
        'CLOSE': 'Close',
        'TRADE VOLUME (NO.)': 'trade_count',
        'SHARE VOLUME (NO.)': 'share_volume',
        'TURNOVER (RS.)': 'turnover'
    }
    df = df.rename(columns=column_mapping)

    # --- STEP C: CLEAN NUMBERS (Fixes "10,261" error) ---
    # Remove commas from columns that should be numbers
    num_cols = ['Open', 'High', 'Low', 'Close', 'trade_count', 'share_volume', 'turnover']
    for col in num_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)

    # Convert Date
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.sort_values(['Symbol', 'Date'])

    def engineer_features(group):
        # Math remains standard
        group['Intraday_Return'] = (group['Close'] - group['Open']) / (group['Open'] + 1e-9)
        group['Log_Volatility'] = np.log(group['High'] / (group['Low'] + 1e-9) + 1e-9)
        group['Avg_Trade_Size'] = group['share_volume'] / (group['trade_count'] + 1e-9)
        group['Price_Impact'] = group['Intraday_Return'] / (group['turnover'] + 1e-9)
        group['Trade_Density'] = group['trade_count'] / (group['turnover'] + 1e-9)
        group['Vol_Spike'] = group['share_volume'] / (group['share_volume'].rolling(window=5).mean() + 1e-9)
        return group

    df = df.groupby('Symbol', group_keys=False).apply(engineer_features)

    # Preprocessing and Scaling
    df['Log_Turnover'] = np.log1p(df['turnover'])
    df['Log_Avg_Trade_Size'] = np.log1p(df['Avg_Trade_Size'])

    features_to_scale = [
        'Intraday_Return', 'Log_Volatility', 'Log_Avg_Trade_Size', 
        'Price_Impact', 'Trade_Density', 'Vol_Spike', 'Log_Turnover'
    ]
    
    scaler = StandardScaler()
    df[features_to_scale] = scaler.fit_transform(df[features_to_scale])
    df = df.fillna(0)
    
    return df, features_to_scale

if __name__ == "__main__":
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.normpath(os.path.join(current_script_dir, '..', 'data', 'model2-dataset.csv'))
    
    if os.path.exists(file_path):
        processed_df, active_features = build_cse_forensic_architecture(file_path)
        
        if processed_df is not None:
            output_dir = os.path.join(current_script_dir, '..', 'data', 'processed')
            if not os.path.exists(output_dir): os.makedirs(output_dir)
            
            save_path = os.path.join(output_dir, 'cse_standardized_features.csv')
            processed_df.to_csv(save_path, index=False)
            print("✅ Phase 1: Data Architecture Complete")
            print(f"File saved to: {save_path}")