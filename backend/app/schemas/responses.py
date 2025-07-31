from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class DatasetInfo(BaseModel):
    dataset_id: str
    filename: str
    size: int
    rows: int
    columns: int
    column_names: List[str]
    data_types: Dict[str, str]
    missing_data_ratio: float
    upload_timestamp: datetime

class StatisticsRequest(BaseModel):
    dataset_id: str
    options: List[str]  # ["descriptive", "correlation", "distribution", etc.]

class BasicStatsResponse(BaseModel):
    dataset_id: str
    descriptive_stats: Optional[Dict[str, Any]] = None
    correlation_matrix: Optional[Dict[str, Any]] = None
    distribution_analysis: Optional[Dict[str, Any]] = None
    missing_data_summary: Optional[Dict[str, Any]] = None

class AdvancedStatsRequest(BaseModel):
    dataset_id: str
    options: List[str]  # ["regression", "clustering", "pca", "time_series", etc.]

class AdvancedStatsResponse(BaseModel):
    dataset_id: str
    regression_analysis: Optional[Dict[str, Any]] = None
    clustering_results: Optional[Dict[str, Any]] = None
    pca_analysis: Optional[Dict[str, Any]] = None
    time_series_analysis: Optional[Dict[str, Any]] = None
    anomaly_detection: Optional[Dict[str, Any]] = None

class ChatMessage(BaseModel):
    message: str
    dataset_id: str

class ChatResponse(BaseModel):
    response: str
    dataset_id: str
    timestamp: datetime
    context_used: List[str]

class ValidationMetrics(BaseModel):
    statistical_accuracy: float
    missing_data_accuracy: float
    insight_relevance: float
    completeness: float
    consistency: float
    composite_score: float
    justifications: Dict[str, str]

class AnalysisResponse(BaseModel):
    dataset_id: str
    llm_insights: str
    validation_metrics: ValidationMetrics
    recommendations: List[str]
    timestamp: datetime
