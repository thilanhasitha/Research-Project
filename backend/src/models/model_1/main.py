import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from pd_logic import load_and_clean, engineer_features, validate_dump
from config import *

def main():
    print("--- Starting Pump & Dump Detection ---")
    
    # 1. Load
    df = load_and_clean()
    print(f"Loaded {len(df)} rows.")
    
    # 2. Features
    df_feat, X_scaled, feat_cols = engineer_features(df)
    
    # 3. Model
    model = IsolationForest(n_estimators=N_ESTIMATORS, 
                            contamination="auto", 
                            random_state=RANDOM_STATE)
    model.fit(X_scaled)
    
    # 4. Detect
    df_feat["anomaly_score"] = -model.score_samples(X_scaled)
    # Calculate threshold based on top 3% (CONTAMINATION_FRACTION)
    threshold = np.percentile(df_feat["anomaly_score"], 100 * (1 - CONTAMINATION_FRACTION))
    
    # Define Fraud: AI Flag + Price > 10% + Volume > 3x
    mask = (df_feat["anomaly_score"] >= threshold) & \
           (df_feat["gap_return"] > 0.10) & \
           (df_feat["vol_surge_ratio"] > 3.0)
           
    df_feat["anomaly_label"] = 1
    df_feat.loc[mask, "anomaly_label"] = -1
    
    # 5. Validate Dump (The Crash)
    df_results = validate_dump(df_feat)
    
    # 6. PCA Visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(X_pca[df_results['anomaly_label']==1, 0], 
                X_pca[df_results['anomaly_label']==1, 1], 
                alpha=0.2, c='blue', label='Normal')
    plt.scatter(X_pca[df_results['anomaly_label']==-1, 0], 
                X_pca[df_results['anomaly_label']==-1, 1], 
                c='red', label='Pump Candidates', edgecolors='black')
    plt.title("Forensic Analysis: PCA Feature Isolation")
    plt.legend()
    plt.savefig(f"{OUT_PREFIX}_pca_plot.png")
    
    # 7. Final Report
    flagged = df_results[df_results['anomaly_label'] == -1]
    confirmed = flagged[flagged['reversion_ratio'] > 0.5]
    
    print(f"Total Anomalies Flagged: {len(flagged)}")
    print(f"Confirmed with 'Dump' Phase (>50% reversion): {len(confirmed)}")
    
    df_results.to_csv(f"{OUT_PREFIX}_final_results.csv", index=False)
    print(f"Results saved to {OUT_PREFIX}_final_results.csv")

if __name__ == "__main__":
    main()













    import pandas as pd
from config import TICKER_COL, DATE_COL, CHANGE_PCT_COL

# Load the results your model just created
results_df = pd.read_csv("pumpdump_local_final_results.csv")

# Filter for the most suspicious cases
final_report = results_df[results_df['anomaly_label'] == -1].sort_values(by='reversion_ratio', ascending=False)

# Select key columns for the research table
final_report = final_report[[TICKER_COL, DATE_COL, CHANGE_PCT_COL, 'vol_surge_ratio', 'reversion_ratio']]

print("\n" + "="*60)
print("       TOP 10 CONFIRMED PUMP & DUMP EVENTS (2023)")
print("="*60)
print(final_report.head(10).to_string(index=False))
print("="*60)

# Save this specific table for your report
final_report.head(10).to_csv("research_top_10_cases.csv", index=False)