"""
Company Performance Analysis - Cross-Sectional Analysis of Sri Lankan Stock Market
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the data
file_path = r'C:\Users\USER\OneDrive\Documents\GitHub\Research-Project\backend\lstm_stock_prediction\data\processed\Annual.csv'
data = pd.read_excel(file_path, skiprows=4)

# Remove unwanted columns
first_col = data.columns[0]
data = data[[col for col in data.columns if not (col.startswith('Unnamed') or 'MAIN TYPE' in str(col).upper() or 'SUB TYPE' in str(col).upper())]]

# Remove NaN rows
data = data.dropna(subset=[first_col])

# Get necessary columns dynamically
company_col = [col for col in data.columns if 'COMPANY' in str(col).upper()][0]
close_col = [col for col in data.columns if 'CLOSE' in str(col).upper()][0]
open_col = [col for col in data.columns if 'OPEN' in str(col).upper()][0]
high_col = [col for col in data.columns if 'HIGH' in str(col).upper()][0]
low_col = [col for col in data.columns if 'LOW' in str(col).upper()][0]
turnover_col = [col for col in data.columns if 'TURNOVER' in str(col).upper()][0]
shares_col = [col for col in data.columns if 'SHARES' in str(col).upper()][0]

# Convert to numeric
analysis_df = data.copy()
analysis_df[close_col] = pd.to_numeric(analysis_df[close_col], errors='coerce')
analysis_df[open_col] = pd.to_numeric(analysis_df[open_col], errors='coerce')
analysis_df[high_col] = pd.to_numeric(analysis_df[high_col], errors='coerce')
analysis_df[low_col] = pd.to_numeric(analysis_df[low_col], errors='coerce')
analysis_df[turnover_col] = pd.to_numeric(analysis_df[turnover_col], errors='coerce')
analysis_df[shares_col] = pd.to_numeric(analysis_df[shares_col], errors='coerce')

# Remove rows with NaN in key columns
analysis_df = analysis_df.dropna(subset=[close_col, open_col, high_col, low_col])

# Calculate additional metrics
analysis_df['Price_Range'] = analysis_df[high_col] - analysis_df[low_col]
analysis_df['Price_Change_%'] = ((analysis_df[close_col] - analysis_df[open_col]) / analysis_df[open_col]) * 100
analysis_df['Volatility_%'] = (analysis_df['Price_Range'] / analysis_df[open_col]) * 100

# Sort by different metrics
sorted_by_price = analysis_df.sort_values(close_col, ascending=False)
sorted_by_change = analysis_df.sort_values('Price_Change_%', ascending=False)
sorted_by_turnover = analysis_df.sort_values(turnover_col, ascending=False)
sorted_by_volatility = analysis_df.sort_values('Volatility_%', ascending=False)

print("="*100)
print("📊 SRI LANKAN STOCK MARKET - COMPANY PERFORMANCE ANALYSIS")
print("="*100)

# ========== ANALYSIS 1: TOP & BOTTOM BY PRICE ==========
print("\n" + "="*100)
print("TOP 10 HIGHEST VALUED COMPANIES (by Closing Price)")
print("="*100)
print(f"{'Rank':<6}{'Company':<45}{'Open':<12}{'High':<12}{'Low':<12}{'Close':<12}{'Change %':<10}")
print("-"*100)

for idx, (i, row) in enumerate(sorted_by_price.head(10).iterrows(), 1):
    company = str(row[company_col])[:43]
    open_p = row[open_col]
    high_p = row[high_col]
    low_p = row[low_col]
    close_p = row[close_col]
    change = row['Price_Change_%']
    status = "📈" if change > 0 else "📉" if change < 0 else "→"
    
    print(f"{idx:<6}{company:<45}{open_p:<12.2f}{high_p:<12.2f}{low_p:<12.2f}{close_p:<12.2f}{status} {change:>7.2f}%")

print("\n" + "="*100)
print("BOTTOM 10 LOWEST VALUED COMPANIES (by Closing Price)")
print("="*100)
print(f"{'Rank':<6}{'Company':<45}{'Open':<12}{'High':<12}{'Low':<12}{'Close':<12}{'Change %':<10}")
print("-"*100)

for idx, (i, row) in enumerate(sorted_by_price.tail(10).iterrows(), 1):
    company = str(row[company_col])[:43]
    open_p = row[open_col]
    high_p = row[high_col]
    low_p = row[low_col]
    close_p = row[close_col]
    change = row['Price_Change_%']
    status = "📈" if change > 0 else "📉" if change < 0 else "→"
    
    print(f"{idx:<6}{company:<45}{open_p:<12.2f}{high_p:<12.2f}{low_p:<12.2f}{close_p:<12.2f}{status} {change:>7.2f}%")

print("-"*100)

# ========== ANALYSIS 2: BEST & WORST PERFORMERS ==========
print("\n" + "="*100)
print("TOP 10 BEST PERFORMING COMPANIES (by Price Change %)")
print("="*100)
print(f"{'Rank':<6}{'Company':<45}{'Open (Rs.)':<15}{'Close (Rs.)':<15}{'Change %':<12}{'Status':<10}")
print("-"*100)

for idx, (i, row) in enumerate(sorted_by_change.head(10).iterrows(), 1):
    company = str(row[company_col])[:43]
    open_p = row[open_col]
    close_p = row[close_col]
    change = row['Price_Change_%']
    
    if change >= 10:
        status = "🔥 Excellent"
    elif change >= 5:
        status = "✅ Good"
    elif change >= 0:
        status = "➕ Positive"
    else:
        status = "⚠ Negative"
    
    print(f"{idx:<6}{company:<45}{open_p:<15.2f}{close_p:<15.2f}{change:>10.2f}%  {status:<10}")

print("\n" + "="*100)
print("BOTTOM 10 WORST PERFORMING COMPANIES (by Price Change %)")
print("="*100)
print(f"{'Rank':<6}{'Company':<45}{'Open (Rs.)':<15}{'Close (Rs.)':<15}{'Change %':<12}{'Status':<10}")
print("-"*100)

for idx, (i, row) in enumerate(sorted_by_change.tail(10).iterrows(), 1):
    company = str(row[company_col])[:43]
    open_p = row[open_col]
    close_p = row[close_col]
    change = row['Price_Change_%']
    
    if change <= -10:
        status = "❌ Severe"
    elif change <= -5:
        status = "⚠ Poor"
    elif change < 0:
        status = "➖ Negative"
    else:
        status = "→ Neutral"
    
    print(f"{idx:<6}{company:<45}{open_p:<15.2f}{close_p:<15.2f}{change:>10.2f}%  {status:<10}")

print("-"*100)

# ========== ANALYSIS 3: MOST TRADED COMPANIES ==========
print("\n" + "="*100)
print("TOP 10 MOST ACTIVELY TRADED COMPANIES (by Turnover)")
print("="*100)
print(f"{'Rank':<6}{'Company':<45}{'Turnover (Rs.)':<18}{'Shares Traded':<18}{'Close Price':<12}")
print("-"*100)

for idx, (i, row) in enumerate(sorted_by_turnover.head(10).iterrows(), 1):
    company = str(row[company_col])[:43]
    turnover = row[turnover_col]
    shares = row[shares_col]
    close_p = row[close_col]
    
    # Format large numbers
    if turnover >= 1_000_000:
        turnover_str = f"{turnover/1_000_000:.2f}M"
    elif turnover >= 1_000:
        turnover_str = f"{turnover/1_000:.2f}K"
    else:
        turnover_str = f"{turnover:.2f}"
    
    if shares >= 1_000_000:
        shares_str = f"{shares/1_000_000:.2f}M"
    elif shares >= 1_000:
        shares_str = f"{shares/1_000:.2f}K"
    else:
        shares_str = f"{shares:.0f}"
    
    print(f"{idx:<6}{company:<45}{turnover_str:<18}{shares_str:<18}{close_p:<12.2f}")

print("-"*100)
print(f"\n📊 Trading Activity Summary:")
print(f"   Total Market Turnover: Rs. {analysis_df[turnover_col].sum():,.2f}")
print(f"   Total Shares Traded: {analysis_df[shares_col].sum():,.0f}")
print(f"   Average Turnover per Company: Rs. {analysis_df[turnover_col].mean():,.2f}")
print(f"   Median Turnover: Rs. {analysis_df[turnover_col].median():,.2f}")

# ========== ANALYSIS 4: VOLATILITY ANALYSIS ==========
print("\n" + "="*100)
print("TOP 10 MOST VOLATILE COMPANIES (High Risk/High Reward)")
print("="*100)
print(f"{'Rank':<6}{'Company':<45}{'Volatility %':<15}{'Price Range':<15}{'Close Price':<12}")
print("-"*100)

for idx, (i, row) in enumerate(sorted_by_volatility.head(10).iterrows(), 1):
    company = str(row[company_col])[:43]
    volatility = row['Volatility_%']
    price_range = row['Price_Range']
    close_p = row[close_col]
    
    print(f"{idx:<6}{company:<45}{volatility:>12.2f}%  {price_range:<15.2f}{close_p:<12.2f}")

print("\n" + "="*100)
print("TOP 10 LEAST VOLATILE COMPANIES (Low Risk/Stable)")
print("="*100)
print(f"{'Rank':<6}{'Company':<45}{'Volatility %':<15}{'Price Range':<15}{'Close Price':<12}")
print("-"*100)

for idx, (i, row) in enumerate(sorted_by_volatility.tail(10).iterrows(), 1):
    company = str(row[company_col])[:43]
    volatility = row['Volatility_%']
    price_range = row['Price_Range']
    close_p = row[close_col]
    
    print(f"{idx:<6}{company:<45}{volatility:>12.2f}%  {price_range:<15.2f}{close_p:<12.2f}")

print("-"*100)

# ========== OVERALL MARKET SUMMARY ==========
print("\n" + "="*100)
print("📊 COMPREHENSIVE MARKET ANALYSIS SUMMARY")
print("="*100)

print(f"\n1. MARKET OVERVIEW:")
print(f"   • Total Companies Analyzed: {len(analysis_df)}")
print(f"   • Average Closing Price: Rs. {analysis_df[close_col].mean():,.2f}")
print(f"   • Median Closing Price: Rs. {analysis_df[close_col].median():,.2f}")
print(f"   • Highest Stock Price: Rs. {analysis_df[close_col].max():,.2f} ({sorted_by_price.iloc[0][company_col]})")
print(f"   • Lowest Stock Price: Rs. {analysis_df[close_col].min():,.2f} ({sorted_by_price.iloc[-1][company_col]})")

print(f"\n2. PERFORMANCE METRICS:")
positive_returns = len(analysis_df[analysis_df['Price_Change_%'] > 0])
negative_returns = len(analysis_df[analysis_df['Price_Change_%'] < 0])
neutral_returns = len(analysis_df[analysis_df['Price_Change_%'] == 0])

print(f"   • Companies with Positive Returns: {positive_returns} ({100*positive_returns/len(analysis_df):.1f}%)")
print(f"   • Companies with Negative Returns: {negative_returns} ({100*negative_returns/len(analysis_df):.1f}%)")
print(f"   • Companies with No Change: {neutral_returns} ({100*neutral_returns/len(analysis_df):.1f}%)")
print(f"   • Average Price Change: {analysis_df['Price_Change_%'].mean():.2f}%")
print(f"   • Best Performer: {sorted_by_change.iloc[0]['Price_Change_%']:.2f}% ({sorted_by_change.iloc[0][company_col]})")
print(f"   • Worst Performer: {sorted_by_change.iloc[-1]['Price_Change_%']:.2f}% ({sorted_by_change.iloc[-1][company_col]})")

print(f"\n3. VOLATILITY ANALYSIS:")
print(f"   • Average Volatility: {analysis_df['Volatility_%'].mean():.2f}%")
print(f"   • Most Volatile: {sorted_by_volatility.iloc[0]['Volatility_%']:.2f}% ({sorted_by_volatility.iloc[0][company_col]})")
print(f"   • Least Volatile: {sorted_by_volatility.iloc[-1]['Volatility_%']:.2f}% ({sorted_by_volatility.iloc[-1][company_col]})")

high_volatility = len(analysis_df[analysis_df['Volatility_%'] > 10])
moderate_volatility = len(analysis_df[(analysis_df['Volatility_%'] >= 5) & (analysis_df['Volatility_%'] <= 10)])
low_volatility = len(analysis_df[analysis_df['Volatility_%'] < 5])

print(f"   • High Volatility (>10%): {high_volatility} companies ({100*high_volatility/len(analysis_df):.1f}%)")
print(f"   • Moderate Volatility (5-10%): {moderate_volatility} companies ({100*moderate_volatility/len(analysis_df):.1f}%)")
print(f"   • Low Volatility (<5%): {low_volatility} companies ({100*low_volatility/len(analysis_df):.1f}%)")

print(f"\n4. 💡 INVESTMENT INSIGHTS:")
print(f"   ✅ BEST VALUE INVESTMENTS (High price + Positive returns):")
valuable_stocks = analysis_df[(analysis_df[close_col] > analysis_df[close_col].median()) & 
                               (analysis_df['Price_Change_%'] > 0)].sort_values('Price_Change_%', ascending=False).head(5)
for i, (idx, row) in enumerate(valuable_stocks.iterrows(), 1):
    print(f"      {i}. {row[company_col][:50]} - Rs. {row[close_col]:.2f} (+{row['Price_Change_%']:.2f}%)")

print(f"\n   ⚠ HIGH RISK/HIGH REWARD (High volatility + High returns):")
risky_stocks = analysis_df[(analysis_df['Volatility_%'] > analysis_df['Volatility_%'].quantile(0.75)) & 
                            (analysis_df['Price_Change_%'] > 5)].sort_values('Price_Change_%', ascending=False).head(5)
for i, (idx, row) in enumerate(risky_stocks.iterrows(), 1):
    print(f"      {i}. {row[company_col][:50]} - Volatility: {row['Volatility_%']:.2f}%, Return: {row['Price_Change_%']:.2f}%")

print(f"\n   🛡️ STABLE INVESTMENTS (Low volatility + Positive returns):")
stable_stocks = analysis_df[(analysis_df['Volatility_%'] < 5) & 
                             (analysis_df['Price_Change_%'] > 0)].sort_values(close_col, ascending=False).head(5)
for i, (idx, row) in enumerate(stable_stocks.iterrows(), 1):
    print(f"      {i}. {row[company_col][:50]} - Rs. {row[close_col]:.2f} (Volatility: {row['Volatility_%']:.2f}%)")

print("\n" + "="*100)
print("✅ Analysis Complete!")
print("="*100)

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# 1. Top 15 Companies by Closing Price
ax1 = axes[0, 0]
top_15_price = sorted_by_price.head(15)
companies_short = [str(c)[:25] for c in top_15_price[company_col]]
prices = top_15_price[close_col]
colors = plt.cm.viridis(np.linspace(0, 1, len(companies_short)))

ax1.barh(companies_short, prices, color=colors)
ax1.set_xlabel('Closing Price (Rs.)', fontsize=12, fontweight='bold')
ax1.set_title('Top 15 Highest Valued Companies', fontsize=14, fontweight='bold')
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)

# 2. Top 15 Best Performers by Price Change %
ax2 = axes[0, 1]
top_15_change = sorted_by_change.head(15)
companies_change = [str(c)[:25] for c in top_15_change[company_col]]
changes = top_15_change['Price_Change_%']
colors_change = ['green' if x >= 0 else 'red' for x in changes]

ax2.barh(companies_change, changes, color=colors_change)
ax2.set_xlabel('Price Change (%)', fontsize=12, fontweight='bold')
ax2.set_title('Top 15 Best Performers (Price Change %)', fontsize=14, fontweight='bold')
ax2.axvline(x=0, color='black', linestyle='--', linewidth=0.8)
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)

# 3. Top 15 Most Traded Companies by Turnover
ax3 = axes[1, 0]
top_15_turnover = sorted_by_turnover.head(15)
companies_turnover = [str(c)[:25] for c in top_15_turnover[company_col]]
turnovers = top_15_turnover[turnover_col] / 1_000_000  # Convert to millions

ax3.barh(companies_turnover, turnovers, color='steelblue')
ax3.set_xlabel('Turnover (Million Rs.)', fontsize=12, fontweight='bold')
ax3.set_title('Top 15 Most Actively Traded Companies', fontsize=14, fontweight='bold')
ax3.invert_yaxis()
ax3.grid(axis='x', alpha=0.3)

# 4. Volatility Distribution
ax4 = axes[1, 1]
volatilities = analysis_df['Volatility_%']
ax4.hist(volatilities, bins=30, color='coral', edgecolor='black', alpha=0.7)
ax4.axvline(volatilities.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {volatilities.mean():.2f}%')
ax4.axvline(volatilities.median(), color='green', linestyle='--', linewidth=2, label=f'Median: {volatilities.median():.2f}%')
ax4.set_xlabel('Volatility (%)', fontsize=12, fontweight='bold')
ax4.set_ylabel('Number of Companies', fontsize=12, fontweight='bold')
ax4.set_title('Volatility Distribution Across All Companies', fontsize=14, fontweight='bold')
ax4.legend()
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(r'C:\Users\USER\OneDrive\Documents\GitHub\Research-Project\backend\lstm_stock_prediction\company_performance_analysis.png', dpi=300, bbox_inches='tight')
print(f"\n📊 Visualization saved to: company_performance_analysis.png")
plt.show()
