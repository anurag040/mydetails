import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTableModule } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { DatasetService } from '../../services/dataset.service';
import { DatasetInfo, BasicStatsResponse, AdvancedStatsResponse, AdvancedStatsRequest } from '../../models/api.models';
import { Subscription } from 'rxjs';

interface StatOption {
  id: string;
  name: string;
  description: string;
  selected: boolean;
}

@Component({
  selector: 'app-statistics-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatTabsModule,
    MatTableModule,
    MatExpansionModule,
    MatCheckboxModule,
    FormsModule
  ],
  templateUrl: './statistics-dashboard.component.html',
  styleUrls: ['./statistics-dashboard.component.scss']
})
export class StatisticsDashboardComponent implements OnInit, OnDestroy {
  currentDataset: DatasetInfo | null = null;
  selectedAnalysisType: 'basic' | 'advanced' | null = null;
  isLoading = false;
  
  // Statistics options
  basicOptions: StatOption[] = [];
  advancedOptions: StatOption[] = [];
  
  // Results
  basicResults: BasicStatsResponse | null = null;
  advancedResults: AdvancedStatsResponse | null = null;
  quickSummary: any = null;
  
  private subscriptions: Subscription[] = [];

  constructor(
    private apiService: ApiService,
    private datasetService: DatasetService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    // Subscribe to current dataset
    this.subscriptions.push(
      this.datasetService.currentDataset$.subscribe(dataset => {
        this.currentDataset = dataset;
        if (dataset) {
          this.loadQuickSummary();
        }
      })
    );

    // Subscribe to selected analysis type
    this.subscriptions.push(
      this.datasetService.selectedAnalysisType$.subscribe(type => {
        this.selectedAnalysisType = type;
      })
    );

    // Load statistics options
    this.loadStatisticsOptions();
  }

  ngOnDestroy() {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  private loadStatisticsOptions() {
    // Load basic statistics options
    this.apiService.getBasicStatisticsOptions().subscribe({
      next: (response) => {
        this.basicOptions = response.options.map((opt: any) => ({
          ...opt,
          selected: true // Pre-select all options
        }));
      },
      error: (error) => {
        console.error('Failed to load basic options:', error);
      }
    });

    // Load advanced statistics options
    this.apiService.getAdvancedStatisticsOptions().subscribe({
      next: (response) => {
        this.advancedOptions = response.options.map((opt: any) => ({
          ...opt,
          selected: true // Pre-select all options
        }));
      },
      error: (error) => {
        console.error('Failed to load advanced options:', error);
      }
    });
  }

  private loadQuickSummary() {
    if (!this.currentDataset) return;

    this.apiService.getStatisticsSummary(this.currentDataset.dataset_id).subscribe({
      next: (summary) => {
        this.quickSummary = summary;
      },
      error: (error) => {
        console.error('Failed to load quick summary:', error);
      }
    });
  }

  calculateBasicStatistics() {
    if (!this.currentDataset) {
      this.snackBar.open('No dataset selected', 'Close', { duration: 3000 });
      return;
    }

    const selectedOptions = this.basicOptions.filter(opt => opt.selected).map(opt => opt.id);
    if (selectedOptions.length === 0) {
      this.snackBar.open('Please select at least one option', 'Close', { duration: 3000 });
      return;
    }

    this.isLoading = true;
    this.apiService.calculateBasicStats({
      dataset_id: this.currentDataset.dataset_id,
      options: selectedOptions
    }).subscribe({
      next: (results) => {
        this.basicResults = results;
        this.isLoading = false;
        this.snackBar.open('Basic statistics calculated successfully!', 'Close', { duration: 3000 });
      },
      error: (error) => {
        console.error('Failed to calculate basic statistics:', error);
        this.isLoading = false;
        this.snackBar.open('Failed to calculate statistics', 'Close', { duration: 5000 });
      }
    });
  }

  calculateAdvancedStatistics() {
    if (!this.currentDataset) {
      this.snackBar.open('No dataset selected', 'Close', { duration: 3000 });
      return;
    }

    const selectedOptions = this.advancedOptions.filter(opt => opt.selected).map(opt => opt.id);
    if (selectedOptions.length === 0) {
      this.snackBar.open('Please select at least one option', 'Close', { duration: 3000 });
      return;
    }

    this.isLoading = true;
    const request: AdvancedStatsRequest = {
      dataset_id: this.currentDataset.dataset_id,
      options: selectedOptions
    };
    
    this.apiService.calculateAdvancedStats(request).subscribe({
      next: (results) => {
        this.advancedResults = results;
        this.isLoading = false;
        this.snackBar.open('Advanced statistics calculated successfully!', 'Close', { duration: 3000 });
      },
      error: (error) => {
        console.error('Failed to calculate advanced statistics:', error);
        this.isLoading = false;
        this.snackBar.open('Failed to calculate advanced statistics', 'Close', { duration: 5000 });
      }
    });
  }

  getDescriptiveStatsKeys(): string[] {
    return this.basicResults?.descriptive_stats ? Object.keys(this.basicResults.descriptive_stats) : [];
  }

  getCorrelationPairs(): any[] {
    if (!this.basicResults?.correlation_matrix?.correlation_pairs) return [];
    return this.basicResults.correlation_matrix.correlation_pairs;
  }

  formatNumber(value: any): string {
    if (typeof value === 'number') {
      return value.toFixed(4);
    }
    return value?.toString() || '';
  }

  getFeatureImportanceEntries(): Array<{key: string, value: number}> {
    if (!this.advancedResults?.regression_analysis?.feature_importance) return [];
    const importance = this.advancedResults.regression_analysis.feature_importance;
    return Object.entries(importance).map(([key, value]) => ({
      key,
      value: typeof value === 'number' ? value : parseFloat(value as string) || 0
    }));
  }

  hasResults(): boolean {
    return !!(this.basicResults || this.advancedResults);
  }
}
