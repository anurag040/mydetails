from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
import os

class AnalysisType(str, Enum):
    DESCRIPTIVE_STATS = "descriptive_statistics"
    CORRELATION = "correlation_analysis"
    DISTRIBUTION = "distribution_analysis"
    MISSING_DATA = "missing_data_analysis"
    OUTLIER_DETECTION = "outlier_detection"
    TREND_ANALYSIS = "trend_analysis"
    BOLLINGER_BANDS = "bollinger_bands"
    REGRESSION = "regression_analysis"
    CLUSTERING = "clustering_analysis"
    HYPOTHESIS_TEST = "hypothesis_testing"

class AnalysisScore(BaseModel):
    methodology_score: float  # 0-100: How well the method was applied
    completeness_score: float  # 0-100: How complete the analysis is
    accuracy_score: float  # 0-100: Statistical accuracy and validity
    interpretation_score: float  # 0-100: Quality of insights provided
    overall_score: float  # 0-100: Weighted average of above scores

class AnalysisRecord(BaseModel):
    id: str
    dataset_id: str
    analysis_type: AnalysisType
    timestamp: datetime
    user_query: str
    method_used: str
    parameters: Dict[str, Any]
    results: Dict[str, Any]
    code_executed: str
    validation_results: Dict[str, Any]
    score: AnalysisScore
    recommendations: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

class AnalysisMatrix(BaseModel):
    dataset_id: str
    dataset_name: str
    total_analyses: int
    analysis_records: List[AnalysisRecord]
    overall_quality_score: float
    coverage_matrix: Dict[str, bool]  # Which analysis types have been performed
    quality_trends: List[Dict[str, Any]]  # Quality over time
    recommendations: List[str]
    
    def get_analysis_coverage(self) -> Dict[str, float]:
        """Calculate what percentage of recommended analyses have been done"""
        coverage = {}
        for analysis_type in AnalysisType:
            performed = any(record.analysis_type == analysis_type for record in self.analysis_records)
            coverage[analysis_type.value] = 100.0 if performed else 0.0
        return coverage
    
    def get_quality_by_type(self) -> Dict[str, float]:
        """Get average quality score by analysis type"""
        quality_by_type = {}
        for analysis_type in AnalysisType:
            records = [r for r in self.analysis_records if r.analysis_type == analysis_type]
            if records:
                avg_score = sum(r.score.overall_score for r in records) / len(records)
                quality_by_type[analysis_type.value] = avg_score
        return quality_by_type

class AnalysisValidator:
    """Validates and scores different types of statistical analyses"""
    
    @staticmethod
    def validate_descriptive_stats(data, results, parameters) -> AnalysisScore:
        """Validate descriptive statistics analysis"""
        methodology_score = 85.0  # Base score for using standard methods
        completeness_score = 0.0
        accuracy_score = 0.0
        interpretation_score = 0.0
        
        # Check completeness
        required_stats = ['mean', 'median', 'std', 'min', 'max', 'count']
        provided_stats = list(results.keys()) if isinstance(results, dict) else []
        completeness_score = (len(set(required_stats) & set(provided_stats)) / len(required_stats)) * 100
        
        # Check accuracy (basic validation)
        if 'mean' in results and 'median' in results:
            accuracy_score = 90.0  # Assume high accuracy for basic stats
        
        # Check interpretation quality
        if any(key in results for key in ['insights', 'summary', 'interpretation']):
            interpretation_score = 75.0
        else:
            interpretation_score = 40.0
            
        overall_score = (methodology_score * 0.25 + completeness_score * 0.3 + 
                        accuracy_score * 0.3 + interpretation_score * 0.15)
        
        return AnalysisScore(
            methodology_score=methodology_score,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            interpretation_score=interpretation_score,
            overall_score=overall_score
        )
    
    @staticmethod
    def validate_correlation_analysis(data, results, parameters) -> AnalysisScore:
        """Validate correlation analysis"""
        methodology_score = 80.0
        completeness_score = 0.0
        accuracy_score = 0.0
        interpretation_score = 0.0
        
        # Check if correlation matrix was computed
        if 'correlation_matrix' in results or 'correlations' in results:
            completeness_score = 85.0
            accuracy_score = 85.0
        
        # Check for significance testing
        if 'p_values' in results or 'significance' in results:
            methodology_score = 95.0
            accuracy_score = 95.0
        
        # Check interpretation
        if 'strong_correlations' in results or 'insights' in results:
            interpretation_score = 80.0
        else:
            interpretation_score = 50.0
            
        overall_score = (methodology_score * 0.3 + completeness_score * 0.25 + 
                        accuracy_score * 0.3 + interpretation_score * 0.15)
        
        return AnalysisScore(
            methodology_score=methodology_score,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            interpretation_score=interpretation_score,
            overall_score=overall_score
        )
    
    @staticmethod
    def validate_bollinger_bands(data, results, parameters) -> AnalysisScore:
        """Validate Bollinger Bands analysis"""
        methodology_score = 0.0
        completeness_score = 0.0
        accuracy_score = 0.0
        interpretation_score = 0.0
        
        # Check methodology
        window = parameters.get('window', 20)
        if 15 <= window <= 25:  # Standard window range
            methodology_score = 90.0
        elif 10 <= window <= 50:  # Acceptable range
            methodology_score = 75.0
        else:
            methodology_score = 50.0
        
        # Check completeness
        required_components = ['ma', 'upper', 'lower', 'values']
        if all(comp in results for comp in required_components):
            completeness_score = 95.0
        else:
            completeness_score = 60.0
        
        # Check accuracy (validate calculations)
        if 'ma' in results and 'upper' in results and 'lower' in results:
            accuracy_score = 90.0  # Assume correct if all components present
        
        # Check interpretation
        if any(key in results for key in ['signals', 'analysis', 'insights']):
            interpretation_score = 85.0
        else:
            interpretation_score = 60.0  # Chart without interpretation
            
        overall_score = (methodology_score * 0.3 + completeness_score * 0.25 + 
                        accuracy_score * 0.3 + interpretation_score * 0.15)
        
        return AnalysisScore(
            methodology_score=methodology_score,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            interpretation_score=interpretation_score,
            overall_score=overall_score
        )
    
    @classmethod
    def validate_analysis(cls, analysis_type: AnalysisType, data, results, parameters) -> AnalysisScore:
        """Main validation method that routes to specific validators"""
        validators = {
            AnalysisType.DESCRIPTIVE_STATS: cls.validate_descriptive_stats,
            AnalysisType.CORRELATION: cls.validate_correlation_analysis,
            AnalysisType.BOLLINGER_BANDS: cls.validate_bollinger_bands,
        }
        
        validator = validators.get(analysis_type)
        if validator:
            return validator(data, results, parameters)
        else:
            # Default scoring for unimplemented validators
            return AnalysisScore(
                methodology_score=70.0,
                completeness_score=70.0,
                accuracy_score=70.0,
                interpretation_score=70.0,
                overall_score=70.0
            )

class AnalysisLogger:
    """Handles logging and persistence of analysis records"""
    
    def __init__(self, base_path: str = "analysis_logs"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def log_analysis(self, record: AnalysisRecord) -> str:
        """Log an analysis record to file"""
        log_file = os.path.join(self.base_path, f"{record.dataset_id}_analysis_log.jsonl")
        
        # Append to JSONL file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(record.json() + '\n')
        
        return log_file
    
    def get_analysis_matrix(self, dataset_id: str) -> Optional[AnalysisMatrix]:
        """Load and construct analysis matrix for a dataset"""
        log_file = os.path.join(self.base_path, f"{dataset_id}_analysis_log.jsonl")
        
        if not os.path.exists(log_file):
            return None
        
        records = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record_data = json.loads(line)
                    records.append(AnalysisRecord(**record_data))
        
        if not records:
            return None
        
        # Calculate overall quality score
        overall_quality = sum(r.score.overall_score for r in records) / len(records)
        
        # Generate coverage matrix
        coverage_matrix = {}
        for analysis_type in AnalysisType:
            coverage_matrix[analysis_type.value] = any(
                r.analysis_type == analysis_type for r in records
            )
        
        # Generate quality trends
        quality_trends = [
            {
                'timestamp': r.timestamp.isoformat(),
                'analysis_type': r.analysis_type.value,
                'score': r.score.overall_score
            }
            for r in records
        ]
        
        # Generate recommendations
        recommendations = AnalysisLogger._generate_recommendations(records, coverage_matrix)
        
        return AnalysisMatrix(
            dataset_id=dataset_id,
            dataset_name=f"Dataset_{dataset_id}",
            total_analyses=len(records),
            analysis_records=records,
            overall_quality_score=overall_quality,
            coverage_matrix=coverage_matrix,
            quality_trends=quality_trends,
            recommendations=recommendations
        )
    
    @staticmethod
    def _generate_recommendations(records: List[AnalysisRecord], coverage: Dict[str, bool]) -> List[str]:
        """Generate recommendations based on analysis history"""
        recommendations = []
        
        # Check coverage gaps
        missing_analyses = [k for k, v in coverage.items() if not v]
        if AnalysisType.DESCRIPTIVE_STATS.value in missing_analyses:
            recommendations.append("🔍 Perform descriptive statistics analysis for data overview")
        if AnalysisType.MISSING_DATA.value in missing_analyses:
            recommendations.append("⚠️ Check for missing data patterns and quality issues")
        if AnalysisType.CORRELATION.value in missing_analyses:
            recommendations.append("📊 Analyze correlations between variables")
        
        # Check quality issues
        low_quality_analyses = [r for r in records if r.score.overall_score < 70]
        if low_quality_analyses:
            recommendations.append(f"🔧 Review and improve {len(low_quality_analyses)} low-quality analyses")
        
        # Check methodology issues
        methodology_issues = [r for r in records if r.score.methodology_score < 70]
        if methodology_issues:
            recommendations.append("📚 Consider using more robust statistical methods")
        
        return recommendations
