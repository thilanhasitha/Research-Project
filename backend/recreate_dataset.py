import pandas as pd
import os

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  

INPUT_FILE = os.path.join(DATA_DIR, "5k.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "investor_risk_dataset.csv")

# -----------------------------
# LOAD DATA
# -----------------------------
print("Loading dataset...")
df = pd.read_csv(INPUT_FILE)

print("Initial shape:", df.shape)
print("Columns:", df.columns.tolist())

# -----------------------------
# CLEAN MONEY COLUMNS
# -----------------------------
money_columns = [
    "Income Level",
    "Account Balance",
    "Deposits",
    "Withdrawals",
    "Transfers",
    "International Transfers",
    "Investments",
    "Loan Amount"
]

for col in money_columns:
    if col in df.columns:
        df[col] = (
            df[col]
            .replace(r'[$,]', '', regex=True)
            .astype(float)
        )

# Clean percentage column
if "Interest Rate" in df.columns:
    df["Interest Rate"] = (
        df["Interest Rate"]
        .str.replace('%', '', regex=True)
        .astype(float)
    )

# -----------------------------
# DROP UNUSED / LEAKAGE COLUMNS
# -----------------------------
drop_columns = [
    "Address",
    "Transaction Description",
    "Risk Tolerance"   # VERY IMPORTANT
]

df = df.drop(columns=[c for c in drop_columns if c in df.columns])

print("After cleaning shape:", df.shape)

# -----------------------------
# RISK SCORE LOGIC (EXPLAINABLE)
# -----------------------------
def calculate_risk_score(row):
    score = 0

    # Age factor
    if row["Age"] < 30:
        score += 2
    elif row["Age"] < 50:
        score += 1

    # Income factor
    if row["Income Level"] > 100000:
        score += 2
    elif row["Income Level"] > 50000:
        score += 1

    # Loan exposure
    if row["Loan Amount"] > 50000:
        score += 2
    elif row["Loan Amount"] > 20000:
        score += 1

    # Investment exposure
    if row["Investments"] > 40000:
        score += 2
    elif row["Investments"] > 20000:
        score += 1

    # Interest burden
    if row["Interest Rate"] > 10:
        score += 2
    elif row["Interest Rate"] > 6:
        score += 1


    return score


def classify_risk(score):
    if score <= 4:
        return "Low"
    elif score <= 6:
        return "Medium"
    else:
        return "High"




# -----------------------------
# APPLY RISK LOGIC
# -----------------------------
print("Calculating risk scores...")
df["Risk Score"] = df.apply(calculate_risk_score, axis=1)
df["Risk Level"] = df["Risk Score"].apply(classify_risk)

# -----------------------------
# SAVE NEW DATASET
# -----------------------------
df.to_csv(OUTPUT_FILE, index=False)

print("SUCCESS ")
print("Saved file:", OUTPUT_FILE)
print(df["Risk Level"].value_counts())
