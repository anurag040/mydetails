from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import pandas as pd

from app.services.file_handler import FileHandler
from app.services.analysis_matrix_service import analysis_matrix_service
from app.models.analysis_matrix import AnalysisType

router = APIRouter()
file_handler = FileHandler()

class AnalysisMatrixResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str

@router.get("/analysis-matrix/{dataset_id}", response_model=AnalysisMatrixResponse)
async def get_analysis_matrix(dataset_id: str):
    """Get the analysis matrix for a specific dataset"""
    try:
        matrix = analysis_matrix_service.get_analysis_matrix(dataset_id)
        
        if not matrix:
            return AnalysisMatrixResponse(
                success=False,
                data={},
                message="No analysis history found for this dataset"
            )
        
        return AnalysisMatrixResponse(
            success=True,
            data=matrix.dict(),
            message="Analysis matrix retrieved successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis matrix: {str(e)}")

@router.get("/analysis-report/{dataset_id}", response_model=AnalysisMatrixResponse)
async def get_analysis_report(dataset_id: str):
    """Get a comprehensive analysis report for a dataset"""
    try:
        report = analysis_matrix_service.generate_analysis_report(dataset_id)
        
        if "error" in report:
            return AnalysisMatrixResponse(
                success=False,
                data={},
                message=report["error"]
            )
        
        return AnalysisMatrixResponse(
            success=True,
            data=report,
            message="Analysis report generated successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis report: {str(e)}")

@router.post("/record-analysis/{dataset_id}")
async def record_analysis_endpoint(
    dataset_id: str,
    analysis_type: str,
    user_query: str,
    method_used: str,
    parameters: Dict[str, Any],
    results: Dict[str, Any],
    code_executed: str = ""
):
    """Manually record an analysis (for testing purposes)"""
    try:
        # Load dataset
        df = await file_handler.load_dataset(dataset_id)
        if df is None:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Convert string to AnalysisType enum
        try:
            analysis_type_enum = AnalysisType(analysis_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid analysis type: {analysis_type}")
        
        # Record the analysis
        record = analysis_matrix_service.record_analysis(
            dataset_id=dataset_id,
            analysis_type=analysis_type_enum,
            user_query=user_query,
            method_used=method_used,
            parameters=parameters,
            results=results,
            code_executed=code_executed,
            data=df
        )
        
        return AnalysisMatrixResponse(
            success=True,
            data={
                "analysis_id": record.id,
                "score": record.score.dict(),
                "recommendations": record.recommendations,
                "warnings": record.warnings
            },
            message="Analysis recorded successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording analysis: {str(e)}")

@router.get("/analysis-types")
async def get_analysis_types():
    """Get all available analysis types"""
    return {
        "analysis_types": [
            {
                "value": analysis_type.value,
                "name": analysis_type.value.replace("_", " ").title(),
                "description": _get_analysis_description(analysis_type)
            }
            for analysis_type in AnalysisType
        ]
    }

def _get_analysis_description(analysis_type: AnalysisType) -> str:
    """Get description for each analysis type"""
    descriptions = {
        AnalysisType.DESCRIPTIVE_STATS: "Basic statistical measures (mean, median, std dev, etc.)",
        AnalysisType.CORRELATION: "Correlation analysis between variables",
        AnalysisType.DISTRIBUTION: "Distribution analysis and normality testing",
        AnalysisType.MISSING_DATA: "Missing data patterns and recommendations",
        AnalysisType.OUTLIER_DETECTION: "Outlier detection using statistical methods",
        AnalysisType.TREND_ANALYSIS: "Time series trend analysis",
        AnalysisType.BOLLINGER_BANDS: "Bollinger Bands technical analysis",
        AnalysisType.REGRESSION: "Regression analysis and modeling",
        AnalysisType.CLUSTERING: "Clustering and segmentation analysis",
        AnalysisType.HYPOTHESIS_TEST: "Statistical hypothesis testing"
    }
    return descriptions.get(analysis_type, "Statistical analysis")
