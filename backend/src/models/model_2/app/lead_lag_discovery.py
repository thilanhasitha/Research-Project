import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import networkx as nx
import os
import warnings

warnings.filterwarnings("ignore")

def perform_lead_lag_discovery(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found")
        return None, None
        
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Clean duplicates to ensure the pivot works
    df = df.drop_duplicates(subset=['Date', 'Symbol'], keep='last')

    # Pivot the data: Rows = Dates, Columns = Stocks
    pivot_df = df.pivot(index='Date', columns='Symbol', values='Intraday_Return').fillna(0)
    symbols = pivot_df.columns.tolist()
    
    lead_lag_edges = []
    max_search = min(len(symbols), 50)
    print(f"🔍 Analyzing {max_search} stocks with Relaxed Thresholds...")
    
    for i in range(max_search):
        for j in range(i + 1, max_search):
            try:
                # Force 1-D arrays and convert to standard lists
                s1 = np.array(pivot_df[symbols[i]].values).flatten()
                s2 = np.array(pivot_df[symbols[j]].values).flatten()
                
                # Z-score scaling: making a 10 LKR and 1000 LKR stock comparable
                s1_scaled = (s1 - np.mean(s1)) / (np.std(s1) + 1e-9)
                s2_scaled = (s2 - np.mean(s2)) / (np.std(s2) + 1e-9)
                
                # Calculate DTW
                distance, path = fastdtw(s1_scaled.tolist(), s2_scaled.tolist(), dist=euclidean)
                
                # Lead-Lag Logic: avg_diff > 0 means stock_i leads stock_j
                diffs = [p[0] - p[1] for p in path]
                avg_diff = np.mean(diffs)
                
                # RELAXED THRESHOLDS for Forensic Discovery
                if distance < 500: 
                    print(f"🔗 Match found: {symbols[i]} & {symbols[j]} (Dist: {round(distance,1)})")
                    if avg_diff > 0.2:
                        lead_lag_edges.append((symbols[i], symbols[j], distance))
                    elif avg_diff < -0.2:
                        lead_lag_edges.append((symbols[j], symbols[i], distance))
                        
            except Exception:
                continue

    # 4. Build the Directed Network
    G = nx.DiGraph()
    for leader, follower, dist in lead_lag_edges:
        G.add_edge(leader, follower, weight=round(100/dist, 2))

    # Identify the Syndicates (Communities)
    communities = list(nx.community.greedy_modularity_communities(G.to_undirected()))
    print(f"✅ Success! Found {len(communities)} potential syndicates.")
    return G, communities

if __name__ == "__main__":
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.normpath(os.path.join(current_script_dir, '..', 'data', 'processed', 'cse_standardized_features.csv'))
    
    graph, syndicates = perform_lead_lag_discovery(input_path)
    
    if graph:
        output_dir = os.path.join(current_script_dir, '..', 'data', 'processed')
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        
        report_path = os.path.join(output_dir, 'fraud_syndicates.txt')
        with open(report_path, 'w') as f:
            f.write("--- CSE FORENSIC: SYNDICATE REPORT ---\n")
            f.write("Threshold: Relaxed (Dist < 500, Lag > 0.2)\n\n")
            for idx, s in enumerate(syndicates):
                f.write(f"Syndicate {idx+1}: {', '.join(list(s))}\n")
        print(f"📂 Report saved: {report_path}")