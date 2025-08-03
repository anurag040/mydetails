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
    - missing_value_analysis: Comprehensive missing value report with strategies
    - duplicates_analysis: Full and partial duplicate detection with recommendations
    - type_integrity_validation: Data type and integrity validation with quality scoring
    - univariate_summaries: Comprehensive univariate analysis for numeric, categorical, and temporal data
    - outlier_detection: Multi-method outlier detection (univariate and multivariate)
    - feature_engineering_ideas: Generate feature engineering suggestions based on data characteristics
    - multicollinearity_assessment: Assess multicollinearity using VIF and correlation analysis
    - dimensionality_insights: Provide PCA and clustering insights for dimensionality assessment
    - baseline_model_sanity: Assess data readiness for baseline modeling
    - drift_stability_analysis: Analyze data stability and potential drift indicators
    - bias_fairness_flags: Detect potential bias and fairness issues in the dataset
    - documentation_summary: Generate comprehensive data dictionary and findings summary
    - reproducibility_info: Generate reproducibility information and environment details
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
            },
            {
                "id": "missing_value_analysis",
                "name": "Missing Value Report & Strategy",
                "description": "Comprehensive missing value analysis with suggested handling strategies"
            },
            {
                "id": "duplicates_analysis",
                "name": "Duplicates Check",
                "description": "Full and partial duplicate detection with recommendations for data quality"
            },
            {
                "id": "type_integrity_validation",
                "name": "Type/Integrity Validation",
                "description": "Data type consistency and integrity validation with quality scoring"
            },
            {
                "id": "univariate_summaries",
                "name": "Univariate Summaries",
                "description": "Comprehensive analysis for numeric, categorical, and temporal columns"
            },
            {
                "id": "outlier_detection",
                "name": "Outlier Detection",
                "description": "Multi-method outlier detection using statistical and machine learning approaches"
            },
            {
                "id": "feature_engineering_ideas",
                "name": "Feature Engineering Ideas",
                "description": "Generate feature engineering suggestions based on data characteristics"
            },
            {
                "id": "multicollinearity_assessment",
                "name": "Multicollinearity Assessment",
                "description": "Assess multicollinearity using VIF and correlation analysis"
            },
            {
                "id": "dimensionality_insights",
                "name": "Dimensionality Insights",
                "description": "PCA and clustering insights for dimensionality assessment"
            },
            {
                "id": "baseline_model_sanity",
                "name": "Baseline Model Sanity",
                "description": "Assess data readiness for baseline modeling"
            },
            {
                "id": "drift_stability_analysis",
                "name": "Drift/Stability Analysis",
                "description": "Analyze data stability and potential drift indicators"
            },
            {
                "id": "bias_fairness_flags",
                "name": "Bias/Fairness Flags",
                "description": "Detect potential bias and fairness issues in the dataset"
            },
            {
                "id": "documentation_summary",
                "name": "Documentation Summary",
                "description": "Generate comprehensive data dictionary and findings summary"
            },
            {
                "id": "reproducibility_info",
                "name": "Reproducibility Info",
                "description": "Generate reproducibility information and environment details"
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
