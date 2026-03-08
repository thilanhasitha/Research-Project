"""
API routes for DCF valuation and PDF analysis.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional

from app.services.pdf_analysis_service import PDFAnalysisService
from app.services.dcf_service import DCFCalculator
from app.schemas.valuation import (
    ValuationRequest,
    SensitivityRequest,
    DCFParametersSchema
)

router = APIRouter(prefix="/valuation", tags=["valuation"])


@router.post("/analyze-pdf", summary="Analyze PDF and calculate intrinsic value")
async def analyze_pdf(
    file: UploadFile = File(..., description="Financial report PDF"),
    discount_rate: float = Form(0.10),
    terminal_growth_rate: float = Form(0.03),
    forecast_years: int = Form(5)
):
    """
    Upload a financial report PDF, extract data using Gemini API,
    forecast FCF, and calculate intrinsic value using DCF method.
    
    Process:
    1. Extract financial data from PDF using Gemini AI
    2. Calculate historical Free Cash Flow (OCF - CAPEX)
    3. Forecast future FCF using multiple methods
    4. Apply DCF formula to calculate intrinsic value
    5. Perform sensitivity analysis
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Read PDF content
        pdf_content = await file.read()
        
        # Analyze using PDF Analysis Service
        service = PDFAnalysisService()
        result = await service.analyze_financial_report(
            pdf_content=pdf_content,
            filename=file.filename,
            discount_rate=discount_rate,
            terminal_growth_rate=terminal_growth_rate,
            forecast_years=forecast_years
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/extract-pdf", summary="Extract financial data from PDF only")
async def extract_pdf_data(
    file: UploadFile = File(..., description="Financial report PDF")
):
    """
    Extract financial data from PDF using Gemini API without performing valuation.
    
    Returns structured financial data including:
    - Company information
    - Historical revenue, OCF, CAPEX
    - Additional metrics (shares, cash, debt)
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        pdf_content = await file.read()
        service = PDFAnalysisService()
        result = await service.extract_only(
            pdf_content=pdf_content,
            filename=file.filename
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/calculate", summary="Calculate valuation from provided data")
def calculate_valuation(request: ValuationRequest):
    """
    Calculate DCF valuation from provided financial data (no PDF upload required).
    
    Useful when you already have the financial data and just need valuation.
    """
    try:
        service = PDFAnalysisService()
        result = service.calculate_valuation_only(
            operating_cash_flow=request.financial_data.operating_cash_flow,
            capital_expenditure=request.financial_data.capital_expenditure,
            shares_outstanding=request.financial_data.shares_outstanding,
            cash=request.financial_data.cash,
            debt=request.financial_data.debt,
            discount_rate=request.parameters.discount_rate,
            terminal_growth_rate=request.parameters.terminal_growth_rate,
            forecast_years=request.parameters.forecast_years
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")


@router.post("/forecast-fcf", summary="Forecast future Free Cash Flow")
def forecast_fcf(
    historical_fcf: list[float],
    forecast_years: int = 5
):
    """
    Forecast future Free Cash Flow using multiple methods:
    - Average historical growth rate
    - Linear trend extrapolation
    - Conservative estimate (minimum of both)
    """
    try:
        calculator = DCFCalculator(forecast_years=forecast_years)
        result = calculator.forecast_fcf(historical_fcf)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sensitivity-analysis", summary="Perform sensitivity analysis")
def sensitivity_analysis(request: SensitivityRequest):
    """
    Perform sensitivity analysis on intrinsic value by varying:
    - Discount rates
    - Terminal growth rates
    
    Returns a matrix of intrinsic values for different parameter combinations.
    """
    try:
        calculator = DCFCalculator()
        result = calculator.sensitivity_analysis(
            forecasted_fcf=request.forecasted_fcf,
            shares_outstanding=request.shares_outstanding,
            discount_rates=request.discount_rates,
            terminal_growth_rates=request.terminal_growth_rates
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/example-data", summary="Get example financial data")
def get_example_data():
    """
    Get example financial data for testing the valuation endpoints.
    """
    return {
        "company": "Example Company Ltd.",
        "financial_data": {
            "years": [2020, 2021, 2022, 2023, 2024],
            "revenue": [1500000000, 1650000000, 1800000000, 2000000000, 2200000000],
            "operating_cash_flow": [250000000, 280000000, 310000000, 350000000, 390000000],
            "capital_expenditure": [80000000, 85000000, 90000000, 95000000, 100000000],
            "free_cash_flow": [170000000, 195000000, 220000000, 255000000, 290000000]
        },
        "additional_metrics": {
            "shares_outstanding": 100000000,
            "cash_and_equivalents": 150000000,
            "total_debt": 500000000,
            "current_price": 45.50
        },
        "suggested_parameters": {
            "discount_rate": 0.10,
            "terminal_growth_rate": 0.03,
            "forecast_years": 5
        }
    }
