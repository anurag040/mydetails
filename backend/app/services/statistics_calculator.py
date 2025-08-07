import pandas as pd
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List, Optional
from app.services.file_handler import FileHandler
from app.schemas.responses import BasicStatsResponse, AdvancedStatsResponse

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif hasattr(obj, 'item'):
        return obj.item()
    return obj

class StatisticsCalculator:
    def __init__(self):
        self.file_handler = FileHandler()
    
    async def calculate_basic_stats(self, dataset_id: str, options: List[str]) -> BasicStatsResponse:
        """Calculate basic statistics based on selected options"""
        df = await self.file_handler.load_dataset(dataset_id)
        if df is None:
            raise FileNotFoundError("Dataset not found")
        
        result = BasicStatsResponse(dataset_id=dataset_id)
        
        if "descriptive" in options:
            result.descriptive_stats = self._calculate_descriptive_stats(df)
        
        if "correlation" in options:
            result.correlation_matrix = self._calculate_correlation_analysis(df)
        
        if "distribution" in options:
            result.distribution_analysis = self._calculate_distribution_analysis(df)
        
        if "missing_data" in options:
            result.missing_data_summary = self._calculate_missing_data_analysis(df)
        
        if "missing_value_analysis" in options:
            result.missing_value_analysis = self._calculate_missing_value_analysis(df)
        
        if "duplicates_analysis" in options:
            result.duplicates_analysis = self._calculate_duplicates_analysis(df)
        
        if "type_integrity_validation" in options:
            result.type_integrity_validation = self._calculate_type_integrity_validation(df)
        
        if "univariate_summaries" in options:
            result.univariate_summaries = self._calculate_univariate_summaries(df)
        
        if "outlier_detection" in options:
            result.outlier_detection = self._calculate_outlier_detection(df)
        
        # Advanced analysis components
        if "feature_engineering_ideas" in options:
            result.feature_engineering_ideas = self._calculate_feature_engineering_ideas(df)
        
        if "multicollinearity_assessment" in options:
            result.multicollinearity_assessment = self._calculate_multicollinearity_assessment(df)
        
        if "dimensionality_insights" in options:
            result.dimensionality_insights = self._calculate_dimensionality_insights(df)
        
        if "baseline_model_sanity" in options:
            result.baseline_model_sanity = self._calculate_baseline_model_sanity(df)
        
        if "drift_stability_analysis" in options:
            result.drift_stability_analysis = self._calculate_drift_stability_analysis(df)
        
        if "bias_fairness_flags" in options:
            result.bias_fairness_flags = self._calculate_bias_fairness_flags(df)
        
        if "documentation_summary" in options:
            result.documentation_summary = self._calculate_documentation_summary(df)
        
        if "reproducibility_info" in options:
            result.reproducibility_info = self._calculate_reproducibility_info(df)
        
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
        missing_combinations = df.isnull().groupby(list(df.columns)).size().reset_index(name='count')
        missing_combinations = missing_combinations.sort_values('count', ascending=False)
        
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
        """Validate data types and integrity across the dataset"""
        validation_results = {}
        overall_quality_score = 0
        total_checks = 0
        
        # Check each column for type consistency and integrity
        for col in df.columns:
            col_data = df[col].dropna()  # Exclude missing values from type checks
            if len(col_data) == 0:
                continue
                
            validation_results[col] = {
                "declared_type": str(df[col].dtype),
                "inferred_type": self._infer_optimal_type(col_data),
                "integrity_score": 0,
                "issues": [],
                "recommendations": []
            }
            
            # Type consistency checks
            type_issues = self._check_type_consistency(col_data, col)
            validation_results[col]["issues"].extend(type_issues)
            
            # Data integrity checks
            integrity_issues = self._check_data_integrity(col_data, col)
            validation_results[col]["issues"].extend(integrity_issues)
            
            # Calculate integrity score for this column
            max_possible_issues = 5  # Maximum number of different issue types
            actual_issues = len(validation_results[col]["issues"])
            col_score = max(0, (max_possible_issues - actual_issues) / max_possible_issues * 100)
            validation_results[col]["integrity_score"] = col_score
            
            # Generate recommendations
            validation_results[col]["recommendations"] = self._generate_type_recommendations(
                validation_results[col]["issues"], 
                validation_results[col]["declared_type"], 
                validation_results[col]["inferred_type"]
            )
            
            overall_quality_score += col_score
            total_checks += 1
        
        # Calculate overall data quality score
        overall_quality_score = overall_quality_score / total_checks if total_checks > 0 else 100
        
        # Global integrity checks
        global_issues = self._check_global_integrity(df)
        
        return convert_numpy_types({
            "column_validations": validation_results,
            "overall_quality_score": round(overall_quality_score, 2),
            "global_issues": global_issues,
            "summary": {
                "columns_analyzed": total_checks,
                "columns_with_issues": len([col for col, result in validation_results.items() if result["issues"]]),
                "average_integrity_score": round(overall_quality_score, 2),
                "critical_issues": len([issue for col_result in validation_results.values() for issue in col_result["issues"] if "Critical" in issue]),
                "warning_issues": len([issue for col_result in validation_results.values() for issue in col_result["issues"] if "Warning" in issue])
            },
            "recommendations": self._generate_global_type_recommendations(validation_results, global_issues)
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
                    "mean": float(data.mean()),
                    "median": float(data.median()),
                    "mode": float(data.mode().iloc[0]) if len(data.mode()) > 0 else None,
                    "std": float(data.std()),
                    "variance": float(data.var()),
                    "min": float(data.min()),
                    "max": float(data.max()),
                    "range": float(data.max() - data.min()),
                    "q1": float(data.quantile(0.25)),
                    "q3": float(data.quantile(0.75)),
                    "iqr": float(data.quantile(0.75) - data.quantile(0.25))
                },
                "distribution_stats": {
                    "skewness": float(stats.skew(data)),
                    "kurtosis": float(stats.kurtosis(data)),
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
        """Calculate descriptive statistics"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "No numeric columns found"}
        
        desc_stats = numeric_df.describe()
        
        return {
            "summary": convert_numpy_types(desc_stats.to_dict()),
            "additional_stats": {
                col: {
                    "variance": float(numeric_df[col].var()),
                    "coefficient_of_variation": float(numeric_df[col].std() / numeric_df[col].mean()) if numeric_df[col].mean() != 0 else None,
                    "range": float(numeric_df[col].max() - numeric_df[col].min())
                }
                for col in numeric_df.columns
            }
        }
    
    def _calculate_correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate correlation analysis with heatmap data"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.shape[1] < 2:
            return {"message": "Need at least 2 numeric columns for correlation analysis"}
        
        corr_matrix = numeric_df.corr()
        
        # Find strong correlations (>0.7 or <-0.7)
        strong_correlations = []
        all_correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                correlation_entry = {
                    "var1": corr_matrix.columns[i],
                    "var2": corr_matrix.columns[j],
                    "correlation": float(corr_val),
                    "strength": self._get_correlation_strength(corr_val)
                }
                
                all_correlations.append(correlation_entry)
                
                if abs(corr_val) > 0.7:
                    strong_correlations.append(correlation_entry)
        
        # Prepare heatmap data
        heatmap_data = {
            "variables": corr_matrix.columns.tolist(),
            "correlation_matrix": convert_numpy_types(corr_matrix.values.tolist()),
            "correlation_dict": convert_numpy_types(corr_matrix.to_dict())
        }
        
        return {
            "correlation_matrix": convert_numpy_types(corr_matrix.to_dict()),
            "heatmap_data": heatmap_data,
            "all_correlations": all_correlations,
            "strong_correlations": strong_correlations,
            "average_correlation": float(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean())
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
        """Provide PCA and clustering insights for dimensionality assessment"""
        try:
            numeric_df = df.select_dtypes(include=[np.number]).dropna()
            if len(numeric_df.columns) < 2:
                return convert_numpy_types({"message": "Insufficient numeric columns for dimensionality analysis"})
            
            # Standardize data
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(numeric_df)
            
            # PCA Analysis
            pca = PCA()
            pca.fit(X_scaled)
            
            explained_variance = pca.explained_variance_ratio_
            cumulative_variance = np.cumsum(explained_variance)
            
            # Get feature loadings (components) for each PC
            feature_names = numeric_df.columns.tolist()
            components = pca.components_
            
            # Find number of components for 95% variance
            n_components_95 = np.argmax(cumulative_variance >= 0.95) + 1
            n_components_90 = np.argmax(cumulative_variance >= 0.90) + 1
            
            # Get top contributing features for each component
            component_features = []
            for i in range(min(10, len(explained_variance))):  # Show up to 10 components
                component_loadings = components[i]
                # Get absolute values for ranking
                abs_loadings = np.abs(component_loadings)
                # Get indices of top 5 contributing features
                top_indices = np.argsort(abs_loadings)[-5:][::-1]
                
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
                
                component_features.append({
                    "component": f"PC{i+1}",
                    "variance_explained": float(explained_variance[i]),
                    "variance_percentage": float(explained_variance[i] * 100),
                    "top_features": top_features
                })
            
            pca_insights = {
                "total_components": len(explained_variance),
                "components_for_95_variance": int(n_components_95),
                "components_for_90_variance": int(n_components_90),
                "explained_variance_ratio": explained_variance.tolist(),
                "component_variances": explained_variance.tolist(),  # For frontend compatibility
                "cumulative_variance": cumulative_variance.tolist(),
                "cumulative_variances": cumulative_variance.tolist(),  # For frontend compatibility
                "first_component_variance": float(explained_variance[0]),
                "dimensionality_reduction_potential": "high" if n_components_95 < len(numeric_df.columns) * 0.7 else "low",
                "component_features": component_features,  # New: detailed feature contributions
                "feature_names": feature_names  # New: all feature names for reference
            }
            
            # Clustering Analysis
            max_clusters = min(10, len(numeric_df) // 10)
            if max_clusters >= 2:
                inertias = []
                silhouette_scores = []
                
                for k in range(2, max_clusters + 1):
                    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                    labels = kmeans.fit_predict(X_scaled)
                    inertias.append(float(kmeans.inertia_))
                    
                    # Calculate silhouette score
                    from sklearn.metrics import silhouette_score
                    sil_score = silhouette_score(X_scaled, labels)
                    silhouette_scores.append(float(sil_score))
                
                # Find elbow point
                best_k = 2
                if len(silhouette_scores) > 0:
                    best_k = int(np.argmax(silhouette_scores) + 2)
                
                clustering_insights = {
                    "optimal_clusters": best_k,
                    "inertia_values": inertias,
                    "silhouette_scores": silhouette_scores,
                    "clustering_recommendation": (
                        "strong clustering structure" if max(silhouette_scores) > 0.5 else
                        "moderate clustering structure" if max(silhouette_scores) > 0.3 else
                        "weak clustering structure"
                    )
                }
            else:
                clustering_insights = {"message": "Insufficient data for clustering analysis"}
            
            # Overall recommendations
            recommendations = []
            if n_components_95 < len(numeric_df.columns) * 0.8:
                recommendations.append(f"Consider PCA: {n_components_95} components explain 95% variance")
            
            if max_clusters >= 2 and max(silhouette_scores) > 0.3:
                recommendations.append(f"Data shows clustering structure with {best_k} optimal clusters")
            
            if len(numeric_df.columns) > 10:
                recommendations.append("Consider feature selection techniques")
            
            return convert_numpy_types({
                "pca_analysis": pca_insights,
                "clustering_analysis": clustering_insights,
                "recommendations": recommendations,
                "data_complexity": {
                    "original_dimensions": len(numeric_df.columns),
                    "samples": len(numeric_df),
                    "dimensions_to_samples_ratio": float(len(numeric_df.columns) / len(numeric_df))
                },
                "overview": {
                    "total_features": len(numeric_df.columns),
                    "reduction_potential": "high" if n_components_95 < len(numeric_df.columns) * 0.7 else "moderate" if n_components_95 < len(numeric_df.columns) * 0.9 else "low",
                    "data_complexity": "high" if len(numeric_df.columns) > 20 else "moderate" if len(numeric_df.columns) > 10 else "low"
                }
            })
            
        except Exception as e:
            return convert_numpy_types({"error": str(e)})
    
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
