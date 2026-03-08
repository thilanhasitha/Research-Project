# Plot Visualization Service - Integration Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                             │
│  "Show me the stock price chart"                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FRONTEND (React/Vite)                          │
│  Port: 3001 (dev) / 80 (docker)                                 │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  AIChat.jsx                                              │    │
│  │  • Detects plot keywords                                │    │
│  │  • Calls plotService.searchPlots()                      │    │
│  │  • Fetches plots in parallel with RAG response          │    │
│  └────────────────┬────────────────────────────────────────┘    │
│                   │                                              │
│  ┌────────────────▼────────────────────────────────────────┐    │
│  │  plotService.js                                          │    │
│  │  • API client for plot endpoints                        │    │
│  │  • Base URL: http://localhost:8001/api                  │    │
│  └────────────────┬────────────────────────────────────────┘    │
│                   │                                              │
└───────────────────┼──────────────────────────────────────────────┘
                    │ HTTP GET /api/plots/search?query=...
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                  VITE PROXY (Development)                        │
│  Forwards /api/* → http://localhost:8001                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                              │
│  Port: 8001                                                      │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  app/main.py                                             │    │
│  │  app.include_router(plot_router, prefix="/api")        │    │
│  └────────────────┬────────────────────────────────────────┘    │
│                   │                                              │
│  ┌────────────────▼────────────────────────────────────────┐    │
│  │  app/routes/plot_routes.py                              │    │
│  │  • GET /api/plots/health                                │    │
│  │  • GET /api/plots/search                                │    │
│  │  • GET /api/plots/{id}                                  │    │
│  │  • GET /api/plots/{id}/image                            │    │
│  └────────────────┬────────────────────────────────────────┘    │
│                   │                                              │
└───────────────────┼──────────────────────────────────────────────┘
                    │ Uses PlotManager
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│           LSTM Stock Prediction Module                           │
│  backend/lstm_stock_prediction/                                  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  src/plot_manager.py                                     │    │
│  │  • save_plot() - Save plot with metadata                │    │
│  │  • search_plots() - Keyword-based search                │    │
│  │  • get_plot_by_id() - Retrieve specific plot            │    │
│  │  • get_stats() - Storage statistics                     │    │
│  └────────────────┬────────────────────────────────────────┘    │
│                   │                                              │
│                   │ Reads/Writes                                 │
│                   ▼                                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  data/plots/                                             │    │
│  │  ├── plot_index.json (metadata)                         │    │
│  │  ├── stock_price_time_series.png                        │    │
│  │  ├── trading_volume_time_series.png                     │    │
│  │  ├── ohlc_candlestick_chart.png                         │    │
│  │  ├── daily_returns_distribution.png                     │    │
│  │  ├── moving_averages_chart.png                          │    │
│  │  ├── rolling_volatility_chart.png                       │    │
│  │  └── feature_correlation_heatmap.png                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                   ▲                                              │
│                   │ Generated by                                 │
│  ┌────────────────┴────────────────────────────────────────┐    │
│  │  generate_plots.py                                       │    │
│  │  • Loads stock data from CSV                            │    │
│  │  • Creates 7 visualization plots                        │    │
│  │  • Saves with keywords and descriptions                 │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Response Flow

```
User Query → Frontend → Backend API → PlotManager → Plot Index
                 ↓           ↓             ↓            ↓
              AIChat → plot_routes → search_plots() → JSON
                 ↓           ↓             ↓            ↓
            ChatMessage ← Response ← Results ← Matching Plots
                 ↓
         Display Plots + Text
```

## Data Flow for Plot Search

1. **User asks**: "Show me the stock price chart"

2. **AIChat.jsx detects** plot keywords: ["show", "stock", "price", "chart"]

3. **plotService.js calls**:
   ```
   GET http://localhost:8001/api/plots/search?query=stock+price+chart&limit=3
   ```

4. **plot_routes.py** receives request and calls PlotManager

5. **PlotManager.search_plots()** scores each plot:
   - Title match: "Stock Price" → +10 points
   - Keywords match: ["stock", "price"] → +7 each
   - Description match: relevant terms → +5
   
6. **Returns JSON**:
   ```json
   {
     "success": true,
     "query": "stock price chart",
     "plots": [
       {
         "plot_id": "stock_price_time_series",
         "title": "Stock Closing Price Over Time",
         "description": "Historical closing price trend...",
         "image_url": "/api/plots/stock_price_time_series/image",
         "relevance_score": 95
       }
     ],
     "count": 1
   }
   ```

7. **ChatMessage.jsx renders**:
   - Text response from RAG
   - Plot images with descriptions
   - Expand buttons for fullscreen view

## File Dependencies

```
frontend/utils/plotService.js
    ↓ calls
backend/app/routes/plot_routes.py
    ↓ imports
backend/lstm_stock_prediction/src/plot_manager.py
    ↓ reads
backend/lstm_stock_prediction/data/plots/plot_index.json
    ↓ references
backend/lstm_stock_prediction/data/plots/*.png
```

## Configuration Chain

```
Frontend: VITE_API_BASE_URL (env) → http://localhost:8001/api
    ↓
Vite Proxy: /api/* → http://backend:8001
    ↓
FastAPI: plot_router @ /api/plots/*
    ↓
PlotManager: plots_dir = data/plots/
```

## Integration Points

### ✅ Backend to PlotManager
- **Location**: `app/routes/plot_routes.py` line 17-25
- **Import**: `from src.plot_manager import PlotManager`
- **Instance**: `plot_manager = PlotManager(...)`

### ✅ FastAPI to Routes
- **Location**: `app/main.py` line 97
- **Register**: `app.include_router(plot_router, prefix="/api")`

### ✅ Frontend to Backend
- **Location**: `frontend/utils/plotService.js` line 6
- **API URL**: `http://localhost:8001/api`
- **Proxy**: `frontend/vite.config.js` lines 18-21

### ✅ AIChat to PlotService
- **Location**: `frontend/src/components/chat/AIChat.jsx` line 6
- **Import**: `import plotService from '../../../utils/plotService'`
- **Usage**: Lines 113-141 (parallel fetch)

### ✅ ChatMessage Display
- **Location**: `frontend/src/components/chat/ChatMessage.jsx` lines 90-125
- **Props**: `plots={msg.plots}`
- **Features**: Collapsible, modal expansion, relevance scoring

## Summary

**Status**: ✅ **FULLY INTEGRATED**

All components are connected and ready. The only remaining step is to run `generate_plots.py` to create the actual visualization files.
