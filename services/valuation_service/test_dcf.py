"""
Test script for DCF valuation - No external dependencies required.
This script demonstrates the DCF calculation logic with sample data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.dcf_service import DCFCalculator


def test_basic_fcf_calculation():
    """Test basic Free Cash Flow calculation."""
    print("\n" + "="*60)
    print("TEST 1: Free Cash Flow Calculation")
    print("="*60)
    
    calculator = DCFCalculator()
    
    ocf = [100000000, 120000000, 140000000, 160000000, 180000000]
    capex = [30000000, 35000000, 40000000, 45000000, 50000000]
    
    fcf = calculator.calculate_free_cash_flow(ocf, capex)
    
    print("\nOperating Cash Flow:", [f"{v/1e6:.0f}M" for v in ocf])
    print("Capital Expenditure:", [f"{v/1e6:.0f}M" for v in capex])
    print("Free Cash Flow:     ", [f"{v/1e6:.0f}M" for v in fcf])
    
    expected_fcf = [70000000, 85000000, 100000000, 115000000, 130000000]
    assert fcf == expected_fcf, "FCF calculation failed!"
    print("\n✓ Test passed!")
    

def test_fcf_forecasting():
    """Test FCF forecasting methods."""
    print("\n" + "="*60)
    print("TEST 2: FCF Forecasting")
    print("="*60)
    
    calculator = DCFCalculator(forecast_years=5)
    
    historical_fcf = [70000000, 85000000, 100000000, 115000000, 130000000]
    
    forecast = calculator.forecast_fcf(historical_fcf)
    
    print("\nHistorical FCF:", [f"{v/1e6:.0f}M" for v in historical_fcf])
    print(f"Growth Rate: {forecast['average_growth_rate']:.2%}")
    print("\nForecasted (Avg Growth):", [f"{v/1e6:.0f}M" for v in forecast['forecasted_fcf_avg_growth']])
    print("Forecasted (Linear):    ", [f"{v/1e6:.0f}M" for v in forecast['forecasted_fcf_linear']])
    print("Forecasted (Conservative):", [f"{v/1e6:.0f}M" for v in forecast['forecasted_fcf_conservative']])
    
    assert len(forecast['forecasted_fcf_conservative']) == 5, "Forecast length incorrect!"
    print("\n✓ Test passed!")


def test_present_value_calculation():
    """Test present value calculation."""
    print("\n" + "="*60)
    print("TEST 3: Present Value Calculation")
    print("="*60)
    
    calculator = DCFCalculator(discount_rate=0.10)
    
    future_fcf = [140400000, 151632000, 163762560, 176863564, 190852729]
    
    pv_data = calculator.calculate_present_value(future_fcf)
    
    print("\nFuture FCF:", [f"{v/1e6:.0f}M" for v in future_fcf])
    print("Discount Rate: 10%")
    print("\nPresent Values:", [f"{v/1e6:.0f}M" for v in pv_data['present_values']])
    print(f"\nTotal PV: {pv_data['total_pv']/1e6:.0f}M")
    
    assert pv_data['total_pv'] > 0, "PV calculation failed!"
    print("\n✓ Test passed!")


def test_terminal_value():
    """Test terminal value calculation."""
    print("\n" + "="*60)
    print("TEST 4: Terminal Value Calculation")
    print("="*60)
    
    calculator = DCFCalculator(
        discount_rate=0.10,
        terminal_growth_rate=0.03,
        forecast_years=5
    )
    
    final_fcf = 190852729
    
    terminal = calculator.calculate_terminal_value(final_fcf)
    
    print(f"\nFinal FCF: {final_fcf/1e6:.0f}M")
    print(f"Terminal Growth: {calculator.terminal_growth_rate:.1%}")
    print(f"Discount Rate: {calculator.discount_rate:.1%}")
    print(f"\nTerminal Value: {terminal['terminal_value']/1e6:.0f}M")
    print(f"PV of Terminal: {terminal['pv_terminal_value']/1e6:.0f}M")
    
    assert terminal['pv_terminal_value'] > 0, "Terminal value calculation failed!"
    print("\n✓ Test passed!")


def test_intrinsic_value():
    """Test complete intrinsic value calculation."""
    print("\n" + "="*60)
    print("TEST 5: Intrinsic Value Calculation (Complete DCF)")
    print("="*60)
    
    calculator = DCFCalculator(
        discount_rate=0.10,
        terminal_growth_rate=0.03,
        forecast_years=5
    )
    
    forecasted_fcf = [140400000, 151632000, 163762560, 176863564, 190852729]
    shares = 50000000  # 50M shares
    cash = 100000000   # 100M cash
    debt = 300000000   # 300M debt
    
    valuation = calculator.calculate_intrinsic_value(
        forecasted_fcf=forecasted_fcf,
        shares_outstanding=shares,
        cash=cash,
        debt=debt
    )
    
    print(f"\nForecasted FCF: {[f'{v/1e6:.0f}M' for v in forecasted_fcf]}")
    print(f"\nPV of Forecasted FCF: {valuation['present_value_fcf']/1e6:.0f}M")
    print(f"PV of Terminal Value: {valuation['pv_terminal_value']/1e6:.0f}M")
    print(f"Enterprise Value: {valuation['enterprise_value']/1e6:.0f}M")
    print(f"\nPlus: Cash: {cash/1e6:.0f}M")
    print(f"Less: Debt: {debt/1e6:.0f}M")
    print(f"Equity Value: {valuation['equity_value']/1e6:.0f}M")
    print(f"\nShares Outstanding: {shares/1e6:.0f}M")
    print(f"\n{'='*60}")
    print(f"INTRINSIC VALUE PER SHARE: ${valuation['intrinsic_value_per_share']:.2f}")
    print(f"{'='*60}")
    
    assert valuation['intrinsic_value_per_share'] > 0, "Intrinsic value calculation failed!"
    print("\n✓ Test passed!")


def test_sensitivity_analysis():
    """Test sensitivity analysis."""
    print("\n" + "="*60)
    print("TEST 6: Sensitivity Analysis")
    print("="*60)
    
    calculator = DCFCalculator()
    
    forecasted_fcf = [140400000, 151632000, 163762560, 176863564, 190852729]
    shares = 50000000
    
    sensitivity = calculator.sensitivity_analysis(
        forecasted_fcf=forecasted_fcf,
        shares_outstanding=shares,
        discount_rates=[0.08, 0.10, 0.12],
        terminal_growth_rates=[0.02, 0.03, 0.04]
    )
    
    print("\nIntrinsic Value Sensitivity Matrix:")
    print(f"{'DR / TGR':<12}", end="")
    for tgr in sensitivity['terminal_growth_rates']:
        print(f"{tgr:>10.1%}", end="")
    print("\n" + "-"*42)
    
    for dr in sensitivity['discount_rates']:
        print(f"{dr:<12.1%}", end="")
        for tgr in sensitivity['terminal_growth_rates']:
            result = next(
                (r for r in sensitivity['sensitivity_matrix'] 
                 if r['discount_rate'] == dr and r['terminal_growth_rate'] == tgr),
                None
            )
            if result:
                print(f"${result['intrinsic_value_per_share']:>9.2f}", end="")
        print()
    
    assert len(sensitivity['sensitivity_matrix']) > 0, "Sensitivity analysis failed!"
    print("\n✓ Test passed!")


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  DCF VALUATION - UNIT TESTS".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_basic_fcf_calculation()
        test_fcf_forecasting()
        test_present_value_calculation()
        test_terminal_value()
        test_intrinsic_value()
        test_sensitivity_analysis()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✓")
        print("="*60)
        print("\nThe DCF calculation engine is working correctly.")
        print("You can now use the API endpoints or run the demo script.")
        print("\n")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
