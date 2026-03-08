import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import seaborn as sns
import os
from config import DATE_COL, DAY_CLOSE_COL, TICKER_COL, OUT_PREFIX

def save_forensic_plots(df, ticker_name, shap_contributions=None):
    """Generates a report image for a specific fraud case."""
    stock_data = df[df[TICKER_COL] == ticker_name].sort_values(DATE_COL)
    anomalies = stock_data[stock_data['anomaly_label'] == -1]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1]})
    
    # Panel 1: Price Action
    ax1.plot(stock_data[DATE_COL], stock_data[DAY_CLOSE_COL], color='dodgerblue', label='Price')
    ax1.scatter(anomalies[DATE_COL], anomalies[DAY_CLOSE_COL], color='red', s=100, label='Pump Detected', zorder=5)
    ax1.set_title(f"Forensic Analysis: {ticker_name} Pump & Dump Signature")
    ax1.legend()

    # Panel 2: Reasonings (Placeholder if SHAP not provided)
    if shap_contributions:
        features = list(shap_contributions.keys())
        impacts = list(shap_contributions.values())
        sns.barplot(x=impacts, y=features, ax=ax2, palette="Reds_r")
        ax2.set_title("AI Decision Logic: Feature Impact (%)")
    
    plt.tight_layout()
    filename = f"{OUT_PREFIX}_{ticker_name}_report.png"
    plt.savefig(filename)
    plt.close()