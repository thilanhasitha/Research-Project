import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from config import *

def load_and_clean():
    df = pd.read_csv(DATA_PATH)
    # Specified format to avoid UserWarning
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], dayfirst=True, errors="coerce")
    
    for col in [PREV_CLOSE_COL, DAY_CLOSE_COL, TURNOVER_COL]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors="coerce")

    # Recalculate Change % to ensure numeric consistency
    df[CHANGE_PCT_COL] = ((df[DAY_CLOSE_COL] - df[PREV_CLOSE_COL]) / df[PREV_CLOSE_COL]) * 100
    return df.dropna(subset=[PREV_CLOSE_COL, DAY_CLOSE_COL, TICKER_COL])

def engineer_features(df):
    df = df.copy().sort_values([TICKER_COL, DATE_COL])
    
    def _add_rolling(group):
        # We assume columns are available in the group
        group["gap_return"] = (group[DAY_CLOSE_COL] - group[PREV_CLOSE_COL]) / group[PREV_CLOSE_COL]
        group["turnover_log"] = np.log1p(group[TURNOVER_COL].fillna(0.0))
        
        avg_vol = group[TURNOVER_COL].rolling(window=20).mean()
        group["vol_surge_ratio"] = group[TURNOVER_COL] / (avg_vol + 1e-9)
        
        # Price Z-Score over last 5 days
        rolling_mean = group["gap_return"].rolling(5).mean()
        rolling_std = group["gap_return"].rolling(5).std()
        group["price_z_score"] = (group["gap_return"] - rolling_mean) / (rolling_std + 1e-9)
        return group

    # Fix: include_groups=False and reset_index() prevents the KeyError: 'Company'
    df = df.groupby(TICKER_COL, group_keys=False).apply(_add_rolling, include_groups=True).reset_index(drop=True)
    df = df.fillna(0.0).replace([np.inf, -np.inf], 0.0)
    
    feature_cols = ["gap_return", "turnover_log", "vol_surge_ratio", "price_z_score"]
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(df[feature_cols].values)
    return df, X_scaled, feature_cols

def validate_dump(df, window=5):
    """Checks for price crash after the pump detection."""
    df = df.copy()
    df["reversion_ratio"] = 0.0
    
    anom_indices = df[df["anomaly_label"] == -1].index
    
    for idx in anom_indices:
        ticker = df.loc[idx, TICKER_COL]
        pump_date = df.loc[idx, DATE_COL]
        pump_price = df.loc[idx, DAY_CLOSE_COL]
        prev_price = df.loc[idx, PREV_CLOSE_COL]
        
        # Look forward in time for the same ticker
        future = df[(df[TICKER_COL] == ticker) & (df[DATE_COL] > pump_date)].head(window)
        
        if not future.empty:
            min_future_price = future[DAY_CLOSE_COL].min()
            pump_gain = pump_price - prev_price
            price_drop = pump_price - min_future_price
            # If drop > gain, reversion_ratio > 1.0
            df.at[idx, "reversion_ratio"] = price_drop / (pump_gain + 1e-9)
            
    return df