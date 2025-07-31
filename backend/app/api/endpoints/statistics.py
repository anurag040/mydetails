from fastapi import APIRouter, HTTPException
from app.schemas.responses import StatisticsRequest, BasicStatsResponse, AdvancedStatsRequest, AdvancedStatsResponse
from app.services.statistics_calculator import StatisticsCalculator
from typing import List

router = APIRouter()
stats_calculator = StatisticsCalculator()

@router.post("/statistics/basic", response_model=BasicStatsResponse)
async def calculate_basic_statistics(request: StatisticsRequest):
    """
    Calculate basic statistics for a dataset
    Available options:
    - descriptive: Mean, median, mode, std, min, max, quartiles
    - correlation: Correlation matrix and analysis
    - distribution: Distribution analysis, skewness, kurtosis
    - missing_data: Missing data analysis and patterns
    """
    try:
        result = await stats_calculator.calculate_basic_stats(
            request.dataset_id, 
            request.options
        )
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics calculation failed: {str(e)}")

@router.post("/statistics/advanced", response_model=AdvancedStatsResponse)
async def calculate_advanced_statistics(request: AdvancedStatsRequest):
    """
    Calculate advanced statistics and machine learning insights
    Available options:
    - regression: Linear/polynomial regression analysis
    - clustering: K-means, hierarchical clustering
    - pca: Principal Component Analysis
    - time_series: Time series analysis (if applicable)
    - anomaly_detection: Outlier detection using multiple methods
    - feature_importance: Feature importance analysis
    """
    try:
        result = await stats_calculator.calculate_advanced_stats(
            request.dataset_id,
            request.options
        )
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced statistics calculation failed: {str(e)}")

@router.get("/statistics/options/basic")
async def get_basic_statistics_options():
    """
    Get available basic statistics options
    """
    return {
        "options": [
            {
                "id": "descriptive",
                "name": "Descriptive Statistics",
                "description": "Mean, median, mode, standard deviation, min, max, quartiles"
            },
            {
                "id": "correlation",
                "name": "Correlation Analysis",
                "description": "Correlation matrix, correlation strengths, and relationships"
            },
            {
                "id": "distribution",
                "name": "Distribution Analysis",
                "description": "Data distribution, skewness, kurtosis, normality tests"
            },
            {
                "id": "missing_data",
                "name": "Missing Data Analysis",
                "description": "Missing data patterns, percentages, and recommendations"
            }
        ]
    }

@router.get("/statistics/options/advanced")
async def get_advanced_statistics_options():
    """
    Get available advanced statistics options
    """
    return {
        "options": [
            {
                "id": "regression",
                "name": "Regression Analysis",
                "description": "Linear and polynomial regression with feature relationships"
            },
            {
                "id": "clustering",
                "name": "Clustering Analysis",
                "description": "K-means and hierarchical clustering to find data groups"
            },
            {
                "id": "pca",
                "name": "Principal Component Analysis",
                "description": "Dimensionality reduction and feature importance"
            },
            {
                "id": "time_series",
                "name": "Time Series Analysis",
                "description": "Trend analysis, seasonality, and forecasting (for time-based data)"
            },
            {
                "id": "anomaly_detection",
                "name": "Anomaly Detection",
                "description": "Outlier detection using statistical and ML methods"
            },
            {
                "id": "feature_importance",
                "name": "Feature Importance",
                "description": "Identify the most important features in your dataset"
            }
        ]
    }

@router.get("/statistics/{dataset_id}/summary")
async def get_statistics_summary(dataset_id: str):
    """
    Get a quick statistical summary of the dataset
    """
    try:
        summary = await stats_calculator.get_quick_summary(dataset_id)
        return summary
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
