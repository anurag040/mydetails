import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { 
  DatasetInfo, 
  StatisticsRequest, 
  AdvancedStatsRequest,
  BasicStatsResponse, 
  AdvancedStatsResponse,
  ChatMessage,
  ChatResponse,
  AnalysisResponse
} from '../models/api.models';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  // Talk to My Data endpoints
  talkToData(datasetId: string, query: string, column?: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/talk-to-data`, {
      dataset_id: datasetId,
      query,
      column
    });
  }

  talkToDataPlot(datasetId: string, plotType: string, column?: string, window?: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/talk-to-data/plot`, {
      dataset_id: datasetId,
      query: `Create ${plotType} visualization`,  // Required field
      plot_type: plotType,
      column,
      window
    });
  }
  private baseUrl = environment.apiUrl || 'http://localhost:8000/api/v1';

  constructor(private http: HttpClient) { }

  // Health check
  checkHealth(): Observable<{status: string, message: string}> {
    return this.http.get<{status: string, message: string}>(`http://localhost:8000/health`);
  }

  // Upload endpoints
  uploadFile(file: File): Observable<DatasetInfo> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<DatasetInfo>(`${this.baseUrl}/upload`, formData);
  }

  getDatasets(): Observable<{datasets: DatasetInfo[]}> {
    return this.http.get<{datasets: DatasetInfo[]}>(`${this.baseUrl}/datasets`);
  }

  getDatasetInfo(datasetId: string): Observable<DatasetInfo> {
    return this.http.get<DatasetInfo>(`${this.baseUrl}/dataset/${datasetId}`);
  }

  deleteDataset(datasetId: string): Observable<{message: string}> {
    return this.http.delete<{message: string}>(`${this.baseUrl}/dataset/${datasetId}`);
  }

  previewDataset(datasetId: string, rows: number = 10): Observable<any> {
    return this.http.get(`${this.baseUrl}/dataset/${datasetId}/preview?rows=${rows}`);
  }

  // Statistics endpoints
  calculateBasicStats(request: StatisticsRequest): Observable<BasicStatsResponse> {
    return this.http.post<BasicStatsResponse>(`${this.baseUrl}/statistics/basic`, request);
  }

  calculateAdvancedStats(request: AdvancedStatsRequest): Observable<AdvancedStatsResponse> {
    return this.http.post<AdvancedStatsResponse>(`${this.baseUrl}/statistics/advanced`, request);
  }

  getBasicStatsOptions(): Observable<any> {
    return this.http.get(`${this.baseUrl}/statistics/options/basic`);
  }

  getAdvancedStatsOptions(): Observable<any> {
    return this.http.get(`${this.baseUrl}/statistics/options/advanced`);
  }

  getBasicStatisticsOptions(): Observable<any> {
    return this.http.get(`${this.baseUrl}/statistics/options/basic`);
  }

  getAdvancedStatisticsOptions(): Observable<any> {
    return this.http.get(`${this.baseUrl}/statistics/options/advanced`);
  }

  getStatisticsSummary(datasetId: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/statistics/${datasetId}/summary`);
  }

  // Regression Analysis endpoint
  performRegressionAnalysis(datasetId: string, xColumn: string, yColumn: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/advanced/regression`, {
      dataset_id: datasetId,
      x_column: xColumn,
      y_column: yColumn
    });
  }

  // Analysis endpoints
  performFullAnalysis(datasetId: string): Observable<AnalysisResponse> {
    return this.http.post<AnalysisResponse>(`${this.baseUrl}/analysis/full`, { dataset_id: datasetId });
  }

  generateInsights(datasetId: string, focusAreas?: string[]): Observable<any> {
    return this.http.post(`${this.baseUrl}/analysis/insights`, { 
      dataset_id: datasetId, 
      focus_areas: focusAreas 
    });
  }

  getValidationMetrics(datasetId: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/analysis/${datasetId}/validation`);
  }

  validateCustomAnalysis(datasetId: string, customAnalysis: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/analysis/validate`, {
      dataset_id: datasetId,
      custom_analysis: customAnalysis
    });
  }

  getAnalysisOptions(): Observable<any> {
    return this.http.get(`${this.baseUrl}/analysis/options`);
  }

  // Chat endpoints
  chatWithData(message: ChatMessage): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.baseUrl}/chat`, message);
  }

  getChatHistory(datasetId: string, limit: number = 50): Observable<any> {
    return this.http.get(`${this.baseUrl}/chat/${datasetId}/history?limit=${limit}`);
  }

  clearChatHistory(datasetId: string): Observable<{message: string}> {
    return this.http.delete<{message: string}>(`${this.baseUrl}/chat/${datasetId}/history`);
  }

  getChatSuggestions(datasetId: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/chat/suggestions`, { dataset_id: datasetId });
  }

  getChatCapabilities(): Observable<any> {
    return this.http.get(`${this.baseUrl}/chat/capabilities`);
  }

  // Clustering Analysis endpoints
  performClusteringAnalysis(datasetId: string, method: string = 'kmeans', nClusters?: number, columns?: string[]): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/clustering/analyze`, {
      file_id: datasetId,
      method: method,
      n_clusters: nClusters,
      columns: columns
    });
  }

  // Anomaly Detection endpoints
  performAnomalyDetection(datasetId: string, method: string = 'isolation_forest', contamination: number = 0.1, columns?: string[]): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/anomaly-detection/analyze`, {
      file_id: datasetId,
      method: method,
      contamination: contamination,
      columns: columns
    });
  }
}
