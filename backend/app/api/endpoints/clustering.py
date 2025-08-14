from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
import warnings
warnings.filterwarnings('ignore')

router = APIRouter()

class ClusteringRequest(BaseModel):
    file_id: str
    method: str = "kmeans"  # kmeans, dbscan, hierarchical
    n_clusters: Optional[int] = None
    columns: Optional[List[str]] = None

class AnomalyDetectionRequest(BaseModel):
    file_id: str
    method: str = "isolation_forest"  # isolation_forest, local_outlier_factor
    contamination: float = 0.1
    columns: Optional[List[str]] = None

@router.post("/clustering/analyze")
async def perform_clustering_analysis(request: ClusteringRequest):
    """
    Perform clustering analysis on the uploaded data.
    """
    try:
        # Load the data
        file_path = f"uploads/{request.file_id}.csv"
        df = pd.read_csv(file_path)
        
        # Select numeric columns for clustering
        if request.columns:
            numeric_cols = [col for col in request.columns if col in df.columns and df[col].dtype in ['int64', 'float64']]
        else:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 numeric columns for clustering")
        
        # Prepare data
        X = df[numeric_cols].dropna()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Determine optimal number of clusters if not provided
        if request.method == "kmeans" and request.n_clusters is None:
            optimal_k = find_optimal_clusters(X_scaled)
        else:
            optimal_k = request.n_clusters or 3
        
        # Perform clustering
        if request.method == "kmeans":
            clusterer = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        elif request.method == "dbscan":
            clusterer = DBSCAN(eps=0.5, min_samples=5)
        elif request.method == "hierarchical":
            clusterer = AgglomerativeClustering(n_clusters=optimal_k)
        else:
            raise HTTPException(status_code=400, detail="Invalid clustering method")
        
        # Fit the model
        cluster_labels = clusterer.fit_predict(X_scaled)
        
        # Calculate clustering metrics
        if len(set(cluster_labels)) > 1:  # Need at least 2 clusters for metrics
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            calinski_harabasz = calinski_harabasz_score(X_scaled, cluster_labels)
            davies_bouldin = davies_bouldin_score(X_scaled, cluster_labels)
        else:
            silhouette_avg = calinski_harabasz = davies_bouldin = None
        
        # Get cluster statistics
        cluster_stats = get_cluster_statistics(df, numeric_cols, cluster_labels)
        
        # Generate PCA for visualization
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        # Prepare cluster centers for visualization
        cluster_centers = None
        if request.method == "kmeans":
            centers_scaled = clusterer.cluster_centers_
            cluster_centers = pca.transform(centers_scaled)
        
        return {
            "success": True,
            "method": request.method,
            "n_clusters": len(set(cluster_labels)),
            "cluster_labels": cluster_labels.tolist(),
            "metrics": {
                "silhouette_score": float(silhouette_avg) if silhouette_avg is not None else None,
                "calinski_harabasz_score": float(calinski_harabasz) if calinski_harabasz is not None else None,
                "davies_bouldin_score": float(davies_bouldin) if davies_bouldin is not None else None
            },
            "cluster_statistics": cluster_stats,
            "visualization_data": {
                "pca_coordinates": X_pca.tolist(),
                "cluster_centers": cluster_centers.tolist() if cluster_centers is not None else None,
                "explained_variance_ratio": pca.explained_variance_ratio_.tolist()
            },
            "columns_used": numeric_cols,
            "data_points": len(X)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering analysis failed: {str(e)}")

@router.post("/anomaly-detection/analyze")
async def perform_anomaly_detection(request: AnomalyDetectionRequest):
    """
    Perform anomaly detection on the uploaded data.
    """
    try:
        # Load the data
        file_path = f"uploads/{request.file_id}.csv"
        df = pd.read_csv(file_path)
        
        # Select numeric columns
        if request.columns:
            numeric_cols = [col for col in request.columns if col in df.columns and df[col].dtype in ['int64', 'float64']]
        else:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 1:
            raise HTTPException(status_code=400, detail="Need at least 1 numeric column for anomaly detection")
        
        # Prepare data
        X = df[numeric_cols].dropna()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform anomaly detection
        if request.method == "isolation_forest":
            detector = IsolationForest(
                contamination=request.contamination,
                random_state=42,
                n_estimators=100
            )
        elif request.method == "local_outlier_factor":
            detector = LocalOutlierFactor(
                contamination=request.contamination,
                n_neighbors=20
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid anomaly detection method")
        
        # Fit and predict
        if request.method == "isolation_forest":
            anomaly_labels = detector.fit_predict(X_scaled)
            anomaly_scores = detector.decision_function(X_scaled)
        else:  # LOF
            anomaly_labels = detector.fit_predict(X_scaled)
            anomaly_scores = detector.negative_outlier_factor_
        
        # Convert labels (-1 for anomaly, 1 for normal) to (1 for anomaly, 0 for normal)
        anomaly_binary = (anomaly_labels == -1).astype(int)
        
        # Get anomaly statistics
        n_anomalies = np.sum(anomaly_binary)
        anomaly_percentage = (n_anomalies / len(X)) * 100
        
        # Find most anomalous points
        anomaly_indices = np.where(anomaly_binary == 1)[0]
        top_anomalies = []
        
        if len(anomaly_indices) > 0:
            # Sort by anomaly score (most anomalous first)
            if request.method == "isolation_forest":
                sorted_indices = anomaly_indices[np.argsort(anomaly_scores[anomaly_indices])]
            else:  # LOF (lower scores = more anomalous)
                sorted_indices = anomaly_indices[np.argsort(anomaly_scores[anomaly_indices])]
            
            # Get top 10 anomalies
            for idx in sorted_indices[:10]:
                original_idx = X.index[idx]
                top_anomalies.append({
                    "index": int(original_idx),
                    "anomaly_score": float(anomaly_scores[idx]),
                    "data_point": df.iloc[original_idx][numeric_cols].to_dict()
                })
        
        # Generate PCA for visualization
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        # Statistical analysis of anomalies vs normal points
        anomaly_stats = analyze_anomaly_characteristics(df, numeric_cols, anomaly_binary, X.index)
        
        return {
            "success": True,
            "method": request.method,
            "contamination": request.contamination,
            "anomaly_labels": anomaly_binary.tolist(),
            "anomaly_scores": anomaly_scores.tolist(),
            "summary": {
                "total_points": len(X),
                "anomalies_detected": int(n_anomalies),
                "anomaly_percentage": round(anomaly_percentage, 2)
            },
            "top_anomalies": top_anomalies,
            "anomaly_statistics": anomaly_stats,
            "visualization_data": {
                "pca_coordinates": X_pca.tolist(),
                "explained_variance_ratio": pca.explained_variance_ratio_.tolist()
            },
            "columns_used": numeric_cols
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

def find_optimal_clusters(X, max_k=10):
    """Find optimal number of clusters using elbow method and silhouette analysis."""
    if len(X) < 4:
        return 2
    
    max_k = min(max_k, len(X) - 1)
    silhouette_scores = []
    
    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        if len(set(labels)) > 1:
            score = silhouette_score(X, labels)
            silhouette_scores.append(score)
        else:
            silhouette_scores.append(0)
    
    # Return k with highest silhouette score
    if silhouette_scores:
        optimal_k = silhouette_scores.index(max(silhouette_scores)) + 2
        return optimal_k
    return 3

def get_cluster_statistics(df, numeric_cols, cluster_labels):
    """Calculate statistics for each cluster."""
    cluster_stats = {}
    unique_clusters = set(cluster_labels)
    
    for cluster_id in unique_clusters:
        if cluster_id == -1:  # Noise points in DBSCAN
            cluster_name = "Noise"
        else:
            cluster_name = f"Cluster_{cluster_id}"
        
        cluster_mask = np.array(cluster_labels) == cluster_id
        cluster_data = df[numeric_cols].iloc[cluster_mask]
        
        cluster_stats[cluster_name] = {
            "size": int(np.sum(cluster_mask)),
            "percentage": round((np.sum(cluster_mask) / len(cluster_labels)) * 100, 2),
            "mean_values": cluster_data.mean().to_dict(),
            "std_values": cluster_data.std().to_dict()
        }
    
    return cluster_stats

def analyze_anomaly_characteristics(df, numeric_cols, anomaly_binary, data_index):
    """Analyze characteristics of anomalous vs normal points."""
    normal_mask = anomaly_binary == 0
    anomaly_mask = anomaly_binary == 1
    
    normal_data = df.loc[data_index[normal_mask], numeric_cols]
    anomaly_data = df.loc[data_index[anomaly_mask], numeric_cols]
    
    stats = {
        "normal_points": {
            "count": len(normal_data),
            "mean_values": normal_data.mean().to_dict() if len(normal_data) > 0 else {},
            "std_values": normal_data.std().to_dict() if len(normal_data) > 0 else {}
        },
        "anomalous_points": {
            "count": len(anomaly_data),
            "mean_values": anomaly_data.mean().to_dict() if len(anomaly_data) > 0 else {},
            "std_values": anomaly_data.std().to_dict() if len(anomaly_data) > 0 else {}
        }
    }
    
    # Calculate difference in means
    if len(normal_data) > 0 and len(anomaly_data) > 0:
        mean_differences = {}
        for col in numeric_cols:
            normal_mean = normal_data[col].mean()
            anomaly_mean = anomaly_data[col].mean()
            mean_differences[col] = {
                "absolute_difference": abs(anomaly_mean - normal_mean),
                "percentage_difference": abs((anomaly_mean - normal_mean) / normal_mean * 100) if normal_mean != 0 else 0
            }
        stats["mean_differences"] = mean_differences
    
    return stats
