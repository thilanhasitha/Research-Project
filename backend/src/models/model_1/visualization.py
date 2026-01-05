import matplotlib
matplotlib.use("Agg") # Required for Uvicorn/FastAPI servers
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.decomposition import PCA
from .config import DATE_COL, DAY_CLOSE_COL, TICKER_COL, OUT_PREFIX

# --- PREVIOUS DETAILS (The original charts) ---

def plot_price_with_anomalies(df: pd.DataFrame):
    """The original chart requested by your API."""
    df = df.sort_values(DATE_COL)
    anom = df[df["anomaly_label"] == -1]

    plt.figure(figsize=(12, 5))
    plt.plot(df[DATE_COL], df[DAY_CLOSE_COL], label="Day Close", color="blue", alpha=0.6)
    plt.scatter(anom[DATE_COL], anom[DAY_CLOSE_COL], color="red", label="Fraud Candidate", s=30, zorder=3)
    
    plt.title("Historical Price with Pump & Dump Flags")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{OUT_PREFIX}_price_anomalies.png")
    plt.close()

def plot_anomaly_counts(df: pd.DataFrame):
    """Simple bar chart of normal vs fraud."""
    n_anom = int((df["anomaly_label"] == -1).sum())
    n_norm = int((df["anomaly_label"] == 1).sum())

    plt.figure(figsize=(6, 4))
    sns.barplot(x=["Normal", "Fraud Candidate"], y=[n_norm, n_anom], palette=["green", "red"])
    plt.title("Detection Summary: Total Flagged Stocks")
    plt.tight_layout()
    plt.savefig(f"{OUT_PREFIX}_anomaly_counts.png")
    plt.close()

# --- NEW FORENSIC DETAILS (Advanced Analysis) ---

def plot_pca_separation(df, X_scaled):
    """Mathematical proof of why these stocks are fraud."""
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    plt.figure(figsize=(10, 7))
    plt.scatter(X_pca[df['anomaly_label']==1, 0], X_pca[df['anomaly_label']==1, 1], 
                c='blue', label='Normal', alpha=0.3, s=10)
    plt.scatter(X_pca[df['anomaly_label']==-1, 0], X_pca[df['anomaly_label']==-1, 1], 
                c='red', label='Pump Candidate', s=40, edgecolors='black')
    
    plt.title("PCA Spatial Isolation: Fraud vs Market Noise")
    plt.legend()
    plt.savefig(f"{OUT_PREFIX}_pca_proof.png")
    plt.close()

def plot_specific_case(df, ticker_name):
    """Deep-dive into a single pump and dump event."""
    stock_data = df[df[TICKER_COL] == ticker_name].sort_values(DATE_COL)
    anomalies = stock_data[stock_data['anomaly_label'] == -1]

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(stock_data[DATE_COL], stock_data[DAY_CLOSE_COL], color='tab:blue', label='Price')
    ax1.scatter(anomalies[DATE_COL], anomalies[DAY_CLOSE_COL], color='red', s=100, label='Detection', zorder=5)
    
    ax2 = ax1.twinx()
    ax2.bar(stock_data[DATE_COL], stock_data.get('vol_surge_ratio', 0), alpha=0.2, color='gray', label='Vol Surge')
    
    plt.title(f"Forensic Case Study: {ticker_name}")
    plt.savefig(f"{OUT_PREFIX}_case_study_{ticker_name}.png")
    plt.close()




    