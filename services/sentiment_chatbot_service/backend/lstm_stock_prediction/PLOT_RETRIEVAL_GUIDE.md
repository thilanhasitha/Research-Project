# Plot Retrieval System for RAG Chatbot

This system allows you to store visualization plots with metadata and retrieve them based on user queries.

## 🎯 Features

- **Save plots with metadata**: Store matplotlib plots with descriptions, keywords, and categories
- **Smart search**: Find relevant plots based on user queries
- **FastAPI integration**: REST API for serving plots
- **Category organization**: Organize plots by type (price trends, volume, statistical, etc.)
- **Relevance scoring**: Automatic ranking of plot relevance to queries

## 📁 Files Created

1. **`src/plot_manager.py`**: Core plot management system
2. **`notebooks/01b_save_plots_for_rag.ipynb`**: Notebook to save all plots
3. **`plot_retrieval_example.py`**: Usage examples and integration guide
4. **`api_plot_server.py`**: FastAPI server for plot retrieval

## 🚀 Quick Start

### Step 1: Run the notebook to save plots

```bash
# Open and run the notebook
01b_save_plots_for_rag.ipynb
```

This will:
- Load your stock data
- Generate all visualizations
- Save them with metadata to `data/plots/`
- Create a searchable index at `data/plots/plot_index.json`

### Step 2: Test plot retrieval

```bash
python plot_retrieval_example.py
```

### Step 3: Start the API server

```bash
python api_plot_server.py
```

Visit `http://localhost:8005/docs` for interactive API documentation.

## 🔍 Usage Examples

### Python API

```python
from src.plot_manager import PlotManager

# Initialize
pm = PlotManager()

# Search for plots
results = pm.search_plots("stock price change over time", limit=3)

for plot in results:
    print(f"{plot['title']}: {plot['filepath']}")
```

### REST API

```bash
# Search for plots
curl "http://localhost:8005/api/plots/search?query=stock%20price&limit=3"

# Get specific plot
curl "http://localhost:8005/api/plots/stock_closing_price_timeline"

# Get plot image
curl "http://localhost:8005/api/plots/stock_closing_price_timeline/image"

# Get all categories
curl "http://localhost:8005/api/plots/categories"
```

## 📊 Available Plot Categories

- **price_trends**: Stock price over time, OHLC charts
- **volume**: Trading volume analysis
- **statistical**: Distribution, correlation heatmaps
- **returns**: Daily returns, price changes
- **technical_analysis**: Moving averages, indicators
- **risk_analysis**: Volatility, risk metrics

## 🔗 Integration with Your RAG System

Add this to your existing chatbot:

```python
from src.plot_manager import PlotManager

# In your chatbot initialization
plot_manager = PlotManager()

# In your query handler
def handle_user_query(user_query: str):
    # Get text response from RAG
    rag_response = your_rag_system.query(user_query)
    
    # Get relevant plots
    plots = plot_manager.search_plots(user_query, limit=3)
    
    # Return combined response
    return {
        "text": rag_response,
        "plots": plots,
        "has_visuals": len(plots) > 0
    }
```

## 📋 Example Queries That Work

- "How has the stock price changed over the past 20 years?"
- "Show me the trading volume patterns"
- "What is the price volatility?"
- "Can you show me the price distribution?"
- "How do the moving averages look?"
- "What are the daily returns?"
- "Show me correlation between features"

## 🎨 Frontend Integration

### React Example

```jsx
function ChatMessage({ message }) {
  return (
    <div>
      <p>{message.text}</p>
      {message.has_visuals && (
        <div className="plots">
          {message.plots.map(plot => (
            <div key={plot.plot_id}>
              <img 
                src={`/api/plots/${plot.plot_id}/image`} 
                alt={plot.title}
              />
              <p>{plot.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

## 📈 Plot Metadata Structure

Each plot is stored with:

```json
{
  "plot_id": "stock_closing_price_timeline",
  "filename": "stock_closing_price_timeline.png",
  "filepath": "data/plots/stock_closing_price_timeline.png",
  "title": "Stock Closing Price Over Time",
  "description": "Historical stock closing prices from 2000 to 2021...",
  "keywords": ["stock price", "closing price", "price trend", ...],
  "category": "price_trends",
  "created_at": "2026-03-05 10:30:00",
  "file_size_kb": 245.67
}
```

## 🛠️ Customization

### Add New Plot

```python
import matplotlib.pyplot as plt
from src.plot_manager import PlotManager

pm = PlotManager()

# Create your plot
fig, ax = plt.subplots()
ax.plot(data)

# Save with metadata
pm.save_plot(
    plot_id="my_custom_plot",
    title="My Custom Analysis",
    description="Detailed description of what this shows",
    keywords=["keyword1", "keyword2", "keyword3"],
    category="my_category",
    fig=fig
)
```

### Search by Category

```python
# Get all price trend plots
price_plots = pm.get_all_plots(category="price_trends")

# Search within a category
results = pm.search_plots("volatility", category="risk_analysis")
```

## 📊 Statistics

```python
stats = pm.get_stats()
print(f"Total plots: {stats['total_plots']}")
print(f"Categories: {stats['categories']}")
print(f"Storage: {stats['total_size_mb']} MB")
```

## 🔄 Update Existing Plots

To update plots with new data:

1. Run the `01b_save_plots_for_rag.ipynb` notebook again
2. Plots with the same `plot_id` will be replaced
3. The index is automatically updated

## 🗑️ Delete a Plot

```python
pm.delete_plot("plot_id_to_delete")
```

## 💡 Best Practices

1. **Use descriptive plot_ids**: `stock_price_2020_2025` not `plot1`
2. **Add comprehensive keywords**: Include variations users might search
3. **Write detailed descriptions**: Explain what insights the plot provides
4. **Categorize appropriately**: Use consistent category names
5. **Update regularly**: Re-run when you have new data

## 🚨 Troubleshooting

**Plots not found in search:**
- Check if the notebook ran successfully
- Verify `data/plots/plot_index.json` exists
- Try broader search terms

**Images not loading:**
- Ensure the API server is running
- Check file permissions on `data/plots/` directory
- Verify file paths in the index

**Low relevance scores:**
- Add more keywords to plot metadata
- Make descriptions more detailed
- Use category filters

## 📚 Next Steps

1. ✅ Run `01b_save_plots_for_rag.ipynb` to generate plots
2. ✅ Test with `plot_retrieval_example.py`
3. ✅ Start API server with `api_plot_server.py`
4. ✅ Integrate with your RAG chatbot
5. ✅ Update frontend to display images
6. ✅ Add to your existing service architecture

---

**Ready to enhance your RAG system with visual intelligence!** 🎉
