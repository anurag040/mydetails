import { Component, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ApiService } from '../../services/api.service';

interface AnalysisScore {
  methodology_score: number;
  completeness_score: number;
  accuracy_score: number;
  interpretation_score: number;
  overall_score: number;
}

interface AnalysisRecord {
  id: string;
  analysis_type: string;
  timestamp: string;
  user_query: string;
  method_used: string;
  score: AnalysisScore;
  recommendations: string[];
  warnings: string[];
}

interface AnalysisMatrix {
  dataset_id: string;
  total_analyses: number;
  overall_quality_score: number;
  analysis_records: AnalysisRecord[];
  coverage_matrix: { [key: string]: boolean };
  recommendations: string[];
}

@Component({
  selector: 'app-analysis-matrix',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './analysis-matrix.component.html',
  styleUrls: ['./analysis-matrix.component.scss']
})
export class AnalysisMatrixComponent implements OnInit {
  @Input() datasetId: string = '';
  
  matrix: AnalysisMatrix | null = null;
  report: any = null;
  loading = false;
  error = '';
  
  // Analysis type display names
  analysisTypeNames: { [key: string]: string } = {
    'descriptive_statistics': 'Descriptive Stats',
    'correlation_analysis': 'Correlation',
    'distribution_analysis': 'Distribution',
    'missing_data_analysis': 'Missing Data',
    'outlier_detection': 'Outliers',
    'trend_analysis': 'Trends',
    'bollinger_bands': 'Bollinger Bands',
    'regression_analysis': 'Regression',
    'clustering_analysis': 'Clustering',
    'hypothesis_testing': 'Hypothesis Tests'
  };

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    if (this.datasetId) {
      this.loadAnalysisMatrix();
      this.loadAnalysisReport();
    }
  }

  async loadAnalysisMatrix() {
    this.loading = true;
    this.error = '';
    
    try {
      const response = await this.apiService.getAnalysisMatrix(this.datasetId).toPromise();
      if (response.success) {
        this.matrix = response.data;
      } else {
        this.error = response.message;
      }
    } catch (err: any) {
      this.error = err.error?.detail || 'Failed to load analysis matrix';
    } finally {
      this.loading = false;
    }
  }

  async loadAnalysisReport() {
    try {
      const response = await this.apiService.getAnalysisReport(this.datasetId).toPromise();
      if (response.success) {
        this.report = response.data;
      }
    } catch (err) {
      console.error('Failed to load analysis report:', err);
    }
  }

  getScoreColor(score: number): string {
    if (score >= 80) return '#00ff88'; // Green
    if (score >= 60) return '#ffaa00'; // Orange
    return '#ff4444'; // Red
  }

  getScoreLabel(score: number): string {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  }

  getCoveragePercentage(): number {
    if (!this.matrix) return 0;
    const total = Object.keys(this.matrix.coverage_matrix).length;
    const covered = Object.values(this.matrix.coverage_matrix).filter(v => v).length;
    return Math.round((covered / total) * 100);
  }

  getAnalysisTypeName(type: string): string {
    return this.analysisTypeNames[type] || type.replace(/_/g, ' ');
  }

  formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }

  refreshMatrix() {
    this.loadAnalysisMatrix();
    this.loadAnalysisReport();
  }
}
