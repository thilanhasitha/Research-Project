"""
Example script showing how to use the valuation API endpoints.
Run the FastAPI server first: uvicorn app.main:app --reload
"""
import requests
import json


BASE_URL = "http://localhost:8000/api/v1"


def example_1_get_sample_data():
    """Get example financial data."""
    print("\n" + "="*60)
    print("Example 1: Get Sample Data")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/valuation/example-data")
    data = response.json()
    
    print("\nSample Company Data:")
    print(json.dumps(data, indent=2))
    
    return data


def example_2_calculate_valuation(sample_data):
    """Calculate valuation from provided data."""
    print("\n" + "="*60)
    print("Example 2: Calculate Valuation from Data")
    print("="*60)
    
    payload = {
        "financial_data": {
            "operating_cash_flow": sample_data["financial_data"]["operating_cash_flow"],
            "capital_expenditure": sample_data["financial_data"]["capital_expenditure"],
            "shares_outstanding": sample_data["additional_metrics"]["shares_outstanding"],
            "cash": sample_data["additional_metrics"]["cash_and_equivalents"],
            "debt": sample_data["additional_metrics"]["total_debt"]
        },
        "parameters": {
            "discount_rate": 0.10,
            "terminal_growth_rate": 0.03,
            "forecast_years": 5
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/valuation/calculate",
        json=payload
    )
    
    result = response.json()
    
    print("\nValuation Results:")
    print(f"  Intrinsic Value per Share: LKR {result['valuation']['intrinsic_value_per_share']:.2f}")
    print(f"  Enterprise Value: LKR {result['valuation']['enterprise_value']/1e6:.0f}M")
    print(f"  Equity Value: LKR {result['valuation']['equity_value']/1e6:.0f}M")
    print(f"  Current Market Price: LKR {sample_data['additional_metrics']['current_price']:.2f}")
    
    intrinsic = result['valuation']['intrinsic_value_per_share']
    market = sample_data['additional_metrics']['current_price']
    margin = ((intrinsic - market) / market) * 100
    
    print(f"\n  Margin of Safety: {margin:+.1f}%")
    if margin > 20:
        print("  → Stock is UNDERVALUED (Good buy)")
    elif margin < -20:
        print("  → Stock is OVERVALUED (Avoid)")
    else:
        print("  → Stock is FAIRLY VALUED")
    
    return result


def example_3_forecast_fcf():
    """Forecast Free Cash Flow."""
    print("\n" + "="*60)
    print("Example 3: Forecast Free Cash Flow")
    print("="*60)
    
    historical_fcf = [170000000, 195000000, 220000000, 255000000, 290000000]
    
    response = requests.post(
        f"{BASE_URL}/valuation/forecast-fcf",
        json=historical_fcf,
        params={"forecast_years": 5}
    )
    
    result = response.json()
    
    print("\nHistorical FCF (LKR M):", [f"{v/1e6:.0f}" for v in historical_fcf])
    print(f"Average Growth Rate: {result['average_growth_rate']:.2%}")
    print("\nForecasted FCF (Conservative Method):")
    for i, fcf in enumerate(result['forecasted_fcf_conservative'], 1):
        print(f"  Year {i}: LKR {fcf/1e6:.0f}M")
    
    return result


def example_4_sensitivity_analysis():
    """Perform sensitivity analysis."""
    print("\n" + "="*60)
    print("Example 4: Sensitivity Analysis")
    print("="*60)
    
    payload = {
        "forecasted_fcf": [313200000, 338256000, 365316480, 394241798, 425541141],
        "shares_outstanding": 100000000,
        "discount_rates": [0.08, 0.09, 0.10, 0.11, 0.12],
        "terminal_growth_rates": [0.02, 0.025, 0.03, 0.035, 0.04]
    }
    
    response = requests.post(
        f"{BASE_URL}/valuation/sensitivity-analysis",
        json=payload
    )
    
    result = response.json()
    
    print("\nIntrinsic Value Sensitivity Matrix (LKR per share):")
    print(f"{'DR / TGR':<12}", end="")
    for tgr in result['terminal_growth_rates']:
        print(f"{tgr:>10.1%}", end="")
    print("\n" + "-"*72)
    
    for dr in result['discount_rates']:
        print(f"{dr:<12.1%}", end="")
        for tgr in result['terminal_growth_rates']:
            val = next(
                (r['intrinsic_value_per_share'] for r in result['sensitivity_matrix']
                 if r['discount_rate'] == dr and r['terminal_growth_rate'] == tgr),
                None
            )
            if val:
                print(f"LKR {val:>6.2f}", end="")
        print()
    
    return result


def example_5_upload_pdf():
    """Upload and analyze PDF (requires Gemini API key)."""
    print("\n" + "="*60)
    print("Example 5: Upload PDF for Analysis")
    print("="*60)
    
    print("\nTo test PDF upload:")
    print("1. Set VE_GEMINI_API_KEY in .env file")
    print("2. Prepare a financial report PDF")
    print("3. Use this code:\n")
    
    example_code = """
    with open('annual_report.pdf', 'rb') as f:
        files = {'file': ('annual_report.pdf', f, 'application/pdf')}
        data = {
            'discount_rate': 0.10,
            'terminal_growth_rate': 0.03,
            'forecast_years': 5
        }
        response = requests.post(
            f"{BASE_URL}/valuation/analyze-pdf",
            files=files,
            data=data
        )
        result = response.json()
        print(f"Intrinsic Value: {result['valuation']['intrinsic_value_per_share']}")
    """
    
    print(example_code)
    print("\nNote: This requires a valid Gemini API key.")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  VALUATION API - USAGE EXAMPLES".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/../health")
        if response.status_code != 200:
            print("\n⚠ Warning: API server may not be running")
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to API server")
        print("Please start the server first:")
        print("  uvicorn app.main:app --reload")
        print("\n")
        return
    
    try:
        # Run examples
        sample_data = example_1_get_sample_data()
        valuation = example_2_calculate_valuation(sample_data)
        forecast = example_3_forecast_fcf()
        sensitivity = example_4_sensitivity_analysis()
        example_5_upload_pdf()
        
        print("\n" + "="*60)
        print("All examples completed successfully! ✓")
        print("="*60)
        print("\nAPI Documentation: http://localhost:8000/docs")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
