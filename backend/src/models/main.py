import os
import pandas as pd
import joblib  # <-- NEW: add this import

from config import DATA_PATH, OUT_PREFIX, DATE_COL, TICKER_COL
from data_preprocessing import load_data, engineer_features
from model import train_isolation_forest, apply_model, summarise_anomalies
from visualization import plot_price_with_anomalies, plot_anomaly_counts

def export_results(df: pd.DataFrame):
    out_csv = f"{OUT_PREFIX}_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"[INFO] Saved annotated data to {out_csv}")

def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"{DATA_PATH} not found.")

    print("=== 1. LOAD DATA ===")
    df = load_data()

    print("\n=== 2. FEATURES & SCALING ===")
    df_feat, X_scaled, feature_cols, scaler = engineer_features(df)

    print("\n=== 3. TRAIN MODEL ===")
    model = train_isolation_forest(X_scaled)

    # --- NEW: Save trained model and scaler
    joblib.dump(model, f"{OUT_PREFIX}_iforest_model.joblib")
    print(f"[INFO] Model saved as {OUT_PREFIX}_iforest_model.joblib")
    joblib.dump(scaler, f"{OUT_PREFIX}_scaler.joblib")
    print(f"[INFO] Scaler saved as {OUT_PREFIX}_scaler.joblib")
    # ---

    print("\n=== 4. APPLY MODEL ===")
    df_out = apply_model(df_feat, model, X_scaled)

    print("\n=== 5. SUMMARY ===")
    summary = summarise_anomalies(df_out)
    print(f"Total rows        : {summary['total_rows']}")
    print(f"Anomaly count     : {summary['anomaly_count']}")
    print(f"Anomaly %         : {summary['anomaly_percentage']:.2f}%")

    print("\n=== 6. VISUALIZATION ===")
    plot_price_with_anomalies(df_out)
    plot_anomaly_counts(df_out)

    print("\n=== 7. EXPORT ===")
    export_results(df_out)

    print("\n[DONE] Local pump & dump candidate detection finished.")

if __name__ == "__main__":
    main()
