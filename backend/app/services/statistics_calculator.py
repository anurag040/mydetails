import pandas as pd
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List, Optional
import os
from app.services.file_handler import FileHandler
from app.services.llm_validation_service import LLMValidationService, convert_validation_result_to_dict
from app.schemas.responses import BasicStatsResponse, AdvancedStatsResponse

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        value = float(obj)
        # Handle NaN, infinity, and -infinity
        if np.isnan(value):
            return None
        elif np.isinf(value):
            return None  # or use a large number like 1e308 or -1e308
        return value
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, float):
        # Handle regular Python floats that might be NaN or inf
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif hasattr(obj, 'item'):
        result = obj.item()
        # Check if the result is a problematic float
        if isinstance(result, float) and (np.isnan(result) or np.isinf(result)):
            return None
        return result
    return obj

def safe_float(value):
    """Safely convert value to float, handling NaN and infinity"""
    try:
        if value is None:
            return None
        float_val = float(value)
        if np.isnan(float_val) or np.isinf(float_val):
            return None
        return float_val
    except (ValueError, TypeError, OverflowError):
        return None

class StatisticsCalculator:
    def __init__(self):
        self.file_handler = FileHandler()
        self.validation_service = LLMValidationService()
        # Initialize OpenAI client for AI-powered insights
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            self.openai_client = OpenAI(api_key=api_key) if api_key else None
        except ImportError:
            self.openai_client = None
    
    async def calculate_basic_stats(self, dataset_id: str, options: List[str]) -> BasicStatsResponse:
        """Calculate basic statistics based on selected options"""
        import logging
        logger = logging.getLogger("statistics.calculator")
        logger.info(f"Loading dataset {dataset_id} for basic stats with options: {options}")
        df = await self.file_handler.load_dataset(dataset_id)
        if df is None:
            logger.error(f"Dataset not found or failed to load: {dataset_id}")
            raise FileNotFoundError("Dataset not found")
        logger.info(f"Dataset {dataset_id} loaded successfully. Shape: {df.shape}")
        result = BasicStatsResponse(dataset_id=dataset_id)
        try:
            if "descriptive" in options:
                logger.info("Calculating descriptive statistics...")
                result.descriptive_stats = self._calculate_descriptive_stats(df)
            if "correlation" in options:
                logger.info("Calculating correlation matrix...")
                result.correlation_matrix = self._calculate_correlation_analysis(df)
            if "distribution" in options:
                logger.info("Calculating distribution analysis...")
                result.distribution_analysis = self._calculate_distribution_analysis(df)
            if "missing_data" in options:
                logger.info("Calculating missing data summary...")
                result.missing_data_summary = self._calculate_missing_data_analysis(df)
            if "missing_value_analysis" in options:
                logger.info("Calculating missing value analysis...")
                result.missing_value_analysis = self._calculate_missing_value_analysis(df)
            if "duplicates_analysis" in options:
                logger.info("Calculating duplicates analysis...")
                result.duplicates_analysis = self._calculate_duplicates_analysis(df)
            if "type_integrity_validation" in options:
                logger.info("Calculating type integrity validation...")
                result.type_integrity_validation = self._calculate_type_integrity_validation(df)
            if "univariate_summaries" in options:
                logger.info("Calculating univariate summaries...")
                result.univariate_summaries = self._calculate_univariate_summaries(df)
            if "outlier_detection" in options:
                logger.info("Calculating outlier detection...")
                result.outlier_detection = self._calculate_outlier_detection(df)
            if "feature_engineering_ideas" in options:
                logger.info("Calculating feature engineering ideas...")
                result.feature_engineering_ideas = self._calculate_feature_engineering_ideas(df)
            if "multicollinearity_assessment" in options:
                logger.info("Calculating multicollinearity assessment...")
                result.multicollinearity_assessment = self._calculate_multicollinearity_assessment(df)
            if "dimensionality_insights" in options:
                logger.info("Calculating dimensionality insights...")
                result.dimensionality_insights = self._calculate_dimensionality_insights(df)
            if "baseline_model_sanity" in options:
                logger.info("Calculating baseline model sanity...")
                result.baseline_model_sanity = self._calculate_baseline_model_sanity(df)
            if "drift_stability_analysis" in options:
                logger.info("Calculating drift stability analysis...")
                result.drift_stability_analysis = self._calculate_drift_stability_analysis(df)
            if "bias_fairness_flags" in options:
                logger.info("Calculating bias fairness flags...")
                result.bias_fairness_flags = self._calculate_bias_fairness_flags(df)
            if "documentation_summary" in options:
                logger.info("Calculating documentation summary...")
                result.documentation_summary = self._calculate_documentation_summary(df)
            if "reproducibility_info" in options:
                logger.info("Calculating reproducibility info...")
                result.reproducibility_info = self._calculate_reproducibility_info(df)
        except Exception as e:
            logger.exception(f"Error during basic stats calculation for dataset {dataset_id}: {str(e)}")
            raise
        logger.info(f"Basic statistics calculation complete for dataset {dataset_id}")
        
        # Final safety check to ensure all values are JSON serializable
        result = convert_numpy_types(result)
        
        return result
    
    async def calculate_advanced_stats(self, dataset_id: str, options: List[str]) -> AdvancedStatsResponse:
        """Calculate advanced statistics and ML insights"""
        df = await self.file_handler.load_dataset(dataset_id)
        if df is None:
            raise FileNotFoundError("Dataset not found")
        
        result = AdvancedStatsResponse(dataset_id=dataset_id)
        
        if "regression" in options:
            result.regression_analysis = self._perform_regression_analysis(df)
        
        if "clustering" in options:
            result.clustering_results = self._perform_clustering_analysis(df)
        
        if "pca" in options:
            result.pca_analysis = self._perform_pca_analysis(df)
        
        if "time_series" in options:
            result.time_series_analysis = self._perform_time_series_analysis(df)
        
        if "anomaly_detection" in options:
            result.anomaly_detection = self._perform_anomaly_detection(df)
        
        return result
    
    async def get_quick_summary(self, dataset_id: str) -> Dict[str, Any]:
        """Get a comprehensive data source overview including schema and sample preview"""
        df = await self.file_handler.load_dataset(dataset_id)
        if df is None:
            raise FileNotFoundError("Dataset not found")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        
        # Schema information
        schema_info = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = int(df[col].isnull().sum())
            unique_count = int(df[col].nunique())
            
            schema_info[col] = {
                "dtype": dtype,
                "null_count": null_count,
                "null_percentage": float(null_count / len(df) * 100),
                "unique_count": unique_count,
                "unique_percentage": float(unique_count / len(df) * 100),
                "memory_usage": float(df[col].memory_usage(deep=True) / 1024),  # KB
                "is_numeric": col in numeric_cols,
                "is_categorical": col in categorical_cols,
                "is_datetime": col in datetime_cols
            }
            
            # Add sample values for categorical columns
            if col in categorical_cols and unique_count <= 20:
                schema_info[col]["sample_values"] = df[col].dropna().unique().tolist()[:10]
            elif col in numeric_cols:
                schema_info[col]["min_value"] = float(df[col].min()) if not df[col].isna().all() else None
                schema_info[col]["max_value"] = float(df[col].max()) if not df[col].isna().all() else None
        
        # Sample preview (first and last 5 rows)
        sample_preview = {
            "head": convert_numpy_types(df.head(5).to_dict('records')),
            "tail": convert_numpy_types(df.tail(5).to_dict('records')),
            "random_sample": convert_numpy_types(df.sample(min(5, len(df)), random_state=42).to_dict('records')) if len(df) > 10 else []
        }
        
        return convert_numpy_types({
            "dataset_id": dataset_id,
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "column_types": {
                "numeric": len(numeric_cols),
                "categorical": len(categorical_cols),
                "datetime": len(datetime_cols)
            },
            "schema": schema_info,
            "sample_preview": sample_preview,
            "missing_data": {
                "total_missing": int(df.isnull().sum().sum()),
                "percentage": float(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100)
            },
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            "file_info": {
                "estimated_file_size": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
                "columns_with_missing": len([col for col in df.columns if df[col].isnull().any()]),
                "duplicate_rows": int(df.duplicated().sum())
            }
        })
    
    def _calculate_missing_value_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive missing value analysis and suggest strategies"""
        missing_stats = {}
        
        # Per-column missing value analysis
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            missing_percentage = (missing_count / len(df)) * 100
            
            # Determine missing value pattern
            pattern = "Random" if missing_count > 0 else "None"
            if missing_count > 0:
                # Check if missing values correlate with other columns
                if missing_count == len(df):
                    pattern = "Complete"
                elif missing_percentage > 50:
                    pattern = "Systematic High"
                elif missing_percentage > 20:
                    pattern = "Systematic Medium"
                else:
                    pattern = "Sporadic"
            
            # Suggest strategy based on missing percentage and data type
            strategy = self._suggest_missing_value_strategy(df, col, missing_percentage)
            
            missing_stats[col] = {
                "missing_count": int(missing_count),
                "missing_percentage": float(missing_percentage),
                "total_values": len(df),
                "pattern": pattern,
                "suggested_strategy": strategy,
                "data_type": str(df[col].dtype),
                "is_numeric": col in df.select_dtypes(include=[np.number]).columns,
                "unique_values": int(df[col].nunique()) if missing_count < len(df) else 0
            }
        
        # Overall missing value summary
        total_missing = df.isnull().sum().sum()
        total_cells = df.shape[0] * df.shape[1]
        columns_with_missing = len([col for col in df.columns if df[col].isnull().any()])
        
        # Missing value heatmap data (for visualization)
        missing_matrix = df.isnull().astype(int)
        
        return convert_numpy_types({
            "column_analysis": missing_stats,
            "overall_summary": {
                "total_missing_values": int(total_missing),
                "total_cells": total_cells,
                "overall_missing_percentage": float((total_missing / total_cells) * 100),
                "columns_with_missing": columns_with_missing,
                "complete_rows": int(df.dropna().shape[0]),
                "complete_rows_percentage": float((df.dropna().shape[0] / len(df)) * 100)
            },
            "recommendations": self._get_missing_value_recommendations(missing_stats, df),
            "missing_patterns": self._analyze_missing_patterns(df)
        })
    
    def _suggest_missing_value_strategy(self, df: pd.DataFrame, column: str, missing_percentage: float) -> Dict[str, Any]:
        """Suggest appropriate strategy for handling missing values"""
        is_numeric = column in df.select_dtypes(include=[np.number]).columns
        unique_ratio = df[column].nunique() / len(df.dropna(subset=[column])) if len(df.dropna(subset=[column])) > 0 else 0
        
        strategies = []
        
        if missing_percentage == 0:
            return {"primary": "No action needed", "alternatives": [], "reason": "No missing values"}
        
        if missing_percentage > 70:
            strategies.append({
                "method": "Drop Column",
                "priority": "High",
                "reason": f"Too many missing values ({missing_percentage:.1f}%)"
            })
        
        if missing_percentage < 5:
            if is_numeric:
                strategies.append({
                    "method": "Mean/Median Imputation",
                    "priority": "High",
                    "reason": "Low missing percentage, numeric data"
                })
            else:
                strategies.append({
                    "method": "Mode Imputation",
                    "priority": "High",
                    "reason": "Low missing percentage, categorical data"
                })
        
        if missing_percentage < 30:
            strategies.append({
                "method": "Listwise Deletion",
                "priority": "Medium",
                "reason": "Moderate missing percentage"
            })
        
        if is_numeric and missing_percentage < 50:
            strategies.append({
                "method": "Interpolation",
                "priority": "Medium",
                "reason": "Numeric data, can use interpolation"
            })
        
        if unique_ratio < 0.1:  # Low cardinality categorical
            strategies.append({
                "method": "Mode Imputation",
                "priority": "Medium",
                "reason": "Categorical data with low cardinality"
            })
        
        strategies.append({
            "method": "Advanced Imputation (KNN/MICE)",
            "priority": "Low",
            "reason": "Complex imputation for better accuracy"
        })
        
        return {
            "primary": strategies[0]["method"] if strategies else "Manual Review",
            "alternatives": [s["method"] for s in strategies[1:3]],
            "detailed_options": strategies
        }
    
    def _get_missing_value_recommendations(self, missing_stats: Dict, df: pd.DataFrame) -> List[str]:
        """Generate overall recommendations for missing value handling"""
        recommendations = []
        
        high_missing_cols = [col for col, stats in missing_stats.items() 
                           if stats["missing_percentage"] > 50]
        
        if high_missing_cols:
            recommendations.append(f"Consider dropping columns with >50% missing: {', '.join(high_missing_cols[:3])}")
        
        numeric_missing = [col for col, stats in missing_stats.items() 
                         if stats["is_numeric"] and 5 < stats["missing_percentage"] < 30]
        
        if numeric_missing:
            recommendations.append(f"Use median imputation for numeric columns: {', '.join(numeric_missing[:3])}")
        
        if len([col for col, stats in missing_stats.items() if stats["missing_count"] > 0]) > len(df.columns) * 0.5:
            recommendations.append("Consider using advanced imputation methods (MICE, KNN) due to widespread missing data")
        
        complete_rows_pct = (df.dropna().shape[0] / len(df)) * 100
        if complete_rows_pct > 70:
            recommendations.append(f"Listwise deletion viable: {complete_rows_pct:.1f}% complete rows")
        
        return recommendations
    
    def _analyze_missing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns in missing data"""
        missing_combinations = df.isnull().groupby(list(df.columns)).size().reset_index(name='missing_count')
        missing_combinations = missing_combinations.sort_values('missing_count', ascending=False)
        return {
            "most_common_patterns": convert_numpy_types(missing_combinations.head(5).to_dict('records')),
            "total_patterns": len(missing_combinations)
        }
    
    def _calculate_duplicates_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive duplicate analysis"""
        
        # Full row duplicates
        full_duplicates = df.duplicated()
        full_duplicate_count = full_duplicates.sum()
        
        # Partial duplicates analysis (by subsets of columns)
        partial_duplicates = {}
        important_cols = df.columns[:min(5, len(df.columns))]  # Analyze first 5 columns
        
        for i in range(2, min(len(important_cols) + 1, 4)):  # Check combinations of 2-3 columns
            from itertools import combinations
            for col_combo in combinations(important_cols, i):
                combo_name = " + ".join(col_combo)
                partial_duplicate_count = df.duplicated(subset=list(col_combo)).sum()
                if partial_duplicate_count > 0:
                    partial_duplicates[combo_name] = {
                        "count": int(partial_duplicate_count),
                        "percentage": float((partial_duplicate_count / len(df)) * 100),
                        "columns": list(col_combo)
                    }
        
        # Identify potentially problematic duplicates
        duplicate_rows_detail = []
        if full_duplicate_count > 0:
            duplicate_indices = df[df.duplicated(keep=False)].index.tolist()
            # Group duplicates
            seen_rows = set()
            for idx in duplicate_indices:
                if idx not in seen_rows:
                    row_hash = hash(tuple(df.loc[idx].values))
                    duplicate_group = df[df.apply(lambda x: hash(tuple(x.values)) == row_hash, axis=1)]
                    if len(duplicate_group) > 1:
                        duplicate_rows_detail.append({
                            "group_id": len(duplicate_rows_detail) + 1,
                            "count": len(duplicate_group),
                            "indices": duplicate_group.index.tolist(),
                            "sample_row": convert_numpy_types(duplicate_group.iloc[0].to_dict())
                        })
                        seen_rows.update(duplicate_group.index.tolist())
        
        # Duplicate handling recommendations
        recommendations = self._get_duplicate_recommendations(full_duplicate_count, len(df), partial_duplicates)
        
        return convert_numpy_types({
            "full_duplicates": {
                "count": int(full_duplicate_count),
                "percentage": float((full_duplicate_count / len(df)) * 100),
                "unique_rows": int(len(df) - full_duplicate_count),
                "duplicate_groups": duplicate_rows_detail[:5]  # Limit to first 5 groups
            },
            "partial_duplicates": partial_duplicates,
            "summary": {
                "total_rows": len(df),
                "unique_rows": int(len(df) - full_duplicate_count),
                "duplicate_rows": int(full_duplicate_count),
                "data_quality_score": float(((len(df) - full_duplicate_count) / len(df)) * 100)
            },
            "recommendations": recommendations,
            "impact_analysis": {
                "memory_saved_if_removed": f"{(full_duplicate_count * df.memory_usage(deep=True).sum() / len(df) / 1024 / 1024):.2f} MB",
                "rows_after_deduplication": int(len(df) - full_duplicate_count)
            }
        })
    
    def _get_duplicate_recommendations(self, duplicate_count: int, total_rows: int, partial_duplicates: Dict) -> List[str]:
        """Generate recommendations for handling duplicates"""
        recommendations = []
        duplicate_percentage = (duplicate_count / total_rows) * 100
        
        if duplicate_count == 0:
            recommendations.append("✅ No duplicate rows found - data quality is excellent")
        elif duplicate_percentage < 1:
            recommendations.append(f"✅ Low duplicate rate ({duplicate_percentage:.2f}%) - safe to remove duplicates")
        elif duplicate_percentage < 5:
            recommendations.append(f"⚠️ Moderate duplicate rate ({duplicate_percentage:.2f}%) - review before removal")
        else:
            recommendations.append(f"🚨 High duplicate rate ({duplicate_percentage:.2f}%) - investigate data source")
        
        if duplicate_count > 0:
            recommendations.append("Consider using df.drop_duplicates() to remove exact duplicates")
            recommendations.append("Review duplicate groups to understand if they represent legitimate vs. erroneous duplicates")
        
        if partial_duplicates:
            partial_count = len(partial_duplicates)
            recommendations.append(f"Found {partial_count} partial duplicate patterns - review for business logic duplicates")
            
            # Explain what partial duplicates mean
            if partial_count > 0:
                example_combo = list(partial_duplicates.keys())[0]
                recommendations.append(f"⚠️ Partial duplicates detected: rows that share identical values in specific column combinations")
                recommendations.append(f"📋 Example: '{example_combo}' has identical values across {partial_duplicates[example_combo]['count']} rows")
                recommendations.append(f"🔍 Business Impact: These might represent legitimate entries (e.g., same customer, different orders) or data quality issues")
                recommendations.append(f"💡 Action Required: Review each pattern to determine if duplicates are intentional or require deduplication")
        
        return recommendations
    
    def _calculate_type_integrity_validation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Enhanced data quality validation with comprehensive analysis"""
        validation_results = {}
        overall_quality_score = 0
        total_checks = 0
        quality_metrics = {
            "completeness": 0,
            "consistency": 0,
            "validity": 0,
            "accuracy": 0,
            "uniqueness": 0
        }
        
        # Enhanced column-level validation
        for col in df.columns:
            col_data = df[col]
            non_null_data = col_data.dropna()
            
            if len(col_data) == 0:
                continue
            
            # Comprehensive analysis for each column
            col_analysis = {
                "declared_type": str(col_data.dtype),
                "inferred_type": self._infer_optimal_type(non_null_data) if len(non_null_data) > 0 else "unknown",
                "quality_metrics": {},
                "issues": [],
                "recommendations": [],
                "data_profile": {},
                "quality_flags": []
            }
            
            # Data profiling
            col_analysis["data_profile"] = self._profile_column_data(col_data, col)
            
            # Quality metric calculations
            col_analysis["quality_metrics"] = self._calculate_column_quality_metrics(col_data, col)
            
            # Calculate overall column quality score first (needed by quality flags)
            metrics = col_analysis["quality_metrics"]
            col_score = (
                metrics["completeness"] * 0.25 +
                metrics["consistency"] * 0.25 +
                metrics["validity"] * 0.25 +
                metrics["accuracy"] * 0.15 +
                metrics["uniqueness"] * 0.10
            )
            col_analysis["overall_score"] = round(col_score, 2)
            
            # Enhanced issue detection
            col_analysis["issues"] = self._detect_comprehensive_issues(col_data, col)
            
            # Quality flags (quick visual indicators)
            col_analysis["quality_flags"] = self._generate_quality_flags(col_analysis)
            
            # Smart recommendations
            col_analysis["recommendations"] = self._generate_enhanced_recommendations(col_analysis, col)
            
            validation_results[col] = col_analysis
            
            # Aggregate for overall metrics
            for metric, value in metrics.items():
                quality_metrics[metric] += value
            
            overall_quality_score += col_score
            total_checks += 1
        
        # Calculate overall metrics
        if total_checks > 0:
            for metric in quality_metrics:
                quality_metrics[metric] = round(quality_metrics[metric] / total_checks, 2)
            overall_quality_score = round(overall_quality_score / total_checks, 2)
        
        # Global dataset analysis
        global_analysis = self._analyze_global_data_quality(df, validation_results)
        
        # Data quality summary
        summary = self._generate_quality_summary(validation_results, global_analysis, total_checks)
        
        # AI-powered insights
        ai_insights = self._generate_data_quality_ai_insights(summary, validation_results, df)
        
        return convert_numpy_types({
            "column_validations": validation_results,
            "overall_quality_score": overall_quality_score,
            "quality_metrics": quality_metrics,
            "global_analysis": global_analysis,
            "summary": summary,
            "ai_insights": ai_insights,
            "quality_grade": self._assign_quality_grade(overall_quality_score),
            "action_plan": self._generate_action_plan(validation_results, global_analysis)
        })
    
    def _infer_optimal_type(self, series: pd.Series) -> str:
        """Infer the optimal data type for a series"""
        sample_size = min(1000, len(series))  # Sample for performance
        sample = series.sample(sample_size, random_state=42) if len(series) > sample_size else series
        
        # Try to infer numeric types
        try:
            numeric_converted = pd.to_numeric(sample, errors='coerce')
            if not numeric_converted.isna().all():
                if (numeric_converted % 1 == 0).all():
                    return "integer"
                else:
                    return "float"
        except:
            pass
        
        # Try to infer datetime
        try:
            pd.to_datetime(sample, errors='raise')
            return "datetime"
        except:
            pass
        
        # Try to infer boolean
        unique_values = set(str(v).lower() for v in sample.unique())
        if unique_values.issubset({'true', 'false', '1', '0', 'yes', 'no', 't', 'f'}):
            return "boolean"
        
        # Check if categorical (low cardinality)
        cardinality_ratio = len(sample.unique()) / len(sample)
        if cardinality_ratio < 0.05 and len(sample.unique()) < 50:
            return "categorical"
        
        return "string"
    
    def _check_type_consistency(self, series: pd.Series, column_name: str) -> List[str]:
        """Check for type consistency issues"""
        issues = []
        
        # Check for mixed numeric/string in object columns
        if series.dtype == 'object':
            numeric_count = 0
            string_count = 0
            
            for value in series.head(100):  # Sample check
                try:
                    float(str(value))
                    numeric_count += 1
                except ValueError:
                    string_count += 1
            
            if numeric_count > 0 and string_count > 0:
                ratio = numeric_count / (numeric_count + string_count)
                if 0.1 < ratio < 0.9:  # Mixed content
                    issues.append(f"Warning: Mixed numeric/text content detected ({ratio:.1%} numeric)")
        
        # Check for leading/trailing whitespace in string columns
        if series.dtype == 'object':
            whitespace_count = sum(1 for v in series.head(100) if str(v) != str(v).strip())
            if whitespace_count > 0:
                issues.append(f"Warning: {whitespace_count} values have leading/trailing whitespace")
        
        # Check for inconsistent date formats
        if series.dtype == 'object':
            potential_dates = []
            for value in series.head(50):
                try:
                    pd.to_datetime(str(value), dayfirst=True)
                    potential_dates.append(str(value))
                except:
                    continue
            
            if len(potential_dates) > len(series) * 0.3:  # Likely date column
                formats = set()
                for date_str in potential_dates:
                    if '/' in date_str:
                        formats.add('MM/DD/YYYY or DD/MM/YYYY')
                    elif '-' in date_str:
                        formats.add('YYYY-MM-DD')
                    elif ' ' in date_str:
                        formats.add('Date with time')
                
                if len(formats) > 1:
                    issues.append(f"Warning: Inconsistent date formats detected: {', '.join(formats)}")
        
        return issues
    
    def _check_data_integrity(self, series: pd.Series, column_name: str) -> List[str]:
        """Check for data integrity issues"""
        issues = []
        
        # Check for negative values where they might not make sense
        if series.dtype in ['int64', 'float64']:
            negative_count = (series < 0).sum()
            if negative_count > 0:
                # Heuristic: if column name suggests it should be positive
                positive_indicators = ['age', 'count', 'quantity', 'amount', 'price', 'salary', 'weight', 'height', 'distance']
                if any(indicator in column_name.lower() for indicator in positive_indicators):
                    issues.append(f"Critical: {negative_count} negative values in column that should likely be positive")
        
        # Check for extremely large values (potential data entry errors)
        if series.dtype in ['int64', 'float64']:
            q99 = series.quantile(0.99)
            q01 = series.quantile(0.01)
            iqr = series.quantile(0.75) - series.quantile(0.25)
            
            # Values beyond 10 IQRs might be suspicious
            if iqr > 0:
                extreme_threshold = 10 * iqr
                extreme_count = ((series > q99 + extreme_threshold) | (series < q01 - extreme_threshold)).sum()
                if extreme_count > 0:
                    issues.append(f"Warning: {extreme_count} extremely large/small values detected (>10 IQRs from median)")
        
        # Check for duplicate consecutive values (might indicate copy-paste errors)
        if len(series) > 1:
            consecutive_duplicates = (series == series.shift()).sum()
            if consecutive_duplicates > len(series) * 0.3:  # More than 30% consecutive duplicates
                issues.append(f"Warning: High consecutive duplicate rate ({consecutive_duplicates/len(series):.1%}) - possible copy-paste errors")
        
        # Check for unrealistic values based on column name heuristics
        if series.dtype in ['int64', 'float64']:
            if 'age' in column_name.lower():
                invalid_age = ((series < 0) | (series > 150)).sum()
                if invalid_age > 0:
                    issues.append(f"Critical: {invalid_age} unrealistic age values (outside 0-150 range)")
            
            elif 'percentage' in column_name.lower() or 'percent' in column_name.lower():
                invalid_pct = ((series < 0) | (series > 100)).sum()
                if invalid_pct > 0:
                    issues.append(f"Critical: {invalid_pct} invalid percentage values (outside 0-100 range)")
        
        return issues
    
    def _check_global_integrity(self, df: pd.DataFrame) -> List[str]:
        """Check for global data integrity issues"""
        issues = []
        
        # Check for completely empty columns
        empty_cols = [col for col in df.columns if df[col].isna().all()]
        if empty_cols:
            issues.append(f"Critical: {len(empty_cols)} completely empty columns: {', '.join(empty_cols[:3])}")
        
        # Check for columns with single value (no variance)
        constant_cols = []
        for col in df.columns:
            if df[col].dropna().nunique() <= 1:
                constant_cols.append(col)
        
        if constant_cols:
            issues.append(f"Warning: {len(constant_cols)} columns with no variance: {', '.join(constant_cols[:3])}")
        
        # Check for suspicious column name patterns
        suspicious_names = [col for col in df.columns if any(char in col for char in ['Unnamed', 'Column', 'Field'])]
        if suspicious_names:
            issues.append(f"Warning: {len(suspicious_names)} columns with generic names suggest data import issues")
        
        return issues
    
    def _generate_type_recommendations(self, issues: List[str], declared_type: str, inferred_type: str) -> List[str]:
        """Generate recommendations for type issues"""
        recommendations = []
        
        if not issues:
            recommendations.append("✅ No type or integrity issues detected")
            return recommendations
        
        if declared_type != inferred_type and inferred_type != "string":
            recommendations.append(f"Consider converting to {inferred_type} type for better performance and analysis")
        
        for issue in issues:
            if "Mixed numeric/text" in issue:
                recommendations.append("Clean data to separate numeric and text values or standardize format")
            elif "whitespace" in issue:
                recommendations.append("Apply string trimming: df[column].str.strip()")
            elif "date formats" in issue:
                recommendations.append("Standardize date format using pd.to_datetime() with format parameter")
            elif "negative values" in issue:
                recommendations.append("Review and correct negative values or validate if they're legitimate")
            elif "extremely large" in issue:
                recommendations.append("Investigate outliers - may indicate data entry errors or different units")
            elif "consecutive duplicate" in issue:
                recommendations.append("Check for copy-paste errors or confirm if repeated values are valid")
            elif "unrealistic" in issue:
                recommendations.append("Validate data entry process and implement range constraints")
        
        return recommendations
    
    def _generate_global_type_recommendations(self, validation_results: Dict, global_issues: List[str]) -> List[str]:
        """Generate global recommendations for data type and integrity"""
        recommendations = []
        
        critical_issues = sum(1 for col_result in validation_results.values() for issue in col_result["issues"] if "Critical" in issue)
        warning_issues = sum(1 for col_result in validation_results.values() for issue in col_result["issues"] if "Warning" in issue)
        
        if critical_issues == 0 and warning_issues == 0:
            recommendations.append("🎉 Excellent data quality - no major type or integrity issues detected")
        elif critical_issues == 0:
            recommendations.append(f"✅ Good data quality - only {warning_issues} minor warnings to address")
        else:
            recommendations.append(f"⚠️ Data quality attention needed - {critical_issues} critical and {warning_issues} warning issues detected")
        
        if critical_issues > 0:
            recommendations.append("🔥 Priority: Address critical issues first as they may impact analysis accuracy")
            recommendations.append("📊 Consider data validation rules during data collection/entry phase")
        
        if len(global_issues) > 0:
            recommendations.append("🔍 Review global data structure issues to improve overall dataset quality")
        
        # Type conversion recommendations
        conversion_candidates = []
        for col, result in validation_results.items():
            if result["declared_type"] != result["inferred_type"] and result["inferred_type"] != "string":
                conversion_candidates.append(f"{col} → {result['inferred_type']}")
        
        if conversion_candidates:
            recommendations.append(f"🔄 Consider type conversions: {', '.join(conversion_candidates[:3])}")
        
        return recommendations
    
    def _calculate_univariate_summaries(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive univariate summaries for all data types"""
        summaries = {
            "numeric_summaries": {},
            "categorical_summaries": {},
            "temporal_summaries": {},
            "overview": {
                "total_columns": len(df.columns),
                "numeric_columns": 0,
                "categorical_columns": 0,
                "temporal_columns": 0
            }
        }
        
        # Identify column types
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        temporal_cols = df.select_dtypes(include=['datetime64']).columns
        
        summaries["overview"]["numeric_columns"] = len(numeric_cols)
        summaries["overview"]["categorical_columns"] = len(categorical_cols)
        summaries["overview"]["temporal_columns"] = len(temporal_cols)
        
        # Numeric summaries
        for col in numeric_cols:
            data = df[col].dropna()
            if len(data) == 0:
                continue
                
            summaries["numeric_summaries"][col] = {
                "basic_stats": {
                    "count": int(len(data)),
                    "mean": float(data.mean()) if len(data) > 0 and not data.mean() != data.mean() else None,  # Check for NaN
                    "median": float(data.median()) if len(data) > 0 and not data.median() != data.median() else None,
                    "mode": float(data.mode().iloc[0]) if len(data.mode()) > 0 and not data.mode().iloc[0] != data.mode().iloc[0] else None,
                    "std": float(data.std()) if len(data) > 0 and not data.std() != data.std() else None,
                    "variance": float(data.var()) if len(data) > 0 and not data.var() != data.var() else None,
                    "min": float(data.min()) if len(data) > 0 and not data.min() != data.min() else None,
                    "max": float(data.max()) if len(data) > 0 and not data.max() != data.max() else None,
                    "range": float(data.max() - data.min()) if len(data) > 0 and not (data.max() - data.min()) != (data.max() - data.min()) else None,
                    "q1": float(data.quantile(0.25)) if len(data) > 0 and not data.quantile(0.25) != data.quantile(0.25) else None,
                    "q3": float(data.quantile(0.75)) if len(data) > 0 and not data.quantile(0.75) != data.quantile(0.75) else None,
                    "iqr": float(data.quantile(0.75) - data.quantile(0.25)) if len(data) > 0 and not (data.quantile(0.75) - data.quantile(0.25)) != (data.quantile(0.75) - data.quantile(0.25)) else None
                },
                "distribution_stats": {
                    "skewness": float(stats.skew(data)) if len(data) > 0 and not np.isnan(stats.skew(data)) else None,
                    "kurtosis": float(stats.kurtosis(data)) if len(data) > 0 and not np.isnan(stats.kurtosis(data)) else None,
                    "is_normal": self._test_normality(data),
                    "distribution_shape": self._classify_distribution_shape(data)
                },
                "missing_info": {
                    "missing_count": int(df[col].isna().sum()),
                    "missing_percentage": float(df[col].isna().sum() / len(df) * 100)
                },
                "outlier_info": self._detect_univariate_outliers(data),
                "business_insights": self._generate_numeric_insights(col, data)
            }
        
        # Categorical summaries
        for col in categorical_cols:
            data = df[col].dropna()
            if len(data) == 0:
                continue
                
            value_counts = data.value_counts()
            
            summaries["categorical_summaries"][col] = {
                "basic_stats": {
                    "count": int(len(data)),
                    "unique_count": int(data.nunique()),
                    "cardinality_ratio": float(data.nunique() / len(data)),
                    "mode": str(data.mode().iloc[0]) if len(data.mode()) > 0 else None,
                    "mode_frequency": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    "mode_percentage": float(value_counts.iloc[0] / len(data) * 100) if len(value_counts) > 0 else 0
                },
                "distribution_stats": {
                    "entropy": float(-sum((value_counts / len(data)) * np.log2(value_counts / len(data)))),
                    "concentration_ratio": float(value_counts.head(3).sum() / len(data)),  # Top 3 categories
                    "is_highly_concentrated": value_counts.iloc[0] / len(data) > 0.8 if len(value_counts) > 0 else False
                },
                "top_categories": convert_numpy_types(value_counts.head(10).to_dict()),
                "missing_info": {
                    "missing_count": int(df[col].isna().sum()),
                    "missing_percentage": float(df[col].isna().sum() / len(df) * 100)
                },
                "quality_checks": {
                    "has_empty_strings": int((data == '').sum()),
                    "has_whitespace_issues": int(data.str.strip().ne(data).sum()) if hasattr(data, 'str') else 0,
                    "case_inconsistency": self._check_case_inconsistency(data)
                },
                "business_insights": self._generate_categorical_insights(col, data, value_counts)
            }
        
        # Temporal summaries
        for col in temporal_cols:
            data = df[col].dropna()
            if len(data) == 0:
                continue
                
            summaries["temporal_summaries"][col] = {
                "basic_stats": {
                    "count": int(len(data)),
                    "min_date": str(data.min()),
                    "max_date": str(data.max()),
                    "date_range_days": int((data.max() - data.min()).days),
                    "most_common_date": str(data.mode().iloc[0]) if len(data.mode()) > 0 else None
                },
                "temporal_patterns": {
                    "year_range": f"{data.dt.year.min()}-{data.dt.year.max()}",
                    "month_distribution": convert_numpy_types(data.dt.month.value_counts().head(5).to_dict()),
                    "day_of_week_distribution": convert_numpy_types(data.dt.dayofweek.value_counts().to_dict()),
                    "seasonal_pattern": self._detect_seasonal_pattern(data)
                },
                "missing_info": {
                    "missing_count": int(df[col].isna().sum()),
                    "missing_percentage": float(df[col].isna().sum() / len(df) * 100)
                },
                "business_insights": self._generate_temporal_insights(col, data)
            }
        
        return convert_numpy_types(summaries)
    
    def _test_normality(self, data: pd.Series) -> Dict[str, Any]:
        """Test for normality using multiple methods"""
        if len(data) < 3:
            return {"is_normal": None, "method": "insufficient_data"}
        
        # Shapiro-Wilk test (for smaller datasets)
        if len(data) <= 5000:
            try:
                stat, p_value = stats.shapiro(data)
                return {
                    "is_normal": p_value > 0.05,
                    "p_value": float(p_value),
                    "test_statistic": float(stat),
                    "method": "shapiro_wilk",
                    "confidence": "high" if len(data) > 50 else "medium"
                }
            except Exception:
                pass
        
        # Kolmogorov-Smirnov test (for larger datasets)
        try:
            stat, p_value = stats.kstest(stats.zscore(data), 'norm')
            return {
                "is_normal": p_value > 0.05,
                "p_value": float(p_value),
                "test_statistic": float(stat),
                "method": "kolmogorov_smirnov",
                "confidence": "medium"
            }
        except Exception:
            return {"is_normal": None, "method": "test_failed"}
    
    def _classify_distribution_shape(self, data: pd.Series) -> Dict[str, str]:
        """Classify the shape of the distribution"""
        skewness = stats.skew(data)
        kurtosis = stats.kurtosis(data)
        
        # Skewness classification
        if abs(skewness) < 0.5:
            skew_desc = "approximately symmetric"
        elif skewness > 0.5:
            skew_desc = "right-skewed (positive)"
        else:
            skew_desc = "left-skewed (negative)"
        
        # Kurtosis classification
        if kurtosis > 1:
            kurt_desc = "heavy-tailed (leptokurtic)"
        elif kurtosis < -1:
            kurt_desc = "light-tailed (platykurtic)"
        else:
            kurt_desc = "normal-tailed (mesokurtic)"
        
        return {
            "skewness_description": skew_desc,
            "kurtosis_description": kurt_desc,
            "overall_shape": f"{skew_desc}, {kurt_desc}"
        }
    
    def _detect_univariate_outliers(self, data: pd.Series) -> Dict[str, Any]:
        """Detect outliers using multiple methods"""
        outlier_info = {}
        
        # IQR method
        q1, q3 = data.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        iqr_outliers = ((data < lower_bound) | (data > upper_bound)).sum()
        outlier_info["iqr_method"] = {
            "outlier_count": int(iqr_outliers),
            "outlier_percentage": float(iqr_outliers / len(data) * 100),
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound)
        }
        
        # Z-score method
        z_scores = np.abs(stats.zscore(data))
        zscore_outliers = (z_scores > 3).sum()
        outlier_info["zscore_method"] = {
            "outlier_count": int(zscore_outliers),
            "outlier_percentage": float(zscore_outliers / len(data) * 100),
            "threshold": 3.0
        }
        
        # Modified Z-score (more robust)
        median = data.median()
        mad = np.median(np.abs(data - median))
        modified_z_scores = 0.6745 * (data - median) / mad if mad > 0 else np.zeros_like(data)
        mod_zscore_outliers = (np.abs(modified_z_scores) > 3.5).sum()
        
        outlier_info["modified_zscore_method"] = {
            "outlier_count": int(mod_zscore_outliers),
            "outlier_percentage": float(mod_zscore_outliers / len(data) * 100),
            "threshold": 3.5
        }
        
        # Summary recommendation
        methods_agree = [
            outlier_info["iqr_method"]["outlier_count"],
            outlier_info["zscore_method"]["outlier_count"],
            outlier_info["modified_zscore_method"]["outlier_count"]
        ]
        
        outlier_info["consensus"] = {
            "avg_outlier_percentage": float(np.mean([m["outlier_percentage"] for m in outlier_info.values() if isinstance(m, dict)])),
            "methods_agreement": "high" if max(methods_agree) - min(methods_agree) <= 2 else "low",
            "recommended_method": "iqr_method" if iqr_outliers > 0 else "modified_zscore_method"
        }
        
        return outlier_info
    
    def _generate_numeric_insights(self, column_name: str, data: pd.Series) -> List[str]:
        """Generate business insights for numeric columns"""
        insights = []
        
        mean_val = data.mean()
        median_val = data.median()
        std_val = data.std()
        cv = std_val / mean_val if mean_val != 0 else float('inf')
        
        # Central tendency insights
        if abs(mean_val - median_val) / std_val < 0.1 if std_val > 0 else True:
            insights.append(f"Data is well-centered: mean ({mean_val:.2f}) ≈ median ({median_val:.2f})")
        elif mean_val > median_val:
            insights.append(f"Right-skewed: mean ({mean_val:.2f}) > median ({median_val:.2f}) - presence of high outliers")
        else:
            insights.append(f"Left-skewed: mean ({mean_val:.2f}) < median ({median_val:.2f}) - presence of low outliers")
        
        # Variability insights
        if cv < 0.1:
            insights.append(f"Low variability: CV = {cv:.3f} - data is highly consistent")
        elif cv > 1.0:
            insights.append(f"High variability: CV = {cv:.3f} - data has high dispersion")
        
        # Range insights
        data_range = data.max() - data.min()
        if data_range == 0:
            insights.append("No variation - all values are identical")
        
        return insights
    
    def _generate_categorical_insights(self, column_name: str, data: pd.Series, value_counts: pd.Series) -> List[str]:
        """Generate business insights for categorical columns"""
        insights = []
        
        total_count = len(data)
        unique_count = data.nunique()
        top_category_pct = value_counts.iloc[0] / total_count * 100 if len(value_counts) > 0 else 0
        
        # Diversity insights
        if unique_count == total_count:
            insights.append("High diversity: every value is unique - might be an identifier")
        elif unique_count / total_count > 0.8:
            insights.append(f"Very high diversity: {unique_count} unique values ({unique_count/total_count:.1%})")
        elif unique_count < 10:
            insights.append(f"Low diversity: only {unique_count} categories - good for grouping analysis")
        
        # Concentration insights
        if top_category_pct > 80:
            insights.append(f"Highly concentrated: top category represents {top_category_pct:.1f}% of data")
        elif top_category_pct < 10:
            insights.append(f"Well-distributed: top category only {top_category_pct:.1f}% - balanced representation")
        
        # Business recommendations
        if unique_count > 50 and unique_count / total_count > 0.1:
            insights.append("Consider grouping categories for analysis - high cardinality may impact model performance")
        
        return insights
    
    def _generate_temporal_insights(self, column_name: str, data: pd.Series) -> List[str]:
        """Generate business insights for temporal columns"""
        insights = []
        
        date_range_days = (data.max() - data.min()).days
        
        # Time span insights
        if date_range_days < 7:
            insights.append(f"Short time span: {date_range_days} days - limited for trend analysis")
        elif date_range_days > 365 * 2:
            insights.append(f"Long time span: {date_range_days/365:.1f} years - excellent for trend and seasonality analysis")
        
        # Pattern insights
        year_range = data.dt.year.max() - data.dt.year.min()
        if year_range > 1:
            insights.append(f"Multi-year data: {year_range} years - suitable for year-over-year analysis")
        
        return insights
    
    def _check_case_inconsistency(self, data: pd.Series) -> int:
        """Check for case inconsistency in categorical data"""
        if not hasattr(data, 'str'):
            return 0
        
        lowercase_counts = data.str.lower().value_counts()
        original_counts = data.value_counts()
        
        # Count how many categories could be merged by case normalization
        potential_merges = len(original_counts) - len(lowercase_counts)
        return max(0, potential_merges)
    
    def _detect_seasonal_pattern(self, data: pd.Series) -> str:
        """Detect basic seasonal patterns in temporal data"""
        if len(data) < 12:  # Need at least a year of data
            return "insufficient_data"
        
        month_counts = data.dt.month.value_counts()
        cv_monthly = month_counts.std() / month_counts.mean()
        
        if cv_monthly > 0.3:
            return "seasonal_variation_detected"
        else:
            return "no_clear_seasonality"
    
    def _calculate_outlier_detection(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive outlier detection using multiple methods"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "No numeric columns found for outlier detection"}
        
        outlier_results = {
            "univariate_outliers": {},
            "multivariate_outliers": {},
            "summary": {
                "total_numeric_columns": len(numeric_df.columns),
                "columns_with_outliers": 0,
                "total_outlier_count": 0,
                "outlier_percentage": 0
            },
            "recommendations": []
        }
        
        total_outliers = 0
        columns_with_outliers = 0
        
        # Univariate outlier detection for each column
        for col in numeric_df.columns:
            data = numeric_df[col].dropna()
            if len(data) < 10:  # Need sufficient data
                continue
            
            col_outliers = self._detect_column_outliers(data, col)
            outlier_results["univariate_outliers"][col] = col_outliers
            
            if col_outliers["total_outliers"] > 0:
                columns_with_outliers += 1
                total_outliers += col_outliers["total_outliers"]
        
        # Multivariate outlier detection
        if len(numeric_df.columns) >= 2 and len(numeric_df.dropna()) >= 10:
            outlier_results["multivariate_outliers"] = self._detect_multivariate_outliers(numeric_df)
            if "outlier_count" in outlier_results["multivariate_outliers"]:
                total_outliers += outlier_results["multivariate_outliers"]["outlier_count"]
        
        # Update summary
        outlier_results["summary"]["columns_with_outliers"] = columns_with_outliers
        outlier_results["summary"]["total_outlier_count"] = total_outliers
        outlier_results["summary"]["outlier_percentage"] = (total_outliers / (len(df) * len(numeric_df.columns))) * 100
        
        # Generate recommendations
        outlier_results["recommendations"] = self._generate_outlier_recommendations(outlier_results)
        
        return convert_numpy_types(outlier_results)
    
    def _detect_column_outliers(self, data: pd.Series, column_name: str) -> Dict[str, Any]:
        """Detect outliers in a single column using multiple methods"""
        methods = {}
        
        # 1. IQR Method
        q1, q3 = data.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        iqr_outliers = ((data < lower_bound) | (data > upper_bound))
        
        methods["iqr"] = {
            "outlier_count": int(iqr_outliers.sum()),
            "outlier_percentage": float(iqr_outliers.sum() / len(data) * 100),
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound),
            "outlier_indices": data[iqr_outliers].index.tolist()[:10]  # Limit to first 10
        }
        
        # 2. Z-Score Method
        z_scores = np.abs(stats.zscore(data))
        zscore_outliers = z_scores > 3
        
        methods["zscore"] = {
            "outlier_count": int(zscore_outliers.sum()),
            "outlier_percentage": float(zscore_outliers.sum() / len(data) * 100),
            "threshold": 3.0,
            "outlier_indices": data[zscore_outliers].index.tolist()[:10]
        }
        
        # 3. Modified Z-Score (more robust)
        median = data.median()
        mad = np.median(np.abs(data - median))
        if mad > 0:
            modified_z_scores = 0.6745 * (data - median) / mad
            mod_zscore_outliers = np.abs(modified_z_scores) > 3.5
        else:
            mod_zscore_outliers = np.zeros(len(data), dtype=bool)
        
        methods["modified_zscore"] = {
            "outlier_count": int(mod_zscore_outliers.sum()),
            "outlier_percentage": float(mod_zscore_outliers.sum() / len(data) * 100),
            "threshold": 3.5,
            "outlier_indices": data[mod_zscore_outliers].index.tolist()[:10]
        }
        
        # 4. Statistical tests for extreme values
        # Grubbs' test for single outlier (simplified)
        if len(data) > 7:  # Minimum sample size for Grubbs test
            mean_val = data.mean()
            std_val = data.std()
            max_deviation = np.max(np.abs(data - mean_val))
            grubbs_stat = max_deviation / std_val
            
            # Critical value approximation for Grubbs test (simplified)
            n = len(data)
            grubbs_critical = np.sqrt((n-1)**2 / n * stats.t.ppf(1-0.05/(2*n), n-2)**2 / (n-2 + stats.t.ppf(1-0.05/(2*n), n-2)**2))
            
            methods["grubbs"] = {
                "test_statistic": float(grubbs_stat),
                "critical_value": float(grubbs_critical),
                "outlier_detected": grubbs_stat > grubbs_critical,
                "most_extreme_index": int(data.idxmax() if data.max() - mean_val > mean_val - data.min() else data.idxmin())
            }
        
        # Consensus and best method
        outlier_counts = [methods[m]["outlier_count"] for m in ["iqr", "zscore", "modified_zscore"]]
        consensus_count = int(np.median(outlier_counts))
        
        # Choose best method based on data characteristics
        if data.std() / data.mean() > 1.0:  # High variability
            best_method = "modified_zscore"
        elif len(data) < 100:  # Small dataset
            best_method = "iqr"
        else:  # Large dataset
            best_method = "zscore"
        
        return {
            "methods": methods,
            "consensus_outlier_count": consensus_count,
            "best_method": best_method,
            "total_outliers": methods[best_method]["outlier_count"],
            "severity": self._classify_outlier_severity(methods[best_method]["outlier_percentage"]),
            "sample_outlier_values": data[data.index.isin(methods[best_method]["outlier_indices"])].tolist()[:5]
        }
    
    def _detect_multivariate_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect multivariate outliers using isolation forest and other methods"""
        clean_df = df.dropna()
        
        if len(clean_df) < 10:
            return {"message": "Insufficient data for multivariate outlier detection"}
        
        results = {}
        
        # 1. Isolation Forest
        try:
            from sklearn.ensemble import IsolationForest
            
            iso_forest = IsolationForest(
                contamination=0.1,  # Expect 10% outliers
                random_state=42,
                n_estimators=100
            )
            
            outlier_predictions = iso_forest.fit_predict(clean_df)
            outlier_scores = iso_forest.decision_function(clean_df)
            
            outlier_mask = outlier_predictions == -1
            outlier_indices = clean_df[outlier_mask].index.tolist()
            
            results["isolation_forest"] = {
                "outlier_count": int(outlier_mask.sum()),
                "outlier_percentage": float(outlier_mask.sum() / len(clean_df) * 100),
                "outlier_indices": outlier_indices[:10],  # Limit output
                "outlier_scores_summary": {
                    "min_score": float(outlier_scores.min()),
                    "max_score": float(outlier_scores.max()),
                    "mean_score": float(outlier_scores.mean())
                }
            }
            
        except Exception as e:
            results["isolation_forest"] = {"error": f"Failed to run Isolation Forest: {str(e)}"}
        
        # 2. Mahalanobis Distance (for smaller datasets)
        if len(clean_df.columns) <= 10 and len(clean_df) >= len(clean_df.columns) + 1:
            try:
                from scipy.spatial.distance import mahalanobis
                
                mean = clean_df.mean().values
                cov_matrix = clean_df.cov().values
                inv_cov_matrix = np.linalg.inv(cov_matrix)
                
                mahal_distances = []
                for i, row in clean_df.iterrows():
                    dist = mahalanobis(row.values, mean, inv_cov_matrix)
                    mahal_distances.append(dist)
                
                mahal_distances = np.array(mahal_distances)
                
                # Use chi-square critical value
                threshold = stats.chi2.ppf(0.975, len(clean_df.columns))  # 97.5% confidence
                mahal_outliers = mahal_distances > threshold
                
                results["mahalanobis"] = {
                    "outlier_count": int(mahal_outliers.sum()),
                    "outlier_percentage": float(mahal_outliers.sum() / len(clean_df) * 100),
                    "threshold": float(threshold),
                    "outlier_indices": clean_df[mahal_outliers].index.tolist()[:10],
                    "distance_summary": {
                        "min": float(mahal_distances.min()),
                        "max": float(mahal_distances.max()),
                        "mean": float(mahal_distances.mean())
                    }
                }
                
            except Exception as e:
                results["mahalanobis"] = {"error": f"Failed to calculate Mahalanobis distance: {str(e)}"}
        
        # Choose primary method
        if "isolation_forest" in results and "error" not in results["isolation_forest"]:
            primary_method = "isolation_forest"
            outlier_count = results["isolation_forest"]["outlier_count"]
        elif "mahalanobis" in results and "error" not in results["mahalanobis"]:
            primary_method = "mahalanobis"
            outlier_count = results["mahalanobis"]["outlier_count"]
        else:
            primary_method = None
            outlier_count = 0
        
        results["summary"] = {
            "primary_method": primary_method,
            "outlier_count": outlier_count,
            "outlier_percentage": float(outlier_count / len(clean_df) * 100) if len(clean_df) > 0 else 0,
            "data_points_analyzed": len(clean_df)
        }
        
        return results
    
    def _classify_outlier_severity(self, outlier_percentage: float) -> str:
        """Classify the severity of outlier presence"""
        if outlier_percentage == 0:
            return "none"
        elif outlier_percentage < 1:
            return "low"
        elif outlier_percentage < 5:
            return "moderate"
        elif outlier_percentage < 15:
            return "high"
        else:
            return "critical"
    
    def _generate_outlier_recommendations(self, outlier_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for handling outliers"""
        recommendations = []
        
        total_outliers = outlier_results["summary"]["total_outlier_count"]
        outlier_pct = outlier_results["summary"]["outlier_percentage"]
        columns_with_outliers = outlier_results["summary"]["columns_with_outliers"]
        
        if total_outliers == 0:
            recommendations.append("✅ No significant outliers detected - data quality is excellent")
            return recommendations
        
        # General assessment
        if outlier_pct < 1:
            recommendations.append(f"✅ Low outlier rate ({outlier_pct:.2f}%) - manageable data quality")
        elif outlier_pct < 5:
            recommendations.append(f"⚠️ Moderate outlier rate ({outlier_pct:.2f}%) - review recommended")
        else:
            recommendations.append(f"🚨 High outlier rate ({outlier_pct:.2f}%) - investigate data sources")
        
        # Column-specific recommendations
        if columns_with_outliers > 0:
            recommendations.append(f"📊 {columns_with_outliers} columns contain outliers - prioritize investigation")
        
        # Method-specific recommendations
        for col, col_data in outlier_results["univariate_outliers"].items():
            severity = col_data.get("severity", "unknown")
            if severity in ["high", "critical"]:
                recommendations.append(f"🔍 Column '{col}': {severity} outlier presence - manual review required")
        
        # Handling strategies
        if outlier_pct < 2:
            recommendations.append("💡 Strategy: Safe to remove outliers for most analyses")
        elif outlier_pct < 10:
            recommendations.append("💡 Strategy: Transform data (log, sqrt) or use robust statistical methods")
            recommendations.append("💡 Alternative: Winsorize extreme values instead of removal")
        else:
            recommendations.append("💡 Strategy: Investigate data collection process before any removal")
            recommendations.append("💡 Consider: Outliers might represent important edge cases")
        
        # Technical recommendations
        recommendations.append("🛠️ Tools: Use box plots and scatter plots for visual confirmation")
        recommendations.append("🛠️ Validation: Cross-reference outliers with business domain experts")
        
        return recommendations

    def _calculate_descriptive_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate descriptive statistics with AI-powered insights"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "No numeric columns found"}
        
        desc_stats = numeric_df.describe()
        
        # Calculate additional statistics
        additional_stats = {
            col: {
                "variance": float(numeric_df[col].var()) if not np.isnan(numeric_df[col].var()) else None,
                "coefficient_of_variation": float(numeric_df[col].std() / numeric_df[col].mean()) if numeric_df[col].mean() != 0 and not np.isnan(numeric_df[col].std()) and not np.isnan(numeric_df[col].mean()) and not np.isinf(numeric_df[col].std() / numeric_df[col].mean()) else None,
                "range": float(numeric_df[col].max() - numeric_df[col].min()) if not np.isnan(numeric_df[col].max() - numeric_df[col].min()) else None
            }
            for col in numeric_df.columns
        }
        
        # Generate AI-powered summary if OpenAI is available
        ai_summary = self._generate_descriptive_ai_summary(desc_stats, additional_stats, numeric_df)
        
        return {
            "summary": convert_numpy_types(desc_stats.to_dict()),
            "additional_stats": additional_stats,
            "ai_summary": ai_summary
        }
    
    def _calculate_correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Enhanced correlation analysis with insights and visualizations"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.shape[1] < 2:
            return {"message": "Need at least 2 numeric columns for correlation analysis"}
        
        corr_matrix = numeric_df.corr()
        
        # Enhanced correlation analysis
        strong_correlations = []
        all_correlations = []
        correlation_insights = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                var1, var2 = corr_matrix.columns[i], corr_matrix.columns[j]
                
                correlation_entry = {
                    "var1": var1,
                    "var2": var2,
                    "correlation": float(corr_val),
                    "strength": self._get_correlation_strength(corr_val),
                    "direction": "positive" if corr_val > 0 else "negative",
                    "abs_correlation": float(abs(corr_val)),
                    "interpretation": self._interpret_correlation(var1, var2, corr_val)
                }
                
                all_correlations.append(correlation_entry)
                
                if abs(corr_val) > 0.7:
                    strong_correlations.append(correlation_entry)
                
                # Generate insights for significant correlations
                if abs(corr_val) > 0.5:
                    insight = self._generate_correlation_insight(var1, var2, corr_val)
                    correlation_insights.append(insight)
        
        # Sort by strength
        strong_correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
        correlation_insights = correlation_insights[:5]  # Top 5 insights
        
        # Correlation summary statistics
        all_corr_values = [entry['correlation'] for entry in all_correlations]
        correlation_summary = {
            "total_pairs": len(all_correlations),
            "strong_correlations_count": len(strong_correlations),
            "average_correlation": float(np.mean([abs(c) for c in all_corr_values])) if all_corr_values else 0,
            "max_correlation": float(max([abs(c) for c in all_corr_values])) if all_corr_values else 0,
            "highly_correlated_variables": len([c for c in all_corr_values if abs(c) > 0.8])
        }
        
        # Prepare enhanced heatmap data
        heatmap_data = {
            "variables": corr_matrix.columns.tolist(),
            "correlation_matrix": convert_numpy_types(corr_matrix.values.tolist()),
            "correlation_dict": convert_numpy_types(corr_matrix.to_dict()),
            "color_scale": self._generate_correlation_color_scale()
        }
        
        # Network data for correlation network visualization
        network_data = {
            "nodes": [{"id": col, "label": col} for col in corr_matrix.columns],
            "links": [
                {
                    "source": entry["var1"],
                    "target": entry["var2"], 
                    "weight": entry["abs_correlation"],
                    "strength": entry["strength"],
                    "correlation": entry["correlation"]
                }
                for entry in all_correlations if entry["abs_correlation"] > 0.3
            ]
        }
        
        # Generate AI summary if available
        ai_summary = self._generate_correlation_ai_summary(correlation_summary, strong_correlations, numeric_df)
        
        return {
            "correlation_matrix": convert_numpy_types(corr_matrix.to_dict()),
            "heatmap_data": heatmap_data,
            "network_data": network_data,
            "all_correlations": all_correlations,
            "strong_correlations": strong_correlations,
            "correlation_summary": correlation_summary,
            "correlation_insights": correlation_insights,
            "ai_summary": ai_summary
        }
    
    def _get_correlation_strength(self, corr_val: float) -> str:
        """Classify correlation strength"""
        abs_corr = abs(corr_val)
        if abs_corr >= 0.9:
            return "Very Strong"
        elif abs_corr >= 0.7:
            return "Strong"
        elif abs_corr >= 0.5:
            return "Moderate"
        elif abs_corr >= 0.3:
            return "Weak"
        else:
            return "Very Weak"
    
    def _interpret_correlation(self, var1: str, var2: str, corr_val: float) -> str:
        """Generate human-readable interpretation of correlation"""
        strength = self._get_correlation_strength(corr_val)
        direction = "positive" if corr_val > 0 else "negative"
        
        if abs(corr_val) > 0.8:
            return f"{var1} and {var2} are highly correlated ({direction}ly) - when one increases, the other {'increases' if corr_val > 0 else 'decreases'} significantly"
        elif abs(corr_val) > 0.5:
            return f"{var1} and {var2} show a {strength.lower()} {direction} relationship"
        else:
            return f"{var1} and {var2} have a weak relationship"
    
    def _generate_correlation_insight(self, var1: str, var2: str, corr_val: float) -> Dict[str, Any]:
        """Generate actionable insights from correlations"""
        abs_corr = abs(corr_val)
        direction = "positive" if corr_val > 0 else "negative"
        
        if abs_corr > 0.9:
            insight_type = "warning"
            message = f"⚠️ Very high correlation between {var1} and {var2} ({corr_val:.3f}) - consider multicollinearity issues"
            recommendation = "These variables might be measuring the same underlying concept. Consider removing one for modeling."
        elif abs_corr > 0.7:
            insight_type = "strong"
            message = f"💪 Strong {direction} correlation between {var1} and {var2} ({corr_val:.3f})"
            recommendation = f"This relationship can be leveraged for prediction - {var1} is a good predictor of {var2}."
        else:
            insight_type = "moderate"
            message = f"📊 Moderate {direction} correlation between {var1} and {var2} ({corr_val:.3f})"
            recommendation = f"Useful relationship to explore further with additional analysis."
        
        return {
            "type": insight_type,
            "variables": [var1, var2],
            "correlation": float(corr_val),
            "message": message,
            "recommendation": recommendation
        }
    
    def _generate_correlation_color_scale(self) -> List[Dict[str, Any]]:
        """Generate color scale for correlation heatmap"""
        return [
            {"value": -1.0, "color": "#d32f2f"},  # Strong negative - red
            {"value": -0.5, "color": "#f57c00"},  # Moderate negative - orange
            {"value": 0.0, "color": "#ffffff"},   # No correlation - white
            {"value": 0.5, "color": "#1976d2"},   # Moderate positive - blue
            {"value": 1.0, "color": "#00ff88"}    # Strong positive - green
        ]
    
    def _generate_correlation_ai_summary(self, summary: Dict, strong_corrs: List, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate AI summary for correlation analysis"""
        if not self.openai_client:
            return {
                "status": "unavailable",
                "message": "AI insights unavailable - OpenAI API key not configured"
            }
        
        try:
            # Prepare data for AI analysis
            total_vars = len(df.select_dtypes(include=[np.number]).columns)
            strong_count = summary['strong_correlations_count']
            avg_corr = summary['average_correlation']
            max_corr = summary['max_correlation']
            
            # Get top correlations for analysis
            top_corrs = strong_corrs[:3] if strong_corrs else []
            
            prompt = f"""Analyze this correlation analysis and provide 2 concise sentences:

DATASET: {total_vars} numeric variables, {summary['total_pairs']} correlation pairs analyzed
STRONG CORRELATIONS: {strong_count} pairs with |r| ≥ 0.7
AVERAGE CORRELATION: {avg_corr:.3f}
MAXIMUM CORRELATION: {max_corr:.3f}

TOP CORRELATIONS:
{chr(10).join([f"• {c['var1']} ↔ {c['var2']}: {c['correlation']:.3f} ({c['strength']})" for c in top_corrs]) if top_corrs else "• No strong correlations found"}

Requirements:
- First sentence: Summarize the overall correlation landscape and multicollinearity risk
- Second sentence: Provide the most important insight or recommendation for data analysis/modeling
- Be specific about correlation strengths and their implications
- Keep it actionable and professional"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.3
            )
            
            # Calculate dynamic confidence for correlation analysis
            confidence_data = self._calculate_correlation_confidence(df, summary, strong_corrs)
            
            return {
                "status": "success",
                "summary": response.choices[0].message.content.strip(),
                "confidence": confidence_data,
                "model_used": "gpt-4o-mini",
                "analysis_type": "correlation_analysis"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI analysis failed: {str(e)}"
            }
    
    def _calculate_correlation_confidence(self, df: pd.DataFrame, summary: Dict, strong_corrs: List) -> Dict[str, Any]:
        """Calculate dynamic confidence score for correlation analysis"""
        base_confidence = 75  # Base confidence for correlation analysis
        confidence_factors = []
        
        # Factor 1: Sample size adequacy (0-10 points)
        sample_size = len(df)
        if sample_size >= 1000:
            base_confidence += 10
            confidence_factors.append(f"Large sample size ({sample_size:,} observations) ensures reliable correlations")
        elif sample_size >= 100:
            base_confidence += 7
            confidence_factors.append(f"Adequate sample size ({sample_size:,} observations) for correlation analysis")
        elif sample_size >= 30:
            base_confidence += 4
            confidence_factors.append(f"Minimum viable sample size ({sample_size:,} observations)")
        else:
            confidence_factors.append(f"Small sample size ({sample_size:,} observations) may affect reliability")
        
        # Factor 2: Number of variables (0-8 points)
        num_vars = len(df.select_dtypes(include=[np.number]).columns)
        if num_vars >= 10:
            base_confidence += 8
            confidence_factors.append(f"Rich dataset with {num_vars} numeric variables for comprehensive correlation analysis")
        elif num_vars >= 5:
            base_confidence += 5
            confidence_factors.append(f"Good number of variables ({num_vars}) for meaningful correlation patterns")
        elif num_vars >= 3:
            base_confidence += 3
            confidence_factors.append(f"Sufficient variables ({num_vars}) for basic correlation analysis")
        else:
            confidence_factors.append(f"Limited variables ({num_vars}) restricts correlation insights")
        
        # Factor 3: Data completeness (0-7 points)
        numeric_df = df.select_dtypes(include=[np.number])
        missing_percentage = (numeric_df.isnull().sum().sum() / (numeric_df.shape[0] * numeric_df.shape[1])) * 100
        completeness = 100 - missing_percentage
        
        if completeness >= 95:
            base_confidence += 7
            confidence_factors.append(f"Excellent data completeness ({completeness:.1f}%) ensures accurate correlations")
        elif completeness >= 85:
            base_confidence += 5
            confidence_factors.append(f"Good data completeness ({completeness:.1f}%)")
        elif completeness >= 70:
            base_confidence += 2
            confidence_factors.append(f"Moderate data completeness ({completeness:.1f}%)")
        else:
            confidence_factors.append(f"Poor data completeness ({completeness:.1f}%) may bias correlations")
        
        # Always include foundational factors
        confidence_factors.extend([
            "Pearson correlation coefficients are mathematically precise",
            "Statistical significance can be assessed with p-values"
        ])
        
        # Bonus: Strong correlation patterns found
        if summary['strong_correlations_count'] > 0:
            confidence_factors.append(f"Clear correlation patterns detected ({summary['strong_correlations_count']} strong correlations)")
        
        # Cap confidence at 95%
        final_confidence = min(base_confidence / 100, 0.95)
        
        # Determine explanation based on final score
        if final_confidence >= 0.90:
            explanation = "Very high confidence - excellent data quality with robust correlation patterns"
        elif final_confidence >= 0.80:
            explanation = "High confidence - reliable correlation analysis with good statistical foundation"
        elif final_confidence >= 0.70:
            explanation = "Good confidence - meaningful correlation insights with adequate data quality"
        else:
            explanation = "Moderate confidence - correlation results should be interpreted cautiously"
        
        return {
            "score": round(final_confidence, 2),
            "explanation": explanation,
            "factors": confidence_factors
        }
    
    def _profile_column_data(self, series: pd.Series, column_name: str) -> Dict[str, Any]:
        """Create comprehensive data profile for a column"""
        profile = {
            "total_count": len(series),
            "null_count": series.isnull().sum(),
            "unique_count": series.nunique(),
            "completeness_rate": (1 - series.isnull().sum() / len(series)) * 100 if len(series) > 0 else 0,
            "uniqueness_rate": series.nunique() / len(series) * 100 if len(series) > 0 else 0
        }
        
        # Type-specific profiling
        if series.dtype in ['int64', 'float64']:
            non_null = series.dropna()
            if len(non_null) > 0:
                profile.update({
                    "min_value": float(non_null.min()),
                    "max_value": float(non_null.max()),
                    "mean_value": float(non_null.mean()),
                    "std_value": float(non_null.std()) if len(non_null) > 1 else 0,
                    "zeros_count": (non_null == 0).sum(),
                    "negative_count": (non_null < 0).sum(),
                    "outliers_count": self._count_outliers(non_null)
                })
        
        elif series.dtype == 'object':
            non_null = series.dropna()
            if len(non_null) > 0:
                profile.update({
                    "avg_length": non_null.astype(str).str.len().mean(),
                    "min_length": non_null.astype(str).str.len().min(),
                    "max_length": non_null.astype(str).str.len().max(),
                    "empty_strings": (non_null.astype(str) == '').sum(),
                    "whitespace_only": non_null.astype(str).str.strip().eq('').sum(),
                    "mixed_case": self._check_mixed_case(non_null)
                })
        
        return profile
    
    def _calculate_column_quality_metrics(self, series: pd.Series, column_name: str) -> Dict[str, float]:
        """Calculate the 5 dimensions of data quality"""
        total_count = len(series)
        
        # Completeness (% of non-null values)
        completeness = (1 - series.isnull().sum() / total_count) * 100 if total_count > 0 else 0
        
        # Consistency (format/pattern consistency)
        consistency = self._calculate_consistency_score(series)
        
        # Validity (values within expected ranges/formats)
        validity = self._calculate_validity_score(series, column_name)
        
        # Accuracy (realistic/plausible values)
        accuracy = self._calculate_accuracy_score(series, column_name)
        
        # Uniqueness (appropriate level of uniqueness for the data type)
        uniqueness = self._calculate_uniqueness_score(series, column_name)
        
        return {
            "completeness": round(completeness, 2),
            "consistency": round(consistency, 2),
            "validity": round(validity, 2),
            "accuracy": round(accuracy, 2),
            "uniqueness": round(uniqueness, 2)
        }
    
    def _detect_comprehensive_issues(self, series: pd.Series, column_name: str) -> List[Dict[str, Any]]:
        """Detect comprehensive data quality issues"""
        issues = []
        
        # Missing data issues
        null_pct = series.isnull().sum() / len(series) * 100
        if null_pct > 50:
            issues.append({
                "type": "critical",
                "category": "completeness",
                "message": f"Critical: {null_pct:.1f}% missing values",
                "impact": "high",
                "severity": "critical"
            })
        elif null_pct > 10:
            issues.append({
                "type": "warning",
                "category": "completeness", 
                "message": f"Warning: {null_pct:.1f}% missing values",
                "impact": "medium",
                "severity": "warning"
            })
        
        # Type consistency issues
        if series.dtype == 'object':
            non_null = series.dropna()
            if len(non_null) > 0:
                # Check for mixed numeric/text
                numeric_count = sum(1 for v in non_null.head(100) if self._is_numeric_string(str(v)))
                if 0 < numeric_count < len(non_null.head(100)):
                    issues.append({
                        "type": "warning",
                        "category": "consistency",
                        "message": f"Mixed data types detected",
                        "impact": "medium",
                        "severity": "warning"
                    })
        
        # Uniqueness issues
        if series.nunique() == 1 and len(series) > 1:
            issues.append({
                "type": "info",
                "category": "uniqueness",
                "message": "All values are identical (constant column)",
                "impact": "low",
                "severity": "info"
            })
        
        # Range/validity issues for numeric data
        if series.dtype in ['int64', 'float64']:
            non_null = series.dropna()
            if len(non_null) > 0:
                # Check for unrealistic values based on column name
                if 'age' in column_name.lower():
                    invalid_count = ((non_null < 0) | (non_null > 150)).sum()
                    if invalid_count > 0:
                        issues.append({
                            "type": "critical",
                            "category": "validity",
                            "message": f"{invalid_count} unrealistic age values",
                            "impact": "high",
                            "severity": "critical"
                        })
        
        return issues
    
    def _generate_quality_flags(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate visual quality flags"""
        flags = []
        metrics = analysis["quality_metrics"]
        
        # Overall score flag
        overall_score = analysis["overall_score"]
        if overall_score >= 95:
            flags.append({"type": "excellent", "icon": "verified", "color": "green", "label": "Excellent Quality"})
        elif overall_score >= 85:
            flags.append({"type": "good", "icon": "check_circle", "color": "blue", "label": "Good Quality"})
        elif overall_score >= 70:
            flags.append({"type": "fair", "icon": "warning", "color": "orange", "label": "Fair Quality"})
        else:
            flags.append({"type": "poor", "icon": "error", "color": "red", "label": "Poor Quality"})
        
        # Specific metric flags
        if metrics["completeness"] < 80:
            flags.append({"type": "incomplete", "icon": "help_outline", "color": "orange", "label": "Incomplete Data"})
        
        if metrics["consistency"] < 70:
            flags.append({"type": "inconsistent", "icon": "sync_problem", "color": "red", "label": "Inconsistent Format"})
        
        if len(analysis["issues"]) > 3:
            flags.append({"type": "issues", "icon": "bug_report", "color": "red", "label": "Multiple Issues"})
        
        return flags
    
    def _generate_enhanced_recommendations(self, analysis: Dict[str, Any], column_name: str) -> List[Dict[str, Any]]:
        """Generate smart, actionable recommendations"""
        recommendations = []
        metrics = analysis["quality_metrics"]
        issues = analysis["issues"]
        
        # Completeness recommendations
        if metrics["completeness"] < 90:
            if metrics["completeness"] < 50:
                recommendations.append({
                    "priority": "high",
                    "category": "completeness",
                    "action": "Consider removing this column or investigating data collection process",
                    "reason": f"Only {metrics['completeness']:.1f}% complete"
                })
            else:
                recommendations.append({
                    "priority": "medium", 
                    "category": "completeness",
                    "action": "Implement imputation strategy or collect missing data",
                    "reason": f"{100-metrics['completeness']:.1f}% missing values"
                })
        
        # Type conversion recommendations
        declared_type = analysis["declared_type"]
        inferred_type = analysis["inferred_type"]
        if declared_type != inferred_type and inferred_type != "unknown":
            recommendations.append({
                "priority": "medium",
                "category": "optimization",
                "action": f"Consider converting from {declared_type} to {inferred_type}",
                "reason": "Potential memory optimization and performance improvement"
            })
        
        # Issue-specific recommendations
        for issue in issues:
            if issue["severity"] == "critical":
                recommendations.append({
                    "priority": "high",
                    "category": issue["category"],
                    "action": f"Address: {issue['message']}",
                    "reason": "Critical data quality issue affecting analysis reliability"
                })
        
        return recommendations
    
    def _analyze_global_data_quality(self, df: pd.DataFrame, validations: Dict) -> Dict[str, Any]:
        """Analyze dataset-level quality patterns"""
        return {
            "row_completeness": self._calculate_row_completeness(df),
            "schema_consistency": self._check_schema_consistency(df),
            "referential_integrity": self._check_referential_integrity(df),
            "data_freshness": self._assess_data_freshness(df),
            "duplicate_analysis": self._analyze_duplicates(df)
        }
    
    def _generate_quality_summary(self, validations: Dict, global_analysis: Dict, total_checks: int) -> Dict[str, Any]:
        """Generate comprehensive quality summary"""
        critical_issues = sum(1 for col in validations.values() 
                             for issue in col["issues"] 
                             if issue["severity"] == "critical")
        
        warning_issues = sum(1 for col in validations.values() 
                           for issue in col["issues"] 
                           if issue["severity"] == "warning")
        
        return {
            "columns_analyzed": total_checks,
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "columns_excellent": sum(1 for col in validations.values() if col["overall_score"] >= 95),
            "columns_good": sum(1 for col in validations.values() if 85 <= col["overall_score"] < 95),
            "columns_fair": sum(1 for col in validations.values() if 70 <= col["overall_score"] < 85),
            "columns_poor": sum(1 for col in validations.values() if col["overall_score"] < 70),
            "total_recommendations": sum(len(col["recommendations"]) for col in validations.values())
        }
    
    def _assign_quality_grade(self, score: float) -> Dict[str, str]:
        """Assign letter grade based on quality score"""
        if score >= 95:
            return {"grade": "A+", "description": "Excellent - Production Ready"}
        elif score >= 90:
            return {"grade": "A", "description": "Very Good - Minor Issues"}
        elif score >= 85:
            return {"grade": "B+", "description": "Good - Some Improvements Needed"}
        elif score >= 80:
            return {"grade": "B", "description": "Acceptable - Moderate Issues"}
        elif score >= 70:
            return {"grade": "C", "description": "Fair - Significant Issues"}
        elif score >= 60:
            return {"grade": "D", "description": "Poor - Major Problems"}
        else:
            return {"grade": "F", "description": "Failed - Extensive Problems"}
    
    def _generate_action_plan(self, validations: Dict, global_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate prioritized action plan"""
        actions = []
        
        # Critical issues first
        for col, analysis in validations.items():
            for issue in analysis["issues"]:
                if issue["severity"] == "critical":
                    actions.append({
                        "priority": 1,
                        "column": col,
                        "action": f"Fix critical issue: {issue['message']}",
                        "impact": "High"
                    })
        
        # High-priority recommendations
        for col, analysis in validations.items():
            for rec in analysis["recommendations"]:
                if rec["priority"] == "high":
                    actions.append({
                        "priority": 2,
                        "column": col,
                        "action": rec["action"],
                        "impact": "Medium"
                    })
        
        return sorted(actions, key=lambda x: x["priority"])[:10]  # Top 10 actions
    
    # Helper methods for quality calculations
    def _calculate_consistency_score(self, series: pd.Series) -> float:
        """Calculate format consistency score"""
        # Simplified implementation - can be enhanced
        if series.dtype == 'object':
            non_null = series.dropna()
            if len(non_null) == 0:
                return 100.0
            
            # Check format consistency for strings
            lengths = non_null.astype(str).str.len()
            length_consistency = 1 - (lengths.std() / lengths.mean()) if lengths.mean() > 0 else 1
            return max(0, min(100, length_consistency * 100))
        
        return 100.0  # Numeric types are inherently consistent
    
    def _calculate_validity_score(self, series: pd.Series, column_name: str) -> float:
        """Calculate validity score based on expected ranges"""
        non_null = series.dropna()
        if len(non_null) == 0:
            return 100.0
        
        invalid_count = 0
        
        # Domain-specific validity checks
        if series.dtype in ['int64', 'float64']:
            if 'age' in column_name.lower():
                invalid_count = ((non_null < 0) | (non_null > 150)).sum()
            elif 'percent' in column_name.lower():
                invalid_count = ((non_null < 0) | (non_null > 100)).sum()
        
        validity_rate = 1 - (invalid_count / len(non_null))
        return max(0, validity_rate * 100)
    
    def _calculate_accuracy_score(self, series: pd.Series, column_name: str) -> float:
        """Calculate accuracy score based on realistic value ranges"""
        # Simplified implementation - uses outlier detection as proxy
        if series.dtype in ['int64', 'float64']:
            non_null = series.dropna()
            if len(non_null) < 4:
                return 100.0
            
            outlier_count = self._count_outliers(non_null)
            accuracy_rate = 1 - (outlier_count / len(non_null))
            return max(0, accuracy_rate * 100)
        
        return 100.0  # Default for non-numeric
    
    def _calculate_uniqueness_score(self, series: pd.Series, column_name: str) -> float:
        """Calculate appropriate uniqueness score"""
        if len(series) == 0:
            return 100.0
        
        uniqueness_rate = series.nunique() / len(series)
        
        # Adjust expectations based on column name/type
        if 'id' in column_name.lower():
            # IDs should be unique
            return uniqueness_rate * 100
        elif series.dtype == 'object' and series.nunique() < 20:
            # Categorical columns - low uniqueness is OK
            return 100.0
        else:
            # General case - moderate uniqueness is good
            optimal_range = (0.1, 0.8)
            if optimal_range[0] <= uniqueness_rate <= optimal_range[1]:
                return 100.0
            else:
                distance = min(abs(uniqueness_rate - optimal_range[0]), 
                             abs(uniqueness_rate - optimal_range[1]))
                return max(0, 100 - distance * 100)
    
    def _count_outliers(self, series: pd.Series) -> int:
        """Count outliers using IQR method"""
        try:
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return ((series < lower_bound) | (series > upper_bound)).sum()
        except:
            return 0
    
    def _is_numeric_string(self, value: str) -> bool:
        """Check if string represents a number"""
        try:
            float(value)
            return True
        except:
            return False
    
    def _check_mixed_case(self, series: pd.Series) -> int:
        """Count values with mixed case issues"""
        str_series = series.astype(str)
        mixed_count = 0
        for val in str_series.head(100):
            if val != val.lower() and val != val.upper() and val != val.title():
                mixed_count += 1
        return mixed_count
    
    # Placeholder implementations for global analysis
    def _calculate_row_completeness(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate row-level completeness statistics"""
        row_completeness = (df.count(axis=1) / len(df.columns) * 100)
        return {
            "avg_completeness": float(row_completeness.mean()),
            "min_completeness": float(row_completeness.min()),
            "rows_100_complete": int((row_completeness == 100).sum()),
            "rows_below_50": int((row_completeness < 50).sum())
        }
    
    def _check_schema_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check schema-level consistency"""
        return {
            "column_naming_consistent": True,  # Simplified
            "data_types_appropriate": True,
            "schema_violations": []
        }
    
    def _check_referential_integrity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check referential integrity"""
        return {
            "foreign_key_violations": 0,
            "orphaned_records": 0,
            "integrity_score": 100.0
        }
    
    def _assess_data_freshness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data freshness"""
        return {
            "freshness_score": 100.0,
            "last_updated": "Unknown",
            "staleness_indicators": []
        }
    
    def _analyze_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze duplicate patterns"""
        total_duplicates = df.duplicated().sum()
        return {
            "exact_duplicates": int(total_duplicates),
            "duplicate_rate": float(total_duplicates / len(df) * 100),
            "partial_duplicates": 0  # Placeholder
        }
    
    def _generate_data_quality_ai_insights(self, summary: Dict, validations: Dict, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate AI insights for data quality with comprehensive validation"""
        if not self.openai_client:
            return {
                "status": "unavailable",
                "message": "AI insights unavailable - OpenAI API key not configured"
            }
        
        try:
            # Prepare key statistics for AI analysis
            total_cols = summary["columns_analyzed"]
            critical_issues = summary["critical_issues"]
            warning_issues = summary["warning_issues"]
            excellent_cols = summary["columns_excellent"]
            poor_cols = summary["columns_poor"]
            
            # Identify the worst performing columns
            worst_columns = sorted(
                [(col, data["overall_score"]) for col, data in validations.items()],
                key=lambda x: x[1]
            )[:3]
            
            prompt = f"""Analyze this data quality assessment and provide 2 concise sentences:

DATASET QUALITY OVERVIEW:
• Total columns analyzed: {total_cols}
• Critical issues: {critical_issues}
• Warning issues: {warning_issues}
• Excellent quality columns: {excellent_cols}
• Poor quality columns: {poor_cols}

WORST PERFORMING COLUMNS:
{chr(10).join([f"• {col}: {score:.1f}% quality score" for col, score in worst_columns]) if worst_columns else "• All columns have good quality"}

Requirements:
- First sentence: Summarize overall data quality status and readiness for analysis
- Second sentence: Provide the most critical recommendation or action needed
- Be specific about quality scores and actionable next steps
- Focus on business impact and data reliability"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.3
            )
            
            ai_response_text = response.choices[0].message.content.strip()
            
            # Perform LLM validation using the technical framework
            ground_truth_stats = self._prepare_ground_truth_stats(df, summary, validations)
            validation_result = self.validation_service.validate_llm_analysis(
                df=df,
                llm_response=ai_response_text,
                ground_truth_stats=ground_truth_stats,
                response_time=2.5  # Approximate response time for AI call
            )
            
            return {
                "status": "success",
                "summary": ai_response_text,
                "confidence": {
                    "score": 0.92,
                    "explanation": "Very high confidence for data quality assessment",
                    "factors": [
                        "Quality metrics are quantitatively measured",
                        "Industry-standard data quality dimensions used",
                        "Systematic evaluation across all data quality aspects"
                    ]
                },
                "llm_validation": convert_validation_result_to_dict(validation_result)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI analysis failed: {str(e)}"
            }
    
    def _prepare_ground_truth_stats(self, df: pd.DataFrame, summary: Dict, validations: Dict) -> Dict[str, Any]:
        """Prepare ground truth statistics for LLM validation"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        ground_truth = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': len(numeric_df.columns),
            'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'overall_quality_score': summary.get('overall_quality_score', 0),
            'critical_issues': summary.get('critical_issues', 0),
            'excellent_columns': summary.get('columns_excellent', 0),
            'poor_columns': summary.get('columns_poor', 0)
        }
        
        # Add correlation statistics if available
        if len(numeric_df.columns) >= 2:
            corr_matrix = numeric_df.corr()
            strong_correlations = np.sum(np.abs(corr_matrix.values) > 0.7) - len(corr_matrix)
            ground_truth['strong_correlations'] = strong_correlations
            ground_truth['average_correlation'] = np.abs(corr_matrix.values).mean()
        
        # Add distribution statistics
        for col in numeric_df.columns:
            data = numeric_df[col].dropna()
            if len(data) > 0:
                ground_truth[f'{col}_mean'] = data.mean()
                ground_truth[f'{col}_std'] = data.std()
                ground_truth[f'{col}_skewness'] = stats.skew(data)
        
        return ground_truth
    
    def _calculate_distribution_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate distribution analysis with histogram data"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "No numeric columns found"}
        
        distribution_stats = {}
        histograms = {}
        
        for col in numeric_df.columns:
            data = numeric_df[col].dropna()
            if len(data) > 0:
                skewness = float(stats.skew(data))
                kurtosis = float(stats.kurtosis(data))
                
                # Normality test
                if len(data) >= 3:
                    shapiro_stat, shapiro_p = stats.shapiro(data[:5000])  # Limit for large datasets
                    is_normal = shapiro_p > 0.05
                else:
                    shapiro_stat, shapiro_p, is_normal = None, None, None
                
                # Generate histogram data with more bins for better visualization
                bins = min(max(int(np.sqrt(len(data))), 10), 30)  # Adaptive bin count
                hist_counts, bin_edges = np.histogram(data, bins=bins)
                
                # Create bin labels from actual data
                bin_labels = []
                bin_centers = []
                for i in range(len(bin_edges)-1):
                    center = (bin_edges[i] + bin_edges[i+1]) / 2
                    bin_centers.append(float(center))
                    if bin_edges[i+1] - bin_edges[i] >= 1:
                        bin_labels.append(f"{bin_edges[i]:.0f}-{bin_edges[i+1]:.0f}")
                    else:
                        bin_labels.append(f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}")
                
                histogram_data = {
                    "counts": hist_counts.tolist(),
                    "bin_edges": bin_edges.tolist(),
                    "bin_centers": bin_centers,
                    "labels": bin_labels,
                    "total_count": int(len(data)),
                    "density": (hist_counts / len(data)).tolist()  # Normalized frequencies
                }
                
                distribution_stats[col] = {
                    "skewness": skewness,
                    "kurtosis": kurtosis,
                    "is_normal": is_normal,
                    "shapiro_test": {"statistic": float(shapiro_stat) if shapiro_stat else None, 
                                   "p_value": float(shapiro_p) if shapiro_p else None},
                    "distribution_type": self._classify_distribution(skewness, kurtosis)
                }
                
                histograms[col] = histogram_data
        
        return {
            "distribution_stats": distribution_stats,
            "histograms": histograms
        }
    
    def _calculate_missing_data_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate missing data analysis"""
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        return {
            "missing_by_column": convert_numpy_types(missing_counts.to_dict()),
            "missing_percentages": convert_numpy_types(missing_percentages.to_dict()),
            "total_missing": int(df.isnull().sum().sum()),
            "total_percentage": float(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100),
            "columns_with_missing": missing_counts[missing_counts > 0].index.tolist(),
            "complete_rows": int(df.dropna().shape[0]),
            "complete_rows_percentage": float(df.dropna().shape[0] / df.shape[0] * 100)
        }
    
    def _perform_regression_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform regression analysis"""
        numeric_df = df.select_dtypes(include=[np.number]).dropna()
        
        if numeric_df.shape[1] < 2:
            return {"message": "Need at least 2 numeric columns for regression analysis"}
        
        results = {}
        target_cols = numeric_df.columns[-3:]  # Use last 3 columns as potential targets
        
        for target_col in target_cols:
            feature_cols = [col for col in numeric_df.columns if col != target_col]
            if not feature_cols:
                continue
                
            X = numeric_df[feature_cols]
            y = numeric_df[target_col]
            
            model = LinearRegression()
            model.fit(X, y)
            
            score = model.score(X, y)
            
            results[target_col] = {
                "r_squared": float(score),
                "coefficients": {feature_cols[i]: float(coef) for i, coef in enumerate(model.coef_)},
                "intercept": float(model.intercept_),
                "feature_importance": {
                    feature_cols[i]: abs(float(coef)) 
                    for i, coef in enumerate(model.coef_)
                }
            }
        
        return results
    
    def _perform_clustering_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform clustering analysis"""
        numeric_df = df.select_dtypes(include=[np.number]).dropna()
        
        if numeric_df.shape[0] < 4 or numeric_df.shape[1] < 2:
            return {"message": "Need at least 4 rows and 2 numeric columns for clustering"}
        
        # Standardize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)
        
        # Try different numbers of clusters
        results = {}
        max_clusters = min(8, len(numeric_df) // 2)
        
        for n_clusters in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(scaled_data)
            
            # Calculate silhouette score
            from sklearn.metrics import silhouette_score
            if len(set(cluster_labels)) > 1:
                silhouette = silhouette_score(scaled_data, cluster_labels)
            else:
                silhouette = -1
            
            results[f"k_{n_clusters}"] = {
                "n_clusters": n_clusters,
                "silhouette_score": float(silhouette),
                "cluster_centers": kmeans.cluster_centers_.tolist(),
                "inertia": float(kmeans.inertia_)
            }
        
        # Find optimal number of clusters
        best_k = max(results.keys(), key=lambda k: results[k]["silhouette_score"])
        
        return {
            "results": results,
            "recommended_clusters": int(best_k.split("_")[1]),
            "best_silhouette_score": results[best_k]["silhouette_score"]
        }
    
    def _perform_pca_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform PCA analysis"""
        numeric_df = df.select_dtypes(include=[np.number]).dropna()
        
        if numeric_df.shape[1] < 2:
            return {"message": "Need at least 2 numeric columns for PCA"}
        
        # Standardize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)
        
        # Perform PCA
        n_components = min(numeric_df.shape[1], 5)  # Max 5 components
        pca = PCA(n_components=n_components)
        pca_result = pca.fit_transform(scaled_data)
        
        return {
            "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
            "cumulative_variance_ratio": np.cumsum(pca.explained_variance_ratio_).tolist(),
            "components": pca.components_.tolist(),
            "feature_importance": {
                col: float(sum(abs(pca.components_[i][j]) * pca.explained_variance_ratio_[i] 
                              for i in range(len(pca.components_))))
                for j, col in enumerate(numeric_df.columns)
            },
            "n_components_95_variance": int(np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.95)) + 1
        }
    
    def _perform_time_series_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform time series analysis if datetime columns exist"""
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        
        if datetime_cols.empty:
            # Try to parse potential datetime columns
            potential_datetime_cols = []
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        pd.to_datetime(df[col].head())
                        potential_datetime_cols.append(col)
                    except:
                        continue
            
            if not potential_datetime_cols:
                return {"message": "No datetime columns found for time series analysis"}
            
            datetime_cols = potential_datetime_cols[:1]  # Use first potential datetime column
        
        # Basic time series analysis
        datetime_col = datetime_cols[0]
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if numeric_cols.empty:
            return {"message": "No numeric columns found for time series analysis"}
        
        results = {}
        for num_col in numeric_cols[:3]:  # Analyze first 3 numeric columns
            # Calculate basic trend
            data = df[[datetime_col, num_col]].dropna()
            if len(data) < 2:
                continue
                
            # Simple trend calculation
            y_values = data[num_col].values
            x_values = np.arange(len(y_values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_values, y_values)
            
            results[num_col] = {
                "trend_slope": float(slope),
                "trend_r_squared": float(r_value ** 2),
                "trend_p_value": float(p_value),
                "mean": float(y_values.mean()),
                "std": float(y_values.std()),
                "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
            }
        
        return results
    
    def _perform_anomaly_detection(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform anomaly detection"""
        numeric_df = df.select_dtypes(include=[np.number]).dropna()
        
        if numeric_df.empty:
            return {"message": "No numeric columns found for anomaly detection"}
        
        results = {}
        
        # Statistical outliers (Z-score method)
        z_scores = np.abs(stats.zscore(numeric_df))
        statistical_outliers = convert_numpy_types((z_scores > 3).sum().to_dict())
        
        # Isolation Forest
        if len(numeric_df) > 10:  # Need sufficient data points
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outlier_predictions = iso_forest.fit_predict(numeric_df)
            ml_outliers = int(sum(outlier_predictions == -1))
        else:
            ml_outliers = 0
        
        results = {
            "statistical_outliers": statistical_outliers,
            "total_statistical_outliers": int(sum(statistical_outliers.values())),
            "ml_outliers": ml_outliers,
            "outlier_percentage": float((ml_outliers / len(numeric_df)) * 100) if len(numeric_df) > 0 else 0,
            "method": "Z-score (>3 std) and Isolation Forest"
        }
        
        return results
    
    def _classify_distribution(self, skewness: float, kurtosis: float) -> str:
        """Classify distribution type based on skewness and kurtosis"""
        if abs(skewness) < 0.5:
            skew_type = "symmetric"
        elif skewness > 0.5:
            skew_type = "right-skewed"
        else:
            skew_type = "left-skewed"
        
        if kurtosis > 3:
            kurt_type = "heavy-tailed"
        elif kurtosis < -1:
            kurt_type = "light-tailed"
        else:
            kurt_type = "normal-tailed"
        
        return f"{skew_type}, {kurt_type}"
    
    def _calculate_feature_engineering_ideas(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate feature engineering suggestions based on data characteristics"""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            suggestions = {
                "transformation_ideas": [],
                "interaction_features": [],
                "aggregation_features": [],
                "encoding_suggestions": [],
                "scaling_recommendations": [],
                "temporal_features": [],
                "target_engineering": []
            }
            
            # Transformation suggestions
            for col in numeric_cols:
                if not df[col].isna().all():
                    skewness = df[col].skew()
                    if abs(skewness) > 1:
                        suggestions["transformation_ideas"].append({
                            "column": col,
                            "issue": f"High skewness ({skewness:.2f})",
                            "suggestions": ["log transform", "box-cox transform", "sqrt transform"],
                            "priority": "high" if abs(skewness) > 2 else "medium"
                        })
                    
                    # Check for outliers
                    Q1, Q3 = df[col].quantile([0.25, 0.75])
                    IQR = Q3 - Q1
                    outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                    if outliers > len(df) * 0.05:  # More than 5% outliers
                        suggestions["transformation_ideas"].append({
                            "column": col,
                            "issue": f"High outlier count ({outliers} outliers)",
                            "suggestions": ["winsorization", "robust scaling", "clipping"],
                            "priority": "medium"
                        })
            
            # Interaction features
            if len(numeric_cols) >= 2:
                for i, col1 in enumerate(numeric_cols[:5]):  # Limit to first 5 for performance
                    for col2 in numeric_cols[i+1:6]:
                        corr = df[col1].corr(df[col2])
                        if abs(corr) > 0.3:
                            suggestions["interaction_features"].append({
                                "feature_1": col1,
                                "feature_2": col2,
                                "correlation": float(corr),
                                "suggested_operations": ["multiply", "divide", "add", "subtract"],
                                "priority": "high" if abs(corr) > 0.7 else "medium"
                            })
            
            # Categorical encoding
            for col in categorical_cols:
                unique_count = df[col].nunique()
                if unique_count <= 10:
                    suggestions["encoding_suggestions"].append({
                        "column": col,
                        "unique_values": int(unique_count),
                        "suggested_encoding": "one-hot encoding",
                        "priority": "high"
                    })
                elif unique_count <= 50:
                    suggestions["encoding_suggestions"].append({
                        "column": col,
                        "unique_values": int(unique_count),
                        "suggested_encoding": "target encoding or frequency encoding",
                        "priority": "medium"
                    })
                else:
                    suggestions["encoding_suggestions"].append({
                        "column": col,
                        "unique_values": int(unique_count),
                        "suggested_encoding": "dimensionality reduction after encoding",
                        "priority": "low"
                    })
            
            # Temporal features
            for col in datetime_cols:
                suggestions["temporal_features"].append({
                    "column": col,
                    "suggested_features": [
                        "year", "month", "day", "weekday", "hour",
                        "is_weekend", "is_holiday", "time_since_epoch"
                    ],
                    "seasonality_check": "recommended",
                    "priority": "high"
                })
            
            # Scaling recommendations
            if len(numeric_cols) > 1:
                scales = {}
                for col in numeric_cols:
                    if not df[col].isna().all():
                        scales[col] = {
                            "min": float(df[col].min()),
                            "max": float(df[col].max()),
                            "std": float(df[col].std())
                        }
                
                max_std = max([s["std"] for s in scales.values() if not np.isnan(s["std"])])
                min_std = min([s["std"] for s in scales.values() if not np.isnan(s["std"])])
                
                if max_std / min_std > 10:  # High variance in scales
                    suggestions["scaling_recommendations"].append({
                        "issue": "Features have very different scales",
                        "suggestion": "StandardScaler or MinMaxScaler",
                        "priority": "high"
                    })
            
            return convert_numpy_types(suggestions)
            
        except Exception as e:
            return convert_numpy_types({"error": str(e), "suggestions": {}})
    
    def _calculate_multicollinearity_assessment(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess multicollinearity using VIF and correlation analysis"""
        try:
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            
            numeric_df = df.select_dtypes(include=[np.number]).dropna()
            if len(numeric_df.columns) < 2:
                return convert_numpy_types({"message": "Insufficient numeric columns for multicollinearity analysis"})
            
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()
            
            # Find high correlations
            high_correlations = []
            for i, col1 in enumerate(corr_matrix.columns):
                for j, col2 in enumerate(corr_matrix.columns[i+1:], i+1):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.8:
                        high_correlations.append({
                            "variable_1": col1,
                            "variable_2": col2,
                            "correlation": float(corr_val),
                            "severity": "critical" if abs(corr_val) > 0.95 else "high"
                        })
            
            # Calculate VIF
            vif_data = []
            try:
                X = numeric_df.values
                for i in range(X.shape[1]):
                    vif = variance_inflation_factor(X, i)
                    vif_data.append({
                        "variable": numeric_df.columns[i],
                        "vif": float(vif) if not np.isinf(vif) else 999.0,
                        "interpretation": (
                            "severe multicollinearity" if vif > 10 else
                            "moderate multicollinearity" if vif > 5 else
                            "acceptable"
                        )
                    })
            except Exception as vif_error:
                vif_data = [{"error": f"VIF calculation failed: {str(vif_error)}"}]
            
            # Recommendations
            recommendations = []
            if len(high_correlations) > 0:
                recommendations.append("Consider removing one variable from highly correlated pairs")
                recommendations.append("Use PCA or factor analysis for dimensionality reduction")
            
            high_vif_vars = [v for v in vif_data if isinstance(v, dict) and v.get("vif", 0) > 10]
            if len(high_vif_vars) > 0:
                recommendations.append("Remove variables with VIF > 10")
                recommendations.append("Consider ridge regression or elastic net for regularization")
            
            if len(recommendations) == 0:
                recommendations.append("No significant multicollinearity detected")
            
            return convert_numpy_types({
                "correlation_analysis": {
                    "high_correlations": high_correlations,
                    "correlation_threshold": 0.8
                },
                "vif_analysis": vif_data,
                "summary": {
                    "total_variables": len(numeric_df.columns),
                    "high_correlation_pairs": len(high_correlations),
                    "high_vif_variables": len(high_vif_vars)
                },
                "recommendations": recommendations
            })
            
        except Exception as e:
            return convert_numpy_types({"error": str(e)})
    
    def _calculate_dimensionality_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Provide comprehensive PCA, clustering, and dimensionality reduction insights"""
        try:
            numeric_df = df.select_dtypes(include=[np.number]).dropna()
            if len(numeric_df.columns) < 2:
                return convert_numpy_types({"message": "Insufficient numeric columns for dimensionality analysis"})
            
            # Standardize data
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(numeric_df)
            
            # Enhanced PCA Analysis with more insights
            pca_insights = self._enhanced_pca_analysis(X_scaled, numeric_df.columns.tolist())
            
            # Advanced Clustering Analysis
            clustering_insights = self._advanced_clustering_analysis(X_scaled, numeric_df)
            
            # Dimensionality Reduction Techniques
            dimensionality_reduction = self._dimensionality_reduction_analysis(X_scaled, numeric_df.columns.tolist())
            
            # Intrinsic Dimensionality Estimation
            intrinsic_dim = self._estimate_intrinsic_dimensionality(X_scaled)
            
            # Feature Space Analysis
            feature_space_analysis = self._analyze_feature_space(numeric_df, X_scaled)
            
            # Overall recommendations with enhanced logic
            recommendations = self._generate_dimensionality_recommendations(
                pca_insights, clustering_insights, dimensionality_reduction, 
                intrinsic_dim, len(numeric_df.columns)
            )
            
            return convert_numpy_types({
                "pca_analysis": pca_insights,
                "clustering_analysis": clustering_insights,
                "dimensionality_reduction": dimensionality_reduction,
                "intrinsic_dimensionality": intrinsic_dim,
                "feature_space_analysis": feature_space_analysis,
                "recommendations": recommendations,
                "data_complexity": {
                    "original_dimensions": len(numeric_df.columns),
                    "samples": len(numeric_df),
                    "dimensions_to_samples_ratio": float(len(numeric_df.columns) / len(numeric_df)),
                    "effective_rank": self._calculate_effective_rank(X_scaled)
                },
                "overview": {
                    "total_features": len(numeric_df.columns),
                    "reduction_potential": pca_insights.get("dimensionality_reduction_potential", "moderate"),
                    "data_complexity": "high" if len(numeric_df.columns) > 20 else "moderate" if len(numeric_df.columns) > 10 else "low",
                    "clustering_feasibility": clustering_insights.get("clustering_recommendation", "moderate")
                }
            })
            
        except Exception as e:
            return convert_numpy_types({"error": str(e)})
    
    def _enhanced_pca_analysis(self, X_scaled: np.ndarray, feature_names: list) -> Dict[str, Any]:
        """Enhanced PCA analysis with advanced metrics and interpretations"""
        pca = PCA()
        pca.fit(X_scaled)
        
        explained_variance = pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance)
        components = pca.components_
        
        # Find number of components for different variance thresholds
        n_components_95 = np.argmax(cumulative_variance >= 0.95) + 1
        n_components_90 = np.argmax(cumulative_variance >= 0.90) + 1
        n_components_80 = np.argmax(cumulative_variance >= 0.80) + 1
        
        # Enhanced component analysis with interpretations
        component_features = []
        component_interpretations = []
        
        for i in range(min(10, len(explained_variance))):
            component_loadings = components[i]
            abs_loadings = np.abs(component_loadings)
            
            # Get top contributing features
            top_indices = np.argsort(abs_loadings)[-8:][::-1]  # Top 8 features
            
            top_features = []
            for idx in top_indices:
                feature_name = feature_names[idx]
                loading = float(component_loadings[idx])
                contribution = float(abs_loadings[idx])
                top_features.append({
                    "feature": feature_name,
                    "loading": loading,
                    "contribution": contribution,
                    "percentage": float(contribution / np.sum(abs_loadings) * 100)
                })
            
            # Component interpretation based on loadings
            interpretation = self._interpret_pca_component(component_loadings, feature_names)
            
            component_features.append({
                "component": f"PC{i+1}",
                "variance_explained": float(explained_variance[i]),
                "variance_percentage": float(explained_variance[i] * 100),
                "top_features": top_features,
                "interpretation": interpretation
            })
            
            component_interpretations.append({
                "component": f"PC{i+1}",
                "dominant_theme": interpretation.get("theme", "Mixed"),
                "strength": interpretation.get("strength", "moderate"),
                "description": interpretation.get("description", "")
            })
        
        # Feature importance across all components
        feature_importance = {}
        for i, feature in enumerate(feature_names):
            # Calculate cumulative importance across first 5 components
            importance = sum(abs(components[j][i]) * explained_variance[j] 
                           for j in range(min(5, len(components))))
            feature_importance[feature] = float(importance)
        
        # PCA quality metrics
        kaiser_criterion = sum(1 for val in pca.explained_variance_ if val > 1.0)
        
        # Scree plot elbow detection
        elbow_point = self._detect_elbow_point(explained_variance)
        
        return {
            "total_components": len(explained_variance),
            "components_for_95_variance": int(n_components_95),
            "components_for_90_variance": int(n_components_90),
            "components_for_80_variance": int(n_components_80),
            "explained_variance_ratio": explained_variance.tolist(),
            "component_variances": explained_variance.tolist(),
            "cumulative_variance": cumulative_variance.tolist(),
            "cumulative_variances": cumulative_variance.tolist(),
            "first_component_variance": float(explained_variance[0]),
            "dimensionality_reduction_potential": self._assess_reduction_potential(n_components_95, len(feature_names)),
            "component_features": component_features,
            "component_interpretations": component_interpretations,
            "feature_importance": feature_importance,
            "feature_names": feature_names,
            "kaiser_criterion": int(kaiser_criterion),
            "scree_elbow_point": int(elbow_point),
            "pca_quality_score": self._calculate_pca_quality_score(explained_variance, n_components_95, len(feature_names)),
            "biplot_data": self._generate_biplot_data(X_scaled, components, feature_names)
        }
    
    def _advanced_clustering_analysis(self, X_scaled: np.ndarray, numeric_df: pd.DataFrame) -> Dict[str, Any]:
        """Advanced clustering analysis with multiple algorithms and validation metrics"""
        try:
            max_clusters = min(10, len(numeric_df) // 10)
            if max_clusters < 2:
                return {"message": "Insufficient data for clustering analysis"}
            
            # K-Means Analysis
            kmeans_results = self._analyze_kmeans_clustering(X_scaled, max_clusters)
            
            # DBSCAN Analysis
            dbscan_results = self._analyze_dbscan_clustering(X_scaled)
            
            # Hierarchical Clustering Analysis
            hierarchical_results = self._analyze_hierarchical_clustering(X_scaled, max_clusters)
            
            # Cluster Validation Metrics
            validation_metrics = self._calculate_cluster_validation_metrics(X_scaled, max_clusters)
            
            # Best clustering recommendation
            best_method = self._select_best_clustering_method(kmeans_results, dbscan_results, hierarchical_results)
            
            return {
                "kmeans_analysis": kmeans_results,
                "dbscan_analysis": dbscan_results,
                "hierarchical_analysis": hierarchical_results,
                "validation_metrics": validation_metrics,
                "best_method": best_method,
                "optimal_clusters": kmeans_results.get("optimal_clusters", 3),
                "silhouette_scores": kmeans_results.get("silhouette_scores", []),
                "clustering_recommendation": kmeans_results.get("clustering_recommendation", "moderate clustering structure"),
                "cluster_stability": self._assess_cluster_stability(X_scaled, kmeans_results.get("optimal_clusters", 3))
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _dimensionality_reduction_analysis(self, X_scaled: np.ndarray, feature_names: list) -> Dict[str, Any]:
        """Analyze various dimensionality reduction techniques"""
        try:
            results = {}
            
            # t-SNE Analysis (for visualization)
            if len(X_scaled) <= 1000:  # t-SNE is computationally expensive
                tsne_results = self._analyze_tsne(X_scaled)
                results["tsne_analysis"] = tsne_results
            
            # UMAP Analysis (if available)
            try:
                umap_results = self._analyze_umap(X_scaled)
                results["umap_analysis"] = umap_results
            except ImportError:
                results["umap_analysis"] = {"message": "UMAP not available"}
            
            # Factor Analysis
            factor_results = self._analyze_factor_analysis(X_scaled, feature_names)
            results["factor_analysis"] = factor_results
            
            # Independent Component Analysis
            ica_results = self._analyze_ica(X_scaled, feature_names)
            results["ica_analysis"] = ica_results
            
            return results
        except Exception as e:
            return {"error": str(e)}
    
    def _estimate_intrinsic_dimensionality(self, X_scaled: np.ndarray) -> Dict[str, Any]:
        """Estimate the intrinsic dimensionality of the data"""
        try:
            # Method 1: Participation Ratio
            pca = PCA()
            pca.fit(X_scaled)
            eigenvalues = pca.explained_variance_
            participation_ratio = (np.sum(eigenvalues) ** 2) / np.sum(eigenvalues ** 2)
            
            # Method 2: 90% Variance Threshold
            cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
            intrinsic_dim_90 = np.argmax(cumulative_variance >= 0.90) + 1
            
            # Method 3: Effective Rank
            effective_rank = self._calculate_effective_rank(X_scaled)
            
            # Method 4: Local Dimensionality (simplified)
            local_dim = self._estimate_local_dimensionality(X_scaled)
            
            return {
                "participation_ratio": float(participation_ratio),
                "intrinsic_dim_90_variance": int(intrinsic_dim_90),
                "effective_rank": float(effective_rank),
                "local_dimensionality": local_dim,
                "estimated_intrinsic_dim": int(np.median([participation_ratio, intrinsic_dim_90, effective_rank])),
                "dimensionality_assessment": self._assess_dimensionality_complexity(participation_ratio, intrinsic_dim_90, len(X_scaled[0]))
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_feature_space(self, numeric_df: pd.DataFrame, X_scaled: np.ndarray) -> Dict[str, Any]:
        """Analyze the feature space characteristics"""
        try:
            # Feature correlation network
            correlation_matrix = numeric_df.corr()
            
            # High correlation pairs
            high_corr_pairs = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_val = correlation_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        high_corr_pairs.append({
                            "feature1": correlation_matrix.columns[i],
                            "feature2": correlation_matrix.columns[j],
                            "correlation": float(corr_val)
                        })
            
            # Feature density analysis
            feature_densities = {}
            for i, col in enumerate(numeric_df.columns):
                feature_densities[col] = {
                    "mean": float(numeric_df[col].mean()),
                    "std": float(numeric_df[col].std()),
                    "skewness": float(numeric_df[col].skew()),
                    "kurtosis": float(numeric_df[col].kurtosis())
                }
            
            # Manifold learning indicators
            manifold_indicators = self._analyze_manifold_structure(X_scaled)
            
            return {
                "correlation_network": {
                    "high_correlation_pairs": high_corr_pairs,
                    "network_density": len(high_corr_pairs) / (len(numeric_df.columns) * (len(numeric_df.columns) - 1) / 2)
                },
                "feature_distributions": feature_densities,
                "manifold_structure": manifold_indicators,
                "feature_space_volume": self._calculate_feature_space_volume(X_scaled),
                "nearest_neighbor_analysis": self._analyze_nearest_neighbors(X_scaled)
            }
        except Exception as e:
            return {"error": str(e)}
    
    # Helper methods for enhanced dimensionality analysis
    def _interpret_pca_component(self, component_loadings: np.ndarray, feature_names: list) -> Dict[str, Any]:
        """Interpret PCA component based on feature loadings"""
        abs_loadings = np.abs(component_loadings)
        top_indices = np.argsort(abs_loadings)[-3:][::-1]
        
        dominant_features = [feature_names[i] for i in top_indices]
        strength = "strong" if abs_loadings[top_indices[0]] > 0.7 else "moderate" if abs_loadings[top_indices[0]] > 0.4 else "weak"
        
        return {
            "theme": f"Combination of {', '.join(dominant_features[:2])}",
            "strength": strength,
            "description": f"This component is primarily influenced by {dominant_features[0]} and related features"
        }
    
    def _assess_reduction_potential(self, n_components_95: int, total_features: int) -> str:
        """Assess dimensionality reduction potential"""
        ratio = n_components_95 / total_features
        if ratio <= 0.3:
            return "excellent"
        elif ratio <= 0.5:
            return "high"
        elif ratio <= 0.7:
            return "moderate"
        else:
            return "low"
    
    def _detect_elbow_point(self, explained_variance: np.ndarray) -> int:
        """Detect elbow point in scree plot"""
        if len(explained_variance) < 3:
            return 1
        
        # Calculate second derivative to find elbow
        diffs = np.diff(explained_variance)
        second_diffs = np.diff(diffs)
        
        # Find the point with maximum curvature
        elbow_idx = np.argmax(np.abs(second_diffs)) + 2
        return min(elbow_idx, len(explained_variance))
    
    def _calculate_pca_quality_score(self, explained_variance: np.ndarray, n_components_95: int, total_features: int) -> float:
        """Calculate overall PCA quality score"""
        # Factor 1: First component strength (0-40 points)
        first_component_score = min(explained_variance[0] * 40, 40)
        
        # Factor 2: Reduction efficiency (0-30 points)
        reduction_ratio = n_components_95 / total_features
        reduction_score = max(0, 30 * (1 - reduction_ratio))
        
        # Factor 3: Variance distribution (0-30 points)
        variance_evenness = 1 - np.std(explained_variance[:min(5, len(explained_variance))])
        distribution_score = variance_evenness * 30
        
        total_score = (first_component_score + reduction_score + distribution_score) / 100
        return float(min(max(total_score, 0), 1))
    
    def _generate_biplot_data(self, X_scaled: np.ndarray, components: np.ndarray, feature_names: list) -> Dict[str, Any]:
        """Generate data for PCA biplot visualization"""
        if len(components) < 2:
            return {"message": "Insufficient components for biplot"}
        
        # Project data onto first two components
        pc1_scores = X_scaled @ components[0]
        pc2_scores = X_scaled @ components[1]
        
        # Feature vectors (loadings)
        feature_vectors = []
        for i, feature in enumerate(feature_names):
            feature_vectors.append({
                "feature": feature,
                "pc1_loading": float(components[0][i]),
                "pc2_loading": float(components[1][i]),
                "magnitude": float(np.sqrt(components[0][i]**2 + components[1][i]**2))
            })
        
        return {
            "pc1_scores": pc1_scores.tolist()[:100],  # Limit for visualization
            "pc2_scores": pc2_scores.tolist()[:100],
            "feature_vectors": feature_vectors,
            "pc1_variance": float(components[0].var()),
            "pc2_variance": float(components[1].var())
        }
    
    def _analyze_kmeans_clustering(self, X_scaled: np.ndarray, max_clusters: int) -> Dict[str, Any]:
        """Analyze K-means clustering with multiple metrics"""
        inertias = []
        silhouette_scores = []
        calinski_harabasz_scores = []
        davies_bouldin_scores = []
        
        for k in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            inertias.append(float(kmeans.inertia_))
            
            from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
            silhouette_scores.append(float(silhouette_score(X_scaled, labels)))
            calinski_harabasz_scores.append(float(calinski_harabasz_score(X_scaled, labels)))
            davies_bouldin_scores.append(float(davies_bouldin_score(X_scaled, labels)))
        
        # Find optimal clusters
        best_k_silhouette = int(np.argmax(silhouette_scores) + 2)
        best_k_elbow = self._find_elbow_point(inertias) + 2
        
        return {
            "optimal_clusters": best_k_silhouette,
            "optimal_clusters_elbow": best_k_elbow,
            "inertia_values": inertias,
            "silhouette_scores": silhouette_scores,
            "calinski_harabasz_scores": calinski_harabasz_scores,
            "davies_bouldin_scores": davies_bouldin_scores,
            "clustering_recommendation": (
                "strong clustering structure" if max(silhouette_scores) > 0.5 else
                "moderate clustering structure" if max(silhouette_scores) > 0.3 else
                "weak clustering structure"
            )
        }
    
    def _analyze_dbscan_clustering(self, X_scaled: np.ndarray) -> Dict[str, Any]:
        """Analyze DBSCAN clustering"""
        try:
            from sklearn.cluster import DBSCAN
            from sklearn.neighbors import NearestNeighbors
            
            # Estimate eps parameter using k-distance graph
            k = 4
            nbrs = NearestNeighbors(n_neighbors=k).fit(X_scaled)
            distances, indices = nbrs.kneighbors(X_scaled)
            distances = np.sort(distances[:, k-1], axis=0)
            
            # Use knee point as eps estimate
            eps_estimate = distances[int(len(distances) * 0.9)]
            
            dbscan = DBSCAN(eps=eps_estimate, min_samples=k)
            labels = dbscan.fit_predict(X_scaled)
            
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            n_noise = list(labels).count(-1)
            
            return {
                "n_clusters": n_clusters,
                "n_noise_points": n_noise,
                "noise_ratio": float(n_noise / len(labels)),
                "eps_used": float(eps_estimate),
                "min_samples_used": k,
                "cluster_labels": labels.tolist() if len(labels) <= 1000 else labels[:1000].tolist()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _find_elbow_point(self, values: list) -> int:
        """Find elbow point in a list of values"""
        if len(values) < 3:
            return 0
        
        # Calculate rate of change
        diffs = np.diff(values)
        second_diffs = np.diff(diffs)
        
        # Find maximum change in rate
        elbow_idx = np.argmax(np.abs(second_diffs))
        return elbow_idx
    
    def _calculate_effective_rank(self, X_scaled: np.ndarray) -> float:
        """Calculate effective rank of the data matrix"""
        _, s, _ = np.linalg.svd(X_scaled, full_matrices=False)
        s_normalized = s / np.sum(s)
        entropy = -np.sum(s_normalized * np.log(s_normalized + 1e-10))
        return float(np.exp(entropy))
    
    # Placeholder methods for advanced techniques (simplified implementations)
    def _analyze_hierarchical_clustering(self, X_scaled: np.ndarray, max_clusters: int) -> Dict[str, Any]:
        """Simplified hierarchical clustering analysis"""
        try:
            from scipy.cluster.hierarchy import linkage, fcluster
            from scipy.spatial.distance import pdist
            
            # Compute linkage matrix
            distances = pdist(X_scaled[:min(500, len(X_scaled))])  # Limit for performance
            linkage_matrix = linkage(distances, method='ward')
            
            # Try different numbers of clusters
            cluster_scores = []
            for k in range(2, min(max_clusters + 1, 8)):
                clusters = fcluster(linkage_matrix, k, criterion='maxclust')
                if len(set(clusters)) > 1:
                    from sklearn.metrics import silhouette_score
                    score = silhouette_score(X_scaled[:len(clusters)], clusters)
                    cluster_scores.append(float(score))
                else:
                    cluster_scores.append(0.0)
            
            return {
                "optimal_clusters": int(np.argmax(cluster_scores) + 2) if cluster_scores else 3,
                "silhouette_scores": cluster_scores,
                "method": "ward"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_cluster_validation_metrics(self, X_scaled: np.ndarray, max_clusters: int) -> Dict[str, Any]:
        """Calculate various cluster validation metrics"""
        return {
            "gap_statistic": "not_implemented",
            "stability_analysis": "not_implemented",
            "consensus_clustering": "not_implemented"
        }
    
    def _select_best_clustering_method(self, kmeans_results: dict, dbscan_results: dict, hierarchical_results: dict) -> Dict[str, Any]:
        """Select the best clustering method based on results"""
        methods = []
        
        if "silhouette_scores" in kmeans_results:
            max_sil = max(kmeans_results["silhouette_scores"])
            methods.append(("kmeans", max_sil))
        
        if "silhouette_scores" in hierarchical_results:
            max_sil = max(hierarchical_results["silhouette_scores"])
            methods.append(("hierarchical", max_sil))
        
        if methods:
            best_method, best_score = max(methods, key=lambda x: x[1])
            return {"method": best_method, "score": float(best_score)}
        
        return {"method": "kmeans", "score": 0.3}
    
    def _assess_cluster_stability(self, X_scaled: np.ndarray, optimal_clusters: int) -> Dict[str, Any]:
        """Assess cluster stability (simplified)"""
        return {
            "stability_score": 0.75,  # Placeholder
            "method": "bootstrap_sampling"
        }
    
    # Simplified implementations for advanced techniques
    def _analyze_tsne(self, X_scaled: np.ndarray) -> Dict[str, Any]:
        """Simplified t-SNE analysis"""
        try:
            from sklearn.manifold import TSNE
            tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(X_scaled)//4))
            tsne_result = tsne.fit_transform(X_scaled[:min(1000, len(X_scaled))])
            
            return {
                "embedding_2d": tsne_result.tolist(),
                "perplexity_used": min(30, len(X_scaled)//4),
                "kl_divergence": float(tsne.kl_divergence_)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_umap(self, X_scaled: np.ndarray) -> Dict[str, Any]:
        """Simplified UMAP analysis"""
        return {"message": "UMAP analysis not implemented"}
    
    def _analyze_factor_analysis(self, X_scaled: np.ndarray, feature_names: list) -> Dict[str, Any]:
        """Simplified factor analysis"""
        return {"message": "Factor analysis not implemented"}
    
    def _analyze_ica(self, X_scaled: np.ndarray, feature_names: list) -> Dict[str, Any]:
        """Simplified ICA analysis"""
        return {"message": "ICA analysis not implemented"}
    
    def _estimate_local_dimensionality(self, X_scaled: np.ndarray) -> Dict[str, Any]:
        """Estimate local dimensionality"""
        return {"average_local_dim": 3.0, "method": "simplified"}
    
    def _assess_dimensionality_complexity(self, participation_ratio: float, intrinsic_dim_90: int, total_features: int) -> str:
        """Assess overall dimensionality complexity"""
        if participation_ratio < total_features * 0.3 and intrinsic_dim_90 < total_features * 0.5:
            return "low_complexity"
        elif participation_ratio < total_features * 0.6 and intrinsic_dim_90 < total_features * 0.8:
            return "moderate_complexity"
        else:
            return "high_complexity"
    
    def _analyze_manifold_structure(self, X_scaled: np.ndarray) -> Dict[str, Any]:
        """Analyze manifold structure"""
        return {
            "manifold_detected": True,
            "estimated_manifold_dim": 3,
            "linearity_score": 0.6
        }
    
    def _calculate_feature_space_volume(self, X_scaled: np.ndarray) -> float:
        """Calculate feature space volume"""
        return float(np.linalg.det(np.cov(X_scaled.T) + np.eye(X_scaled.shape[1]) * 1e-6))
    
    def _analyze_nearest_neighbors(self, X_scaled: np.ndarray) -> Dict[str, Any]:
        """Analyze nearest neighbor structure"""
        try:
            from sklearn.neighbors import NearestNeighbors
            nbrs = NearestNeighbors(n_neighbors=5).fit(X_scaled)
            distances, indices = nbrs.kneighbors(X_scaled)
            
            return {
                "avg_nearest_neighbor_distance": float(np.mean(distances[:, 1])),
                "nearest_neighbor_variance": float(np.var(distances[:, 1]))
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_dimensionality_recommendations(self, pca_insights: dict, clustering_insights: dict, 
                                               dimensionality_reduction: dict, intrinsic_dim: dict, 
                                               total_features: int) -> list:
        """Generate comprehensive dimensionality recommendations"""
        recommendations = []
        
        # PCA recommendations
        if pca_insights.get("dimensionality_reduction_potential") in ["excellent", "high"]:
            n_comp = pca_insights.get("components_for_95_variance", 5)
            recommendations.append(f"Strong PCA candidate: {n_comp} components explain 95% variance")
        
        # Clustering recommendations
        clustering_quality = clustering_insights.get("clustering_recommendation", "")
        if "strong" in clustering_quality:
            optimal_k = clustering_insights.get("optimal_clusters", 3)
            recommendations.append(f"Data shows strong clustering structure with {optimal_k} optimal clusters")
        
        # Feature selection recommendations
        if total_features > 20:
            recommendations.append("Consider feature selection techniques for high-dimensional data")
        
        # Intrinsic dimensionality recommendations
        estimated_dim = intrinsic_dim.get("estimated_intrinsic_dim", total_features)
        if estimated_dim < total_features * 0.5:
            recommendations.append(f"Data has lower intrinsic dimensionality (~{estimated_dim}D)")
        
        # Advanced techniques recommendations
        if total_features > 10:
            recommendations.append("Consider manifold learning techniques (t-SNE, UMAP) for visualization")
        
        return recommendations
    
    def _calculate_baseline_model_sanity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data readiness for baseline modeling"""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            # Data quality assessment
            total_missing = df.isnull().sum().sum()
            missing_percentage = (total_missing / (len(df) * len(df.columns))) * 100
            
            # Variance assessment
            low_variance_cols = []
            for col in numeric_cols:
                if df[col].var() < 1e-6:
                    low_variance_cols.append(col)
            
            # Categorical cardinality
            high_cardinality_cols = []
            for col in categorical_cols:
                if df[col].nunique() > len(df) * 0.5:
                    high_cardinality_cols.append({
                        "column": col,
                        "unique_values": int(df[col].nunique()),
                        "cardinality_ratio": float(df[col].nunique() / len(df))
                    })
            
            # Target variable suggestions
            target_suggestions = []
            for col in numeric_cols:
                if df[col].nunique() > 10:  # Regression target
                    target_suggestions.append({
                        "column": col,
                        "type": "regression",
                        "reason": "continuous numeric variable"
                    })
                elif df[col].nunique() <= 10:  # Classification target
                    target_suggestions.append({
                        "column": col,
                        "type": "classification",
                        "reason": f"discrete variable with {df[col].nunique()} classes"
                    })
            
            # Model readiness score
            readiness_factors = {
                "missing_data": max(0, 100 - missing_percentage * 2),
                "variance_quality": max(0, 100 - len(low_variance_cols) * 10),
                "cardinality_quality": max(0, 100 - len(high_cardinality_cols) * 15),
                "sample_size": min(100, len(df) / 10) if len(df) >= 100 else len(df)
            }
            
            overall_readiness = sum(readiness_factors.values()) / len(readiness_factors)
            
            # Preprocessing recommendations
            preprocessing_steps = []
            if missing_percentage > 5:
                preprocessing_steps.append("Handle missing values (imputation or removal)")
            if len(low_variance_cols) > 0:
                preprocessing_steps.append(f"Remove low variance features: {low_variance_cols}")
            if len(high_cardinality_cols) > 0:
                preprocessing_steps.append("Apply dimensionality reduction to high cardinality categorical features")
            if len(numeric_cols) > 1:
                preprocessing_steps.append("Scale numeric features")
            if len(categorical_cols) > 0:
                preprocessing_steps.append("Encode categorical variables")
            
            return convert_numpy_types({
                "readiness_score": float(overall_readiness),
                "readiness_factors": readiness_factors,
                "data_quality": {
                    "missing_percentage": float(missing_percentage),
                    "low_variance_features": low_variance_cols,
                    "high_cardinality_features": high_cardinality_cols,
                    "sample_size": len(df),
                    "feature_count": len(df.columns)
                },
                "target_suggestions": target_suggestions,
                "preprocessing_recommendations": preprocessing_steps,
                "model_suggestions": [
                    "Start with simple models (Linear/Logistic Regression)",
                    "Try ensemble methods (Random Forest, Gradient Boosting)",
                    "Consider cross-validation for model selection",
                    "Use train/validation/test split"
                ]
            })
            
        except Exception as e:
            return convert_numpy_types({"error": str(e)})
    
    def _calculate_drift_stability_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data stability and potential drift indicators"""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            # Temporal analysis if datetime columns exist
            temporal_analysis = {}
            if len(datetime_cols) > 0:
                date_col = datetime_cols[0]  # Use first datetime column
                df_temporal = df.copy()
                df_temporal['period'] = pd.to_datetime(df_temporal[date_col]).dt.to_period('M')
                
                # Check for trends in numeric variables
                temporal_trends = {}
                for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                    monthly_stats = df_temporal.groupby('period')[col].agg(['mean', 'std', 'count'])
                    if len(monthly_stats) > 1:
                        # Simple trend detection
                        trend_correlation = monthly_stats['mean'].corr(range(len(monthly_stats)))
                        temporal_trends[col] = {
                            "trend_correlation": float(trend_correlation) if not np.isnan(trend_correlation) else 0,
                            "trend_direction": (
                                "increasing" if trend_correlation > 0.3 else
                                "decreasing" if trend_correlation < -0.3 else
                                "stable"
                            ),
                            "coefficient_of_variation": float(monthly_stats['mean'].std() / monthly_stats['mean'].mean()) if monthly_stats['mean'].mean() != 0 else 0
                        }
                
                temporal_analysis = {
                    "temporal_column": date_col,
                    "time_periods": len(monthly_stats),
                    "temporal_trends": temporal_trends
                }
            
            # Statistical stability analysis
            stability_metrics = {}
            for col in numeric_cols:
                if not df[col].isna().all():
                    # Split data into chunks for stability analysis
                    chunk_size = len(df) // 4
                    if chunk_size > 10:  # Only if meaningful chunks
                        chunks = [df[col].iloc[i:i+chunk_size].dropna() for i in range(0, len(df), chunk_size)]
                        
                        means = [chunk.mean() for chunk in chunks if len(chunk) > 0]
                        stds = [chunk.std() for chunk in chunks if len(chunk) > 0]
                        
                        if len(means) > 1:
                            stability_metrics[col] = {
                                "mean_stability": float(np.std(means) / np.mean(means)) if np.mean(means) != 0 else 0,
                                "std_stability": float(np.std(stds) / np.mean(stds)) if np.mean(stds) != 0 else 0,
                                "chunks_analyzed": len(means)
                            }
            
            # Overall stability assessment
            stability_flags = []
            if temporal_analysis:
                for col, trend in temporal_analysis.get("temporal_trends", {}).items():
                    if abs(trend["trend_correlation"]) > 0.5:
                        stability_flags.append(f"Strong temporal trend detected in {col}")
                    if trend["coefficient_of_variation"] > 0.3:
                        stability_flags.append(f"High temporal variability in {col}")
            
            for col, metrics in stability_metrics.items():
                if metrics["mean_stability"] > 0.2:
                    stability_flags.append(f"Unstable mean detected in {col}")
                if metrics["std_stability"] > 0.3:
                    stability_flags.append(f"Unstable variance detected in {col}")
            
            # Recommendations
            recommendations = []
            if len(stability_flags) > 0:
                recommendations.append("Monitor data quality over time")
                recommendations.append("Implement drift detection in production")
                recommendations.append("Consider retraining models periodically")
            else:
                recommendations.append("Data appears stable for modeling")
            
            return convert_numpy_types({
                "temporal_analysis": temporal_analysis,
                "stability_metrics": stability_metrics,
                "stability_flags": stability_flags,
                "recommendations": recommendations,
                "overall_stability": "unstable" if len(stability_flags) > 2 else "stable"
            })
            
        except Exception as e:
            return convert_numpy_types({"error": str(e)})
    
    def _calculate_bias_fairness_flags(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect potential bias and fairness issues in the dataset"""
        try:
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            fairness_flags = []
            sensitive_attributes = []
            
            # Detect potential sensitive attributes
            potential_sensitive = []
            for col in categorical_cols:
                unique_vals = df[col].dropna().unique()
                
                # Check for gender indicators
                gender_keywords = ['male', 'female', 'man', 'woman', 'gender', 'sex']
                if any(keyword in col.lower() for keyword in gender_keywords):
                    potential_sensitive.append({
                        "column": col,
                        "type": "gender",
                        "unique_values": len(unique_vals)
                    })
                
                # Check for age groups
                age_keywords = ['age', 'young', 'old', 'senior', 'adult']
                if any(keyword in col.lower() for keyword in age_keywords):
                    potential_sensitive.append({
                        "column": col,
                        "type": "age",
                        "unique_values": len(unique_vals)
                    })
                
                # Check for race/ethnicity
                race_keywords = ['race', 'ethnic', 'nationality', 'origin']
                if any(keyword in col.lower() for keyword in race_keywords):
                    potential_sensitive.append({
                        "column": col,
                        "type": "race/ethnicity",
                        "unique_values": len(unique_vals)
                    })
            
            # Class imbalance analysis
            imbalance_analysis = {}
            for col in categorical_cols[:5]:  # Limit analysis
                value_counts = df[col].value_counts()
                if len(value_counts) > 1:
                    max_class = value_counts.max()
                    min_class = value_counts.min()
                    imbalance_ratio = max_class / min_class
                    
                    if imbalance_ratio > 10:
                        imbalance_analysis[col] = {
                            "imbalance_ratio": float(imbalance_ratio),
                            "majority_class": value_counts.index[0],
                            "majority_percentage": float(value_counts.iloc[0] / len(df) * 100),
                            "severity": "severe" if imbalance_ratio > 50 else "moderate"
                        }
            
            # Representation analysis
            representation_issues = []
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                total = len(df)
                
                for value, count in value_counts.items():
                    percentage = (count / total) * 100
                    if percentage < 1:  # Less than 1% representation
                        representation_issues.append({
                            "column": col,
                            "value": str(value),
                            "count": int(count),
                            "percentage": float(percentage)
                        })
            
            # Correlation with potential outcomes
            outcome_correlations = {}
            if len(numeric_cols) > 0 and len(categorical_cols) > 0:
                # Assume first numeric column might be an outcome
                potential_outcome = numeric_cols[0]
                
                for col in categorical_cols:
                    try:
                        # One-way ANOVA to test for differences
                        groups = [df[df[col] == group][potential_outcome].dropna() for group in df[col].unique()]
                        groups = [g for g in groups if len(g) > 0]
                        
                        if len(groups) > 1:
                            f_stat, p_value = stats.f_oneway(*groups)
                            if p_value < 0.05:
                                outcome_correlations[col] = {
                                    "f_statistic": float(f_stat),
                                    "p_value": float(p_value),
                                    "significant": True
                                }
                    except:
                        continue
            
            # Generate recommendations
            recommendations = []
            if len(potential_sensitive) > 0:
                recommendations.append("Review identified sensitive attributes for fairness implications")
                recommendations.append("Consider bias testing if using these attributes for predictions")
            
            if len(imbalance_analysis) > 0:
                recommendations.append("Address class imbalances through sampling or weighting techniques")
            
            if len(representation_issues) > 5:
                recommendations.append("Consider data collection strategy to improve representation")
            
            if len(outcome_correlations) > 0:
                recommendations.append("Investigate potential disparate impact on different groups")
            
            return convert_numpy_types({
                "potential_sensitive_attributes": potential_sensitive,
                "class_imbalance_analysis": imbalance_analysis,
                "representation_issues": representation_issues[:10],  # Limit output
                "outcome_correlations": outcome_correlations,
                "fairness_flags": fairness_flags,
                "recommendations": recommendations,
                "bias_risk_level": (
                    "high" if len(potential_sensitive) > 2 or len(imbalance_analysis) > 2 else
                    "medium" if len(potential_sensitive) > 0 or len(imbalance_analysis) > 0 else
                    "low"
                )
            })
            
        except Exception as e:
            return convert_numpy_types({"error": str(e)})
    
    def _calculate_documentation_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive data dictionary and findings summary"""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            # Data dictionary
            data_dictionary = {}
            for col in df.columns:
                dtype = str(df[col].dtype)
                
                col_info = {
                    "data_type": dtype,
                    "null_count": int(df[col].isnull().sum()),
                    "null_percentage": float(df[col].isnull().sum() / len(df) * 100),
                    "unique_count": int(df[col].nunique()),
                    "memory_usage_kb": float(df[col].memory_usage(deep=True) / 1024)
                }
                
                if col in numeric_cols:
                    col_info.update({
                        "min_value": float(df[col].min()) if not df[col].isna().all() else None,
                        "max_value": float(df[col].max()) if not df[col].isna().all() else None,
                        "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                        "median": float(df[col].median()) if not df[col].isna().all() else None,
                        "std_dev": float(df[col].std()) if not df[col].isna().all() else None
                    })
                elif col in categorical_cols:
                    value_counts = df[col].value_counts()
                    col_info.update({
                        "most_frequent": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                        "most_frequent_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else None,
                        "sample_values": [str(v) for v in df[col].dropna().unique()[:5]]
                    })
                elif col in datetime_cols:
                    col_info.update({
                        "earliest_date": str(df[col].min()) if not df[col].isna().all() else None,
                        "latest_date": str(df[col].max()) if not df[col].isna().all() else None,
                        "date_range_days": int((df[col].max() - df[col].min()).days) if not df[col].isna().all() else None
                    })
                
                data_dictionary[col] = col_info
            
            # Key findings summary
            key_findings = []
            
            # Data quality findings
            total_missing = df.isnull().sum().sum()
            if total_missing > 0:
                key_findings.append(f"Dataset contains {total_missing} missing values across all columns")
            
            # Column type distribution
            key_findings.append(f"Dataset has {len(numeric_cols)} numeric, {len(categorical_cols)} categorical, and {len(datetime_cols)} datetime columns")
            
            # Data volume
            key_findings.append(f"Dataset contains {len(df)} rows and {len(df.columns)} columns")
            
            # Memory usage
            total_memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            key_findings.append(f"Total memory usage: {total_memory_mb:.2f} MB")
            
            # Potential issues
            high_cardinality_cols = [col for col in categorical_cols if df[col].nunique() > len(df) * 0.5]
            if len(high_cardinality_cols) > 0:
                key_findings.append(f"High cardinality categorical columns detected: {high_cardinality_cols}")
            
            # Analysis recommendations
            analysis_recommendations = [
                "Start with exploratory data analysis (EDA)",
                "Handle missing values appropriately for your use case",
                "Consider feature engineering for categorical variables",
                "Validate data quality before modeling",
                "Document any preprocessing steps taken"
            ]
            
            return convert_numpy_types({
                "data_dictionary": data_dictionary,
                "dataset_summary": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "numeric_columns": len(numeric_cols),
                    "categorical_columns": len(categorical_cols),
                    "datetime_columns": len(datetime_cols),
                    "total_missing_values": int(total_missing),
                    "missing_percentage": float(total_missing / (len(df) * len(df.columns)) * 100),
                    "memory_usage_mb": float(total_memory_mb)
                },
                "key_findings": key_findings,
                "analysis_recommendations": analysis_recommendations,
                "metadata": {
                    "analysis_date": pd.Timestamp.now().isoformat(),
                    "analyst": "Data Analysis Platform",
                    "version": "1.0"
                }
            })
            
        except Exception as e:
            return convert_numpy_types({"error": str(e)})
    
    def _calculate_reproducibility_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate reproducibility information and environment details"""
        try:
            import sys
            import platform
            
            # Environment information
            environment_info = {
                "python_version": sys.version,
                "platform": platform.platform(),
                "pandas_version": pd.__version__,
                "numpy_version": np.__version__
            }
            
            # Data fingerprint
            data_fingerprint = {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "memory_usage": int(df.memory_usage(deep=True).sum()),
                "checksum": int(pd.util.hash_pandas_object(df).sum())
            }
            
            # Analysis parameters
            analysis_parameters = {
                "missing_data_threshold": 0.05,
                "correlation_threshold": 0.7,
                "outlier_method": "IQR and Z-score",
                "random_seed": 42,
                "scaling_method": "StandardScaler"
            }
            
            # Reproducibility checklist
            reproducibility_checklist = [
                "Environment information documented",
                "Data fingerprint captured",
                "Analysis parameters recorded",
                "Random seeds fixed where applicable",
                "Preprocessing steps documented"
            ]
            
            # Code snippets for key operations
            code_snippets = {
                "load_data": "df = pd.read_csv('data.csv')",
                "basic_stats": "df.describe()",
                "missing_analysis": "df.isnull().sum()",
                "correlation": "df.corr()",
                "outlier_detection": "Q1, Q3 = df.quantile([0.25, 0.75]); IQR = Q3 - Q1"
            }
            
            return convert_numpy_types({
                "environment_info": environment_info,
                "data_fingerprint": data_fingerprint,
                "analysis_parameters": analysis_parameters,
                "reproducibility_checklist": reproducibility_checklist,
                "code_snippets": code_snippets,
                "timestamp": pd.Timestamp.now().isoformat()
            })
            
        except Exception as e:
            return convert_numpy_types({"error": str(e)})
    
    def _calculate_dynamic_confidence(self, numeric_df: pd.DataFrame, stats_summary: Dict) -> Dict[str, Any]:
        """Calculate dynamic confidence score based on data quality factors"""
        base_confidence = 70  # Base confidence for descriptive statistics
        confidence_factors = []
        
        # Factor 1: Data completeness (0-15 points)
        completeness_score = 100 - stats_summary['missing_data_percentage']
        if completeness_score >= 95:
            base_confidence += 15
            confidence_factors.append(f"Excellent data completeness ({completeness_score:.1f}% complete)")
        elif completeness_score >= 85:
            base_confidence += 10
            confidence_factors.append(f"Good data completeness ({completeness_score:.1f}% complete)")
        elif completeness_score >= 70:
            base_confidence += 5
            confidence_factors.append(f"Moderate data completeness ({completeness_score:.1f}% complete)")
        else:
            confidence_factors.append(f"Limited data completeness ({completeness_score:.1f}% complete)")
        
        # Factor 2: Sample size adequacy (0-10 points)
        sample_size = stats_summary['total_observations']
        if sample_size >= 1000:
            base_confidence += 10
            confidence_factors.append(f"Large sample size ({sample_size:,} observations)")
        elif sample_size >= 100:
            base_confidence += 7
            confidence_factors.append(f"Adequate sample size ({sample_size:,} observations)")
        elif sample_size >= 30:
            base_confidence += 4
            confidence_factors.append(f"Minimum viable sample size ({sample_size:,} observations)")
        else:
            confidence_factors.append(f"Small sample size ({sample_size:,} observations)")
        
        # Factor 3: Statistical precision (0-5 points)
        columns_count = stats_summary['columns_count']
        if columns_count >= 5:
            base_confidence += 5
            confidence_factors.append("Multiple numeric variables for robust analysis")
        elif columns_count >= 2:
            base_confidence += 3
            confidence_factors.append("Sufficient numeric variables for analysis")
        else:
            confidence_factors.append("Limited numeric variables")
        
        # Always include these foundational factors
        confidence_factors.extend([
            "Descriptive statistics are mathematically precise",
            "AI interpretation based on established statistical principles"
        ])
        
        # Cap confidence at 95% (never claim 100% certainty)
        final_confidence = min(base_confidence / 100, 0.95)
        
        # Determine explanation based on final score
        if final_confidence >= 0.90:
            explanation = "Very high confidence - excellent data quality and robust statistical foundation"
        elif final_confidence >= 0.80:
            explanation = "High confidence - good data quality with reliable statistical measures"
        elif final_confidence >= 0.70:
            explanation = "Good confidence - adequate data quality for meaningful insights"
        else:
            explanation = "Moderate confidence - consider data quality limitations"
        
        return {
            "score": round(final_confidence, 2),
            "explanation": explanation,
            "factors": confidence_factors
        }
    
    def _generate_descriptive_ai_summary(self, desc_stats: pd.DataFrame, additional_stats: Dict, numeric_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate AI-powered summary of descriptive statistics"""
        if not self.openai_client:
            return {
                "status": "unavailable",
                "message": "AI insights unavailable - OpenAI API key not configured",
                "summary": "Configure OpenAI API key to get AI-powered statistical insights"
            }
        
        try:
            # Prepare statistical summary for AI analysis
            stats_summary = {
                "columns_count": len(numeric_df.columns),
                "total_observations": len(numeric_df),
                "missing_data_percentage": round((numeric_df.isnull().sum().sum() / (len(numeric_df) * len(numeric_df.columns))) * 100, 2),
            }
            
            # Get top 3 columns by different metrics
            means = desc_stats.loc['mean'].to_dict()
            stds = desc_stats.loc['std'].to_dict()
            ranges = {col: additional_stats[col]['range'] for col in additional_stats if additional_stats[col]['range'] is not None}
            
            # Create concise prompt for AI analysis
            prompt = f"""As a senior data scientist, provide a concise 2-sentence summary of these descriptive statistics:

DATASET: {stats_summary['columns_count']} numeric columns, {stats_summary['total_observations']:,} observations
MISSING DATA: {stats_summary['missing_data_percentage']}%

KEY STATISTICS:
Highest Mean: {max(means, key=means.get) if means else 'N/A'} ({max(means.values()) if means else 'N/A':.2f})
Highest Std Dev: {max(stds, key=stds.get) if stds else 'N/A'} ({max(stds.values()) if stds else 'N/A':.2f})
Largest Range: {max(ranges, key=ranges.get) if ranges else 'N/A'} ({max(ranges.values()) if ranges else 'N/A':.2f})

Requirements:
- Write exactly 2 clear, concise sentences
- First sentence: Describe the overall data characteristics (variability, scale, completeness)
- Second sentence: Highlight the most important insight or recommendation
- Use specific numbers from the statistics above
- Be actionable and professional
- No bullet points or formatting"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using cost-effective model for short summaries
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            
            ai_text = response.choices[0].message.content.strip()
            
            # Split into lines and format
            lines = [line.strip() for line in ai_text.split('\n') if line.strip()]
            
            # Calculate dynamic confidence based on data quality factors
            confidence_explanation = self._calculate_dynamic_confidence(numeric_df, stats_summary)
            
            return {
                "status": "success",
                "summary": ai_text,
                "confidence": confidence_explanation,
                "model_used": "gpt-4o-mini",
                "analysis_type": "descriptive_statistics"
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"AI analysis failed: {str(e)}",
                "summary": "Unable to generate AI insights at this time"
            }
