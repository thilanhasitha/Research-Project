# data_preprocessing.py

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.models.config import DATA_PATH,DATE_COL,TICKER_COL, PREV_CLOSE_COL, DAY_CLOSE_COL, CHANGE_PCT_COL, TURNOVER_COL




def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    # Parse date
    if DATE_COL in df.columns:
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], dayfirst=True, errors="coerce")

    # Ensure numeric for prices
    for col in [PREV_CLOSE_COL, DAY_CLOSE_COL]:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in CSV.")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Turnover optional
    if TURNOVER_COL in df.columns:
        df[TURNOVER_COL] = pd.to_numeric(df[TURNOVER_COL], errors="coerce")

    # Clean Change (%) if exists
    if CHANGE_PCT_COL in df.columns:
        df[CHANGE_PCT_COL] = (
            df[CHANGE_PCT_COL]
            .astype(str)
            .str.replace("(", "-", regex=False)
            .str.replace(")", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df[CHANGE_PCT_COL] = pd.to_numeric(df[CHANGE_PCT_COL], errors="coerce")

    # Drop rows without usable prices
    df = df.dropna(subset=[PREV_CLOSE_COL, DAY_CLOSE_COL])

    print("HEAD:")
    print(df.head())
    print("\nDESCRIBE:")
    print(df.describe(include="all"))

    return df


def engineer_features(df: pd.DataFrame):
    df = df.copy()

    # Sort by company and date for rolling features
    if DATE_COL in df.columns and TICKER_COL in df.columns:
        df = df.sort_values([TICKER_COL, DATE_COL])

    # Gap return
    df["gap_return"] = (df[DAY_CLOSE_COL] - df[PREV_CLOSE_COL]) / df[PREV_CLOSE_COL]

    # Use Change (%) if present, else use gap_return
    if CHANGE_PCT_COL in df.columns:
        df["change_pct"] = df[CHANGE_PCT_COL] / 100.0
    else:
        df["change_pct"] = df["gap_return"]

    # Turnover log
    if TURNOVER_COL in df.columns:
        df["turnover_log"] = np.log1p(df[TURNOVER_COL].fillna(0.0))
    else:
        df["turnover_log"] = 0.0

    # Rolling z‑scores per company
    def _add_rolling(group: pd.DataFrame) -> pd.DataFrame:
        group = group.sort_values(DATE_COL)

        group["gap_return_ma_5"] = group["gap_return"].rolling(5).mean()
        group["gap_return_std_5"] = group["gap_return"].rolling(5).std()
        group["gap_return_z_5"] = (group["gap_return"] - group["gap_return_ma_5"]) / group[
            "gap_return_std_5"
        ]

        if TURNOVER_COL in group.columns:
            group["turnover_ma_5"] = group[TURNOVER_COL].rolling(5).mean()
            group["turnover_std_5"] = group[TURNOVER_COL].rolling(5).std()
            group["turnover_z_5"] = (group[TURNOVER_COL] - group["turnover_ma_5"]) / group[
                "turnover_std_5"
            ]
        else:
            group["turnover_ma_5"] = 0.0
            group["turnover_std_5"] = 0.0
            group["turnover_z_5"] = 0.0

        return group

    if TICKER_COL in df.columns:
        df = df.groupby(TICKER_COL, group_keys=False).apply(_add_rolling)
    else:
        df = _add_rolling(df)

    df = df.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    feature_cols = [
        PREV_CLOSE_COL,
        DAY_CLOSE_COL,
        "gap_return",
        "change_pct",
        "turnover_log",
        "gap_return_z_5",
        "turnover_z_5",
    ]

    X = df[feature_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("\nFEATURE COLUMNS USED:")
    print(feature_cols)

    return df, X_scaled, feature_cols, scaler
