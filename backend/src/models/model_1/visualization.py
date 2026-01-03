# visualization.py

import matplotlib
matplotlib.use("Agg")     # <<< IMPORTANT: disable Tkinter GUI backend

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.decomposition import PCA


from .config import DATE_COL, TICKER_COL, DAY_CLOSE_COL, OUT_PREFIX


def plot_price_with_anomalies(df: pd.DataFrame):
    df = df.sort_values(DATE_COL)
    anom = df[df["anomaly_label"] == -1]

    plt.figure(figsize=(12, 5))
    plt.plot(df[DATE_COL], df[DAY_CLOSE_COL], label="Day Close", color="blue", alpha=0.6)

    plt.scatter(
        anom[DATE_COL],
        anom[DAY_CLOSE_COL],
        color="red",
        label="Anomaly",
        s=30,
        zorder=3,
    )
    plt.title("Day Close with detected anomalies (pump & dump candidates)")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()

    filename = f"{OUT_PREFIX}_price_anomalies.png"
    plt.savefig(filename, dpi=200)
    print(f"[INFO] Saved {filename}")

    plt.close()


def plot_anomaly_counts(df: pd.DataFrame):
    n_anom = int((df["anomaly_label"] == -1).sum())
    n_norm = int((df["anomaly_label"] == 1).sum())

    plt.figure(figsize=(4, 4))
    plt.bar(["Normal", "Anomaly"], [n_norm, n_anom], color=["green", "red"])
    plt.title("Number of normal vs anomalous rows")
    plt.ylabel("Count")
    plt.tight_layout()

    filename = f"{OUT_PREFIX}_anomaly_counts.png"
    plt.savefig(filename, dpi=200)
    print(f"[INFO] Saved {filename}")

    plt.close()



def plot_pca_separation(df, X_scaled):
    # 1. Reduce your 7 features to 2 dimensions
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    df['pca_1'] = X_pca[:, 0]
    df['pca_2'] = X_pca[:, 1]
    
    # 2. Separate normal and anomalies
    normal = df[df['anomaly_label'] == 1]
    anomalies = df[df['anomaly_label'] == -1]
    
    # 3. Create the Plot
    plt.figure(figsize=(10, 7))
    plt.scatter(normal['pca_1'], normal['pca_2'], c='blue', label='Normal', alpha=0.5, s=10)
    plt.scatter(anomalies['pca_1'], anomalies['pca_2'], c='red', label='Fraud Candidate', s=30)
    
    plt.title("PCA Proof: Spatial Isolation of Pump & Dump Candidates")
    plt.xlabel(f"Principal Component 1 ({pca.explained_variance_ratio_[0]:.1%} variance)")
    plt.ylabel(f"Principal Component 2 ({pca.explained_variance_ratio_[1]:.1%} variance)")
    plt.legend()
    filename = f"{OUT_PREFIX}_pca_proof_chart.png"
    plt.savefig(filename, dpi=200)
    # plt.show()
    print(f"[INFO] Saved {filename}")