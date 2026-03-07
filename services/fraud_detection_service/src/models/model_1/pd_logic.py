import numpy as np
import pandas as pd
import shap
import os
from sklearn.preprocessing import RobustScaler

# Constants for consistency across files
DATE_COL = "Date"
TICKER_COL = "Company"
PREV_CLOSE_COL = "Prev Close"
DAY_CLOSE_COL = "Day Close"
TURNOVER_COL = "Turnover"

def load_and_clean(data_path):
    """Loads and standardizes numeric and date columns with safety checks."""
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing data file at: {data_path}")
        
    df = pd.read_csv(data_path)
    df.columns = df.columns.str.strip() # Remove hidden spaces in headers
    
    # Standardize numeric columns
    numeric_cols = [DAY_CLOSE_COL, PREV_CLOSE_COL, TURNOVER_COL]
    for col in numeric_cols:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '').astype(float)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Standardize Dates
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], dayfirst=True, errors='coerce')
    return df.dropna(subset=[TICKER_COL, DATE_COL])

def engineer_features(df):
    """
    Cleans data and calculates indicators. 
    Fixes 'ValueError: could not convert string to float' by stripping commas early.
    """
    df = df.copy()

    # --- 1. MANDATORY CLEANING (Do this BEFORE any math) ---
    # List all columns that are used in calculations
    cols_to_fix = [DAY_CLOSE_COL, PREV_CLOSE_COL, TURNOVER_COL]
    
    for col in cols_to_fix:
        if col in df.columns:
            # Remove commas and convert to float
            df[col] = df[col].astype(str).str.replace(',', '').astype(float)
            # Ensure it is purely numeric
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fix Date format
    if DATE_COL in df.columns:
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], dayfirst=True, errors='coerce')

    # Sort for rolling window math (Crucial!)
    df = df.sort_values([TICKER_COL, DATE_COL])
    
    # --- 2. NOW DO THE MATH (Safely) ---
    df["gap_return"] = (df[DAY_CLOSE_COL] - df[PREV_CLOSE_COL]) / (df[PREV_CLOSE_COL] + 1e-9)
    
    # This line was previously crashing because TURNOVER_COL was still a string
    df["avg_vol_20d"] = df.groupby(TICKER_COL)[TURNOVER_COL].transform(
        lambda x: x.rolling(20, min_periods=1).mean()
    )
    
    df["vol_surge_ratio"] = df[TURNOVER_COL] / (df["avg_vol_20d"] + 1e-9)
    
    # Rest of your indicators...
    df["rolling_std"] = df.groupby(TICKER_COL)["gap_return"].transform(
        lambda x: x.rolling(5, min_periods=1).std()
    )
    df["price_z_score"] = df["gap_return"] / (df["rolling_std"] + 1e-9)
    
    # Validation / Reversion (Look-ahead logic)
    df['future_close_3d'] = df.groupby(TICKER_COL)[DAY_CLOSE_COL].shift(-3)
    df['reversion_ratio'] = (df[DAY_CLOSE_COL] - df['future_close_3d']) / (df[DAY_CLOSE_COL] - df[PREV_CLOSE_COL] + 1e-9)
    
    df = df.fillna(0).replace([np.inf, -np.inf], 0)
    feat_cols = ["gap_return", "vol_surge_ratio", "price_z_score"]
    
    return df, feat_cols
def get_explanations(model, X_scaled, feature_names):
    """Explains why the Isolation Forest isolated a specific point using SHAP."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_scaled)
    
    mapping = {
        "gap_return": "Extreme vertical price movement.",
        "vol_surge_ratio": "Abnormal volume spike.",
        "price_z_score": "Price action decoupled from volatility."
    }
    
    reasons = []
    for i in range(len(shap_values)):
        top_idx = np.argmax(np.abs(shap_values[i]))
        reasons.append(mapping.get(feature_names[top_idx], "Complex anomaly."))
    return reasons