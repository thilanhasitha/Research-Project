"""
Demo script to showcase DCF valuation and PDF analysis capabilities.

This script demonstrates:
1. Manual DCF calculation with sample data
2. Free Cash Flow forecasting
3. Sensitivity analysis
4. Complete valuation workflow

Run this script to see the backend functionality in action.
"""
import asyncio
from app.services.dcf_service import DCFCalculator
from app.services.pdf_analysis_service import PDFAnalysisService


def demo_dcf_calculation():
    """Demonstrate DCF calculation with sample data."""
    print("\n" + "="*80)
    print("1. DCF CALCULATION DEMO")
    print("="*80 + "\n")
    
    # Sample historical data for a company
    company_name = "Dialog Axiata PLC"
    years = [2020, 2021, 2022, 2023, 2024]
    operating_cash_flow = [25000000000, 28000000000, 31000000000, 35000000000, 39000000000]  # LKR
    capital_expenditure = [8000000000, 8500000000, 9000000000, 9500000000, 10000000000]  # LKR
    shares_outstanding = 1000000000  # 1 billion shares
    cash = 15000000000  # LKR 15B
    debt = 50000000000  # LKR 50B
    
    print(f"Company: {company_name}")
    print(f"Analysis Period: {years[0]} - {years[-1]}")
    print(f"Shares Outstanding: {shares_outstanding:,}")
    print(f"\nHistorical Financial Data (in LKR millions):")
    print("-" * 80)
    print(f"{'Year':<10}{'Revenue':<20}{'Op. Cash Flow':<20}{'CapEx':<20}")
    print("-" * 80)
    
    for i, year in enumerate(years):
        print(f"{year:<10}{(operating_cash_flow[i]/1000000):>18,.0f}{(operating_cash_flow[i]/1000000):>18,.0f}{(capital_expenditure[i]/1000000):>18,.0f}")
    
    # Initialize DCF Calculator
    calculator = DCFCalculator(
        discount_rate=0.10,  # 10% WACC
        terminal_growth_rate=0.03,  # 3% perpetual growth
        forecast_years=5
    )
    
    # Step 1: Calculate Free Cash Flow
    print("\n" + "-"*80)
    print("Step 1: Calculate Historical Free Cash Flow")
    print("-"*80)
    historical_fcf = calculator.calculate_free_cash_flow(
        operating_cash_flow=operating_cash_flow,
        capital_expenditure=capital_expenditure
    )
    
    print(f"\n{'Year':<10}{'Free Cash Flow (LKR M)':<30}")
    print("-" * 40)
    for year, fcf in zip(years, historical_fcf):
        print(f"{year:<10}{(fcf/1000000):>28,.0f}")
    
    # Step 2: Forecast Future FCF
    print("\n" + "-"*80)
    print("Step 2: Forecast Future Free Cash Flow")
    print("-"*80)
    forecast_result = calculator.forecast_fcf(historical_fcf)
    
    print(f"\nHistorical Growth Rates: {[f'{rate:.1%}' for rate in forecast_result['historical_growth_rates']]}")
    print(f"Average Growth Rate: {forecast_result['average_growth_rate']:.2%}")
    print(f"\nForecasted FCF (Conservative Method) - LKR Millions:")
    print("-" * 40)
    
    forecasted_fcf = forecast_result['forecasted_fcf_conservative']
    for year, fcf in enumerate(forecasted_fcf, start=1):
        print(f"Year {year:<5}{(fcf/1000000):>28,.0f}")
    
    # Step 3: Calculate Intrinsic Value
    print("\n" + "-"*80)
    print("Step 3: Calculate Intrinsic Value (DCF Method)")
    print("-"*80)
    
    valuation = calculator.calculate_intrinsic_value(
        forecasted_fcf=forecasted_fcf,
        shares_outstanding=shares_outstanding,
        cash=cash,
        debt=debt
    )
    
    print(f"\nPresent Value of Forecasted FCF: LKR {(valuation['present_value_fcf']/1000000):,.0f}M")
    print(f"Terminal Value: LKR {(valuation['terminal_value']/1000000):,.0f}M")
    print(f"PV of Terminal Value: LKR {(valuation['pv_terminal_value']/1000000):,.0f}M")
    print(f"\nEnterprise Value: LKR {(valuation['enterprise_value']/1000000):,.0f}M")
    print(f"Plus: Cash: LKR {(cash/1000000):,.0f}M")
    print(f"Less: Debt: LKR {(debt/1000000):,.0f}M")
    print(f"Equity Value: LKR {(valuation['equity_value']/1000000):,.0f}M")
    print(f"\nShares Outstanding: {shares_outstanding:,}")
    print(f"\n{'='*80}")
    print(f"INTRINSIC VALUE PER SHARE: LKR {valuation['intrinsic_value_per_share']:.2f}")
    print(f"{'='*80}")
    
    return valuation


def demo_sensitivity_analysis():
    """Demonstrate sensitivity analysis."""
    print("\n" + "="*80)
    print("2. SENSITIVITY ANALYSIS")
    print("="*80 + "\n")
    
    # Use forecasted FCF from previous calculation
    forecasted_fcf = [32000000000, 34560000000, 37324800000, 40310784000, 43535646720]
    shares_outstanding = 1000000000
    
    calculator = DCFCalculator()
    
    sensitivity = calculator.sensitivity_analysis(
        forecasted_fcf=forecasted_fcf,
        shares_outstanding=shares_outstanding,
        discount_rates=[0.08, 0.09, 0.10, 0.11, 0.12],
        terminal_growth_rates=[0.02, 0.025, 0.03, 0.035, 0.04]
    )
    
    print("Intrinsic Value Per Share - Sensitivity Matrix")
    print("(Rows: Discount Rate, Columns: Terminal Growth Rate)\n")
    
    # Create matrix display
    tgr_values = sensitivity['terminal_growth_rates']
    dr_values = sensitivity['discount_rates']
    
    print(f"{'DR / TGR':<12}", end="")
    for tgr in tgr_values:
        print(f"{tgr:>10.1%}", end="")
    print("\n" + "-"*72)
    
    for dr in dr_values:
        print(f"{dr:<12.1%}", end="")
        for tgr in tgr_values:
            # Find matching result
            result = next(
                (r for r in sensitivity['sensitivity_matrix'] 
                 if r['discount_rate'] == dr and r['terminal_growth_rate'] == tgr),
                None
            )
            if result:
                print(f"LKR {result['intrinsic_value_per_share']:>6.2f}", end="")
            else:
                print(f"{'N/A':>10}", end="")
        print()
    
    print("\n" + "="*80)


def demo_forecast_methods():
    """Demonstrate different forecasting methods."""
    print("\n" + "="*80)
    print("3. FCF FORECASTING METHODS COMPARISON")
    print("="*80 + "\n")
    
    historical_fcf = [17000000000, 19500000000, 22000000000, 25500000000, 29000000000]
    years = [2020, 2021, 2022, 2023, 2024]
    
    print("Historical Free Cash Flow (LKR Millions):")
    for year, fcf in zip(years, historical_fcf):
        print(f"  {year}: {(fcf/1000000):>10,.0f}")
    
    calculator = DCFCalculator(forecast_years=5)
    forecast = calculator.forecast_fcf(historical_fcf)
    
    print(f"\nAverage Growth Rate: {forecast['average_growth_rate']:.2%}")
    print(f"Median Growth Rate: {forecast['median_growth_rate']:.2%}")
    
    print("\n" + "-"*80)
    print(f"{'Year':<10}{'Avg Growth':<20}{'Linear Trend':<20}{'Conservative':<20}")
    print("-"*80)
    
    for i in range(5):
        year = 2025 + i
        avg = forecast['forecasted_fcf_avg_growth'][i] / 1000000
        linear = forecast['forecasted_fcf_linear'][i] / 1000000
        cons = forecast['forecasted_fcf_conservative'][i] / 1000000
        print(f"{year:<10}{avg:>18,.0f}{linear:>18,.0f}{cons:>18,.0f}")
    
    print("\n" + "="*80)


async def demo_pdf_extraction():
    """Demonstrate PDF extraction (mock example without actual PDF)."""
    print("\n" + "="*80)
    print("4. PDF EXTRACTION WORKFLOW (Conceptual)")
    print("="*80 + "\n")
    
    print("Process Flow:")
    print("1. User uploads financial report PDF")
    print("2. PDF content is sent to Gemini API with structured prompt")
    print("3. Gemini extracts:")
    print("   - Company name and report year")
    print("   - Historical revenue data")
    print("   - Operating cash flow by year")
    print("   - Capital expenditure by year")
    print("   - Additional metrics (shares, cash, debt)")
    print("4. System calculates Free Cash Flow")
    print("5. System forecasts future FCF")
    print("6. DCF valuation is performed")
    print("7. Complete analysis returned to user")
    
    print("\nGemini Prompt Example:")
    print("-" * 80)
    print("""
    Analyze this financial report PDF and extract the following information in JSON format:
    {
        "company_name": "Company name",
        "report_year": 2024,
        "currency": "LKR",
        "financial_data": {
            "years": [2021, 2022, 2023, 2024, 2025],
            "revenue": [numbers for each year],
            "operating_cash_flow": [numbers for each year],
            "capital_expenditure": [numbers for each year]
        },
        "additional_metrics": {
            "shares_outstanding": number,
            "cash_and_equivalents": number,
            "total_debt": number
        }
    }
    """)
    print("-" * 80)
    
    print("\nNote: To test PDF extraction, use the API endpoint:")
    print("  POST /api/v1/valuation/analyze-pdf")
    print("  - Upload a financial report PDF")
    print("  - Set VE_GEMINI_API_KEY environment variable")
    
    print("\n" + "="*80)


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "     DCF VALUATION & PDF ANALYSIS - BACKEND DEMO".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Run demos
    valuation = demo_dcf_calculation()
    demo_sensitivity_analysis()
    demo_forecast_methods()
    asyncio.run(demo_pdf_extraction())
    
    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)
    print("\nAvailable API Endpoints:")
    print("  POST /api/v1/valuation/analyze-pdf - Full PDF analysis with DCF")
    print("  POST /api/v1/valuation/extract-pdf - Extract data from PDF only")
    print("  POST /api/v1/valuation/calculate - Calculate valuation from data")
    print("  POST /api/v1/valuation/forecast-fcf - Forecast future FCF")
    print("  POST /api/v1/valuation/sensitivity-analysis - Sensitivity analysis")
    print("  GET  /api/v1/valuation/example-data - Get sample data for testing")
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("\n")


if __name__ == "__main__":
    main()
