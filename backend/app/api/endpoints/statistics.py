from fastapi import APIRouter, HTTPException
import logging
import pandas as pd
from app.schemas.responses import StatisticsRequest, BasicStatsResponse, AdvancedStatsRequest, AdvancedStatsResponse
from app.services.statistics_calculator import StatisticsCalculator
from app.services.comprehensive_analysis_validator import ComprehensiveAnalysisValidator
from app.services.file_handler import FileHandler
from typing import List

router = APIRouter()
logger = logging.getLogger("statistics")
logging.basicConfig(level=logging.INFO)
stats_calculator = StatisticsCalculator()
analysis_validator = ComprehensiveAnalysisValidator()
file_handler = FileHandler()

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
        logger.info(f"Calculating basic statistics for dataset_id={request.dataset_id}, options={request.options}")
        result = await stats_calculator.calculate_basic_stats(
            request.dataset_id, 
            request.options
        )
        logger.info(f"Successfully calculated basic statistics for dataset_id={request.dataset_id}")
        return result
    except FileNotFoundError:
        logger.error(f"Dataset not found: {request.dataset_id}")
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        logger.exception(f"Statistics calculation failed for dataset_id={request.dataset_id}: {str(e)}")
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

@router.post("/statistics/{dataset_id}/validate")
async def validate_analysis_accuracy(dataset_id: str):
    """
    Validate the accuracy and quality of statistical analyses performed on a dataset.
    
    This endpoint evaluates:
    - Statistical accuracy of computed metrics
    - Completeness of analysis coverage
    - Methodology appropriateness
    - Data quality considerations
    
    Returns comprehensive validation metrics for each analysis type.
    """
    try:
        logger.info(f"Starting comprehensive analysis validation for dataset: {dataset_id}")
        
        # Load the dataset
        df = await file_handler.load_dataset(dataset_id)
        if df is None:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Get all available analysis options and run comprehensive analysis
        basic_options = [
            "descriptive", "correlation", "distribution", "missing_data",
            "missing_value_analysis", "duplicates_analysis", "type_integrity_validation",
            "univariate_summaries", "outlier_detection", "feature_engineering_ideas",
            "multicollinearity_assessment", "dimensionality_insights", 
            "baseline_model_sanity", "drift_stability_analysis", "bias_fairness_flags",
            "documentation_summary", "reproducibility_info"
        ]
        
        # Calculate comprehensive statistics
        analysis_results = await stats_calculator.calculate_basic_stats(dataset_id, basic_options)
        
        # Convert to dictionary for validation
        analysis_dict = {
            'descriptive_stats': analysis_results.descriptive_stats,
            'correlation_matrix': analysis_results.correlation_matrix,
            'distribution_analysis': analysis_results.distribution_analysis,
            'missing_data_summary': analysis_results.missing_data_summary,
            'missing_value_analysis': analysis_results.missing_value_analysis,
            'duplicates_analysis': analysis_results.duplicates_analysis,
            'type_integrity_validation': analysis_results.type_integrity_validation,
            'univariate_summaries': analysis_results.univariate_summaries,
            'outlier_detection': analysis_results.outlier_detection,
            'feature_engineering_ideas': analysis_results.feature_engineering_ideas,
            'multicollinearity_assessment': analysis_results.multicollinearity_assessment,
            'dimensionality_insights': analysis_results.dimensionality_insights,
            'baseline_model_sanity': analysis_results.baseline_model_sanity,
            'drift_stability_analysis': analysis_results.drift_stability_analysis,
            'bias_fairness_flags': analysis_results.bias_fairness_flags,
            'documentation_summary': analysis_results.documentation_summary,
            'reproducibility_info': analysis_results.reproducibility_info
        }
        
        # Perform comprehensive validation
        validation_report = analysis_validator.validate_analysis_results(
            dataset_id, analysis_dict, df
        )
        
        logger.info(f"Validation completed for dataset: {dataset_id}, overall score: {validation_report['overall_quality_score']}")
        
        return validation_report
        
    except FileNotFoundError:
        logger.error(f"Dataset not found: {dataset_id}")
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        logger.exception(f"Analysis validation failed for dataset: {dataset_id}")
        raise HTTPException(status_code=500, detail=f"Analysis validation failed: {str(e)}")

@router.get("/statistics/{dataset_id}/validation-metrics")
async def get_validation_metrics(dataset_id: str):
    """
    Get detailed validation metrics for a specific dataset's analyses.
    
    Returns:
    - Quality scores for each analysis type
    - Accuracy assessments
    - Methodology evaluations
    - Recommendations for improvement
    """
    try:
        # Trigger validation if not cached
        validation_report = await validate_analysis_accuracy(dataset_id)
        
        # Format for Analysis Matrix display
        formatted_metrics = {
            'dataset_id': dataset_id,
            'overall_quality_score': validation_report['overall_quality_score'],
            'statistical_accuracy': validation_report.get('statistical_accuracy', 0),
            'analysis_completeness': validation_report.get('analysis_completeness', 0),
            'logical_consistency': validation_report.get('logical_consistency', 0),
            'response_efficiency': validation_report.get('response_efficiency', 0),
            'analysis_scores': {},
            'quality_breakdown': {
                'excellent_analyses': 0,
                'good_analyses': 0,
                'needs_improvement': 0
            },
            'detailed_evaluations': validation_report['analysis_validations'],
            'summary': validation_report['summary'],
            'recommendations': validation_report['recommendations'],
            'validation_timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Process individual analysis scores
        for analysis_type, validation in validation_report['analysis_validations'].items():
            score = validation['quality_score']
            formatted_metrics['analysis_scores'][analysis_type] = {
                'quality_score': score,
                'grade': validation_report.get('summary', {}).get('overall_grade', 'N/A'),
                'accuracy_metrics': validation.get('accuracy_metrics', {}),
                'strengths': validation.get('strengths', []),
                'issues': validation.get('issues', [])
            }
            
            # Categorize quality levels
            if score >= 85:
                formatted_metrics['quality_breakdown']['excellent_analyses'] += 1
            elif score >= 70:
                formatted_metrics['quality_breakdown']['good_analyses'] += 1
            else:
                formatted_metrics['quality_breakdown']['needs_improvement'] += 1
        
        return formatted_metrics
        
    except Exception as e:
        logger.exception(f"Failed to get validation metrics for dataset: {dataset_id}")
        raise HTTPException(status_code=500, detail=f"Failed to get validation metrics: {str(e)}")
