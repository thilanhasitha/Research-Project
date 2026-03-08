import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

def build_cse_forensic_architecture(file_path):
    # 1. LOAD DATA
    df = pd.read_csv(file_path)

    # --- STEP A: CLEAN HEADERS ---
    df.columns = df.columns.str.strip().str.upper()

    # --- STEP B: MAPPING ---
    column_mapping = {
        'SYMBOL':               'Symbol',
        'DATE':                 'Date',
        'OPEN':                 'Open',
        'HIGH':                 'High',
        'LOW':                  'Low',
        'CLOSE':                'Close',
        'TRADE VOLUME (NO.)':   'trade_count',
        'SHARE VOLUME (NO.)':   'share_volume',
        'TURNOVER (RS.)':       'turnover'
    }
    df = df.rename(columns=column_mapping)

    # Drop junk unnamed columns (caused by trailing commas in CSV)
    df = df.loc[:, ~df.columns.str.upper().str.startswith('UNNAMED')]

    # --- STEP C: CLEAN NUMBERS ---
    num_cols = ['Open', 'High', 'Low', 'Close', 'trade_count', 'share_volume', 'turnover']
    for col in num_cols:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')

    # Convert Date — explicit format removes UserWarning
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y', errors='coerce')
    df = df.sort_values(['Symbol', 'Date'])

    # FIX: Replace 0 prices with NaN and fill from nearest valid trading day
    price_cols = ['Open', 'High', 'Low', 'Close']
    df[price_cols] = df[price_cols].replace(0, np.nan)
    df[price_cols] = df.groupby('Symbol')[price_cols].ffill().bfill()

    # --- STEP D: FEATURE ENGINEERING ---
    def engineer_features(group):
        eps = 1e-9
        group['Intraday_Return'] = (group['Close'] - group['Open']) / (group['Open'] + eps)
        group['Log_Volatility']  = np.log(group['High'] / (group['Low'] + eps) + eps)
        group['Avg_Trade_Size']  = group['share_volume'] / (group['trade_count'] + eps)
        group['Price_Impact']    = group['Intraday_Return'] / (group['turnover'] + eps)
        group['Trade_Density']   = group['trade_count'] / (group['turnover'] + eps)
        group['Vol_Spike']       = group['share_volume'] / (group['share_volume'].rolling(window=5).mean() + eps)
        return group

    # Save Symbol — include_groups=False drops it from result
    symbols = df['Symbol'].copy()
    df = df.groupby('Symbol', group_keys=False).apply(engineer_features, include_groups=False)
    df['Symbol'] = symbols

    # --- STEP E: LOG FEATURES ---
    df['Log_Turnover']       = np.log1p(df['turnover'])
    df['Log_Avg_Trade_Size'] = np.log1p(df['Avg_Trade_Size'])

    # --- STEP F: SCALING ---
    features_to_scale = [
        'Intraday_Return', 'Log_Volatility', 'Log_Avg_Trade_Size',
        'Price_Impact', 'Trade_Density', 'Vol_Spike', 'Log_Turnover'
    ]
    df[features_to_scale] = df[features_to_scale].fillna(0)
    scaler = StandardScaler()
    df[features_to_scale] = scaler.fit_transform(df[features_to_scale])
    df = df.fillna(0)

    # Symbol as first column
    df = df[['Symbol'] + [c for c in df.columns if c != 'Symbol']]

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
            print(" Phase 1: Data Architecture Complete")
            print(f" File saved to: {save_path}")