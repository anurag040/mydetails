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
        """Get a quick statistical summary"""
        df = await self.file_handler.load_dataset(dataset_id)
        if df is None:
            raise FileNotFoundError("Dataset not found")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        return {
            "dataset_id": dataset_id,
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "column_types": {
                "numeric": len(numeric_cols),
                "categorical": len(categorical_cols),
                "datetime": len(df.select_dtypes(include=['datetime']).columns)
            },
            "missing_data": {
                "total_missing": int(df.isnull().sum().sum()),
                "percentage": float(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100)
            },
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
        }
    
    def _calculate_descriptive_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate descriptive statistics"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "No numeric columns found"}
        
        desc_stats = numeric_df.describe()
        
        return {
            "summary": desc_stats.to_dict(),
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
        """Calculate correlation analysis"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.shape[1] < 2:
            return {"message": "Need at least 2 numeric columns for correlation analysis"}
        
        corr_matrix = numeric_df.corr()
        
        # Find strong correlations (>0.7 or <-0.7)
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_correlations.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": float(corr_val),
                        "strength": "strong positive" if corr_val > 0.7 else "strong negative"
                    })
        
        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "average_correlation": float(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean())
        }
    
    def _calculate_distribution_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate distribution analysis"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "No numeric columns found"}
        
        distribution_stats = {}
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
                
                distribution_stats[col] = {
                    "skewness": skewness,
                    "kurtosis": kurtosis,
                    "is_normal": is_normal,
                    "shapiro_test": {"statistic": float(shapiro_stat) if shapiro_stat else None, 
                                   "p_value": float(shapiro_p) if shapiro_p else None},
                    "distribution_type": self._classify_distribution(skewness, kurtosis)
                }
        
        return distribution_stats
    
    def _calculate_missing_data_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate missing data analysis"""
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        return {
            "missing_by_column": missing_counts.to_dict(),
            "missing_percentages": missing_percentages.to_dict(),
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
        statistical_outliers = (z_scores > 3).sum().to_dict()
        
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
