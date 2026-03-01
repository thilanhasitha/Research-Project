"""
Example: Using ChromaDB Integration with LSTM Predictions

Add these cells to your notebook after training models
"""

# ==========================================
# CELL 1: Import ChromaDB Integration
# ==========================================
import sys
sys.path.append('..')  # Adjust path if needed

from chromadb_integration import LSTMPredictionStore

# Initialize ChromaDB store
# Use 'localhost' when running notebook locally
# Use 'chromadb' when running inside Docker network
store = LSTMPredictionStore(host="localhost", port=8000)


# ==========================================
# CELL 2: Store All Prediction Results
# ==========================================
# After running STEP 3 (train_company_lstm for multiple companies)
# You should have a 'results' variable with all predictions

if 'results' in globals():
    # Filter successful results
    successful_results = [r for r in results if r['status'] == 'success']
    
    print(f"Storing {len(successful_results)} predictions...")
    stored_ids = store.store_batch(successful_results, model_version="v1.0")
    
    print(f"\n✓ Successfully stored {len(stored_ids)} predictions")
else:
    print("⚠ No 'results' variable found. Please run STEP 3 first.")


# ==========================================
# CELL 3: Query by Company Name
# ==========================================
# Search for predictions by company name
company_search = "Bank"  # Change this to your company name

results = store.query_by_company(company_search, limit=5)

print(f"\nFound {len(results['ids'])} predictions for companies containing '{company_search}':")
print("="*70)

for i, (doc_id, metadata) in enumerate(zip(results['ids'], results['metadatas']), 1):
    print(f"{i}. {metadata['company']}")
    print(f"   R² Score: {metadata['r2_score']:.4f}")
    print(f"   MAE: {metadata['mae']:.6f}")
    print(f"   Performance: {metadata['performance']}")
    print(f"   Timestamp: {metadata['timestamp']}\n")


# ==========================================
# CELL 4: Get Best Performing Predictions
# ==========================================
# Get predictions with high R² scores
min_r2 = 0.7

best_results = store.query_by_r2_threshold(min_r2=min_r2, limit=10)

print(f"\nTop predictions with R² ≥ {min_r2}:")
print("="*70)

# Sort by R² score
sorted_results = sorted(
    zip(best_results['ids'], best_results['metadatas']),
    key=lambda x: x[1]['r2_score'],
    reverse=True
)

for i, (doc_id, metadata) in enumerate(sorted_results, 1):
    print(f"{i}. {metadata['company'][:45]:<45} | R²={metadata['r2_score']:.4f} | MAE={metadata['mae']:.6f}")


# ==========================================
# CELL 5: Query by Performance Category
# ==========================================
# Get predictions grouped by performance
import pandas as pd

categories = ["excellent", "good", "fair", "poor"]

print("\nPREDICTIONS BY PERFORMANCE CATEGORY")
print("="*70)

summary = []

for category in categories:
    results = store.query_by_performance(category, limit=100)
    count = len(results['ids'])
    
    print(f"\n{category.upper()}: {count} predictions")
    
    if count > 0:
        # Show top 3
        for i, (doc_id, metadata) in enumerate(zip(results['ids'][:3], results['metadatas'][:3]), 1):
            print(f"  {i}. {metadata['company'][:40]} | R²={metadata['r2_score']:.4f}")
    
    summary.append({"category": category, "count": count})

# Summary DataFrame
df_summary = pd.DataFrame(summary)
print("\n" + "="*70)
print("SUMMARY:")
print(df_summary.to_string(index=False))


# ==========================================
# CELL 6: Get All Predictions as DataFrame
# ==========================================
# Get complete DataFrame for analysis
df_all = store.get_all_as_dataframe()

print(f"\nTotal Predictions: {len(df_all)}")
print("\nTop 10 by R² Score:")
print(df_all[['company', 'r2_score', 'mae', 'rmse', 'performance', 'timestamp']].head(10))

print("\n" + "="*70)
print("STATISTICS:")
print(df_all[['r2_score', 'mae', 'rmse', 'mse']].describe())


# ==========================================
# CELL 7: Visualize ChromaDB Results
# ==========================================
import matplotlib.pyplot as plt

df = store.get_all_as_dataframe()

if not df.empty:
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. R² Score distribution
    ax1 = axes[0, 0]
    ax1.hist(df['r2_score'], bins=20, color='steelblue', alpha=0.7, edgecolor='black')
    ax1.axvline(df['r2_score'].mean(), color='red', linestyle='--', label=f"Mean: {df['r2_score'].mean():.3f}")
    ax1.set_xlabel('R² Score')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of R² Scores')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Performance category pie chart
    ax2 = axes[0, 1]
    performance_counts = df['performance'].value_counts()
    colors = {'excellent': 'green', 'good': 'lightgreen', 'fair': 'orange', 'poor': 'red'}
    pie_colors = [colors.get(cat, 'gray') for cat in performance_counts.index]
    ax2.pie(performance_counts, labels=performance_counts.index, autopct='%1.1f%%', 
            colors=pie_colors, startangle=90)
    ax2.set_title('Performance Distribution')
    
    # 3. R² vs MAE scatter
    ax3 = axes[1, 0]
    scatter = ax3.scatter(df['mae'], df['r2_score'], 
                         c=df['r2_score'], cmap='RdYlGn', 
                         s=100, alpha=0.6, edgecolors='black')
    ax3.set_xlabel('Mean Absolute Error')
    ax3.set_ylabel('R² Score')
    ax3.set_title('R² Score vs MAE')
    ax3.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax3, label='R² Score')
    
    # 4. Top 10 companies
    ax4 = axes[1, 1]
    top10 = df.nlargest(10, 'r2_score')
    companies_short = [c[:20] for c in top10['company']]
    ax4.barh(companies_short, top10['r2_score'], color='steelblue', alpha=0.7)
    ax4.set_xlabel('R² Score')
    ax4.set_title('Top 10 Companies by R² Score')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print("✓ Visualizations created from ChromaDB data")
else:
    print("⚠ No data in ChromaDB to visualize")


# ==========================================
# CELL 8: Get Collection Statistics
# ==========================================
stats = store.get_statistics()

print("\nCHROMADB COLLECTION STATISTICS")
print("="*70)
print(f"Total Predictions: {stats['total_predictions']}")
print(f"Unique Companies: {stats['companies']}")
print(f"\nR² Score Statistics:")
print(f"  Average: {stats['avg_r2_score']:.4f}")
print(f"  Median:  {stats['median_r2_score']:.4f}")
print(f"  Best:    {stats['best_r2_score']:.4f}")
print(f"  Worst:   {stats['worst_r2_score']:.4f}")
print(f"\nAverage MAE: {stats['avg_mae']:.6f}")
print(f"\nPerformance Distribution:")
for category, count in stats['performance_distribution'].items():
    print(f"  {category}: {count}")


# ==========================================
# CELL 9: Compare Multiple Training Runs
# ==========================================
# If you train models multiple times, you can track improvements

def compare_model_versions(store):
    """Compare predictions across different model versions"""
    df = store.get_all_as_dataframe()
    
    if 'model_version' in df.columns:
        print("\nMODEL VERSION COMPARISON")
        print("="*70)
        
        comparison = df.groupby('model_version').agg({
            'r2_score': ['mean', 'median', 'max', 'min', 'count'],
            'mae': 'mean',
            'rmse': 'mean'
        }).round(4)
        
        print(comparison)
        
        # Plot comparison
        import matplotlib.pyplot as plt
        
        versions = df['model_version'].unique()
        if len(versions) > 1:
            fig, ax = plt.subplots(1, 2, figsize=(14, 5))
            
            df.boxplot(column='r2_score', by='model_version', ax=ax[0])
            ax[0].set_title('R² Score by Model Version')
            ax[0].set_xlabel('Model Version')
            ax[0].set_ylabel('R² Score')
            
            df.boxplot(column='mae', by='model_version', ax=ax[1])
            ax[1].set_title('MAE by Model Version')
            ax[1].set_xlabel('Model Version')
            ax[1].set_ylabel('MAE')
            
            plt.suptitle('')  # Remove default title
            plt.tight_layout()
            plt.show()
    else:
        print("⚠ Only one model version found")

compare_model_versions(store)


# ==========================================
# CELL 10: Export Results
# ==========================================
# Export ChromaDB data for reporting

df = store.get_all_as_dataframe()

if not df.empty:
    # Export to CSV
    output_file = "chromadb_predictions_export.csv"
    df.to_csv(output_file, index=False)
    print(f"✓ Exported {len(df)} predictions to {output_file}")
    
    # Create summary report
    summary_file = "prediction_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("LSTM STOCK PREDICTION SUMMARY\n")
        f.write("="*70 + "\n\n")
        
        stats = store.get_statistics()
        f.write(f"Total Predictions: {stats['total_predictions']}\n")
        f.write(f"Unique Companies: {stats['companies']}\n")
        f.write(f"Average R² Score: {stats['avg_r2_score']:.4f}\n")
        f.write(f"Median R² Score: {stats['median_r2_score']:.4f}\n")
        f.write(f"Best R² Score: {stats['best_r2_score']:.4f}\n")
        f.write(f"Average MAE: {stats['avg_mae']:.6f}\n\n")
        
        f.write("Performance Distribution:\n")
        for category, count in stats['performance_distribution'].items():
            pct = (count / stats['total_predictions']) * 100
            f.write(f"  {category.capitalize()}: {count} ({pct:.1f}%)\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("TOP 10 PREDICTIONS:\n\n")
        
        top10 = df.nlargest(10, 'r2_score')
        for i, row in enumerate(top10.itertuples(), 1):
            f.write(f"{i}. {row.company}\n")
            f.write(f"   R²: {row.r2_score:.4f} | MAE: {row.mae:.6f} | RMSE: {row.rmse:.6f}\n\n")
    
    print(f"✓ Created summary report: {summary_file}")
else:
    print("⚠ No data to export")
