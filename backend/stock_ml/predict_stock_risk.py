import joblib
import pandas as pd

MODEL_PATH = "stock_ml/stock_model.pkl"

def predict_stock_risk(stock_features_df):
    """
    stock_features_df:
      columns = mean_return, volatility, avg_hl_range, max_drawdown
    """

    saved = joblib.load(MODEL_PATH)
    model = saved["model"]
    encoder = saved["encoder"]
    feature_cols = saved["features"]

    X = stock_features_df[feature_cols]

    preds = model.predict(X)
    risk_labels = encoder.inverse_transform(preds)

    stock_features_df = stock_features_df.copy()
    stock_features_df["predicted_risk"] = risk_labels

    return stock_features_df
    
