import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "2023_Data_With_Change.csv")

DATE_COL = "Date"
TICKER_COL = "Company"
PREV_CLOSE_COL = "Prev Close"
DAY_CLOSE_COL = "Day Close"
CHANGE_PCT_COL = "Change (%)"
TURNOVER_COL = "Turnover"

RANDOM_STATE = 42
N_ESTIMATORS = 300
# Only flag top 3% as anomalies to be more precise
CONTAMINATION_FRACTION = 0.03 
OUT_PREFIX = "pumpdump_local"