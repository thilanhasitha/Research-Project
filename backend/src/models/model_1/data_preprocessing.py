import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
# Ensure your config.py has these exact names matching your CSV headers
from .config import DATA_PATH, DATE_COL, TICKER_COL, PREV_CLOSE_COL, DAY_CLOSE_COL, CHANGE_PCT_COL, TURNOVER_COL

def load_data() -> pd.DataFrame:
    """Loads the CSV and cleans numeric columns to prevent string errors."""
    df = pd.read_csv(DATA_PATH)
    
    # 1. Convert Date
    if DATE_COL in df.columns:
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], dayfirst=True, errors="coerce")

    # 2. Clean Price Columns (Handle commas and convert to numeric)
    for col in [PREV_CLOSE_COL, DAY_CLOSE_COL]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors="coerce")

    # 3. Clean Turnover Column (This fixes your AttributeError/TypeError)
    if TURNOVER_COL in df.columns:
        df[TURNOVER_COL] = pd.to_numeric(df[TURNOVER_COL].astype(str).str.replace(',', ''), errors="coerce")

    # 4. Clean or Calculate Change (%)
    if CHANGE_PCT_COL in df.columns:
        df[CHANGE_PCT_COL] = (
            df[CHANGE_PCT_COL].astype(str)
            .str.replace("(", "-", regex=False)
            .str.replace(")", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df[CHANGE_PCT_COL] = pd.to_numeric(df[CHANGE_PCT_COL], errors="coerce")
    else:
        # Calculate manually if the column is missing from CSV
        df[CHANGE_PCT_COL] = ((df[DAY_CLOSE_COL] - df[PREV_CLOSE_COL]) / df[PREV_CLOSE_COL]) * 100

    # Remove rows with missing prices as they break calculations
    df = df.dropna(subset=[PREV_CLOSE_COL, DAY_CLOSE_COL])
    
    return df

def engineer_features(df: pd.DataFrame):
    """Calculates rolling statistics and logs for fraud/anomaly detection."""
    df = df.copy().sort_values([TICKER_COL, DATE_COL])
    
    # Intraday returns
    df["gap_return"] = (df[DAY_CLOSE_COL] - df[PREV_CLOSE_COL]) / df[PREV_CLOSE_COL]
    
    # Use existing Change % or fallback to gap_return
    df["change_pct"] = df[CHANGE_PCT_COL] / 100.0 if CHANGE_PCT_COL in df.columns else df["gap_return"]
    
    # Log transform turnover (Now works because column is numeric)
    if TURNOVER_COL in df.columns:
        df["turnover_log"] = np.log1p(df[TURNOVER_COL].fillna(0.0))
    else:
        df["turnover_log"] = 0.0

    def _add_rolling(group):
        group = group.sort_values(DATE_COL)
        # Z-Score for price movement (Detects unusual spikes)
        group["gap_return_z_5"] = (group["gap_return"] - group["gap_return"].rolling(5).mean()) / (group["gap_return"].rolling(5).std() + 1e-9)
        
        # Z-Score for turnover (Detects unusual volume)
        if TURNOVER_COL in group.columns:
            group["turnover_z_5"] = (group[TURNOVER_COL] - group[TURNOVER_COL].rolling(5).mean()) / (group[TURNOVER_COL].rolling(5).std() + 1e-9)
        return group

    # Apply rolling logic per stock
    df = df.groupby(TICKER_COL, group_keys=False).apply(_add_rolling)
    
    # Drop rows where rolling window isn't full yet, handle Inf values
    df = df.dropna(subset=["gap_return_z_5"]).replace([np.inf, -np.inf], 0.0).fillna(0.0)

    # Define feature list for the model
    feature_cols = [PREV_CLOSE_COL, DAY_CLOSE_COL, "gap_return", "change_pct", "turnover_log", "gap_return_z_5"]
    if "turnover_z_5" in df.columns:
        feature_cols.append("turnover_z_5")

    X = df[feature_cols].values
    
    # Scale features
    scaler = RobustScaler() 
    X_scaled = scaler.fit_transform(X)

    return df, X_scaled, feature_cols, scaler