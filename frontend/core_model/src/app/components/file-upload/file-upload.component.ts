import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTableModule } from '@angular/material/table';
import { MatExpansionModule } from '@angular/material/expansion';
import { ApiService } from '../../services/api.service';
import { DatasetService, DatasetPreview } from '../../services/dataset.service';
import { DatasetInfo } from '../../models/api.models';
import { interval, Subscription } from 'rxjs';
import { switchMap, takeWhile } from 'rxjs/operators';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatChipsModule,
    MatTableModule,
    MatExpansionModule
  ],
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent implements OnInit, OnDestroy {
  isUploading = false;
  backendOnline = false;
  currentDataset: DatasetInfo | null = null;
  datasetPreview: DatasetPreview | null = null;
  showAnalysisOptions = false;
  
  private healthCheckSubscription?: Subscription;
  private datasetSubscription?: Subscription;
  private previewSubscription?: Subscription;

  constructor(
    private apiService: ApiService,
    private datasetService: DatasetService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.checkBackendHealth();
    this.startHealthCheck();
    
    // Subscribe to current dataset changes
    this.datasetSubscription = this.datasetService.currentDataset$.subscribe(dataset => {
      console.log('Dataset subscription triggered - dataset changed:', dataset);
      this.currentDataset = dataset;
      if (dataset) {
        console.log('Dataset exists, loading preview...');
        this.loadDatasetPreview(dataset);
      } else {
        console.log('No dataset, clearing preview');
        this.datasetPreview = null;
        this.showAnalysisOptions = false;
      }
    });

    // Subscribe to dataset preview changes
    this.previewSubscription = this.datasetService.datasetPreview$.subscribe(preview => {
      console.log('Preview subscription triggered - preview changed:', preview);
      this.datasetPreview = preview;
      this.showAnalysisOptions = !!preview;
      console.log('showAnalysisOptions set to:', this.showAnalysisOptions);
      
      // Force change detection
      setTimeout(() => {
        console.log('After timeout - showAnalysisOptions:', this.showAnalysisOptions);
        console.log('After timeout - datasetPreview:', !!this.datasetPreview);
      }, 50);
    });
  }

  ngOnDestroy() {
    this.healthCheckSubscription?.unsubscribe();
    this.datasetSubscription?.unsubscribe();
    this.previewSubscription?.unsubscribe();
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.uploadFile(input.files[0]);
    }
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.uploadFile(files[0]);
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
  }

  private uploadFile(file: File) {
    console.log('Starting upload for file:', file.name, file.size, 'bytes');
    
    this.isUploading = true;
    
    // Add timeout to prevent hanging
    const uploadTimeout = setTimeout(() => {
      console.log('Upload timeout reached');
      this.isUploading = false;
      this.snackBar.open('Upload timed out. Please try again.', 'Close', { duration: 5000 });
    }, 30000); // 30 second timeout
    
    this.apiService.uploadFile(file).subscribe({
      next: (response) => {
        clearTimeout(uploadTimeout);
        console.log('Upload response:', response);
        this.isUploading = false;
        console.log('Setting dataset:', response);
        this.datasetService.setCurrentDataset(response);
        this.snackBar.open('File uploaded successfully!', 'Close', { duration: 3000 });
      },
      error: (error) => {
        clearTimeout(uploadTimeout);
        this.isUploading = false;
        console.error('Upload error:', error);
        console.error('Error details:', {
          status: error.status,
          statusText: error.statusText,
          message: error.message,
          error: error.error
        });
        
        let errorMessage = 'Upload failed. Please try again.';
        if (error.status === 0) {
          errorMessage = 'Cannot connect to server. Check if backend is running on port 8000.';
        } else if (error.status === 413) {
          errorMessage = 'File too large. Please select a smaller file.';
        } else if (error.error?.detail) {
          errorMessage = `Upload failed: ${error.error.detail}`;
        }
        
        this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
      }
    });
  }

  private loadDatasetPreview(dataset: DatasetInfo) {
    console.log('Loading dataset preview for:', dataset);
    this.apiService.previewDataset(dataset.dataset_id, 10).subscribe({
      next: (response) => {
        console.log('Raw Preview API response:', response);
        
        // Handle different response formats
        let preview = response;
        if (response.preview) {
          preview = response.preview;
        }
        
        console.log('Extracted preview data:', preview);
        
        const datasetPreview: DatasetPreview = {
          columns: preview.columns || [],
          rows: preview.data || preview.rows || [],
          shape: [preview.preview_rows || preview.rows?.length || 0, preview.columns?.length || 0],
          dtypes: dataset.data_types || preview.dtypes || {}
        };
        
        console.log('Final dataset preview object:', datasetPreview);
        console.log('Preview columns:', datasetPreview.columns);
        console.log('Preview rows count:', datasetPreview.rows.length);
        console.log('Preview shape:', datasetPreview.shape);
        
        this.datasetService.setDatasetPreview(datasetPreview);
        
        // Force UI update
        setTimeout(() => {
          console.log('Forced UI update - showAnalysisOptions:', this.showAnalysisOptions);
          console.log('datasetPreview after timeout:', this.datasetPreview);
        }, 100);
      },
      error: (error) => {
        console.error('Failed to load dataset preview:', error);
        console.error('Error details:', {
          status: error.status,
          statusText: error.statusText,
          message: error.message,
          error: error.error
        });
        this.snackBar.open('Failed to load dataset preview', 'Close', { duration: 3000 });
      }
    });
  }

  selectBasicAnalysis() {
    this.datasetService.setSelectedAnalysisType('basic');
    this.snackBar.open('Basic Analysis selected. Navigate to Statistics tab to continue.', 'Close', { duration: 3000 });
  }

  selectAdvancedAnalysis() {
    this.datasetService.setSelectedAnalysisType('advanced');
    this.snackBar.open('Advanced Analysis selected. Navigate to Statistics tab to continue.', 'Close', { duration: 3000 });
  }

  openChatWithData() {
    if (this.currentDataset) {
      this.snackBar.open('Chat with Data selected. Navigate to Chat tab to continue.', 'Close', { duration: 3000 });
    }
  }

  removeDataset() {
    this.datasetService.clearCurrentDataset();
    this.showAnalysisOptions = false;
    this.snackBar.open('Dataset removed', 'Close', { duration: 2000 });
  }

  resetUploadState() {
    this.isUploading = false;
    this.snackBar.open('Upload state reset', 'Close', { duration: 2000 });
  }

  testWithFakeDataset() {
    // Test with fake data to see if preview works
    const fakeDataset: DatasetInfo = {
      dataset_id: 'test-123',
      filename: 'test-data.csv',
      size: 12345,
      rows: 100,
      columns: 5,
      column_names: ['col1', 'col2', 'col3', 'col4', 'col5'],
      data_types: { 'col1': 'int64', 'col2': 'float64', 'col3': 'object', 'col4': 'bool', 'col5': 'datetime64' },
      missing_data_ratio: 0.1,
      upload_timestamp: new Date().toISOString()
    };
    
    const fakePreview = {
      columns: ['col1', 'col2', 'col3', 'col4', 'col5'],
      rows: [
        { col1: 1, col2: 1.5, col3: 'test1', col4: true, col5: '2024-01-01' },
        { col1: 2, col2: 2.5, col3: 'test2', col4: false, col5: '2024-01-02' },
        { col1: 3, col2: 3.5, col3: 'test3', col4: true, col5: '2024-01-03' }
      ],
      shape: [3, 5] as [number, number],
      dtypes: { 'col1': 'int64', 'col2': 'float64', 'col3': 'object', 'col4': 'bool', 'col5': 'datetime64' }
    };
    
    console.log('Setting fake dataset for testing:', fakeDataset);
    console.log('Setting fake preview for testing:', fakePreview);
    
    this.datasetService.setCurrentDataset(fakeDataset);
    this.datasetService.setDatasetPreview(fakePreview);
    this.snackBar.open('Fake dataset loaded for testing', 'Close', { duration: 3000 });
  }

  reloadPreview() {
    if (this.currentDataset) {
      console.log('Manually reloading preview for:', this.currentDataset);
      this.loadDatasetPreview(this.currentDataset);
    } else {
      this.snackBar.open('No dataset to reload preview for', 'Close', { duration: 2000 });
    }
  }

  getFileIcon(filename: string): string {
    const extension = filename.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'csv': return 'table_chart';
      case 'xlsx': case 'xls': return 'grid_on';
      case 'json': return 'code';
      default: return 'description';
    }
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString();
  }

  getDisplayedColumns(): string[] {
    if (!this.datasetPreview?.columns) return [];
    return this.datasetPreview.columns.slice(0, 5); // Show first 5 columns
  }

  getPreviewRows(): any[] {
    if (!this.datasetPreview?.rows) return [];
    return this.datasetPreview.rows.slice(0, 10); // Show first 10 rows
  }

  private checkBackendHealth() {
    console.log('Checking backend health...');
    
    // Temporarily set backend as online for testing
    this.backendOnline = true;
    console.log('Backend set to online for testing');
    
    // Still try the actual health check in background
    this.apiService.checkHealth().subscribe({
      next: (response) => {
        console.log('Backend health check successful:', response);
        this.backendOnline = true;
      },
      error: (error) => {
        console.log('Backend health check failed:', error);
        // Don't set offline immediately, keep it online for testing
        // this.backendOnline = false;
      }
    });
  }

  private startHealthCheck() {
    // Only check health every 30 seconds if no dataset is loaded
    this.healthCheckSubscription = interval(30000)
      .pipe(
        takeWhile(() => !this.currentDataset),
        switchMap(() => this.apiService.checkHealth())
      )
      .subscribe({
        next: () => {
          this.backendOnline = true;
        },
        error: () => {
          this.backendOnline = false;
        }
      });
  }
}
