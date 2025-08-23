from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime
import uuid
import json
import os

from app.models.analysis_matrix import (
    AnalysisRecord, AnalysisType, AnalysisValidator, 
    AnalysisLogger, AnalysisMatrix, AnalysisScore
)

class AnalysisMatrixService:
    """Service to track, validate, and score all statistical analyses"""
    
    def __init__(self):
        self.logger = AnalysisLogger()
        self.validator = AnalysisValidator()
    
    def record_analysis(self, 
                       dataset_id: str,
                       analysis_type: AnalysisType,
                       user_query: str,
                       method_used: str,
                       parameters: Dict[str, Any],
                       results: Dict[str, Any],
                       code_executed: str,
                       data: pd.DataFrame) -> AnalysisRecord:
        """Record and validate a statistical analysis operation"""
        
        # Generate unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        
        # Validate the analysis and get scores
        score = self.validator.validate_analysis(analysis_type, data, results, parameters)
        
        # Generate validation results
        validation_results = self._generate_validation_results(analysis_type, data, results, parameters, score)
        
        # Generate recommendations and warnings
        recommendations = self._generate_recommendations(analysis_type, score, results)
        warnings = self._generate_warnings(analysis_type, score, results, data)
        
        # Create metadata with JSON-serializable data types
        metadata = {
            'data_shape': list(data.shape),
            'data_types': {col: str(dtype) for col, dtype in data.dtypes.items()},
            'missing_data_percentage': float((data.isnull().sum().sum() / (data.shape[0] * data.shape[1])) * 100),
            'numeric_columns': data.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': data.select_dtypes(include=['object']).columns.tolist(),
            'execution_time': datetime.now().isoformat()
        }
        
        # Create analysis record
        record = AnalysisRecord(
            id=analysis_id,
            dataset_id=dataset_id,
            analysis_type=analysis_type,
            timestamp=datetime.now(),
            user_query=user_query,
            method_used=method_used,
            parameters=parameters,
            results=results,
            code_executed=code_executed,
            validation_results=validation_results,
            score=score,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata
        )
        
        # Log the record
        self.logger.log_analysis(record)
        
        return record
    
    def get_analysis_matrix(self, dataset_id: str) -> Optional[AnalysisMatrix]:
        """Get the complete analysis matrix for a dataset"""
        return self.logger.get_analysis_matrix(dataset_id)
    
    def _generate_validation_results(self, analysis_type: AnalysisType, data: pd.DataFrame, 
                                   results: Dict[str, Any], parameters: Dict[str, Any], 
                                   score: AnalysisScore) -> Dict[str, Any]:
        """Generate detailed validation results"""
        validation = {
            'data_quality_checks': {
                'sufficient_sample_size': len(data) >= 30,
                'no_all_null_columns': not data.isnull().all().any(),
                'numeric_data_available': len(data.select_dtypes(include=[np.number]).columns) > 0
            },
            'methodology_validation': {},
            'result_validation': {},
            'statistical_assumptions': {}
        }
        
        if analysis_type == AnalysisType.DESCRIPTIVE_STATS:
            validation['methodology_validation'] = {
                'appropriate_measures_used': 'mean' in results and 'std' in results,
                'outlier_consideration': 'median' in results,
                'distribution_awareness': 'skewness' in results or 'kurtosis' in results
            }
            
        elif analysis_type == AnalysisType.CORRELATION:
            validation['methodology_validation'] = {
                'appropriate_correlation_method': parameters.get('method', 'pearson') in ['pearson', 'spearman'],
                'significance_testing': 'p_values' in results,
                'multiple_testing_correction': 'corrected_p_values' in results
            }
            validation['statistical_assumptions'] = {
                'linearity_assumption': True,  # Would need actual testing
                'normality_assumption': True   # Would need actual testing
            }
            
        elif analysis_type == AnalysisType.BOLLINGER_BANDS:
            window = parameters.get('window', 20)
            validation['methodology_validation'] = {
                'appropriate_window_size': 10 <= window <= 50,
                'standard_parameters': window == 20 and parameters.get('std_multiplier', 2) == 2,
                'sufficient_data_points': len(data) >= window * 2
            }
            
        return validation
    
    def _generate_recommendations(self, analysis_type: AnalysisType, score: AnalysisScore, 
                                results: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations for improvement"""
        recommendations = []
        
        if score.methodology_score < 80:
            if analysis_type == AnalysisType.DESCRIPTIVE_STATS:
                recommendations.append("Consider including skewness and kurtosis for distribution analysis")
                recommendations.append("Add confidence intervals for mean estimates")
            elif analysis_type == AnalysisType.CORRELATION:
                recommendations.append("Include significance testing for correlations")
                recommendations.append("Consider non-parametric correlation methods for non-normal data")
            elif analysis_type == AnalysisType.BOLLINGER_BANDS:
                recommendations.append("Use standard 20-period window for better comparability")
                recommendations.append("Consider adding trading volume analysis")
        
        if score.completeness_score < 80:
            recommendations.append("Provide more comprehensive statistical measures")
            recommendations.append("Include data quality assessment in results")
        
        if score.interpretation_score < 80:
            recommendations.append("Add business context and practical interpretation")
            recommendations.append("Explain statistical significance and practical significance")
            recommendations.append("Provide actionable insights based on results")
        
        return recommendations
    
    def _generate_warnings(self, analysis_type: AnalysisType, score: AnalysisScore, 
                          results: Dict[str, Any], data: pd.DataFrame) -> List[str]:
        """Generate warnings about potential issues"""
        warnings = []
        
        # Data quality warnings
        missing_percentage = (data.isnull().sum().sum() / (data.shape[0] * data.shape[1])) * 100
        if missing_percentage > 10:
            warnings.append(f"⚠️ High missing data percentage: {missing_percentage:.1f}%")
        
        if len(data) < 30:
            warnings.append("⚠️ Small sample size may affect statistical reliability")
        
        # Analysis-specific warnings
        if analysis_type == AnalysisType.CORRELATION and len(data.select_dtypes(include=[np.number]).columns) < 2:
            warnings.append("⚠️ Insufficient numeric columns for meaningful correlation analysis")
        
        if analysis_type == AnalysisType.BOLLINGER_BANDS:
            if 'values' in results and len(results['values']) < 50:
                warnings.append("⚠️ Limited data points may reduce Bollinger Bands reliability")
        
        # Score-based warnings
        if score.overall_score < 60:
            warnings.append("⚠️ Low overall analysis quality - consider reviewing methodology")
        
        if score.accuracy_score < 70:
            warnings.append("⚠️ Potential accuracy issues detected in analysis")
        
        return warnings
    
    def generate_analysis_report(self, dataset_id: str) -> Dict[str, Any]:
        """Generate a comprehensive analysis report"""
        matrix = self.get_analysis_matrix(dataset_id)
        if not matrix:
            return {"error": "No analysis history found for this dataset"}
        
        # Calculate detailed metrics
        analysis_by_type = {}
        for record in matrix.analysis_records:
            type_name = record.analysis_type.value
            if type_name not in analysis_by_type:
                analysis_by_type[type_name] = []
            analysis_by_type[type_name].append({
                'timestamp': record.timestamp.isoformat(),
                'score': record.score.overall_score,
                'methodology_score': record.score.methodology_score,
                'completeness_score': record.score.completeness_score,
                'accuracy_score': record.score.accuracy_score,
                'interpretation_score': record.score.interpretation_score
            })
        
        # Quality trends
        quality_over_time = [
            {
                'date': record.timestamp.date().isoformat(),
                'score': record.score.overall_score,
                'type': record.analysis_type.value
            }
            for record in sorted(matrix.analysis_records, key=lambda x: x.timestamp)
        ]
        
        # Coverage analysis
        total_analysis_types = len(AnalysisType)
        covered_types = len([t for t in matrix.coverage_matrix.values() if t])
        coverage_percentage = (covered_types / total_analysis_types) * 100
        
        return {
            'dataset_id': dataset_id,
            'summary': {
                'total_analyses': matrix.total_analyses,
                'overall_quality_score': matrix.overall_quality_score,
                'coverage_percentage': coverage_percentage,
                'average_methodology_score': np.mean([r.score.methodology_score for r in matrix.analysis_records]),
                'average_completeness_score': np.mean([r.score.completeness_score for r in matrix.analysis_records]),
                'average_accuracy_score': np.mean([r.score.accuracy_score for r in matrix.analysis_records]),
                'average_interpretation_score': np.mean([r.score.interpretation_score for r in matrix.analysis_records])
            },
            'analysis_by_type': analysis_by_type,
            'quality_trends': quality_over_time,
            'coverage_matrix': matrix.coverage_matrix,
            'recommendations': matrix.recommendations,
            'recent_analyses': [
                {
                    'id': r.id,
                    'type': r.analysis_type.value,
                    'timestamp': r.timestamp.isoformat(),
                    'query': r.user_query,
                    'score': r.score.overall_score,
                    'warnings': r.warnings
                }
                for r in sorted(matrix.analysis_records, key=lambda x: x.timestamp, reverse=True)[:10]
            ]
        }

# Global instance
analysis_matrix_service = AnalysisMatrixService()
