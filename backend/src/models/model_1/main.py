import os
import joblib
from .config import DATA_PATH, OUT_PREFIX
from data_preprocessing import load_data, engineer_features
from model import train_isolation_forest, apply_model, summarise_anomalies
from visualization import plot_price_with_anomalies, plot_anomaly_counts, plot_pca_separation

def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"{DATA_PATH} not found.")

    print("=== 1. LOADING & PREPROCESSING ===")
    df = load_data()
    df_feat, X_scaled, feature_cols, scaler = engineer_features(df)

    print("=== 2. TRAINING MODEL ===")
    model = train_isolation_forest(X_scaled)
    joblib.dump(model, f"{OUT_PREFIX}_model.joblib")
    joblib.dump(scaler, f"{OUT_PREFIX}_scaler.joblib")

    print("=== 3. APPLYING DETECTION ===")
    df_out = apply_model(df_feat, model, X_scaled)

    print("=== 4. SUMMARY ===")
    s = summarise_anomalies(df_out)
    print(f"Processed Rows: {s['total_rows']}")
    print(f"Anomalies Found: {s['anomaly_count']} ({s['anomaly_percentage']:.2f}%)")

    print("=== 5. GENERATING VISUALS ===")
    plot_price_with_anomalies(df_out)
    plot_anomaly_counts(df_out)
    plot_pca_separation(df_out, X_scaled)

    df_out.to_csv(f"{OUT_PREFIX}_results.csv", index=False)
    print(f"[DONE] Results saved to {OUT_PREFIX}_results.csv")

if __name__ == "__main__":
    main()