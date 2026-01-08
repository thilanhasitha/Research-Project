import pandas as pd
import numpy as np

def extract_stock_features(csv_path):
    df = pd.read_csv(csv_path, low_memory=False)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    df = df.rename(columns={
        "company id": "stock",
        "trading date": "date",
        "price high (rs.)": "high",
        "price low (rs.)": "low",
        "close price (rs.)": "close",
        "open price (rs.)": "open",
        "trade volume (no.)": "volume"
    })

    required_cols = {"stock", "date", "high", "low", "close"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns. Found: {df.columns}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[list(required_cols)].dropna()
    df = df.sort_values(["stock", "date"])

    # --- FEATURE ENGINEERING ---
    df["daily_return"] = df.groupby("stock")["close"].pct_change()
    df["hl_range"] = (df["high"] - df["low"]) / df["low"]

    # CLEAN INVALID VALUES
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    features = []

    for stock, g in df.groupby("stock"):
        if len(g) < 30:
            continue

        mean_return = g["daily_return"].mean()
        volatility = g["daily_return"].std()
        avg_hl_range = g["hl_range"].mean()

        # Max drawdown (safe)
        cum_max = g["close"].cummax()
        drawdown = (cum_max - g["close"]) / cum_max
        max_drawdown = drawdown.max()

        # Skip abnormal values
        if not np.isfinite([mean_return, volatility, avg_hl_range, max_drawdown]).all():
            continue

        features.append({
            "stock": stock,
            "mean_return": mean_return,
            "volatility": volatility,
            "avg_hl_range": avg_hl_range,
            "max_drawdown": max_drawdown
        })

    features_df = pd.DataFrame(features)

    # FINAL SAFETY CLEAN
    features_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    features_df.dropna(inplace=True)

    return features_df
