"""
PDF extraction and analysis service.
"""
from typing import Dict, Any
import io

from app.clients.gemini_client import GeminiClient
from app.services.dcf_service import DCFCalculator


class PDFAnalysisService:
    """Service for analyzing financial PDFs and calculating valuations."""
    
    def __init__(self, gemini_api_key: str | None = None):
        """Initialize PDF analysis service."""
        self.gemini_client = GeminiClient(api_key=gemini_api_key)
    
    async def analyze_financial_report(
        self,
        pdf_content: bytes,
        filename: str,
        discount_rate: float = 0.10,
        terminal_growth_rate: float = 0.03,
        forecast_years: int = 5
    ) -> Dict[str, Any]:
        """
        Complete analysis pipeline: Extract data from PDF and calculate DCF valuation.
        
        Args:
            pdf_content: Binary PDF content
            filename: Name of the PDF file
            discount_rate: WACC or required return rate
            terminal_growth_rate: Perpetual growth rate
            forecast_years: Number of years to forecast
            
        Returns:
            Complete analysis results including extraction and valuation
        """
        # Step 1: Extract financial data using Gemini
        extraction_result = await self.gemini_client.extract_financial_data(
            pdf_content=pdf_content,
            filename=filename
        )
        
        if extraction_result["status"] != "success":
            return {
                "status": "error",
                "error": extraction_result.get("error", "Failed to extract data"),
                "stage": "extraction"
            }
        
        extracted_data = extraction_result["extracted_data"]
        financial_data = extracted_data.get("financial_data", {})
        
        # Validate extracted data
        if not financial_data.get("operating_cash_flow") or not financial_data.get("capital_expenditure"):
            return {
                "status": "error",
                "error": "Missing required financial data (OCF or CAPEX)",
                "stage": "validation",
                "extracted_data": extracted_data
            }
        
        # Step 2: Calculate Free Cash Flow
        dcf_calculator = DCFCalculator(
            discount_rate=discount_rate,
            terminal_growth_rate=terminal_growth_rate,
            forecast_years=forecast_years
        )
        
        historical_fcf = dcf_calculator.calculate_free_cash_flow(
            operating_cash_flow=financial_data["operating_cash_flow"],
            capital_expenditure=financial_data["capital_expenditure"]
        )
        
        # Step 3: Forecast future FCF
        forecast_result = dcf_calculator.forecast_fcf(historical_fcf)
        
        # Use conservative forecast by default
        forecasted_fcf = forecast_result["forecasted_fcf_conservative"]
        
        # Step 4: Calculate intrinsic value
        additional_metrics = extracted_data.get("additional_metrics", {})
        shares_outstanding = additional_metrics.get("shares_outstanding", 100000000)
        cash = additional_metrics.get("cash_and_equivalents", 0)
        debt = additional_metrics.get("total_debt", 0)
        
        valuation = dcf_calculator.calculate_intrinsic_value(
            forecasted_fcf=forecasted_fcf,
            shares_outstanding=shares_outstanding,
            cash=cash,
            debt=debt
        )
        
        # Step 5: Perform sensitivity analysis
        sensitivity = dcf_calculator.sensitivity_analysis(
            forecasted_fcf=forecasted_fcf,
            shares_outstanding=shares_outstanding
        )
        
        return {
            "status": "success",
            "filename": filename,
            "company_name": extracted_data.get("company_name"),
            "report_year": extracted_data.get("report_year"),
            "currency": extracted_data.get("currency", "LKR"),
            "extraction": {
                "historical_years": financial_data.get("years", []),
                "revenue": financial_data.get("revenue", []),
                "operating_cash_flow": financial_data["operating_cash_flow"],
                "capital_expenditure": financial_data["capital_expenditure"],
                "historical_fcf": historical_fcf,
                "additional_metrics": additional_metrics
            },
            "forecast": {
                "method": "conservative",
                "forecasted_fcf": forecasted_fcf,
                "average_growth_rate": forecast_result["average_growth_rate"],
                "forecast_years": forecast_years,
                "all_forecasts": {
                    "avg_growth": forecast_result["forecasted_fcf_avg_growth"],
                    "linear_trend": forecast_result["forecasted_fcf_linear"],
                    "conservative": forecast_result["forecasted_fcf_conservative"]
                }
            },
            "valuation": valuation,
            "sensitivity_analysis": sensitivity
        }
    
    async def extract_only(self, pdf_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract financial data from PDF without performing valuation.
        
        Args:
            pdf_content: Binary PDF content
            filename: Name of the PDF file
            
        Returns:
            Extracted financial data
        """
        return await self.gemini_client.extract_financial_data(
            pdf_content=pdf_content,
            filename=filename
        )
    
    def calculate_valuation_only(
        self,
        operating_cash_flow: list,
        capital_expenditure: list,
        shares_outstanding: int,
        cash: float = 0,
        debt: float = 0,
        discount_rate: float = 0.10,
        terminal_growth_rate: float = 0.03,
        forecast_years: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate valuation from provided financial data (no PDF extraction).
        
        Args:
            operating_cash_flow: Historical OCF data
            capital_expenditure: Historical CAPEX data
            shares_outstanding: Number of shares
            cash: Cash and equivalents
            debt: Total debt
            discount_rate: Discount rate for DCF
            terminal_growth_rate: Terminal growth rate
            forecast_years: Years to forecast
            
        Returns:
            Valuation results
        """
        dcf_calculator = DCFCalculator(
            discount_rate=discount_rate,
            terminal_growth_rate=terminal_growth_rate,
            forecast_years=forecast_years
        )
        
        # Calculate historical FCF
        historical_fcf = dcf_calculator.calculate_free_cash_flow(
            operating_cash_flow=operating_cash_flow,
            capital_expenditure=capital_expenditure
        )
        
        # Forecast FCF
        forecast_result = dcf_calculator.forecast_fcf(historical_fcf)
        forecasted_fcf = forecast_result["forecasted_fcf_conservative"]
        
        # Calculate valuation
        valuation = dcf_calculator.calculate_intrinsic_value(
            forecasted_fcf=forecasted_fcf,
            shares_outstanding=shares_outstanding,
            cash=cash,
            debt=debt
        )
        
        return {
            "status": "success",
            "historical_fcf": historical_fcf,
            "forecast": forecast_result,
            "valuation": valuation
        }
