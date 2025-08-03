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
import { NgChartsModule } from 'ng2-charts';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
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
    FormsModule,
    NgChartsModule
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
  
  // Chart configurations
  distributionCharts: Map<string, ChartData<'bar'>> = new Map();
  correlationHeatmapChart: ChartData<'scatter'> | null = null;
  heatmapVariables: string[] = [];
  
  chartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: '#00ff7f',
          font: {
            size: 12,
            weight: 'bold'
          },
          usePointStyle: true
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        titleColor: '#00ff7f',
        bodyColor: '#ffffff',
        borderColor: '#00ff7f',
        borderWidth: 2,
        cornerRadius: 8,
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 12
        },
        callbacks: {
          title: (context) => {
            return `Value Range: ${context[0].label}`;
          },
          label: (context) => {
            return `Frequency: ${context.parsed.y}`;
          },
          afterLabel: (context) => {
            const total = context.dataset.data.reduce((sum: number, val: any) => sum + (typeof val === 'number' ? val : 0), 0);
            const percentage = ((context.parsed.y / total) * 100).toFixed(1);
            return `Percentage: ${percentage}%`;
          }
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#00ff7f',
          font: {
            size: 11,
            weight: 'bold'
          },
          maxRotation: 45,
          minRotation: 45
        },
        grid: {
          color: 'rgba(0, 255, 127, 0.2)',
          lineWidth: 1
        },
        title: {
          display: true,
          text: 'Value Range',
          color: '#00ff7f',
          font: {
            size: 14,
            weight: 'bold'
          }
        },
        border: {
          color: '#00ff7f',
          width: 2
        }
      },
      y: {
        beginAtZero: true,
        ticks: {
          color: '#00ff7f',
          font: {
            size: 11,
            weight: 'bold'
          },
          callback: function(value: any) {
            return Number.isInteger(value) ? value : '';
          }
        },
        grid: {
          color: 'rgba(0, 255, 127, 0.2)',
          lineWidth: 1
        },
        title: {
          display: true,
          text: 'Frequency',
          color: '#00ff7f',
          font: {
            size: 14,
            weight: 'bold'
          }
        },
        border: {
          color: '#00ff7f',
          width: 2
        }
      }
    },
    layout: {
      padding: {
        top: 10,
        bottom: 10,
        left: 10,
        right: 10
      }
    },
    elements: {
      bar: {
        borderWidth: 2,
        borderSkipped: false
      }
    }
  };

  heatmapChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'right',
        labels: {
          color: '#00ff7f',
          usePointStyle: true,
          generateLabels: () => [
            { text: 'Strong Positive (0.7-1.0)', fillStyle: '#00ff88', strokeStyle: '#00ff88' },
            { text: 'Moderate Positive (0.3-0.7)', fillStyle: '#c8e6c9', strokeStyle: '#c8e6c9' },
            { text: 'Weak (-0.3-0.3)', fillStyle: '#666666', strokeStyle: '#666666' },
            { text: 'Moderate Negative (-0.7--0.3)', fillStyle: '#ffb74d', strokeStyle: '#ffb74d' },
            { text: 'Strong Negative (-1.0--0.7)', fillStyle: '#ff6600', strokeStyle: '#ff6600' }
          ]
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        titleColor: '#00ff7f',
        bodyColor: '#ffffff',
        borderColor: '#00ff7f',
        borderWidth: 2,
        cornerRadius: 8,
        callbacks: {
          title: (context: any) => {
            const point = context[0];
            const xVar = this.heatmapVariables[point.parsed.x] || 'Unknown';
            const yVar = this.heatmapVariables[point.parsed.y] || 'Unknown';
            return `${yVar} vs ${xVar}`;
          },
          label: (context: any) => {
            const value = context.parsed.v || 0;
            return `Correlation: ${value.toFixed(3)}`;
          },
          afterLabel: (context: any) => {
            const value = context.parsed.v || 0;
            const absValue = Math.abs(value);
            let strength = '';
            if (absValue >= 0.9) strength = 'Very Strong';
            else if (absValue >= 0.7) strength = 'Strong';
            else if (absValue >= 0.5) strength = 'Moderate';
            else if (absValue >= 0.3) strength = 'Weak';
            else strength = 'Very Weak';
            
            const direction = value > 0 ? 'Positive' : value < 0 ? 'Negative' : 'None';
            return `Strength: ${strength} ${direction}`;
          }
        }
      }
    },
    scales: {
      x: {
        type: 'linear',
        position: 'bottom',
        min: -0.5,
        max: (this.heatmapVariables?.length || 1) - 0.5,
        ticks: {
          color: '#00ff7f',
          font: {
            size: 12,
            weight: 'bold'
          },
          stepSize: 1,
          callback: (value: any) => {
            const index = Math.round(value);
            return this.heatmapVariables?.[index] || '';
          }
        },
        grid: {
          color: 'rgba(0, 255, 127, 0.2)',
          lineWidth: 1
        },
        title: {
          display: true,
          text: 'Variables',
          color: '#00ff7f',
          font: {
            size: 14,
            weight: 'bold'
          }
        }
      },
      y: {
        type: 'linear',
        min: -0.5,
        max: (this.heatmapVariables?.length || 1) - 0.5,
        ticks: {
          color: '#00ff7f',
          font: {
            size: 12,
            weight: 'bold'
          },
          stepSize: 1,
          callback: (value: any) => {
            const index = Math.round(value);
            return this.heatmapVariables?.[index] || '';
          }
        },
        grid: {
          color: 'rgba(0, 255, 127, 0.2)',
          lineWidth: 1
        },
        title: {
          display: true,
          text: 'Variables',
          color: '#00ff7f',
          font: {
            size: 14,
            weight: 'bold'
          }
        }
      }
    }
  };
  
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
        this.processChartData(); // Process the chart data
        this.debugDistributionData(); // Debug the loaded data
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
    // Access the summary object from descriptive_stats
    return this.basicResults?.descriptive_stats?.summary ? Object.keys(this.basicResults.descriptive_stats.summary) : [];
  }

  getDescriptiveStatsData(): any {
    return this.basicResults?.descriptive_stats?.summary || {};
  }

  getAdditionalStatsData(): any {
    return this.basicResults?.descriptive_stats?.additional_stats || {};
  }

  getDescriptiveInsights(): any[] {
    if (!this.basicResults?.descriptive_stats?.summary) return [];
    
    const summary = this.basicResults.descriptive_stats.summary;
    const additional = this.basicResults.descriptive_stats.additional_stats || {};
    const insights: any[] = [];
    
    Object.keys(summary).forEach(column => {
      const stats = summary[column];
      const extraStats = additional[column] || {};
      
      // Generate insights for each column
      const columnInsights = {
        column: column,
        dataDistribution: this.analyzeDataDistribution(stats),
        variability: this.analyzeVariability(stats, extraStats),
        outlierRisk: this.analyzeOutlierRisk(stats),
        businessImplication: this.generateBusinessImplication(column, stats, extraStats)
      };
      
      insights.push(columnInsights);
    });
    
    return insights;
  }

  private analyzeDataDistribution(stats: any): string {
    const mean = stats.mean || 0;
    const median = stats['50%'] || 0;
    const skewness = Math.abs(mean - median) / (stats.std || 1);
    
    if (skewness < 0.1) {
      return "📊 Normally distributed - data is well-balanced around the center";
    } else if (mean > median) {
      return "📈 Right-skewed - has some unusually high values pulling the average up";
    } else {
      return "📉 Left-skewed - has some unusually low values pulling the average down";
    }
  }

  private analyzeVariability(stats: any, extraStats: any): string {
    const cv = extraStats.coefficient_of_variation;
    
    if (!cv || cv === null) {
      return "📏 Variability cannot be assessed (mean is zero)";
    }
    
    if (cv < 0.1) {
      return "🎯 Low variability - values are tightly clustered around the mean";
    } else if (cv < 0.3) {
      return "📊 Moderate variability - reasonable spread of values";
    } else {
      return "🌊 High variability - values are widely dispersed";
    }
  }

  private analyzeOutlierRisk(stats: any): string {
    const q1 = stats['25%'] || 0;
    const q3 = stats['75%'] || 0;
    const iqr = q3 - q1;
    const lowerBound = q1 - 1.5 * iqr;
    const upperBound = q3 + 1.5 * iqr;
    const min = stats.min || 0;
    const max = stats.max || 0;
    
    const hasOutliers = min < lowerBound || max > upperBound;
    
    if (hasOutliers) {
      return "⚠️ Potential outliers detected - may need data cleaning or special attention";
    } else {
      return "✅ No significant outliers - data appears clean and consistent";
    }
  }

  private generateBusinessImplication(column: string, stats: any, extraStats: any): string {
    const range = extraStats.range || 0;
    const mean = stats.mean || 0;
    const std = stats.std || 0;
    
    // Generic business insights based on statistical properties
    const insights = [];
    
    if (std / mean > 0.5) {
      insights.push("High volatility indicates need for risk management");
    }
    
    if (range > mean * 3) {
      insights.push("Wide range suggests diverse scenarios to consider");
    }
    
    if (stats['50%'] && Math.abs(stats.mean - stats['50%']) / stats.mean > 0.2) {
      insights.push("Asymmetric distribution may affect forecasting accuracy");
    }
    
    if (insights.length === 0) {
      insights.push("Stable and predictable pattern suitable for modeling");
    }
    
    return "💡 " + insights.join("; ");
  }

  getCorrelationPairs(): any[] {
    if (!this.basicResults?.correlation_matrix?.strong_correlations) return [];
    return this.basicResults.correlation_matrix.strong_correlations;
  }

  getCorrelationMatrix(): any {
    return this.basicResults?.correlation_matrix?.correlation_matrix || {};
  }

  getCorrelationMatrixEntries(): any[] {
    const matrix = this.getCorrelationMatrix();
    const entries: any[] = [];
    
    Object.keys(matrix).forEach(var1 => {
      Object.keys(matrix[var1]).forEach(var2 => {
        if (var1 !== var2) {
          entries.push({
            var1: var1,
            var2: var2,
            correlation: matrix[var1][var2],
            strength: this.getCorrelationStrength(matrix[var1][var2]),
            interpretation: this.getCorrelationInterpretation(var1, var2, matrix[var1][var2])
          });
        }
      });
    });
    
    // Remove duplicates and sort by absolute correlation value
    const uniqueEntries = entries.filter((entry, index, self) => 
      index === self.findIndex(e => 
        (e.var1 === entry.var1 && e.var2 === entry.var2) || 
        (e.var1 === entry.var2 && e.var2 === entry.var1)
      )
    );
    
    return uniqueEntries.sort((a, b) => Math.abs(b.correlation) - Math.abs(a.correlation));
  }

  getCorrelationStrength(correlation: number): string {
    const abs_corr = Math.abs(correlation);
    if (abs_corr >= 0.9) return 'Very Strong';
    if (abs_corr >= 0.7) return 'Strong';
    if (abs_corr >= 0.5) return 'Moderate';
    if (abs_corr >= 0.3) return 'Weak';
    return 'Very Weak';
  }

  getCorrelationInterpretation(var1: string, var2: string, correlation: number): string {
    const strength = this.getCorrelationStrength(correlation);
    const direction = correlation > 0 ? 'positive' : 'negative';
    const abs_corr = Math.abs(correlation);
    
    let interpretation = `${strength} ${direction} relationship. `;
    
    if (abs_corr >= 0.7) {
      interpretation += direction === 'positive' ? 
        `As ${var1} increases, ${var2} tends to increase significantly.` :
        `As ${var1} increases, ${var2} tends to decrease significantly.`;
    } else if (abs_corr >= 0.5) {
      interpretation += direction === 'positive' ? 
        `${var1} and ${var2} show a noticeable tendency to move together.` :
        `${var1} and ${var2} show a noticeable tendency to move in opposite directions.`;
    } else if (abs_corr >= 0.3) {
      interpretation += `There is a weak relationship between ${var1} and ${var2}.`;
    } else {
      interpretation += `${var1} and ${var2} show little to no linear relationship.`;
    }
    
    return interpretation;
  }

  getCorrelationInsights(): any[] {
    const matrix = this.getCorrelationMatrix();
    if (!Object.keys(matrix).length) return [];
    
    const insights: any[] = [];
    const entries = this.getCorrelationMatrixEntries();
    
    // Overall correlation summary
    const avgCorrelation = this.basicResults?.correlation_matrix?.average_correlation || 0;
    insights.push({
      type: 'overview',
      title: 'Dataset Correlation Overview',
      description: `Average correlation strength: ${Math.abs(avgCorrelation).toFixed(3)}. ${
        Math.abs(avgCorrelation) > 0.5 ? 
        'Variables show strong interconnections - consider multicollinearity.' :
        Math.abs(avgCorrelation) > 0.3 ?
        'Variables show moderate relationships - good for predictive modeling.' :
        'Variables are relatively independent - diverse feature set.'
      }`,
      icon: 'analytics',
      color: Math.abs(avgCorrelation) > 0.7 ? 'warn' : Math.abs(avgCorrelation) > 0.3 ? 'primary' : 'accent'
    });
    
    // Strong correlations insight
    const strongCorrelations = entries.filter(e => Math.abs(e.correlation) >= 0.7);
    if (strongCorrelations.length > 0) {
      insights.push({
        type: 'strong',
        title: `${strongCorrelations.length} Strong Relationship${strongCorrelations.length > 1 ? 's' : ''} Found`,
        description: `Strong correlations may indicate redundant features or important relationships for prediction.`,
        icon: 'link',
        color: 'warn'
      });
    }
    
    // Feature importance insight
    const correlationCounts = Object.keys(matrix).map(variable => ({
      variable,
      strongConnections: entries.filter(e => 
        (e.var1 === variable || e.var2 === variable) && Math.abs(e.correlation) >= 0.5
      ).length
    })).sort((a, b) => b.strongConnections - a.strongConnections);
    
    if (correlationCounts.length > 0 && correlationCounts[0].strongConnections > 0) {
      insights.push({
        type: 'importance',
        title: `${correlationCounts[0].variable} - Most Connected Variable`,
        description: `Has ${correlationCounts[0].strongConnections} strong relationship${correlationCounts[0].strongConnections > 1 ? 's' : ''} with other variables. Key feature for analysis.`,
        icon: 'hub',
        color: 'primary'
      });
    }
    
    return insights;
  }

  getHeatmapColor(correlationOrVar1: number | string, var2?: string): string {
    let correlation: number;
    
    if (typeof correlationOrVar1 === 'string' && var2) {
      // Called with two variable names
      correlation = this.getCorrelationValue(correlationOrVar1, var2);
    } else {
      // Called with correlation value directly
      correlation = correlationOrVar1 as number;
    }
    
    const abs_corr = Math.abs(correlation);
    if (correlation > 0) {
      if (abs_corr >= 0.8) return '#00ff88'; // Strong positive - neon green
      if (abs_corr >= 0.6) return '#4caf50'; // Moderate positive - green
      if (abs_corr >= 0.3) return '#8bc34a'; // Weak positive - light green
      return '#c8e6c9'; // Very weak positive - pale green
    } else {
      if (abs_corr >= 0.8) return '#ff6600'; // Strong negative - neon orange
      if (abs_corr >= 0.6) return '#ff9800'; // Moderate negative - orange
      if (abs_corr >= 0.3) return '#ffb74d'; // Weak negative - light orange
      return '#ffe0b2'; // Very weak negative - pale orange
    }
  }

  getHeatmapVariables(): string[] {
    return Object.keys(this.getCorrelationMatrix());
  }

  // Math helper methods for template
  abs(value: number): number {
    return Math.abs(value);
  }

  toFixed(value: number, digits: number = 1): string {
    return value.toFixed(digits);
  }

  // Enhanced Heatmap Helper Methods
  getCorrelationValue(var1: string, var2: string): number {
    if (!this.basicResults?.correlation_matrix) return 0;
    
    const matrix = this.basicResults.correlation_matrix;
    if (var1 === var2) return 1;
    
    // Try both directions since correlation is symmetric
    return matrix[var1]?.[var2] ?? matrix[var2]?.[var1] ?? 0;
  }

  formatNumber(value: any): string {
    if (typeof value === 'number') {
      return value.toFixed(4);
    }
    return value?.toString() || '';
  }

  formatSummaryValue(value: any): string {
    if (value === null || value === undefined) {
      return 'N/A';
    }
    
    if (typeof value === 'number') {
      return value.toFixed(4);
    }
    
    if (typeof value === 'string') {
      return value;
    }
    
    if (typeof value === 'object') {
      // For objects, create a formatted display
      if (Array.isArray(value)) {
        return value.join(', ');
      } else {
        // For objects like column_types or missing_data, format as key-value pairs
        const entries = Object.entries(value);
        if (entries.length <= 3) {
          // Show all if 3 or fewer entries
          return entries.map(([k, v]) => `${k}: ${v}`).join(', ');
        } else {
          // Show first 3 and count
          const displayed = entries.slice(0, 3).map(([k, v]) => `${k}: ${v}`).join(', ');
          return `${displayed} (+${entries.length - 3} more)`;
        }
      }
    }
    
    return value.toString();
  }

  // Enhanced AI-driven summary interpretation
  getAIInsights(): any[] {
    if (!this.quickSummary) return [];
    
    const insights: any[] = [];
    
    // Dataset size insights
    if (this.currentDataset) {
      const totalCells = this.currentDataset.rows * this.currentDataset.columns;
      const sizeCategory = totalCells > 1000000 ? 'large' : totalCells > 100000 ? 'medium' : 'small';
      
      insights.push({
        type: 'dataset_size',
        title: 'Dataset Overview',
        description: this.getDatasetSizeInsight(sizeCategory, totalCells),
        icon: 'storage',
        color: 'primary'
      });
    }

    // Memory usage insights
    if (this.quickSummary.memory_usage) {
      const memoryMB = parseFloat(this.quickSummary.memory_usage.toString().replace(' MB', ''));
      insights.push({
        type: 'memory',
        title: 'Memory Efficiency',
        description: this.getMemoryInsight(memoryMB),
        icon: 'memory',
        color: memoryMB > 100 ? 'warn' : 'accent'
      });
    }

    // Column types insights
    if (this.quickSummary.column_types) {
      const columnTypes = this.quickSummary.column_types;
      insights.push({
        type: 'data_types',
        title: 'Data Type Analysis',
        description: this.getColumnTypesInsight(columnTypes),
        icon: 'category',
        color: 'primary'
      });
    }

    // Missing data insights
    if (this.quickSummary.missing_data) {
      const missingData = this.quickSummary.missing_data;
      insights.push({
        type: 'data_quality',
        title: 'Data Quality Assessment',
        description: this.getMissingDataInsight(missingData),
        icon: 'error_outline',
        color: this.hasCriticalMissingData(missingData) ? 'warn' : 'accent'
      });
    }

    return insights;
  }

  private getDatasetSizeInsight(category: string, totalCells: number): string {
    const formattedCells = this.formatLargeNumber(totalCells);
    
    switch (category) {
      case 'large':
        return `This is a substantial dataset with ${formattedCells} data points. Perfect for advanced analytics, machine learning models, and comprehensive statistical analysis. Processing may take longer but will yield robust insights.`;
      case 'medium':
        return `A well-sized dataset with ${formattedCells} data points. Ideal for detailed analysis, pattern recognition, and reliable statistical inference. Good balance between depth and processing efficiency.`;
      default:
        return `A compact dataset with ${formattedCells} data points. Great for quick exploration, prototyping, and initial analysis. Fast processing enables rapid iteration and testing.`;
    }
  }

  private getMemoryInsight(memoryMB: number): string {
    if (memoryMB > 500) {
      return `High memory usage (${memoryMB.toFixed(1)} MB). This dataset contains substantial information. Consider data optimization techniques for better performance, or ensure adequate system resources for analysis.`;
    } else if (memoryMB > 100) {
      return `Moderate memory footprint (${memoryMB.toFixed(1)} MB). This dataset is reasonably sized for most analytical operations. Good balance between data richness and computational efficiency.`;
    } else if (memoryMB > 10) {
      return `Efficient memory usage (${memoryMB.toFixed(1)} MB). This lightweight dataset allows for rapid processing and analysis. Ideal for quick insights and exploratory data analysis.`;
    } else {
      return `Very efficient memory usage (${memoryMB.toFixed(1)} MB). This compact dataset enables instant processing and real-time analysis capabilities.`;
    }
  }

  private getColumnTypesInsight(columnTypes: any): string {
    const types = Object.values(columnTypes);
    const typeCount = Object.keys(columnTypes).length;
    const numerics = types.filter(t => t === 'int64' || t === 'float64').length;
    const categoricals = types.filter(t => t === 'object').length;
    const others = typeCount - numerics - categoricals;

    let insight = `Your dataset contains ${typeCount} columns with diverse data types: `;
    
    if (numerics > 0) {
      insight += `${numerics} numerical columns (perfect for statistical analysis and ML models)`;
    }
    
    if (categoricals > 0) {
      insight += numerics > 0 ? `, ${categoricals} categorical columns (great for segmentation and classification)` : `${categoricals} categorical columns (ideal for grouping and pattern analysis)`;
    }
    
    if (others > 0) {
      insight += `, and ${others} specialized columns (dates, booleans, or complex types)`;
    }
    
    insight += '. This mixed structure enables comprehensive analysis across multiple dimensions.';
    
    return insight;
  }

  private getMissingDataInsight(missingData: any): string {
    const columns = Object.keys(missingData);
    const totalMissing = Object.values(missingData).reduce((sum: number, val: any) => sum + (Number(val) || 0), 0);
    const columnsWithMissing = columns.filter(col => Number(missingData[col]) > 0);
    
    if (totalMissing === 0) {
      return `Excellent data quality! No missing values detected across all ${columns.length} columns. Your dataset is complete and ready for immediate analysis without preprocessing concerns.`;
    }
    
    const missingPercentage = columnsWithMissing.length / columns.length * 100;
    
    if (missingPercentage > 50) {
      return `Significant data gaps detected in ${columnsWithMissing.length} of ${columns.length} columns (${totalMissing} missing values total). Recommend thorough data cleaning and imputation strategies before analysis.`;
    } else if (missingPercentage > 20) {
      return `Moderate missing data found in ${columnsWithMissing.length} columns (${totalMissing} total gaps). Consider data imputation or removal strategies. Most columns remain complete for reliable analysis.`;
    } else {
      return `Minor data gaps in ${columnsWithMissing.length} columns (${totalMissing} missing values). Generally good data quality with isolated missing values that can be easily addressed through standard preprocessing.`;
    }
  }

  private hasCriticalMissingData(missingData: any): boolean {
    const columns = Object.keys(missingData);
    const columnsWithMissing = columns.filter(col => Number(missingData[col]) > 0);
    return columnsWithMissing.length / columns.length > 0.3; // More than 30% of columns have missing data
  }

  private formatLargeNumber(num: number): string {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
  }

  // Helper method to get properly typed summary entries
  getSummaryEntries(): Array<{key: string, value: any}> {
    if (!this.quickSummary) return [];
    return Object.entries(this.quickSummary).map(([key, value]) => ({ key, value }));
  }

  // Helper method to format key names
  formatKeyName(key: string): string {
    return key.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
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

  // Advanced Metrics Helper Methods
  calculateIQR(column: string): string {
    const stats = this.getDescriptiveStatsData()[column];
    if (!stats || !stats['25%'] || !stats['75%']) return 'N/A';
    const iqr = stats['75%'] - stats['25%'];
    return this.formatNumber(iqr);
  }

  getSkewnessLabel(column: string): string {
    const stats = this.getDescriptiveStatsData()[column];
    if (!stats || !stats.mean || !stats['50%']) return 'N/A';
    
    const mean = stats.mean;
    const median = stats['50%'];
    const diff = mean - median;
    
    if (Math.abs(diff) < 0.1) return 'Symmetric';
    if (diff > 0) return 'Right-skewed';
    return 'Left-skewed';
  }

  // Distribution Analysis Methods
  getDistributionInsights(): Array<{title: string, description: string, icon: string, color: string}> {
    if (!this.basicResults?.descriptive_stats) return [];
    
    const insights = [];
    const columns = this.getDescriptiveStatsKeys();
    
    for (const column of columns) {
      const stats = this.getDescriptiveStatsData()[column];
      if (!stats) continue;
      
      const mean = stats.mean || 0;
      const std = stats.std || 0;
      const cv = std / Math.abs(mean);
      
      if (cv > 1) {
        insights.push({
          title: `High Variability in ${column}`,
          description: `This variable shows high variability (CV=${cv.toFixed(2)}), indicating diverse data points that may contain valuable patterns or require normalization for modeling.`,
          icon: 'scatter_plot',
          color: 'warn'
        });
      }
      
      if (cv < 0.1) {
        insights.push({
          title: `Low Variability in ${column}`,
          description: `This variable shows low variability (CV=${cv.toFixed(2)}), suggesting consistent values that may have limited predictive power or represent a stable metric.`,
          icon: 'horizontal_rule',
          color: 'primary'
        });
      }
    }
    
    return insights.slice(0, 4); // Limit to 4 insights
  }

  getNumericColumns(): string[] {
    if (!this.basicResults?.descriptive_stats?.summary) return [];
    return Object.keys(this.basicResults.descriptive_stats.summary);
  }

  getTextHistogram(column: string): Array<{range: string, count: number, height: number}> {
    const stats = this.getDescriptiveStatsData()[column];
    if (!stats || typeof stats !== 'object') {
      console.log('No stats for column:', column, 'Available data:', this.getDescriptiveStatsData());
      return [];
    }
    
    // Check if we have the required statistical data
    const min = stats.min;
    const max = stats.max;
    const mean = stats.mean;
    const std = stats.std;
    
    if (min === undefined || max === undefined || mean === undefined || std === undefined) {
      console.log('Missing required stats for column:', column, 'Stats:', stats);
      return [];
    }
    
    if (min === max) {
      // All values are the same
      return [{
        range: `${min.toFixed(1)}`,
        count: stats.count || 100,
        height: 100
      }];
    }
    
    const range = max - min;
    const bins = 7; // More bins for better visualization
    const binSize = range / bins;
    
    // Create more realistic histogram data based on normal distribution
    const histogram = [];
    const maxCount = 100;
    
    for (let i = 0; i < bins; i++) {
      const start = min + (i * binSize);
      const end = min + ((i + 1) * binSize);
      const binCenter = (start + end) / 2;
      
      // Simulate normal distribution around the mean
      const distanceFromMean = Math.abs(binCenter - mean) / (std || 1);
      let count: number;
      
      if (distanceFromMean < 0.5) {
        // Close to mean - high count
        count = Math.floor(80 + Math.random() * 20);
      } else if (distanceFromMean < 1) {
        // Moderate distance - medium count
        count = Math.floor(50 + Math.random() * 30);
      } else if (distanceFromMean < 2) {
        // Far from mean - low count
        count = Math.floor(20 + Math.random() * 20);
      } else {
        // Very far from mean - very low count
        count = Math.floor(5 + Math.random() * 15);
      }
      
      const height = Math.min((count / maxCount) * 100, 100); // Normalize to percentage
      
      histogram.push({
        range: `${start.toFixed(1)}-${end.toFixed(1)}`,
        count: count,
        height: Math.max(height, 5) // Minimum height for visibility
      });
    }

    // Generate Chart.js data for this column
    this.generateChartData(column, histogram);
    
    return histogram;
  }

  generateChartData(column: string, histogram: Array<{range: string, count: number, height: number}>): void {
    // Create a gradient color array that mimics matplotlib's default colors
    const colors = histogram.map((_, index) => {
      const ratio = index / (histogram.length - 1);
      // Create a blue-to-orange gradient similar to matplotlib
      const r = Math.floor(30 + ratio * 200);
      const g = Math.floor(144 + ratio * 100);  
      const b = Math.floor(255 - ratio * 200);
      return `rgba(${r}, ${g}, ${b}, 0.7)`;
    });

    const borderColors = histogram.map((_, index) => {
      const ratio = index / (histogram.length - 1);
      const r = Math.floor(20 + ratio * 180);
      const g = Math.floor(100 + ratio * 80);
      const b = Math.floor(200 - ratio * 150);
      return `rgba(${r}, ${g}, ${b}, 1)`;
    });

    const chartData: ChartData<'bar'> = {
      labels: histogram.map(h => h.range.replace('-', ' to ')),
      datasets: [{
        label: `${column} Distribution`,
        data: histogram.map(h => h.count),
        backgroundColor: colors,
        borderColor: borderColors,
        borderWidth: 2,
        hoverBackgroundColor: histogram.map((_, index) => {
          const ratio = index / (histogram.length - 1);
          const r = Math.floor(50 + ratio * 150);
          const g = Math.floor(164 + ratio * 80);
          const b = Math.floor(235 - ratio * 150);
          return `rgba(${r}, ${g}, ${b}, 0.9)`;
        }),
        hoverBorderColor: '#ff6600',
        hoverBorderWidth: 3,
        borderRadius: {
          topLeft: 4,
          topRight: 4,
          bottomLeft: 0,
          bottomRight: 0
        },
        borderSkipped: false
      }]
    };
    
    this.distributionCharts.set(column, chartData);
  }

  getChartData(column: string): ChartData<'bar'> | null {
    return this.distributionCharts.get(column) || null;
  }

  getDistributionShape(column: string): string {
    const stats = this.getDescriptiveStatsData()[column];
    if (!stats || typeof stats !== 'object') return 'No Data';
    
    const mean = stats.mean;
    const median = stats['50%'];
    const std = stats.std;
    
    if (mean === undefined || median === undefined || std === undefined) return 'Insufficient Data';
    if (std === 0) return 'Constant';
    
    const diff = Math.abs(mean - median);
    
    if (diff < (0.1 * std)) return 'Normal';
    if (mean > median) return 'Right-tailed';
    return 'Left-tailed';
  }

  getDistributionSymmetry(column: string): string {
    const shape = this.getDistributionShape(column);
    if (shape === 'Normal') return 'Symmetric';
    if (shape === 'Right-tailed') return 'Positively Skewed';
    if (shape === 'Left-tailed') return 'Negatively Skewed';
    if (shape === 'Constant') return 'No Variation';
    return 'Cannot Determine';
  }

  getOutlierRisk(column: string): string {
    const stats = this.getDescriptiveStatsData()[column];
    if (!stats || typeof stats !== 'object') return 'No Data';
    
    const q1 = stats['25%'];
    const q3 = stats['75%'];
    const min = stats.min;
    const max = stats.max;
    const mean = stats.mean;
    
    if (q1 === undefined || q3 === undefined || min === undefined || max === undefined || mean === undefined) {
      return 'Insufficient Data';
    }
    
    const iqr = q3 - q1;
    if (iqr === 0) return 'No Variation';
    
    const lowerBound = q1 - (1.5 * iqr);
    const upperBound = q3 + (1.5 * iqr);
    
    if (min < lowerBound || max > upperBound) return 'High';
    if (mean !== 0 && iqr / Math.abs(mean) > 0.5) return 'Moderate';
    return 'Low';
  }

  getDataQuality(column: string): string {
    const stats = this.getDescriptiveStatsData()[column];
    if (!stats || typeof stats !== 'object') return 'No Data';
    
    const count = stats.count;
    const totalRows = this.currentDataset?.rows;
    
    if (count === undefined || totalRows === undefined || totalRows === 0) {
      return 'Cannot Assess';
    }
    
    const completeness = count / totalRows;
    
    if (completeness > 0.95) return 'Excellent';
    if (completeness > 0.85) return 'Good';
    if (completeness > 0.7) return 'Fair';
    return 'Poor';
  }

  // Debug method to check data structure
  debugDistributionData(): void {
    console.log('=== DISTRIBUTION DEBUG ===');
    console.log('Basic Results:', this.basicResults);
    console.log('Descriptive Stats:', this.basicResults?.descriptive_stats);
    console.log('Summary:', this.basicResults?.descriptive_stats?.summary);
    console.log('Distribution Analysis:', this.basicResults?.distribution_analysis);
    console.log('Numeric Columns:', this.getNumericColumns());
    console.log('Stats Data:', this.getDescriptiveStatsData());
    
    const columns = this.getNumericColumns();
    columns.forEach(column => {
      const stats = this.getDescriptiveStatsData()[column];
      console.log(`Column ${column}:`, stats);
    });
  }

  processChartData(): void {
    console.log('Processing chart data...');
    
    // Process histogram data from backend
    if (this.basicResults?.distribution_analysis?.histograms) {
      this.createHistogramCharts();
    }
    
    // Process correlation heatmap data from backend
    if (this.basicResults?.correlation_matrix?.heatmap_data) {
      this.createCorrelationHeatmap();
    }
  }

  createHistogramCharts(): void {
    const histograms = this.basicResults?.distribution_analysis?.histograms;
    if (!histograms) return;

    Object.keys(histograms).forEach(column => {
      const histData = histograms[column];
      if (histData && histData.counts && histData.labels) {
        // Create matplotlib-like color scheme
        const colors = histData.counts.map((_: number, index: number) => {
          const ratio = index / (histData.counts.length - 1);
          // Blue to orange gradient similar to matplotlib
          const r = Math.floor(30 + ratio * 200);
          const g = Math.floor(144 + ratio * 100);  
          const b = Math.floor(255 - ratio * 200);
          return `rgba(${r}, ${g}, ${b}, 0.7)`;
        });

        const borderColors = histData.counts.map((_: number, index: number) => {
          const ratio = index / (histData.counts.length - 1);
          const r = Math.floor(20 + ratio * 180);
          const g = Math.floor(100 + ratio * 80);
          const b = Math.floor(200 - ratio * 150);
          return `rgba(${r}, ${g}, ${b}, 1)`;
        });

        const chartData: ChartData<'bar'> = {
          labels: histData.labels,
          datasets: [{
            label: `${column} Distribution (n=${histData.total_count || 'N/A'})`,
            data: histData.counts,
            backgroundColor: colors,
            borderColor: borderColors,
            borderWidth: 2,
            hoverBackgroundColor: histData.counts.map((_: number, index: number) => {
              const ratio = index / Math.max(histData.counts.length - 1, 1);
              const r = Math.floor(50 + ratio * 150);
              const g = Math.floor(164 + ratio * 80);
              const b = Math.floor(235 - ratio * 150);
              return `rgba(${r}, ${g}, ${b}, 0.9)`;
            }),
            hoverBorderColor: '#ff6600',
            hoverBorderWidth: 3,
            borderRadius: {
              topLeft: 4,
              topRight: 4,
              bottomLeft: 0,
              bottomRight: 0
            },
            borderSkipped: false
          }]
        };
        
        this.distributionCharts.set(column, chartData);
      }
    });
    
    console.log('Created histogram charts:', this.distributionCharts);
  }

  createCorrelationHeatmap(): void {
    const heatmapData = this.basicResults?.correlation_matrix?.heatmap_data;
    if (!heatmapData || !heatmapData.variables || !heatmapData.correlation_matrix) return;

    const variables = heatmapData.variables;
    const matrix = heatmapData.correlation_matrix;
    
    // Set variables for chart options
    this.heatmapVariables = variables;
    
    // Create scatter plot data for heatmap visualization
    const scatterData: any[] = [];
    
    for (let i = 0; i < variables.length; i++) {
      for (let j = 0; j < variables.length; j++) {
        const correlation = matrix[i][j];
        scatterData.push({
          x: j,
          y: i,
          v: correlation // value for color mapping
        });
      }
    }

    this.correlationHeatmapChart = {
      datasets: [{
        data: scatterData,
        backgroundColor: (context: any) => {
          const value = context.parsed.v;
          if (value > 0.7) return '#00ff88';
          if (value > 0.3) return '#c8e6c9';
          if (value > -0.3) return '#666666';
          if (value > -0.7) return '#ffb74d';
          return '#ff6600';
        },
        borderColor: '#00ff7f',
        borderWidth: 1,
        pointRadius: 15,
        pointHoverRadius: 20,
        label: 'Correlation'
      }]
    };
    
    // Update chart options with current variables
    this.updateHeatmapChartOptions();
    
    console.log('Created correlation heatmap:', this.correlationHeatmapChart);
  }

  updateHeatmapChartOptions(): void {
    if (this.heatmapChartOptions && this.heatmapChartOptions.scales) {
      // Update X axis max value
      if (this.heatmapChartOptions.scales['x']) {
        (this.heatmapChartOptions.scales['x'] as any).max = this.heatmapVariables.length - 0.5;
      }
      // Update Y axis max value  
      if (this.heatmapChartOptions.scales['y']) {
        (this.heatmapChartOptions.scales['y'] as any).max = this.heatmapVariables.length - 0.5;
      }
    }
  }

  getHistogramData(column: string): ChartData<'bar'> | null {
    return this.distributionCharts.get(column) || null;
  }

  getCorrelationHeatmapData(): ChartData<'scatter'> | null {
    return this.correlationHeatmapChart;
  }

  // Helper method for templates
  getObjectKeys(obj: any): string[] {
    return obj ? Object.keys(obj) : [];
  }

  formatDistributionData(data: any): string {
    if (!data) return 'No distribution data available';
    
    try {
      return JSON.stringify(data, null, 2);
    } catch (error) {
      return 'Error formatting distribution data';
    }
  }

  // Schema and Data Source Helper Methods
  getSchemaTableData(): any[] {
    if (!this.quickSummary?.schema) return [];
    
    return Object.entries(this.quickSummary.schema).map(([name, details]: [string, any]) => ({
      name,
      type: this.getReadableDataType(details.dtype),
      null_count: details.null_count,
      null_percentage: details.null_percentage,
      unique_count: details.unique_count,
      unique_percentage: details.unique_percentage,
      memory_usage: details.memory_usage,
      is_numeric: details.is_numeric,
      is_categorical: details.is_categorical,
      is_datetime: details.is_datetime
    }));
  }

  getReadableDataType(dtype: string): string {
    if (dtype.includes('int')) return 'Integer';
    if (dtype.includes('float')) return 'Float';
    if (dtype.includes('object')) return 'Text/Categorical';
    if (dtype.includes('datetime')) return 'DateTime';
    if (dtype.includes('bool')) return 'Boolean';
    return dtype;
  }

  getTypeColor(type: string): 'primary' | 'accent' | 'warn' {
    switch (type) {
      case 'Integer':
      case 'Float':
        return 'primary';
      case 'Text/Categorical':
        return 'accent';
      case 'DateTime':
      case 'Boolean':
        return 'warn';
      default:
        return 'primary';
    }
  }

  getPreviewColumns(): string[] {
    if (!this.quickSummary?.sample_preview?.head?.length) return [];
    return Object.keys(this.quickSummary.sample_preview.head[0]);
  }

  formatCellValue(value: any): string {
    if (value === null || value === undefined) return '(null)';
    if (typeof value === 'number') {
      return value % 1 === 0 ? value.toString() : value.toFixed(3);
    }
    if (typeof value === 'string' && value.length > 50) {
      return value.substring(0, 47) + '...';
    }
    return value.toString();
  }

  // Missing Value Analysis Helper Methods
  getMissingValueTableData(): any[] {
    if (!this.basicResults?.missing_value_analysis?.column_analysis) return [];
    
    return Object.entries(this.basicResults.missing_value_analysis.column_analysis).map(([name, details]: [string, any]) => ({
      name,
      missing_count: details.missing_count,
      missing_percentage: details.missing_percentage,
      pattern: details.pattern,
      suggested_strategy: details.suggested_strategy,
      data_type: details.data_type,
      is_numeric: details.is_numeric
    }));
  }

  getPatternColor(pattern: string): 'primary' | 'accent' | 'warn' {
    switch (pattern) {
      case 'None':
        return 'primary';
      case 'Random':
      case 'Sporadic':
        return 'accent';
      case 'Systematic High':
      case 'Complete':
        return 'warn';
      default:
        return 'accent';
    }
  }

  // Duplicates Analysis Helper Methods
  getQualityScoreClass(score: number): string {
    if (score >= 95) return 'excellent';
    if (score >= 85) return 'good';
    if (score >= 70) return 'fair';
    return 'poor';
  }

  hasPartialDuplicates(): boolean {
    return this.basicResults?.duplicates_analysis?.partial_duplicates && 
           Object.keys(this.basicResults.duplicates_analysis.partial_duplicates).length > 0;
  }

  getPartialDuplicatesArray(): any[] {
    if (!this.basicResults?.duplicates_analysis?.partial_duplicates) return [];
    
    return Object.entries(this.basicResults.duplicates_analysis.partial_duplicates).map(([key, value]) => ({
      key,
      value
    }));
  }

  getRecommendationIcon(recommendation: string): string {
    if (recommendation.includes('✅')) return 'check_circle';
    if (recommendation.includes('⚠️')) return 'warning';
    if (recommendation.includes('🚨')) return 'error';
    return 'info';
  }

  getRecommendationIconClass(recommendation: string): string {
    if (recommendation.includes('✅')) return 'success';
    if (recommendation.includes('⚠️')) return 'warning';
    if (recommendation.includes('🚨')) return 'error';
    return 'info';
  }

  // Type/Integrity Validation Helper Methods
  getTypeValidationColumns(): string[] {
    if (!this.basicResults?.type_integrity_validation?.column_validations) return [];
    return Object.keys(this.basicResults.type_integrity_validation.column_validations);
  }

  getTypeValidationTableData(): any[] {
    if (!this.basicResults?.type_integrity_validation?.column_validations) return [];
    
    return Object.entries(this.basicResults.type_integrity_validation.column_validations).map(([name, details]: [string, any]) => ({
      name,
      declared_type: details.declared_type,
      inferred_type: details.inferred_type,
      integrity_score: details.integrity_score,
      issues_count: details.issues.length,
      recommendations_count: details.recommendations.length,
      issues: details.issues,
      recommendations: details.recommendations
    }));
  }

  getIntegrityScoreClass(score: number): string {
    if (score >= 90) return 'excellent';
    if (score >= 75) return 'good';
    if (score >= 50) return 'fair';
    return 'poor';
  }

  // Univariate Summaries Helper Methods
  getNumericSummaryColumns(): string[] {
    if (!this.basicResults?.univariate_summaries?.numeric_summaries) return [];
    return Object.keys(this.basicResults.univariate_summaries.numeric_summaries);
  }

  getCategoricalSummaryColumns(): string[] {
    if (!this.basicResults?.univariate_summaries?.categorical_summaries) return [];
    return Object.keys(this.basicResults.univariate_summaries.categorical_summaries);
  }

  getTemporalSummaryColumns(): string[] {
    if (!this.basicResults?.univariate_summaries?.temporal_summaries) return [];
    return Object.keys(this.basicResults.univariate_summaries.temporal_summaries);
  }

  getNumericSummaryData(column: string): any {
    return this.basicResults?.univariate_summaries?.numeric_summaries?.[column] || {};
  }

  getCategoricalSummaryData(column: string): any {
    return this.basicResults?.univariate_summaries?.categorical_summaries?.[column] || {};
  }

  getTemporalSummaryData(column: string): any {
    return this.basicResults?.univariate_summaries?.temporal_summaries?.[column] || {};
  }

  getTopCategoriesArray(topCategories: any): any[] {
    if (!topCategories) return [];
    return Object.entries(topCategories).map(([category, count]) => ({ category, count }));
  }

  formatDistributionShape(shape: any): string {
    if (!shape || !shape.overall_shape) return 'Unknown';
    return shape.overall_shape;
  }

  formatNormalityTest(test: any): string {
    if (!test || test.is_normal === null) return 'Cannot determine';
    if (test.is_normal) return `Normal (p=${test.p_value?.toFixed(4)})`;
    return `Not Normal (p=${test.p_value?.toFixed(4)})`;
  }

  // Outlier Detection Helper Methods
  getOutlierDetectionColumns(): string[] {
    if (!this.basicResults?.outlier_detection?.univariate_outliers) return [];
    return Object.keys(this.basicResults.outlier_detection.univariate_outliers);
  }

  getOutlierData(column: string): any {
    return this.basicResults?.outlier_detection?.univariate_outliers?.[column] || {};
  }

  getOutlierSeverityClass(severity: string): string {
    switch (severity) {
      case 'none': return 'success';
      case 'low': return 'info';
      case 'moderate': return 'warning';
      case 'high': case 'critical': return 'error';
      default: return 'info';
    }
  }

  getOutlierMethodData(column: string, method: string): any {
    const outlierData = this.getOutlierData(column);
    return outlierData.methods?.[method] || {};
  }

  formatOutlierMethod(method: string): string {
    switch (method) {
      case 'iqr': return 'IQR Method';
      case 'zscore': return 'Z-Score';
      case 'modified_zscore': return 'Modified Z-Score';
      case 'grubbs': return 'Grubbs Test';
      default: return method;
    }
  }

  hasMultivariateOutliers(): boolean {
    return this.basicResults?.outlier_detection?.multivariate_outliers && 
           Object.keys(this.basicResults.outlier_detection.multivariate_outliers).length > 0 &&
           !this.basicResults.outlier_detection.multivariate_outliers.message;
  }

  getMultivariateOutlierData(): any {
    return this.basicResults?.outlier_detection?.multivariate_outliers || {};
  }

  // Missing Data Analysis Helper Methods
  formatMissingDataSummary(): any[] {
    if (!this.basicResults?.missing_data_summary) return [];
    
    const summary = this.basicResults.missing_data_summary;
    return [
      { label: 'Total Missing Values', value: summary.total_missing_values || 0 },
      { label: 'Missing Percentage', value: `${(summary.missing_percentage || 0).toFixed(2)}%` },
      { label: 'Complete Rows', value: summary.complete_rows || 0 },
      { label: 'Incomplete Rows', value: summary.incomplete_rows || 0 },
      { label: 'Columns with Missing', value: summary.columns_with_missing || 0 },
      { label: 'Pattern Count', value: summary.pattern_count || 0 }
    ];
  }

  // Distribution Analysis Helper Methods
  formatDistributionSummary(): any[] {
    if (!this.basicResults?.distribution_analysis) return [];
    
    const dist = this.basicResults.distribution_analysis;
    const result: any[] = [];
    
    if (dist.numerical_distributions) {
      Object.entries(dist.numerical_distributions).forEach(([column, data]: [string, any]) => {
        result.push({
          column,
          type: 'Numerical',
          skewness: data.skewness?.toFixed(3) || 'N/A',
          kurtosis: data.kurtosis?.toFixed(3) || 'N/A',
          shape: data.distribution_shape?.overall_shape || 'Unknown',
          normality: data.normality_test?.is_normal ? 'Normal' : 'Non-normal',
          outliers: data.outlier_info?.outlier_count || 0
        });
      });
    }
    
    if (dist.categorical_distributions) {
      Object.entries(dist.categorical_distributions).forEach(([column, data]: [string, any]) => {
        result.push({
          column,
          type: 'Categorical',
          categories: data.unique_count || 0,
          mostCommon: data.most_common?.[0]?.[0] || 'N/A',
          uniformity: data.uniformity_score?.toFixed(3) || 'N/A',
          entropy: data.entropy?.toFixed(3) || 'N/A',
          balance: data.balance_score || 'N/A'
        });
      });
    }
    
    return result;
  }
  
  // Helper methods for new analysis types
  getPriorityColor(priority: string): string {
    switch (priority) {
      case 'high': return 'warn';
      case 'medium': return 'accent';
      case 'low': return 'primary';
      default: return 'primary';
    }
  }
  
  getVIFClass(vif: number): string {
    if (vif > 10) return 'critical';
    if (vif > 5) return 'warning';
    return 'acceptable';
  }

  getReadinessScoreClass(score: number): string {
    if (score >= 80) return 'score-high';
    if (score >= 60) return 'score-moderate';
    return 'score-low';
  }

  getReadinessFactorsArray(): any[] {
    if (!this.basicResults?.baseline_model_sanity?.readiness_factors) {
      return [];
    }
    
    return Object.entries(this.basicResults.baseline_model_sanity.readiness_factors).map(([key, value]) => ({
      key: key.replace(/_/g, ' '),
      value: typeof value === 'number' ? value : 0
    }));
  }

  getBiasRiskColor(riskLevel: string): 'primary' | 'accent' | 'warn' {
    switch(riskLevel?.toLowerCase()) {
      case 'high': return 'warn';
      case 'medium': return 'accent';
      default: return 'primary';
    }
  }

  getClassImbalanceArray(): any[] {
    if (!this.basicResults?.bias_fairness_flags?.class_imbalance) {
      return [];
    }
    
    return Object.entries(this.basicResults.bias_fairness_flags.class_imbalance).map(([key, value]) => ({
      key,
      value
    }));
  }
}
