"""
LLM Validation Service - Technical Validation Framework
Implements multi-dimensional assessment using statistical ground truth comparison
and domain-specific evaluation metrics.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any, Tuple
import time
import re
import json
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationMetric:
    """Individual validation metric with normalized score"""
    name: str
    raw_score: float
    normalized_score: float
    weight: float
    details: Dict[str, Any]

@dataclass
class ValidationResult:
    """Complete validation result with all metrics"""
    overall_score: float
    statistical_accuracy: ValidationMetric
    completeness: ValidationMetric
    consistency: ValidationMetric
    efficiency: ValidationMetric
    statistical_tests: Dict[str, Any]
    performance_rating: str
    validation_timestamp: str

class LLMValidationService:
    """
    Technical Validation Framework for LLM Analysis
    
    Mathematical Foundation:
    Overall Score: Σ(normalized_metric_i) / n where n = total metrics, each metric ∈ [0,1]
    Statistical Accuracy: |{correct_claims}| / |{total_claims}| using Pearson correlation analysis
    Completeness: Σ(component_coverage_i) / |components| across 5 analysis domains
    Consistency: 1 - (contradictions_detected / total_contradiction_checks)
    Efficiency: Tier-based scoring using response time quantiles
    """
    
    def __init__(self):
        self.weights = {
            'statistical_accuracy': 0.25,
            'completeness': 0.30,
            'consistency': 0.25,
            'efficiency': 0.20
        }
        
        # Domain coverage thresholds for completeness assessment
        self.analysis_domains = {
            'descriptive_stats': ['mean', 'median', 'std', 'variance', 'quartile', 'distribution'],
            'data_quality': ['missing', 'duplicate', 'outlier', 'integrity', 'validity'],
            'relationships': ['correlation', 'association', 'dependency', 'causation'],
            'visualization': ['chart', 'plot', 'graph', 'visualization', 'trend'],
            'modeling': ['feature', 'prediction', 'classification', 'regression', 'clustering']
        }
        
        # Contradiction term pairs for consistency checking
        self.contradiction_pairs = [
            ('high', 'low'), ('strong', 'weak'), ('significant', 'insignificant'),
            ('positive', 'negative'), ('increase', 'decrease'), ('good', 'poor'),
            ('normal', 'abnormal'), ('balanced', 'imbalanced'), ('stable', 'unstable')
        ]
        
        # Response time quantiles for efficiency scoring
        self.efficiency_tiers = {
            'excellent': (0, 2.0),    # < 2 seconds
            'good': (2.0, 5.0),       # 2-5 seconds
            'acceptable': (5.0, 10.0), # 5-10 seconds
            'poor': (10.0, 1000.0) # > 10 seconds (using large number instead of inf)
        }
    
    @staticmethod
    def safe_float(value, default=0.0):
        """Safely convert value to float, handling NaN and infinity"""
        try:
            result = float(value)
            if np.isnan(result) or np.isinf(result):
                return default
            return result
        except (ValueError, TypeError):
            return default

    def validate_llm_analysis(self, df: pd.DataFrame, llm_response: str, 
                            ground_truth_stats: Dict[str, Any], 
                            response_time: float = None) -> ValidationResult:
        """
        Main validation method implementing the technical framework
        
        Args:
            df: Original dataset
            llm_response: LLM analysis text
            ground_truth_stats: Computed statistical ground truth
            response_time: Response generation time in seconds
        
        Returns:
            ValidationResult with comprehensive metrics
        """
        start_time = time.time()
        
        # Perform statistical tests on dataset
        statistical_tests = self._perform_statistical_tests(df)
        
        # Calculate individual validation metrics
        statistical_accuracy = self._calculate_statistical_accuracy(
            llm_response, ground_truth_stats, df
        )
        
        completeness = self._calculate_completeness(llm_response)
        
        consistency = self._calculate_consistency(llm_response)
        
        efficiency = self._calculate_efficiency(response_time or (time.time() - start_time))
        
        # Calculate overall score using weighted average
        overall_score = (
            statistical_accuracy.normalized_score * self.weights['statistical_accuracy'] +
            completeness.normalized_score * self.weights['completeness'] +
            consistency.normalized_score * self.weights['consistency'] +
            efficiency.normalized_score * self.weights['efficiency']
        )
        
        # Ensure overall score is safe for JSON serialization
        overall_score = self.safe_float(overall_score)
        
        performance_rating = self._get_performance_rating(overall_score)
        
        return ValidationResult(
            overall_score=overall_score,
            statistical_accuracy=statistical_accuracy,
            completeness=completeness,
            consistency=consistency,
            efficiency=efficiency,
            statistical_tests=statistical_tests,
            performance_rating=performance_rating,
            validation_timestamp=datetime.now().isoformat()
        )

    def _perform_statistical_tests(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive statistical tests on dataset
        
        Statistical Tests Applied:
        - Shapiro-Wilk Test: H₀: data follows normal distribution (α = 0.05)
        - Pearson Correlation: r = Σ((xᵢ-x̄)(yᵢ-ȳ)) / √(Σ(xᵢ-x̄)²Σ(yᵢ-ȳ)²)
        - Fisher's Skewness: γ₁ = E[(X-μ)³]/σ³ for distribution asymmetry detection
        - Z-Score Outlier Detection: |z| = |(x-μ)/σ| > 3 threshold
        """
        tests = {}
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) == 0:
            return {"message": "No numeric columns for statistical testing"}
        
        # Shapiro-Wilk normality tests
        normality_tests = {}
        for col in numeric_df.columns:
            data = numeric_df[col].dropna()
            if len(data) >= 3 and len(data) <= 5000:  # Shapiro-Wilk limitations
                try:
                    stat, p_value = stats.shapiro(data)
                    normality_tests[col] = {
                        'statistic': self.safe_float(stat),
                        'p_value': self.safe_float(p_value),
                        'is_normal': p_value > 0.05,
                        'alpha': 0.05
                    }
                except Exception as e:
                    normality_tests[col] = {'error': str(e)}
        
        tests['shapiro_wilk'] = normality_tests
        
        # Pearson correlation matrix
        if len(numeric_df.columns) >= 2:
            correlation_matrix = numeric_df.corr(method='pearson')
            tests['pearson_correlation'] = {
                'matrix': correlation_matrix.to_dict(),
                'strong_correlations': self._find_strong_correlations(correlation_matrix)
            }
        
        # Fisher's skewness for each numeric column
        skewness_tests = {}
        for col in numeric_df.columns:
            data = numeric_df[col].dropna()
            if len(data) > 0:
                skewness = stats.skew(data)  # Default skewness calculation
                skewness_tests[col] = {
                    'skewness': self.safe_float(skewness),
                    'interpretation': self._interpret_skewness(skewness)
                }
        
        tests['fishers_skewness'] = skewness_tests
        
        # Z-Score outlier detection
        outlier_tests = {}
        for col in numeric_df.columns:
            data = numeric_df[col].dropna()
            if len(data) > 0:
                z_scores = np.abs(stats.zscore(data))
                outliers = np.sum(z_scores > 3)
                outlier_tests[col] = {
                    'total_outliers': int(outliers),
                    'outlier_percentage': self.safe_float(outliers / len(data) * 100),
                    'threshold': 3.0
                }
        
        tests['zscore_outliers'] = outlier_tests
        
        return tests

    def _calculate_statistical_accuracy(self, llm_response: str, ground_truth: Dict[str, Any], 
                                      df: pd.DataFrame) -> ValidationMetric:
        """
        Calculate statistical accuracy using tolerance-based matching
        Statistical Accuracy: |{correct_claims}| / |{total_claims}|
        """
        total_claims = 0
        correct_claims = 0
        details = {}
        
        # Extract numerical claims from LLM response
        numerical_claims = self._extract_numerical_claims(llm_response)
        
        # Validate against ground truth statistics
        for claim_type, claimed_values in numerical_claims.items():
            if claim_type in ground_truth:
                total_claims += len(claimed_values)
                for claimed_val in claimed_values:
                    actual_val = ground_truth[claim_type]
                    if self._is_numerically_close(claimed_val, actual_val):
                        correct_claims += 1
        
        # Validate correlation claims
        correlation_accuracy = self._validate_correlation_claims(llm_response, df)
        total_claims += correlation_accuracy['total']
        correct_claims += correlation_accuracy['correct']
        
        # Calculate accuracy score
        accuracy_score = correct_claims / total_claims if total_claims > 0 else 1.0
        
        details = {
            'total_claims': total_claims,
            'correct_claims': correct_claims,
            'numerical_accuracy': accuracy_score,
            'correlation_validation': correlation_accuracy
        }
        
        return ValidationMetric(
            name='Statistical Accuracy',
            raw_score=self.safe_float(accuracy_score),
            normalized_score=self.safe_float(min(accuracy_score, 1.0)),
            weight=self.weights['statistical_accuracy'],
            details=details
        )

    def _calculate_completeness(self, llm_response: str) -> ValidationMetric:
        """
        Calculate completeness across 5 analysis domains
        Completeness: Σ(component_coverage_i) / |components|
        """
        domain_scores = {}
        response_lower = llm_response.lower()
        
        for domain, keywords in self.analysis_domains.items():
            mentions = sum(1 for keyword in keywords if keyword in response_lower)
            threshold = len(keywords) * 0.3  # 30% coverage threshold
            coverage_score = min(mentions / threshold, 1.0) if threshold > 0 else 0
            domain_scores[domain] = {
                'mentions': mentions,
                'total_keywords': len(keywords),
                'coverage_score': coverage_score,
                'threshold': threshold
            }
        
        # Calculate overall completeness
        total_coverage = sum(domain['coverage_score'] for domain in domain_scores.values())
        completeness_score = total_coverage / len(self.analysis_domains)
        
        return ValidationMetric(
            name='Completeness',
            raw_score=self.safe_float(completeness_score),
            normalized_score=self.safe_float(min(completeness_score, 1.0)),
            weight=self.weights['completeness'],
            details={
                'domain_scores': domain_scores,
                'overall_coverage': completeness_score
            }
        )

    def _calculate_consistency(self, llm_response: str) -> ValidationMetric:
        """
        Calculate consistency by detecting logical contradictions
        Consistency: 1 - (contradictions_detected / total_contradiction_checks)
        """
        contradictions_detected = 0
        total_checks = 0
        response_lower = llm_response.lower()
        contradiction_details = []
        
        for term1, term2 in self.contradiction_pairs:
            if term1 in response_lower and term2 in response_lower:
                total_checks += 1
                # Simple proximity check - if contradictory terms appear close together
                term1_positions = [m.start() for m in re.finditer(term1, response_lower)]
                term2_positions = [m.start() for m in re.finditer(term2, response_lower)]
                
                for pos1 in term1_positions:
                    for pos2 in term2_positions:
                        if abs(pos1 - pos2) < 100:  # Within 100 characters
                            contradictions_detected += 1
                            contradiction_details.append({
                                'term1': term1,
                                'term2': term2,
                                'proximity': abs(pos1 - pos2)
                            })
                            break
        
        # Calculate consistency score
        consistency_score = 1 - (contradictions_detected / total_checks) if total_checks > 0 else 1.0
        
        return ValidationMetric(
            name='Consistency',
            raw_score=self.safe_float(consistency_score),
            normalized_score=self.safe_float(max(consistency_score, 0.0)),
            weight=self.weights['consistency'],
            details={
                'contradictions_detected': contradictions_detected,
                'total_checks': total_checks,
                'contradiction_details': contradiction_details
            }
        )

    def _calculate_efficiency(self, response_time: float) -> ValidationMetric:
        """
        Calculate efficiency using tier-based response time evaluation
        """
        tier_scores = {
            'excellent': 1.0,
            'good': 0.8,
            'acceptable': 0.6,
            'poor': 0.3
        }
        
        efficiency_tier = 'poor'
        for tier, (min_time, max_time) in self.efficiency_tiers.items():
            if min_time <= response_time < max_time:
                efficiency_tier = tier
                break
        
        efficiency_score = tier_scores[efficiency_tier]
        
        return ValidationMetric(
            name='Efficiency',
            raw_score=self.safe_float(efficiency_score),
            normalized_score=self.safe_float(efficiency_score),
            weight=self.weights['efficiency'],
            details={
                'response_time': self.safe_float(response_time),
                'efficiency_tier': efficiency_tier,
                'tier_boundaries': self.efficiency_tiers
            }
        )

    def _extract_numerical_claims(self, text: str) -> Dict[str, List[float]]:
        """Extract numerical claims from LLM response"""
        # Pattern to match numbers (including decimals and percentages)
        number_pattern = r'\b\d+\.?\d*%?\b'
        numbers = re.findall(number_pattern, text)
        
        # Categorize by context
        claims = {
            'percentages': [self.safe_float(n.strip('%')) for n in numbers if '%' in n],
            'decimals': [self.safe_float(n) for n in numbers if '.' in n and '%' not in n],
            'integers': [self.safe_float(n) for n in numbers if '.' not in n and '%' not in n]
        }
        
        return claims

    def _is_numerically_close(self, claimed: float, actual: float, tolerance: float = 0.1) -> bool:
        """Check if claimed value is close to actual value within tolerance"""
        if actual == 0:
            return abs(claimed) <= tolerance
        return abs((claimed - actual) / actual) <= tolerance

    def _validate_correlation_claims(self, llm_response: str, df: pd.DataFrame) -> Dict[str, int]:
        """Validate correlation claims against actual correlations"""
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) < 2:
            return {'total': 0, 'correct': 0}
        
        correlation_matrix = numeric_df.corr()
        
        # Extract correlation claims (simplified)
        strong_corr_mentions = len(re.findall(r'strong.{0,20}correlation', llm_response.lower()))
        weak_corr_mentions = len(re.findall(r'weak.{0,20}correlation', llm_response.lower()))
        
        # Count actual strong correlations
        strong_correlations = np.sum(np.abs(correlation_matrix.values) > 0.7) - len(correlation_matrix)
        
        total_claims = strong_corr_mentions + weak_corr_mentions
        correct_claims = 0
        
        # Simplified validation logic
        if strong_corr_mentions > 0 and strong_correlations > 0:
            correct_claims += strong_corr_mentions
        if weak_corr_mentions > 0 and strong_correlations == 0:
            correct_claims += weak_corr_mentions
        
        return {'total': total_claims, 'correct': correct_claims}

    def _find_strong_correlations(self, corr_matrix: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find strong correlations (|r| >= 0.7)"""
        strong_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) >= 0.7:
                    strong_corrs.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': self.safe_float(corr_val),
                        'strength': 'strong'
                    })
        return strong_corrs

    def _interpret_skewness(self, skewness: float) -> str:
        """Interpret Fisher's skewness value"""
        if abs(skewness) < 0.5:
            return 'approximately symmetric'
        elif skewness > 0.5:
            return 'positively skewed (right tail)'
        else:
            return 'negatively skewed (left tail)'

    def _get_performance_rating(self, overall_score: float) -> str:
        """Get performance rating based on overall score"""
        if overall_score >= 0.95:
            return 'Excellent - Academic Grade'
        elif overall_score >= 0.85:
            return 'Very Good - Professional Standard'
        elif overall_score >= 0.75:
            return 'Good - Reliable Analysis'
        elif overall_score >= 0.65:
            return 'Acceptable - Minor Issues'
        else:
            return 'Needs Improvement - Review Required'

def convert_validation_result_to_dict(result: ValidationResult) -> Dict[str, Any]:
    """Convert ValidationResult to dictionary for JSON serialization"""
    return {
        'overall_score': result.overall_score,
        'statistical_accuracy': {
            'name': result.statistical_accuracy.name,
            'raw_score': result.statistical_accuracy.raw_score,
            'normalized_score': result.statistical_accuracy.normalized_score,
            'weight': result.statistical_accuracy.weight,
            'details': result.statistical_accuracy.details
        },
        'completeness': {
            'name': result.completeness.name,
            'raw_score': result.completeness.raw_score,
            'normalized_score': result.completeness.normalized_score,
            'weight': result.completeness.weight,
            'details': result.completeness.details
        },
        'consistency': {
            'name': result.consistency.name,
            'raw_score': result.consistency.raw_score,
            'normalized_score': result.consistency.normalized_score,
            'weight': result.consistency.weight,
            'details': result.consistency.details
        },
        'efficiency': {
            'name': result.efficiency.name,
            'raw_score': result.efficiency.raw_score,
            'normalized_score': result.efficiency.normalized_score,
            'weight': result.efficiency.weight,
            'details': result.efficiency.details
        },
        'statistical_tests': result.statistical_tests,
        'performance_rating': result.performance_rating,
        'validation_timestamp': result.validation_timestamp
    }
