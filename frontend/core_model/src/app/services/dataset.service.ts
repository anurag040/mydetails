import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { DatasetInfo } from '../models/api.models';

export interface AnalysisStep {
  id: string;
  name: string;
  description: string;
  completed: boolean;
  type: 'basic' | 'advanced' | 'visualization' | 'ml';
  requirements?: string;
}

export interface DatasetPreview {
  columns: string[];
  rows: any[];
  shape: [number, number];
  dtypes: { [key: string]: string };
}

export interface WorkflowStep {
  id: 'upload' | 'preview' | 'select_analysis' | 'analysis' | 'results';
  name: string;
  completed: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class DatasetService {
  private currentDatasetSubject = new BehaviorSubject<DatasetInfo | null>(null);
  private datasetPreviewSubject = new BehaviorSubject<DatasetPreview | null>(null);
  private analysisStepsSubject = new BehaviorSubject<AnalysisStep[]>([]);
  private analysisResultsSubject = new BehaviorSubject<any>({});
  private selectedAnalysisTypeSubject = new BehaviorSubject<'basic' | 'advanced' | null>(null);
  private workflowStepsSubject = new BehaviorSubject<WorkflowStep[]>([
    { id: 'upload', name: 'Upload Dataset', completed: false },
    { id: 'preview', name: 'Preview Data', completed: false },
    { id: 'select_analysis', name: 'Select Analysis', completed: false },
    { id: 'analysis', name: 'Run Analysis', completed: false },
    { id: 'results', name: 'View Results', completed: false }
  ]);

  public currentDataset$: Observable<DatasetInfo | null> = this.currentDatasetSubject.asObservable();
  public datasetPreview$ = this.datasetPreviewSubject.asObservable();
  public analysisSteps$ = this.analysisStepsSubject.asObservable();
  public analysisResults$ = this.analysisResultsSubject.asObservable();
  public selectedAnalysisType$ = this.selectedAnalysisTypeSubject.asObservable();
  public workflowSteps$ = this.workflowStepsSubject.asObservable();

  constructor() { }

  setCurrentDataset(dataset: DatasetInfo | null): void {
    this.currentDatasetSubject.next(dataset);
    if (dataset) {
      this.initializeAnalysisSteps(dataset);
      this.updateWorkflowStep('upload', true);
    } else {
      this.clearAllState();
    }
  }

  setDatasetPreview(preview: DatasetPreview): void {
    this.datasetPreviewSubject.next(preview);
    this.updateWorkflowStep('preview', true);
  }

  setSelectedAnalysisType(type: 'basic' | 'advanced'): void {
    this.selectedAnalysisTypeSubject.next(type);
    this.updateWorkflowStep('select_analysis', true);
  }

  getCurrentDataset(): DatasetInfo | null {
    return this.currentDatasetSubject.value;
  }

  getDatasetPreview(): DatasetPreview | null {
    return this.datasetPreviewSubject.value;
  }

  getSelectedAnalysisType(): 'basic' | 'advanced' | null {
    return this.selectedAnalysisTypeSubject.value;
  }

  clearCurrentDataset(): void {
    this.setCurrentDataset(null);
  }

  updateAnalysisStep(stepId: string, completed: boolean): void {
    const steps = this.analysisStepsSubject.value.map(step => 
      step.id === stepId ? { ...step, completed } : step
    );
    this.analysisStepsSubject.next(steps);
  }

  addAnalysisResult(stepId: string, result: any): void {
    const currentResults = this.analysisResultsSubject.value;
    this.analysisResultsSubject.next({
      ...currentResults,
      [stepId]: result
    });
    this.updateAnalysisStep(stepId, true);
    
    // Check if all analysis is complete
    const allCompleted = this.analysisStepsSubject.value.every(step => step.completed);
    if (allCompleted) {
      this.updateWorkflowStep('analysis', true);
      this.updateWorkflowStep('results', true);
    }
  }

  getAnalysisResult(stepId: string): any {
    return this.analysisResultsSubject.value[stepId];
  }

  // Get the dataset ID from the dataset info
  getDatasetId(dataset: DatasetInfo): string {
    return dataset.dataset_id;
  }

  private updateWorkflowStep(stepId: string, completed: boolean): void {
    const steps = this.workflowStepsSubject.value.map(step => 
      step.id === stepId ? { ...step, completed } : step
    );
    this.workflowStepsSubject.next(steps);
  }

  private clearAllState(): void {
    this.datasetPreviewSubject.next(null);
    this.analysisStepsSubject.next([]);
    this.analysisResultsSubject.next({});
    this.selectedAnalysisTypeSubject.next(null);
    const resetSteps = this.workflowStepsSubject.value.map(step => ({ ...step, completed: false }));
    this.workflowStepsSubject.next(resetSteps);
  }

  private initializeAnalysisSteps(dataset: DatasetInfo): void {
    const basicSteps: AnalysisStep[] = [
      {
        id: 'basic_stats',
        name: 'Basic Statistics',
        description: 'Mean, median, mode, std dev, min, max for all columns',
        completed: false,
        type: 'basic',
        requirements: 'Numeric columns'
      },
      {
        id: 'data_types',
        name: 'Data Types Summary',
        description: 'Column names, types, and missing value counts',
        completed: false,
        type: 'basic',
        requirements: 'Any dataset'
      },
      {
        id: 'data_quality',
        name: 'Data Quality Analysis',
        description: 'LLM-powered assessment of data types, missing values',
        completed: false,
        type: 'basic',
        requirements: 'Uploaded dataset'
      },
      {
        id: 'distribution_plots',
        name: 'Distribution Plots',
        description: 'Histograms with skewness analysis',
        completed: false,
        type: 'visualization',
        requirements: 'Numeric columns'
      },
      {
        id: 'correlation_heatmap',
        name: 'Correlation Heatmap',
        description: 'Visual correlation matrix',
        completed: false,
        type: 'visualization',
        requirements: '≥2 numeric columns'
      }
    ];

    const advancedSteps: AnalysisStep[] = [
      {
        id: 'advanced_stats',
        name: 'Skewness & Kurtosis',
        description: 'Distribution shape analysis',
        completed: false,
        type: 'advanced',
        requirements: 'Numeric columns'
      },
      {
        id: 'pca_analysis',
        name: 'PCA Analysis',
        description: 'Principal Component Analysis with explained variance',
        completed: false,
        type: 'advanced',
        requirements: '≥2 numeric columns'
      },
      {
        id: 'outlier_detection',
        name: 'Outlier Detection',
        description: 'Z-score and IQR methods for anomaly detection',
        completed: false,
        type: 'advanced',
        requirements: 'Numeric columns'
      },
      {
        id: 'clustering',
        name: 'K-Means Clustering',
        description: 'Silhouette scores for different cluster numbers',
        completed: false,
        type: 'ml',
        requirements: '≥2 numeric columns'
      },
      {
        id: 'feature_importance',
        name: 'Feature Importance',
        description: 'LLM-driven feature significance analysis',
        completed: false,
        type: 'ml',
        requirements: 'Any dataset'
      },
      {
        id: 'feature_engineering_ideas',
        name: 'Feature Engineering Ideas',
        description: 'Generate feature engineering suggestions based on data characteristics',
        completed: false,
        type: 'ml',
        requirements: 'Any dataset'
      },
      {
        id: 'spearman_correlation',
        name: 'Spearman Correlation',
        description: 'Non-parametric correlation analysis',
        completed: false,
        type: 'advanced',
        requirements: '≥2 numeric columns'
      }
    ];

    // Only include relevant steps based on dataset characteristics
    let steps = [...basicSteps];
    
    // Add advanced steps if dataset has numeric columns
    const numericColumns = dataset.column_names?.filter(col => 
      dataset.data_types?.[col]?.includes('int') || 
      dataset.data_types?.[col]?.includes('float')
    ) || [];

    if (numericColumns.length >= 2) {
      steps = [...steps, ...advancedSteps];
    }

    this.analysisStepsSubject.next(steps);
  }

  getBasicAnalysisOptions(): AnalysisStep[] {
    return this.analysisStepsSubject.value.filter(step => 
      step.type === 'basic' || step.type === 'visualization'
    );
  }

  getAdvancedAnalysisOptions(): AnalysisStep[] {
    return this.analysisStepsSubject.value.filter(step => 
      step.type === 'advanced' || step.type === 'ml'
    );
  }
}
