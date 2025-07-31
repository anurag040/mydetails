from fastapi import APIRouter, HTTPException
from app.schemas.responses import AnalysisResponse
from app.services.llm_service import LLMService
from datetime import datetime

router = APIRouter()
llm_service = LLMService()

@router.post("/analysis/full", response_model=AnalysisResponse)
async def perform_full_analysis(dataset_id: str):
    """
    Perform comprehensive LLM-powered analysis with validation metrics
    """
    try:
        result = await llm_service.perform_full_analysis(dataset_id)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analysis/insights")
async def generate_insights(dataset_id: str, focus_areas: list[str] = None):
    """
    Generate LLM insights for specific focus areas
    Focus areas: ["patterns", "anomalies", "trends", "correlations", "recommendations"]
    """
    try:
        insights = await llm_service.generate_targeted_insights(dataset_id, focus_areas)
        return {
            "dataset_id": dataset_id,
            "insights": insights,
            "focus_areas": focus_areas,
            "timestamp": datetime.now()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")

@router.get("/analysis/{dataset_id}/validation")
async def get_validation_metrics(dataset_id: str):
    """
    Get validation metrics for the latest analysis
    """
    try:
        metrics = await llm_service.get_validation_metrics(dataset_id)
        if not metrics:
            raise HTTPException(status_code=404, detail="No analysis found for this dataset")
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve validation metrics: {str(e)}")

@router.post("/analysis/validate")
async def validate_custom_analysis(dataset_id: str, custom_analysis: str):
    """
    Validate a custom analysis against the dataset
    """
    try:
        validation = await llm_service.validate_custom_analysis(dataset_id, custom_analysis)
        return {
            "dataset_id": dataset_id,
            "validation_metrics": validation,
            "timestamp": datetime.now()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.get("/analysis/options")
async def get_analysis_options():
    """
    Get available analysis focus areas and options
    """
    return {
        "focus_areas": [
            {
                "id": "patterns",
                "name": "Pattern Detection",
                "description": "Identify hidden patterns and relationships in the data"
            },
            {
                "id": "anomalies",
                "name": "Anomaly Detection",
                "description": "Find outliers and unusual data points"
            },
            {
                "id": "trends",
                "name": "Trend Analysis",
                "description": "Analyze trends and temporal patterns"
            },
            {
                "id": "correlations",
                "name": "Correlation Insights",
                "description": "Deep dive into variable relationships and dependencies"
            },
            {
                "id": "recommendations",
                "name": "Data Recommendations",
                "description": "Get actionable recommendations for data improvement"
            },
            {
                "id": "business_insights",
                "name": "Business Insights",
                "description": "Extract business-relevant insights and opportunities"
            }
        ],
        "validation_metrics": [
            "Statistical Accuracy",
            "Missing Data Accuracy", 
            "Insight Relevance",
            "Completeness",
            "Consistency",
            "Composite Score"
        ]
    }
