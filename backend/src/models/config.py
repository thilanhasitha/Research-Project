# config.py

# Path to your merged CSV (same folder or inside "data/")
DATA_PATH = "data/stock_data.csv"
# e.g. "data/merged_pumpdump_dataset.csv" if you put it in data/

# Column names in your CSV (change if your headers differ)
DATE_COL = "Date"
TICKER_COL = "Company"          # company / stock name
PREV_CLOSE_COL = "Prev Close"
DAY_CLOSE_COL = "Day Close"
CHANGE_PCT_COL = "Change (%)"   # if not present, gap_return will be used
TURNOVER_COL = "Turnover"       # if not present, turnover features become 0

# Isolation Forest parameters
CONTAMINATION = 0.03
RANDOM_STATE = 42
N_ESTIMATORS = 200

# Output prefix
OUT_PREFIX = "pumpdump_local"
