"""
Schemas for DCF valuation endpoints.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class DCFParametersSchema(BaseModel):
    """Parameters for DCF calculation."""
    discount_rate: float = Field(0.10, ge=0.01, le=0.30, description="Discount rate (WACC)")
    terminal_growth_rate: float = Field(0.03, ge=0.01, le=0.10, description="Terminal growth rate")
    forecast_years: int = Field(5, ge=3, le=10, description="Number of years to forecast")


class FinancialDataInput(BaseModel):
    """Input financial data for valuation."""
    operating_cash_flow: List[float] = Field(..., description="Historical operating cash flow")
    capital_expenditure: List[float] = Field(..., description="Historical capital expenditure")
    shares_outstanding: int = Field(..., gt=0, description="Number of shares outstanding")
    cash: float = Field(0, ge=0, description="Cash and cash equivalents")
    debt: float = Field(0, ge=0, description="Total debt")


class ValuationRequest(BaseModel):
    """Request for valuation calculation."""
    financial_data: FinancialDataInput
    parameters: Optional[DCFParametersSchema] = DCFParametersSchema()


class ExtractedFinancialData(BaseModel):
    """Extracted financial data from PDF."""
    company_name: Optional[str] = None
    report_year: Optional[int] = None
    currency: str = "LKR"
    years: List[int]
    revenue: List[float]
    operating_cash_flow: List[float]
    capital_expenditure: List[float]
    historical_fcf: List[float]


class ForecastResult(BaseModel):
    """FCF forecast results."""
    method: str
    forecasted_fcf: List[float]
    average_growth_rate: float
    forecast_years: int


class ValuationResult(BaseModel):
    """DCF valuation results."""
    forecasted_fcf: List[float]
    present_value_fcf: float
    present_values_by_year: List[float]
    terminal_value: float
    pv_terminal_value: float
    enterprise_value: float
    equity_value: float
    intrinsic_value_per_share: float
    shares_outstanding: int
    cash: float
    debt: float


class PDFAnalysisResponse(BaseModel):
    """Complete PDF analysis response."""
    status: str
    filename: str
    company_name: Optional[str] = None
    report_year: Optional[int] = None
    currency: str
    extraction: dict
    forecast: dict
    valuation: dict
    sensitivity_analysis: Optional[dict] = None


class SensitivityRequest(BaseModel):
    """Request for sensitivity analysis."""
    forecasted_fcf: List[float]
    shares_outstanding: int
    discount_rates: Optional[List[float]] = None
    terminal_growth_rates: Optional[List[float]] = None
