export interface DatasetInfo {
  dataset_id: string;
  filename: string;
  size: number;
  rows: number;
  columns: number;
  column_names: string[];
  data_types: { [key: string]: string };
  missing_data_ratio: number;
  upload_timestamp: string;
}

export interface StatisticsRequest {
  dataset_id: string;
  options: string[];
}

export interface AdvancedStatsRequest {
  dataset_id: string;
  options: string[];
}

export interface BasicStatsResponse {
  dataset_id: string;
  descriptive_stats?: any;
  correlation_matrix?: any;
  distribution_analysis?: any;
  missing_data_summary?: any;
  missing_value_analysis?: any;
  duplicates_analysis?: any;
  type_integrity_validation?: any;
  univariate_summaries?: any;
  outlier_detection?: any;
}

export interface AdvancedStatsResponse {
  dataset_id: string;
  regression_analysis?: any;
  clustering_results?: any;
  pca_analysis?: any;
  time_series_analysis?: any;
  anomaly_detection?: any;
}

export interface ChatMessage {
  message: string;
  dataset_id: string;
}

export interface ChatResponse {
  response: string;
  dataset_id: string;
  timestamp: string;
  context_used: string[];
}

export interface ValidationMetrics {
  statistical_accuracy: number;
  missing_data_accuracy: number;
  insight_relevance: number;
  completeness: number;
  consistency: number;
  composite_score: number;
  justifications: { [key: string]: string };
}

export interface AnalysisResponse {
  dataset_id: string;
  llm_insights: string;
  validation_metrics: ValidationMetrics;
  recommendations: string[];
  timestamp: string;
}

export interface UploadResponse {
  dataset_id: string;
  filename: string;
  message: string;
}
