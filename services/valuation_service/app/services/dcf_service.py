"""
DCF (Discounted Cash Flow) calculation service for intrinsic value calculation.
"""
from typing import List, Dict, Any
import numpy as np


class DCFCalculator:
    """Handles DCF valuation calculations."""
    
    def __init__(
        self,
        discount_rate: float = 0.10,
        terminal_growth_rate: float = 0.03,
        forecast_years: int = 5
    ):
        """
        Initialize DCF calculator.
        
        Args:
            discount_rate: Weighted Average Cost of Capital (WACC) or required return
            terminal_growth_rate: Perpetual growth rate for terminal value
            forecast_years: Number of years to forecast
        """
        self.discount_rate = discount_rate
        self.terminal_growth_rate = terminal_growth_rate
        self.forecast_years = forecast_years
        
    def calculate_free_cash_flow(
        self,
        operating_cash_flow: List[float],
        capital_expenditure: List[float]
    ) -> List[float]:
        """
        Calculate Free Cash Flow.
        
        FCF = Operating Cash Flow - Capital Expenditure
        
        Args:
            operating_cash_flow: List of OCF values
            capital_expenditure: List of CAPEX values
            
        Returns:
            List of FCF values
        """
        if len(operating_cash_flow) != len(capital_expenditure):
            raise ValueError("OCF and CAPEX lists must have the same length")
            
        return [ocf - capex for ocf, capex in zip(operating_cash_flow, capital_expenditure)]
    
    def forecast_fcf(self, historical_fcf: List[float]) -> Dict[str, Any]:
        """
        Forecast future Free Cash Flows using multiple methods.
        
        Args:
            historical_fcf: Historical FCF data
            
        Returns:
            Dictionary with forecasted FCF and growth rates
        """
        if len(historical_fcf) < 2:
            raise ValueError("At least 2 years of historical data required for forecasting")
        
        # Calculate historical growth rate
        growth_rates = []
        for i in range(1, len(historical_fcf)):
            if historical_fcf[i-1] != 0:
                growth_rate = (historical_fcf[i] - historical_fcf[i-1]) / abs(historical_fcf[i-1])
                growth_rates.append(growth_rate)
        
        avg_growth_rate = np.mean(growth_rates) if growth_rates else 0.08
        median_growth_rate = np.median(growth_rates) if growth_rates else 0.08
        
        # Cap growth rate to reasonable bounds
        avg_growth_rate = max(min(avg_growth_rate, 0.25), -0.10)  # Between -10% and 25%
        
        # Method 1: Average growth rate
        last_fcf = historical_fcf[-1]
        forecasted_avg = []
        for year in range(1, self.forecast_years + 1):
            forecasted_fcf = last_fcf * ((1 + avg_growth_rate) ** year)
            forecasted_avg.append(forecasted_fcf)
        
        # Method 2: Linear regression trend
        years = np.arange(len(historical_fcf))
        coefficients = np.polyfit(years, historical_fcf, deg=1)
        forecasted_linear = []
        for year in range(len(historical_fcf), len(historical_fcf) + self.forecast_years):
            forecasted_fcf = coefficients[0] * year + coefficients[1]
            forecasted_linear.append(max(forecasted_fcf, last_fcf * 0.5))  # Floor at 50% of last FCF
        
        # Method 3: Conservative estimate (lower of the two)
        forecasted_conservative = [min(avg, lin) for avg, lin in zip(forecasted_avg, forecasted_linear)]
        
        return {
            "historical_fcf": historical_fcf,
            "historical_growth_rates": growth_rates,
            "average_growth_rate": avg_growth_rate,
            "median_growth_rate": median_growth_rate,
            "forecasted_fcf_avg_growth": forecasted_avg,
            "forecasted_fcf_linear": forecasted_linear,
            "forecasted_fcf_conservative": forecasted_conservative,
            "forecast_years": self.forecast_years
        }
    
    def calculate_present_value(self, future_cash_flows: List[float]) -> Dict[str, Any]:
        """
        Calculate present value of future cash flows.
        
        PV = FCF / (1 + r)^t
        
        Args:
            future_cash_flows: List of future FCF
            
        Returns:
            Dictionary with PV calculations
        """
        present_values = []
        cumulative_pv = 0
        
        for year, fcf in enumerate(future_cash_flows, start=1):
            pv = fcf / ((1 + self.discount_rate) ** year)
            present_values.append(pv)
            cumulative_pv += pv
        
        return {
            "present_values": present_values,
            "total_pv": cumulative_pv,
            "discount_rate": self.discount_rate,
            "years": list(range(1, len(future_cash_flows) + 1))
        }
    
    def calculate_terminal_value(self, final_fcf: float) -> Dict[str, Any]:
        """
        Calculate terminal value using Gordon Growth Model.
        
        Terminal Value = FCF_final * (1 + g) / (r - g)
        
        Args:
            final_fcf: Free cash flow in the final forecast year
            
        Returns:
            Dictionary with terminal value calculations
        """
        if self.discount_rate <= self.terminal_growth_rate:
            raise ValueError("Discount rate must be greater than terminal growth rate")
        
        terminal_value = (final_fcf * (1 + self.terminal_growth_rate)) / (
            self.discount_rate - self.terminal_growth_rate
        )
        
        # Present value of terminal value
        pv_terminal = terminal_value / ((1 + self.discount_rate) ** self.forecast_years)
        
        return {
            "terminal_value": terminal_value,
            "pv_terminal_value": pv_terminal,
            "terminal_growth_rate": self.terminal_growth_rate,
            "final_fcf": final_fcf,
            "discount_years": self.forecast_years
        }
    
    def calculate_intrinsic_value(
        self,
        forecasted_fcf: List[float],
        shares_outstanding: int,
        cash: float = 0,
        debt: float = 0
    ) -> Dict[str, Any]:
        """
        Calculate intrinsic value per share using DCF method.
        
        Enterprise Value = PV(Forecasted FCF) + PV(Terminal Value)
        Equity Value = Enterprise Value + Cash - Debt
        Intrinsic Value per Share = Equity Value / Shares Outstanding
        
        Args:
            forecasted_fcf: List of forecasted FCF
            shares_outstanding: Number of shares outstanding
            cash: Cash and cash equivalents
            debt: Total debt
            
        Returns:
            Complete DCF valuation results
        """
        # Calculate PV of forecasted FCF
        pv_data = self.calculate_present_value(forecasted_fcf)
        
        # Calculate terminal value
        terminal_data = self.calculate_terminal_value(forecasted_fcf[-1])
        
        # Enterprise value
        enterprise_value = pv_data["total_pv"] + terminal_data["pv_terminal_value"]
        
        # Equity value
        equity_value = enterprise_value + cash - debt
        
        # Intrinsic value per share
        intrinsic_value_per_share = equity_value / shares_outstanding
        
        return {
            "forecasted_fcf": forecasted_fcf,
            "present_value_fcf": pv_data["total_pv"],
            "present_values_by_year": pv_data["present_values"],
            "terminal_value": terminal_data["terminal_value"],
            "pv_terminal_value": terminal_data["pv_terminal_value"],
            "enterprise_value": enterprise_value,
            "cash": cash,
            "debt": debt,
            "equity_value": equity_value,
            "shares_outstanding": shares_outstanding,
            "intrinsic_value_per_share": intrinsic_value_per_share,
            "parameters": {
                "discount_rate": self.discount_rate,
                "terminal_growth_rate": self.terminal_growth_rate,
                "forecast_years": self.forecast_years
            }
        }
    
    def sensitivity_analysis(
        self,
        forecasted_fcf: List[float],
        shares_outstanding: int,
        discount_rates: List[float] = None,
        terminal_growth_rates: List[float] = None
    ) -> Dict[str, Any]:
        """
        Perform sensitivity analysis on intrinsic value.
        
        Args:
            forecasted_fcf: Forecasted FCF
            shares_outstanding: Number of shares
            discount_rates: List of discount rates to test
            terminal_growth_rates: List of terminal growth rates to test
            
        Returns:
            Sensitivity analysis results
        """
        if discount_rates is None:
            discount_rates = [0.08, 0.09, 0.10, 0.11, 0.12]
        
        if terminal_growth_rates is None:
            terminal_growth_rates = [0.02, 0.025, 0.03, 0.035, 0.04]
        
        results = []
        
        for dr in discount_rates:
            for tgr in terminal_growth_rates:
                if dr <= tgr:
                    continue
                
                calc = DCFCalculator(
                    discount_rate=dr,
                    terminal_growth_rate=tgr,
                    forecast_years=self.forecast_years
                )
                
                valuation = calc.calculate_intrinsic_value(
                    forecasted_fcf=forecasted_fcf,
                    shares_outstanding=shares_outstanding
                )
                
                results.append({
                    "discount_rate": dr,
                    "terminal_growth_rate": tgr,
                    "intrinsic_value_per_share": valuation["intrinsic_value_per_share"],
                    "enterprise_value": valuation["enterprise_value"]
                })
        
        return {
            "sensitivity_matrix": results,
            "discount_rates": discount_rates,
            "terminal_growth_rates": terminal_growth_rates
        }
