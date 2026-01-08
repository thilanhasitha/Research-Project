import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

from feature_engineering import extract_stock_features

DATA_PATH = "../data/2023 Data.csv"
MODEL_PATH = "stock_model.pkl"

def train_stock_risk_model():
    df = extract_stock_features(DATA_PATH)

    # Create risk labels using volatility
    q_low = df["volatility"].quantile(0.33)
    q_high = df["volatility"].quantile(0.66)

    def label_risk(v):
        if v <= q_low:
            return "Low"
        elif v <= q_high:
            return "Medium"
        else:
            return "High"

    df["risk_level"] = df["volatility"].apply(label_risk)

    X = df[["mean_return", "volatility", "avg_hl_range", "max_drawdown"]]
    y = df["risk_level"]

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    print("Training accuracy:", model.score(X_train, y_train))
    print("Test accuracy:", model.score(X_test, y_test))

    joblib.dump(
        {"model": model, "encoder": encoder, "features": X.columns.tolist()},
        MODEL_PATH
    )

    print("Stock risk model trained & saved!")

if __name__ == "__main__":
    train_stock_risk_model()
