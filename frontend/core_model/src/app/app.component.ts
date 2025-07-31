import { Component } from '@angular/core';
import { MatTabChangeEvent } from '@angular/material/tabs';
import { DatasetInfo } from './models/api.models';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'data-analysis-app';
  selectedTabIndex = 0;
  selectedDatasetId: string | null = null;
  selectedDataset: DatasetInfo | null = null;

  onTabChange(event: MatTabChangeEvent) {
    this.selectedTabIndex = event.index;
  }

  onFileUploaded(dataset: DatasetInfo) {
    this.selectedDataset = dataset;
    this.selectedDatasetId = dataset.filename; // You might want to use a proper ID
    this.selectedTabIndex = 1; // Switch to Basic Statistics tab
  }

  onDatasetSelected(dataset: DatasetInfo) {
    this.selectedDataset = dataset;
    this.selectedDatasetId = dataset.filename; // You might want to use a proper ID
  }

  formatFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }
}
