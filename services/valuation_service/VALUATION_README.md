# Intrinsic Value Calculator - Backend Implementation

## Overview

This backend implementation demonstrates the complete workflow for calculating intrinsic stock value using the Discounted Cash Flow (DCF) method, including:

1. **PDF Data Extraction** using Gemini AI API
2. **Free Cash Flow Forecasting** using multiple methods
3. **DCF Valuation** with terminal value calculation
4. **Sensitivity Analysis** for different parameters

## Features

### 1. PDF Financial Data Extraction

Extract financial data from annual reports using Google Gemini AI:

```python
from app.services.pdf_analysis_service import PDFAnalysisService

service = PDFAnalysisService()
result = await service.extract_only(pdf_content, filename)
```

**Extracted Data:**
- Company name and report year
- Historical revenue
- Operating cash flow (OCF)
- Capital expenditure (CAPEX)
- Shares outstanding, cash, debt

### 2. Free Cash Flow Calculation & Forecasting

Calculate historical and forecast future Free Cash Flow:

```python
from app.services.dcf_service import DCFCalculator

calculator = DCFCalculator(
    discount_rate=0.10,
    terminal_growth_rate=0.03,
    forecast_years=5
)

# Calculate historical FCF
historical_fcf = calculator.calculate_free_cash_flow(ocf_list, capex_list)

# Forecast future FCF
forecast = calculator.forecast_fcf(historical_fcf)
```

**Forecasting Methods:**
- Average historical growth rate
- Linear trend extrapolation
- Conservative estimate (minimum of both)

### 3. DCF Valuation

Calculate intrinsic value using the DCF method:

```python
valuation = calculator.calculate_intrinsic_value(
    forecasted_fcf=forecasted_fcf,
    shares_outstanding=100000000,
    cash=150000000,
    debt=500000000
)

intrinsic_value_per_share = valuation['intrinsic_value_per_share']
```

**Formula:**
```
Free Cash Flow = Operating Cash Flow - Capital Expenditure

Present Value = Σ (FCF_t / (1 + r)^t)

Terminal Value = FCF_final × (1 + g) / (r - g)

Enterprise Value = PV(Forecasted FCF) + PV(Terminal Value)

Equity Value = Enterprise Value + Cash - Debt

Intrinsic Value per Share = Equity Value / Shares Outstanding
```

Where:
- `r` = Discount rate (WACC)
- `g` = Terminal growth rate
- `t` = Year

### 4. Sensitivity Analysis

Test different scenarios by varying discount rates and terminal growth rates.

## API Endpoints

### Complete PDF Analysis
```bash
POST /api/v1/valuation/analyze-pdf
Content-Type: multipart/form-data

Parameters:
- file: PDF file
- discount_rate: 0.10 (default)
- terminal_growth_rate: 0.03 (default)
- forecast_years: 5 (default)
```

**Response:**
```json
{
  "status": "success",
  "filename": "annual_report_2024.pdf",
  "company_name": "Dialog Axiata PLC",
  "extraction": {
    "historical_years": [2020, 2021, 2022, 2023, 2024],
    "operating_cash_flow": [...],
    "capital_expenditure": [...],
    "historical_fcf": [...]
  },
  "forecast": {
    "forecasted_fcf": [...],
    "average_growth_rate": 0.08
  },
  "valuation": {
    "intrinsic_value_per_share": 52.45,
    "enterprise_value": 5245000000,
    "present_value_fcf": 3500000000,
    "pv_terminal_value": 1745000000
  }
}
```

### Extract Data Only
```bash
POST /api/v1/valuation/extract-pdf
Content-Type: multipart/form-data

Parameters:
- file: PDF file
```

### Calculate Valuation from Data
```bash
POST /api/v1/valuation/calculate
Content-Type: application/json

Body:
{
  "financial_data": {
    "operating_cash_flow": [250000000, 280000000, 310000000],
    "capital_expenditure": [80000000, 85000000, 90000000],
    "shares_outstanding": 100000000,
    "cash": 150000000,
    "debt": 500000000
  },
  "parameters": {
    "discount_rate": 0.10,
    "terminal_growth_rate": 0.03,
    "forecast_years": 5
  }
}
```

### Forecast FCF
```bash
POST /api/v1/valuation/forecast-fcf?forecast_years=5
Content-Type: application/json

Body: [170000000, 195000000, 220000000, 255000000, 290000000]
```

### Sensitivity Analysis
```bash
POST /api/v1/valuation/sensitivity-analysis
Content-Type: application/json

Body:
{
  "forecasted_fcf": [300000000, 324000000, 349920000, 377913600, 408106688],
  "shares_outstanding": 100000000,
  "discount_rates": [0.08, 0.09, 0.10, 0.11, 0.12],
  "terminal_growth_rates": [0.02, 0.025, 0.03, 0.035, 0.04]
}
```

### Get Example Data
```bash
GET /api/v1/valuation/example-data
```

## Setup & Configuration

### 1. Install Dependencies
```bash
cd valuation-engine
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file:
```env
# Gemini API (required for PDF extraction)
VE_GEMINI_API_KEY=your_gemini_api_key_here

# Database (optional for this feature)
VE_POSTGRES_HOST=localhost
VE_POSTGRES_PORT=5432
VE_POSTGRES_USER=postgres
VE_POSTGRES_PASSWORD=postgres
VE_POSTGRES_DB=valuation_engine
```

Get Gemini API key from: https://makersuite.google.com/app/apikey

### 3. Run the Server
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Run the Demo
```bash
python demo_valuation.py
```

## Demo Output

The demo script demonstrates:

1. **DCF Calculation** with sample data
   - Historical FCF calculation
   - Forecasting with multiple methods
   - Intrinsic value calculation

2. **Sensitivity Analysis**
   - Matrix of values for different parameters

3. **Forecast Comparison**
   - Side-by-side comparison of forecasting methods

4. **PDF Extraction Workflow**
   - Conceptual overview of the process

```bash
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║          DCF VALUATION & PDF ANALYSIS - BACKEND DEMO                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

1. DCF CALCULATION DEMO
════════════════════════════════════════════════════════════════════════════════

Company: Dialog Axiata PLC
Analysis Period: 2020 - 2024
...

════════════════════════════════════════════════════════════════════════════════
INTRINSIC VALUE PER SHARE: LKR 42.35
════════════════════════════════════════════════════════════════════════════════
```

## Code Structure

```
valuation-engine/
├── app/
│   ├── clients/
│   │   ├── gemini_client.py          # Gemini API integration
│   │   └── cse_client.py              # CSE data fetching
│   ├── services/
│   │   ├── dcf_service.py             # DCF calculations
│   │   ├── pdf_analysis_service.py    # PDF analysis workflow
│   │   └── cse_service.py             # CSE data service
│   ├── schemas/
│   │   └── valuation.py               # Pydantic schemas
│   └── api/
│       └── routes/
│           └── valuation.py           # API endpoints
├── demo_valuation.py                  # Demo script
└── requirements.txt
```

## Key Classes

### DCFCalculator
Methods:
- `calculate_free_cash_flow()` - Calculate FCF from OCF and CAPEX
- `forecast_fcf()` - Forecast future FCF
- `calculate_present_value()` - Discount future cash flows
- `calculate_terminal_value()` - Gordon Growth Model
- `calculate_intrinsic_value()` - Complete DCF valuation
- `sensitivity_analysis()` - Parameter sensitivity

### GeminiClient
Methods:
- `extract_financial_data()` - Extract structured data from PDF
- `analyze_with_context()` - Custom PDF analysis

### PDFAnalysisService
Methods:
- `analyze_financial_report()` - Complete pipeline (extract + value)
- `extract_only()` - Data extraction only
- `calculate_valuation_only()` - Valuation from provided data

## Testing the API

### Using cURL

**Analyze PDF:**
```bash
curl -X POST "http://localhost:8000/api/v1/valuation/analyze-pdf" \
  -F "file=@annual_report.pdf" \
  -F "discount_rate=0.10" \
  -F "terminal_growth_rate=0.03"
```

**Calculate from Data:**
```bash
curl -X POST "http://localhost:8000/api/v1/valuation/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "financial_data": {
      "operating_cash_flow": [250000000, 280000000, 310000000, 350000000, 390000000],
      "capital_expenditure": [80000000, 85000000, 90000000, 95000000, 100000000],
      "shares_outstanding": 100000000,
      "cash": 150000000,
      "debt": 500000000
    },
    "parameters": {
      "discount_rate": 0.10,
      "terminal_growth_rate": 0.03,
      "forecast_years": 5
    }
  }'
```

### Using Python Requests

```python
import requests

# Example data
url = "http://localhost:8000/api/v1/valuation/calculate"
data = {
    "financial_data": {
        "operating_cash_flow": [250000000, 280000000, 310000000, 350000000, 390000000],
        "capital_expenditure": [80000000, 85000000, 90000000, 95000000, 100000000],
        "shares_outstanding": 100000000,
        "cash": 150000000,
        "debt": 500000000
    }
}

response = requests.post(url, json=data)
result = response.json()
print(f"Intrinsic Value: LKR {result['valuation']['intrinsic_value_per_share']:.2f}")
```

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Notes

- **Gemini API** is required only for PDF extraction. Other endpoints work without it.
- **DCF calculations** are performed locally using numpy.
- **Forecasting** uses both statistical and conservative approaches.
- **Sensitivity analysis** helps understand valuation ranges.

## Example Use Case

A financial analyst wants to value Dialog Axiata PLC:

1. Upload annual report PDF via `/analyze-pdf`
2. Gemini extracts 5 years of financial data
3. System calculates historical FCF
4. System forecasts next 5 years of FCF
5. DCF formula calculates intrinsic value: **LKR 42.35/share**
6. Sensitivity analysis shows range: **LKR 38-48** depending on assumptions
7. Current market price: **LKR 45.50**
8. **Analysis:** Stock is fairly valued to slightly overvalued

## License

See LICENSE file in the project root.
