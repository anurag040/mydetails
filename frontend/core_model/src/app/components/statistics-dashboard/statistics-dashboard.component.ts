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
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
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
    MatSelectModule,
    MatFormFieldModule,
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
  
  // Regression Analysis State
  regressionXColumn: string | null = null;
  regressionYColumn: string | null = null;
  regressionLoading: boolean = false;
  regressionError: string | null = null;
  regressionResults: any = null;
  regressionChartData: any = null;
  regressionChartOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: 'linear',
        position: 'bottom',
        title: {
          display: true,
          text: 'X Variable'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Y Variable'
        }
      }
    },
    plugins: {
      legend: {
        display: true,
        position: 'top'
      },
      title: {
        display: true,
        text: 'Regression Analysis'
      }
    }
  };
  
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
        this.debugRegressionData(); // Debug regression data availability
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

  // Trigger regression analysis
  runRegressionAnalysis() {
    if (!this.currentDataset || !this.regressionXColumn || !this.regressionYColumn) {
      this.regressionError = 'Please select both X and Y columns.';
      return;
    }
    
    this.regressionLoading = true;
    this.regressionError = null;
    
    this.apiService.performRegressionAnalysis(
      this.currentDataset.dataset_id,
      this.regressionXColumn,
      this.regressionYColumn
    ).subscribe({
      next: (result) => {
        if (!this.advancedResults) {
          this.advancedResults = { dataset_id: this.currentDataset!.dataset_id };
        }
        this.advancedResults.regression_analysis = result;
        this.regressionResults = result;
        this.createRegressionChart();
        this.regressionLoading = false;
        this.snackBar.open('Regression analysis completed!', 'Close', { duration: 3000 });
      },
      error: (err) => {
        console.error('Regression analysis error:', err);
        this.regressionError = err.error?.detail || 'Failed to perform regression analysis.';
        this.regressionLoading = false;
        this.snackBar.open('Regression analysis failed', 'Close', { duration: 5000 });
      }
    });
  }

  // New method for the template
  performRegression() {
    this.regressionXColumn = this.selectedXVariable;
    this.regressionYColumn = this.selectedYVariable;
    this.runRegressionAnalysis();
  }

  // Template variables for compatibility
  get selectedXVariable(): string {
    return this.regressionXColumn || '';
  }

  set selectedXVariable(value: string) {
    this.regressionXColumn = value;
  }

  get selectedYVariable(): string {
    return this.regressionYColumn || '';
  }

  set selectedYVariable(value: string) {
    this.regressionYColumn = value;
  }

  // Create regression scatter plot with trend line
  createRegressionChart() {
    if (!this.regressionResults || !this.currentDataset) return;

    // Check if we have scatter plot data from the regression results
    if (this.regressionResults.scatter_data && Array.isArray(this.regressionResults.scatter_data)) {
      const scatterData = this.regressionResults.scatter_data.map((point: any) => ({
        x: point.x,
        y: point.y
      }));

      // Create regression line points from regression results
      const slope = this.regressionResults.model_parameters?.coefficient || this.regressionResults.slope || 0;
      const intercept = this.regressionResults.model_parameters?.intercept || this.regressionResults.intercept || 0;
      
      const xValues = scatterData.map((point: any) => point.x);
      const minX = Math.min(...xValues);
      const maxX = Math.max(...xValues);
      
      const regressionLineData = [
        { x: minX, y: slope * minX + intercept },
        { x: maxX, y: slope * maxX + intercept }
      ];

      this.regressionChartData = {
        datasets: [
          {
            label: 'Data Points',
            data: scatterData,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            showLine: false,
            pointRadius: 4
          },
          {
            label: 'Regression Line',
            data: regressionLineData,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 2,
            showLine: true,
            pointRadius: 0,
            type: 'line'
          }
        ]
      };
    } else {
      // Fallback: create mock data based on regression parameters
      const slope = this.regressionResults.model_parameters?.coefficient || this.regressionResults.slope || 1;
      const intercept = this.regressionResults.model_parameters?.intercept || this.regressionResults.intercept || 0;
      
      // Generate sample data points along the regression line with some scatter
      const scatterData = [];
      for (let i = 0; i < 50; i++) {
        const x = i * 2; // Sample x values
        const y = slope * x + intercept + (Math.random() - 0.5) * 10; // Add some random scatter
        scatterData.push({ x, y });
      }

      const minX = 0;
      const maxX = 100;
      const regressionLineData = [
        { x: minX, y: slope * minX + intercept },
        { x: maxX, y: slope * maxX + intercept }
      ];

      this.regressionChartData = {
        datasets: [
          {
            label: 'Data Points',
            data: scatterData,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            showLine: false,
            pointRadius: 4
          },
          {
            label: 'Regression Line',
            data: regressionLineData,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 2,
            showLine: true,
            pointRadius: 0,
            type: 'line'
          }
        ]
      };
    }

    // Update chart options with variable names
    this.regressionChartOptions = {
      ...this.regressionChartOptions,
      scales: {
        ...this.regressionChartOptions.scales,
        x: {
          ...this.regressionChartOptions.scales.x,
          title: {
            display: true,
            text: this.regressionXColumn || 'X Variable'
          }
        },
        y: {
          ...this.regressionChartOptions.scales.y,
          title: {
            display: true,
            text: this.regressionYColumn || 'Y Variable'
          }
        }
      }
    };
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
    // First try to get from basic results if available
    if (this.basicResults?.descriptive_stats?.summary) {
      return Object.keys(this.basicResults.descriptive_stats.summary);
    }
    
    // Fallback to dataset schema for immediate availability
    if (this.quickSummary?.schema) {
      return Object.entries(this.quickSummary.schema)
        .filter(([_, details]: [string, any]) => {
          // Handle both boolean true and string 'True' from API
          if (details.is_numeric === true || details.is_numeric === 'True') {
            return true;
          }
          // Fallback: check data type for numeric types
          if (details.dtype) {
            const dtype = details.dtype.toLowerCase();
            return dtype.includes('int') || dtype.includes('float') || dtype.includes('number');
          }
          return false;
        })
        .map(([name, _]) => name);
    }
    
    return [];
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

  // Debug method for regression
  debugRegressionData(): void {
    console.log('=== REGRESSION DEBUG ===');
    console.log('Current Dataset:', this.currentDataset);
    console.log('Quick Summary:', this.quickSummary);
    console.log('Quick Summary Schema:', this.quickSummary?.schema);
    console.log('Numeric Columns Available:', this.getNumericColumns());
    console.log('Basic Results Available:', !!this.basicResults);
    console.log('Regression X Column:', this.regressionXColumn);
    console.log('Regression Y Column:', this.regressionYColumn);
    
    if (this.quickSummary?.schema) {
      console.log('Schema Analysis:');
      Object.entries(this.quickSummary.schema).forEach(([name, details]: [string, any]) => {
        console.log(`  ${name}: is_numeric=${details.is_numeric}, dtype=${details.dtype}`);
      });
    }
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

  getStabilityScoreClass(score: number): string {
    if (score >= 80) return 'score-high';
    if (score >= 60) return 'score-moderate';
    return 'score-low';
  }

  getDriftRiskColor(riskLevel: string): 'primary' | 'accent' | 'warn' {
    switch(riskLevel?.toLowerCase()) {
      case 'high': return 'warn';
      case 'medium': return 'accent';
      default: return 'primary';
    }
  }

  getColumnDriftArray(): any[] {
    if (!this.basicResults?.drift_stability_analysis?.column_drift_analysis) {
      return [];
    }
    
    return Object.entries(this.basicResults.drift_stability_analysis.column_drift_analysis).map(([column, data]: [string, any]) => ({
      column,
      drift_detected: data.drift_detected,
      drift_score: data.drift_score,
      detection_method: data.detection_method,
      details: data.details
    }));
  }

  getPackageVersionsArray(): any[] {
    if (!this.basicResults?.reproducibility_info?.package_versions) {
      return [];
    }
    
    return Object.entries(this.basicResults.reproducibility_info.package_versions).map(([key, value]) => ({
      key,
      value
    }));
  }

  getAnalysisConfigArray(): any[] {
    if (!this.basicResults?.reproducibility_info?.analysis_config) {
      return [];
    }
    
    return Object.entries(this.basicResults.reproducibility_info.analysis_config).map(([key, value]) => ({
      key: key.replace(/_/g, ' '),
      value: typeof value === 'object' ? JSON.stringify(value) : value
    }));
  }

  // Missing Data Analysis Helper Methods
  getCompletenessScoreClass(percentage: number): string {
    if (percentage >= 95) return 'score-excellent';
    if (percentage >= 85) return 'score-good';
    if (percentage >= 70) return 'score-fair';
    return 'score-poor';
  }

  getCompletenessTextClass(percentage: number): string {
    if (percentage >= 95) return 'excellent';
    if (percentage >= 85) return 'good';
    if (percentage >= 70) return 'fair';
    return 'poor';
  }

  getCompletenessAssessment(percentage: number): string {
    if (percentage >= 95) return 'Excellent data quality - minimal missing values detected';
    if (percentage >= 85) return 'Good data quality - acceptable level of completeness';
    if (percentage >= 70) return 'Fair data quality - some missing values may impact analysis';
    return 'Poor data quality - significant missing values require attention';
  }

  getUsabilityClass(percentage: number): string {
    if (percentage >= 90) return 'excellent';
    if (percentage >= 75) return 'good';
    if (percentage >= 60) return 'fair';
    return 'poor';
  }

  getUsabilityRating(percentage: number): string {
    if (percentage >= 90) return 'Excellent';
    if (percentage >= 75) return 'Good';
    if (percentage >= 60) return 'Fair';
    return 'Poor';
  }

  getUsabilityIconClass(percentage: number): string {
    if (percentage >= 90) return 'excellent';
    if (percentage >= 75) return 'good';
    if (percentage >= 60) return 'fair';
    return 'poor';
  }

  getUsabilityIcon(percentage: number): string {
    if (percentage >= 90) return 'sentiment_very_satisfied';
    if (percentage >= 75) return 'sentiment_satisfied';
    if (percentage >= 60) return 'sentiment_neutral';
    return 'sentiment_dissatisfied';
  }

  getQuickMissingInsights(summary: any): Array<{type: string, icon: string, message: string}> {
    const insights: Array<{type: string, icon: string, message: string}> = [];
    
    if (!summary) return insights;

    const missingPercentage = summary.total_percentage || 0;
    const completePercentage = summary.complete_rows_percentage || 0;

    if (missingPercentage === 0) {
      insights.push({
        type: 'success',
        icon: 'check_circle',
        message: 'Perfect! No missing values detected in the dataset.'
      });
    } else if (missingPercentage < 5) {
      insights.push({
        type: 'success',
        icon: 'thumb_up',
        message: 'Excellent data quality with minimal missing values.'
      });
    } else if (missingPercentage < 15) {
      insights.push({
        type: 'warning',
        icon: 'info',
        message: 'Moderate missing values detected - manageable with proper handling.'
      });
    } else {
      insights.push({
        type: 'error',
        icon: 'warning',
        message: 'High level of missing values may impact analysis quality.'
      });
    }

    if (completePercentage > 80) {
      insights.push({
        type: 'info',
        icon: 'analytics',
        message: `${completePercentage.toFixed(0)}% of rows are complete - good for most analyses.`
      });
    }

    return insights;
  }

  getColumnImpactColor(count: number): 'primary' | 'accent' | 'warn' {
    if (count === 0) return 'primary';
    if (count <= 3) return 'accent';
    return 'warn';
  }

  getColumnImpactLevel(count: number): string {
    if (count === 0) return 'No Impact';
    if (count <= 3) return 'Low Impact';
    if (count <= 7) return 'Medium Impact';
    return 'High Impact';
  }

  getQualityScoreClass(percentage: number): string {
    if (percentage >= 95) return 'score-excellent';
    if (percentage >= 85) return 'score-good';
    if (percentage >= 70) return 'score-fair';
    return 'score-poor';
  }

  getQualityLabel(percentage: number): string {
    if (percentage >= 95) return 'Excellent';
    if (percentage >= 85) return 'Good';
    if (percentage >= 70) return 'Fair';
    return 'Needs Attention';
  }

  getColumnTypeIcon(type: string): string {
    switch (type?.toLowerCase()) {
      case 'numeric':
      case 'float':
      case 'int':
        return 'functions';
      case 'categorical':
      case 'object':
        return 'label';
      case 'datetime':
      case 'timestamp':
        return 'schedule';
      case 'boolean':
        return 'toggle_on';
      default:
        return 'help_outline';
    }
  }

  getMissingSeverityColor(percentage: number): 'primary' | 'accent' | 'warn' {
    if (percentage === 0) return 'primary';
    if (percentage <= 20) return 'accent';
    return 'warn';
  }

  getMissingSeverityLabel(percentage: number): string {
    if (percentage === 0) return 'Complete';
    if (percentage <= 5) return 'Minimal';
    if (percentage <= 20) return 'Moderate';
    if (percentage <= 50) return 'High';
    return 'Critical';
  }

  getMissingRateClass(percentage: number): string {
    if (percentage === 0) return 'complete';
    if (percentage <= 20) return 'moderate';
    return 'high';
  }

  getRecommendationTypeClass(recommendation: string): string {
    if (recommendation.toLowerCase().includes('warning') || recommendation.toLowerCase().includes('critical')) {
      return 'warning';
    }
    if (recommendation.toLowerCase().includes('error') || recommendation.toLowerCase().includes('urgent')) {
      return 'error';
    }
    if (recommendation.toLowerCase().includes('success') || recommendation.toLowerCase().includes('excellent')) {
      return 'success';
    }
    return 'info';
  }

  // Enhanced Outlier Detection Helper Methods
  getOutlierSeverityDescription(percentage: number): string {
    if (percentage === 0) return 'No outliers detected - excellent data quality';
    if (percentage < 1) return 'Minimal outliers - generally acceptable';
    if (percentage < 5) return 'Moderate outliers - investigate patterns';
    if (percentage < 10) return 'High outliers - requires attention';
    return 'Critical outlier levels - immediate review needed';
  }

  getOutlierPercentageClass(percentage: number): string {
    if (percentage === 0) return 'excellent';
    if (percentage < 1) return 'good';
    if (percentage < 5) return 'warning';
    return 'critical';
  }

  getOutlierPercentageInterpretation(percentage: number): string {
    if (percentage === 0) return 'Perfect - no unusual values detected';
    if (percentage < 1) return 'Excellent - very few outliers';
    if (percentage < 5) return 'Acceptable - monitor for patterns';
    if (percentage < 10) return 'Concerning - investigate causes';
    return 'Critical - immediate action required';
  }

  getColumnAffectedColor(affected: number, total: number): 'primary' | 'accent' | 'warn' {
    const ratio = affected / total;
    if (ratio === 0) return 'primary';
    if (ratio < 0.3) return 'accent';
    return 'warn';
  }

  getColumnAffectedLabel(affected: number, total: number): string {
    const ratio = affected / total;
    if (ratio === 0) return 'No Impact';
    if (ratio < 0.3) return 'Low Impact';
    if (ratio < 0.7) return 'Moderate Impact';
    return 'High Impact';
  }

  getImpactClass(percentage: number): string {
    if (percentage === 0) return 'impact-positive';
    if (percentage < 5) return 'impact-neutral';
    return 'impact-negative';
  }

  getImpactIcon(percentage: number): string {
    if (percentage === 0) return 'thumb_up';
    if (percentage < 5) return 'info';
    return 'warning';
  }

  getImpactTitle(percentage: number): string {
    if (percentage === 0) return 'Excellent Data Quality';
    if (percentage < 1) return 'Good Data Quality';
    if (percentage < 5) return 'Acceptable Data Quality';
    if (percentage < 10) return 'Data Quality Concerns';
    return 'Poor Data Quality';
  }

  getImpactDescription(percentage: number): string {
    if (percentage === 0) {
      return 'No outliers detected. Your data is clean and ready for analysis without preprocessing concerns.';
    }
    if (percentage < 1) {
      return 'Very few outliers detected. These may represent natural variation or rare but valid cases.';
    }
    if (percentage < 5) {
      return 'Moderate number of outliers. Consider investigating patterns and deciding on treatment strategies.';
    }
    if (percentage < 10) {
      return 'Significant outliers detected. Recommend thorough investigation of causes and data cleaning.';
    }
    return 'High level of outliers may indicate data quality issues or require specialized handling strategies.';
  }

  getOutlierSeverityColor(severity: string): 'primary' | 'accent' | 'warn' {
    switch (severity) {
      case 'none': return 'primary';
      case 'low': return 'primary';
      case 'moderate': return 'accent';
      case 'high': case 'critical': return 'warn';
      default: return 'primary';
    }
  }

  getColumnDataTypeIcon(column: string): string {
    // You can enhance this based on actual column metadata
    return 'functions'; // Default for numeric columns
  }

  getMethodResultClass(percentage: number): string {
    if (percentage === 0) return 'result-clean';
    if (percentage < 2) return 'result-low';
    if (percentage < 8) return 'result-moderate';
    return 'result-high';
  }

  getRecommendedMethodIcon(method: string): string {
    switch (method) {
      case 'iqr': return 'straighten';
      case 'zscore': return 'show_chart';
      case 'modified_zscore': return 'analytics';
      default: return 'recommend';
    }
  }

  getMethodRecommendationReason(column: string, method: string): string {
    const data = this.getOutlierData(column);
    
    switch (method) {
      case 'iqr':
        return 'IQR method is recommended for this column because it\'s robust to extreme values and works well with moderate skewness.';
      case 'zscore':
        return 'Z-Score method is recommended for this large dataset with normally distributed values.';
      case 'modified_zscore':
        return 'Modified Z-Score is recommended due to high variability or skewness in the data distribution.';
      default:
        return 'This method provides the most reliable results for the current data characteristics.';
    }
  }

  getOutlierValueSeverity(value: number, column: string): 'primary' | 'accent' | 'warn' {
    // This could be enhanced with more sophisticated logic
    return 'warn'; // Default color for outlier values
  }

  getOutlierValueContext(column: string, values: number[]): string {
    if (!values || values.length === 0) return '';
    
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    if (values.length === 1) {
      return `This extreme value is significantly different from the typical range.`;
    }
    
    return `These values range from ${min.toFixed(2)} to ${max.toFixed(2)}, representing the most extreme cases in your dataset.`;
  }

  getColumnOutlierInsights(column: string): Array<{type: string, icon: string, message: string}> {
    const data = this.getOutlierData(column);
    const insights: Array<{type: string, icon: string, message: string}> = [];
    
    if (!data || data.total_outliers === 0) {
      insights.push({
        type: 'primary',
        icon: 'check_circle',
        message: 'No outliers detected - this column has consistent, well-behaved data.'
      });
      return insights;
    }
    
    const severity = data.severity;
    const outlierCount = data.total_outliers;
    
    if (severity === 'low') {
      insights.push({
        type: 'primary',
        icon: 'info',
        message: `${outlierCount} outliers detected - these may represent natural variation or special cases worth investigating.`
      });
    } else if (severity === 'moderate') {
      insights.push({
        type: 'accent',
        icon: 'warning',
        message: `${outlierCount} outliers suggest some data points deviate significantly. Consider investigating causes.`
      });
    } else if (severity === 'high' || severity === 'critical') {
      insights.push({
        type: 'warn',
        icon: 'error',
        message: `${outlierCount} outliers indicate potential data quality issues or highly variable processes.`
      });
    }
    
    // Add method-specific insights
    const methods = data.methods;
    if (methods) {
      const iqrCount = methods.iqr?.outlier_count || 0;
      const zscoreCount = methods.zscore?.outlier_count || 0;
      
      if (Math.abs(iqrCount - zscoreCount) > outlierCount * 0.5) {
        insights.push({
          type: 'accent',
          icon: 'compare',
          message: 'Detection methods show significant disagreement - data may have complex distribution patterns.'
        });
      }
    }
    
    return insights;
  }

  // Enhanced Bias/Fairness Helper Methods
  getBiasRiskDescription(riskLevel: string): string {
    switch (riskLevel?.toLowerCase()) {
      case 'high':
        return 'Significant bias patterns detected. Immediate attention required to ensure fair and ethical data usage.';
      case 'medium':
        return 'Moderate bias indicators found. Review and mitigation strategies recommended before model development.';
      case 'low':
        return 'Minimal bias concerns detected. Continue with standard fairness monitoring practices.';
      default:
        return 'Bias risk assessment unavailable. Consider manual review of sensitive attributes.';
    }
  }

  getSensitiveAttrSeverity(confidence: string): 'primary' | 'accent' | 'warn' {
    switch (confidence?.toLowerCase()) {
      case 'high': return 'warn';
      case 'medium': return 'accent';
      default: return 'primary';
    }
  }

  getBiasScoreClass(score: number): string {
    if (score >= 0.7) return 'bias-high';
    if (score >= 0.4) return 'bias-medium';
    return 'bias-low';
  }

  getImbalanceSeverityColor(severity: string): 'primary' | 'accent' | 'warn' {
    switch (severity?.toLowerCase()) {
      case 'severe': case 'critical': return 'warn';
      case 'moderate': case 'medium': return 'accent';
      default: return 'primary';
    }
  }

  getImbalanceImpactDescription(imbalanceData: any): string {
    const ratio = imbalanceData.imbalance_ratio || 1;
    const severity = imbalanceData.severity?.toLowerCase() || 'mild';
    
    if (severity === 'severe' || ratio > 10) {
      return `Severe class imbalance detected (${ratio}:1 ratio). This may lead to biased predictions favoring the majority class. Consider resampling techniques, cost-sensitive learning, or ensemble methods.`;
    } else if (severity === 'moderate' || ratio > 3) {
      return `Moderate class imbalance observed (${ratio}:1 ratio). Monitor model performance across all classes and consider balancing techniques if accuracy differs significantly between classes.`;
    } else {
      return `Mild class imbalance detected (${ratio}:1 ratio). Generally acceptable for most machine learning applications, but monitor minority class performance.`;
    }
  }

  getImbalanceSolutions(severity: string): Array<{icon: string, method: string, description: string}> {
    const solutions: Array<{icon: string, method: string, description: string}> = [];
    
    switch (severity?.toLowerCase()) {
      case 'severe':
      case 'critical':
        solutions.push(
          {
            icon: 'add_circle',
            method: 'SMOTE/ADASYN',
            description: 'Generate synthetic minority samples using advanced oversampling techniques for severe imbalances.'
          },
          {
            icon: 'tune',
            method: 'Cost-Sensitive Learning',
            description: 'Adjust model training to penalize misclassification of minority classes more heavily.'
          },
          {
            icon: 'layers',
            method: 'Ensemble Methods',
            description: 'Use ensemble techniques like BalancedRandomForest or EasyEnsemble for robust predictions.'
          }
        );
        break;
      case 'moderate':
      case 'medium':
        solutions.push(
          {
            icon: 'balance',
            method: 'Stratified Sampling',
            description: 'Ensure proportional representation across classes in training and validation sets.'
          },
          {
            icon: 'remove_circle',
            method: 'Random Undersampling',
            description: 'Reduce majority class samples to balance the dataset while preserving data quality.'
          },
          {
            icon: 'settings',
            method: 'Threshold Tuning',
            description: 'Optimize classification thresholds to improve minority class prediction accuracy.'
          }
        );
        break;
      default:
        solutions.push(
          {
            icon: 'analytics',
            method: 'Performance Monitoring',
            description: 'Track precision, recall, and F1-score for all classes to ensure balanced performance.'
          },
          {
            icon: 'visibility',
            method: 'Regular Assessment',
            description: 'Periodically evaluate model fairness and bias metrics during development and production.'
          }
        );
    }
    
    return solutions;
  }

  getFairnessFlagSeverity(severity: string): string {
    switch (severity?.toLowerCase()) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      default: return 'info';
    }
  }

  getFairnessFlagColor(severity: string): 'primary' | 'accent' | 'warn' {
    switch (severity?.toLowerCase()) {
      case 'high': return 'warn';
      case 'medium': return 'accent';
      default: return 'primary';
    }
  }

  getHighPriorityRecommendations(): any[] {
    if (!this.basicResults?.bias_fairness_flags?.recommendations) return [];
    return this.basicResults.bias_fairness_flags.recommendations
      .filter((rec: any) => rec.priority === 'high' || rec.includes('urgent') || rec.includes('critical'));
  }

  getMediumPriorityRecommendations(): any[] {
    if (!this.basicResults?.bias_fairness_flags?.recommendations) return [];
    return this.basicResults.bias_fairness_flags.recommendations
      .filter((rec: any) => rec.priority === 'medium' || (!rec.includes('urgent') && !rec.includes('critical') && !rec.includes('optional')));
  }

  getLowPriorityRecommendations(): any[] {
    if (!this.basicResults?.bias_fairness_flags?.recommendations) return [];
    return this.basicResults.bias_fairness_flags.recommendations
      .filter((rec: any) => rec.priority === 'low' || rec.includes('optional') || rec.includes('consider'));
  }

  getRecommendationCategories(): Array<{title: string, icon: string, recommendations: any[]}> {
    if (!this.basicResults?.bias_fairness_flags?.recommendations) return [];
    
    const categories = [
      {
        title: 'Data Collection & Quality',
        icon: 'storage',
        recommendations: this.basicResults.bias_fairness_flags.recommendations
          .filter((rec: any) => typeof rec === 'string' ? 
            rec.toLowerCase().includes('data') || rec.toLowerCase().includes('collection') || rec.toLowerCase().includes('quality') :
            rec.category === 'data'
          ).map((rec: any) => this.formatRecommendation(rec))
      },
      {
        title: 'Model Development & Training',
        icon: 'model_training',
        recommendations: this.basicResults.bias_fairness_flags.recommendations
          .filter((rec: any) => typeof rec === 'string' ? 
            rec.toLowerCase().includes('model') || rec.toLowerCase().includes('training') || rec.toLowerCase().includes('algorithm') :
            rec.category === 'model'
          ).map((rec: any) => this.formatRecommendation(rec))
      },
      {
        title: 'Evaluation & Monitoring',
        icon: 'monitoring',
        recommendations: this.basicResults.bias_fairness_flags.recommendations
          .filter((rec: any) => typeof rec === 'string' ? 
            rec.toLowerCase().includes('monitor') || rec.toLowerCase().includes('evaluate') || rec.toLowerCase().includes('assess') :
            rec.category === 'monitoring'
          ).map((rec: any) => this.formatRecommendation(rec))
      },
      {
        title: 'Governance & Compliance',
        icon: 'gavel',
        recommendations: this.basicResults.bias_fairness_flags.recommendations
          .filter((rec: any) => typeof rec === 'string' ? 
            rec.toLowerCase().includes('compliance') || rec.toLowerCase().includes('governance') || rec.toLowerCase().includes('legal') :
            rec.category === 'governance'
          ).map((rec: any) => this.formatRecommendation(rec))
      }
    ].filter(category => category.recommendations.length > 0);

    // If no categorized recommendations, create a general category
    if (categories.length === 0) {
      categories.push({
        title: 'General Recommendations',
        icon: 'lightbulb',
        recommendations: this.basicResults.bias_fairness_flags.recommendations
          .map((rec: any) => this.formatRecommendation(rec))
      });
    }

    return categories;
  }

  formatRecommendation(rec: any): any {
    if (typeof rec === 'string') {
      return {
        title: this.extractRecommendationTitle(rec),
        description: rec,
        priority: this.inferPriority(rec),
        actions: this.extractActionItems(rec)
      };
    }
    return rec;
  }

  extractRecommendationTitle(text: string): string {
    // Extract the first sentence or up to 50 characters as title
    const firstSentence = text.split('.')[0];
    return firstSentence.length > 50 ? firstSentence.substring(0, 47) + '...' : firstSentence;
  }

  inferPriority(text: string): string {
    const lowerText = text.toLowerCase();
    if (lowerText.includes('urgent') || lowerText.includes('critical') || lowerText.includes('immediate')) {
      return 'high';
    }
    if (lowerText.includes('recommend') || lowerText.includes('should') || lowerText.includes('important')) {
      return 'medium';
    }
    return 'low';
  }

  extractActionItems(text: string): string[] {
    // Simple extraction of action items (sentences starting with action verbs)
    const sentences = text.split('.');
    return sentences
      .filter(sentence => {
        const trimmed = sentence.trim().toLowerCase();
        return trimmed.startsWith('implement') || trimmed.startsWith('establish') || 
               trimmed.startsWith('monitor') || trimmed.startsWith('review') ||
               trimmed.startsWith('ensure') || trimmed.startsWith('develop');
      })
      .map(sentence => sentence.trim())
      .slice(0, 3); // Limit to 3 action items
  }

  getPriorityIcon(priority: string): string {
    switch (priority?.toLowerCase()) {
      case 'high': return 'priority_high';
      case 'medium': return 'info';
      case 'low': return 'low_priority';
      default: return 'help_outline';
    }
  }

  // Enhanced Dimensionality & PCA Helper Methods
  getDimensionalityReductionClass(potential?: string): string {
    switch (potential?.toLowerCase()) {
      case 'high': return 'high-potential';
      case 'medium': return 'medium-potential';
      case 'low': return 'low-potential';
      default: return 'unknown-potential';
    }
  }

  getDimensionalityRecommendationSummary(): string {
    const potential = this.basicResults?.dimensionality_insights?.overview?.reduction_potential?.toLowerCase();
    switch (potential) {
      case 'high': return 'Reduce Now';
      case 'medium': return 'Consider Reduction';
      case 'low': return 'Keep Current';
      default: return 'Evaluate';
    }
  }

  getPCAVarianceInsight(percentage: number, components?: number, total?: number): string {
    if (!components || !total) return 'Insufficient data for analysis';
    
    const reduction = ((total - components) / total * 100).toFixed(0);
    if (percentage === 95) {
      if (components / total < 0.5) {
        return `Excellent! You can reduce dimensions by ${reduction}% while keeping 95% of information.`;
      } else if (components / total < 0.8) {
        return `Good reduction potential: ${reduction}% fewer dimensions with minimal information loss.`;
      } else {
        return `Limited reduction potential: Most components needed to preserve 95% variance.`;
      }
    } else { // 90%
      if (components / total < 0.3) {
        return `Outstanding! ${reduction}% dimension reduction with only 10% information loss.`;
      } else if (components / total < 0.6) {
        return `Good trade-off: ${reduction}% reduction with acceptable information loss.`;
      } else {
        return `Conservative approach: ${reduction}% reduction with 90% variance preserved.`;
      }
    }
  }

  getReductionPotentialClass(potential: string): string {
    switch (potential?.toLowerCase()) {
      case 'high': return 'potential-high';
      case 'medium': return 'potential-medium';
      case 'low': return 'potential-low';
      default: return 'potential-unknown';
    }
  }

  getReductionPotentialExplanation(potential: string): string {
    switch (potential?.toLowerCase()) {
      case 'high':
        return 'Strong dimensionality reduction recommended. Your data has significant redundancy that can be safely removed.';
      case 'medium':
        return 'Moderate reduction possible. Consider PCA for computational efficiency while monitoring information loss.';
      case 'low':
        return 'Limited reduction potential. Most features contribute unique information to your dataset.';
      default:
        return 'Unable to determine reduction potential. Further analysis required.';
    }
  }

  getPCAComponentsArray(): Array<{component: number, variance: number}> {
    if (!this.basicResults?.dimensionality_insights?.pca_analysis?.component_variances) return [];
    
    return this.basicResults.dimensionality_insights.pca_analysis.component_variances
      .map((variance: number, index: number) => ({
        component: index + 1,
        variance: variance
      }))
      .slice(0, 10); // Show first 10 components
  }

  getComponentDescription(componentNum: number, variance: number): string {
    const percentage = (variance * 100).toFixed(1);
    
    if (componentNum === 1) {
      return `Primary component capturing ${percentage}% of total data variance`;
    } else if (componentNum <= 3) {
      return `Key component explaining ${percentage}% of remaining variance`;
    } else if (variance > 0.05) {
      return `Significant component with ${percentage}% variance contribution`;
    } else {
      return `Minor component contributing ${percentage}% to total variance`;
    }
  }

  getCumulativeVarianceArray(): Array<{cumulative: number}> {
    if (!this.basicResults?.dimensionality_insights?.pca_analysis?.cumulative_variances) return [];
    
    return this.basicResults.dimensionality_insights.pca_analysis.cumulative_variances
      .map((cumVar: number) => ({ cumulative: cumVar }))
      .slice(0, 15); // Show first 15 cumulative values
  }

  getCumulativeLabel(cumulative: number): string {
    const percentage = cumulative * 100;
    if (percentage >= 95) return 'Excellent coverage';
    if (percentage >= 90) return 'Very good coverage';
    if (percentage >= 80) return 'Good coverage';
    if (percentage >= 70) return 'Moderate coverage';
    return 'Limited coverage';
  }

  getPCABusinessInsights(): Array<{type: string, icon: string, title: string, description: string, actions?: string[]}> {
    const insights: Array<{type: string, icon: string, title: string, description: string, actions?: string[]}> = [];
    const pcaData = this.basicResults?.dimensionality_insights?.pca_analysis;
    
    if (!pcaData) return insights;

    // Performance Impact Insight
    const total = pcaData?.total_components;
    const for95 = pcaData?.components_for_95_variance;
    if (total && for95) {
      const reduction = ((total - for95) / total * 100).toFixed(0);
      insights.push({
        type: 'performance',
        icon: 'speed',
        title: 'Performance Optimization',
        description: `Reducing to ${for95} components can improve model training speed by approximately ${reduction}% while preserving 95% of data information.`,
        actions: [
          'Implement PCA preprocessing pipeline',
          'Benchmark model performance before/after reduction',
          'Monitor for any accuracy degradation'
        ]
      });
    }

    // Storage Impact
    if (total && for95 && total > 20) {
      insights.push({
        type: 'storage',
        icon: 'storage',
        title: 'Storage & Memory Benefits',
        description: `Dimensionality reduction can significantly reduce memory usage and storage requirements for large datasets.`,
        actions: [
          'Calculate exact storage savings',
          'Update data pipeline for reduced dimensions',
          'Consider compressed data formats'
        ]
      });
    }

    // Visualization Benefits
    if (for95 && for95 <= 3) {
      insights.push({
        type: 'visualization',
        icon: 'visibility',
        title: 'Enhanced Visualization',
        description: `With ${for95} key components, you can create effective 2D/3D visualizations to understand data patterns and relationships.`,
        actions: [
          'Create 2D/3D scatter plots',
          'Use components for cluster visualization',
          'Develop interactive data exploration tools'
        ]
      });
    }

    // Noise Reduction
    const potential = pcaData?.dimensionality_reduction_potential;
    if (potential === 'high' || potential === 'medium') {
      insights.push({
        type: 'quality',
        icon: 'filter_alt',
        title: 'Noise Reduction',
        description: `PCA can help remove noise and redundant information, potentially improving model performance and interpretability.`,
        actions: [
          'Compare model accuracy with/without PCA',
          'Analyze feature importance in reduced space',
          'Validate results on test dataset'
        ]
      });
    }

    return insights;
  }

  getClusteringInsight(optimalClusters?: number): string {
    if (!optimalClusters) return 'Clustering analysis incomplete';
    
    if (optimalClusters === 1) {
      return 'Your data appears homogeneous with no distinct groupings';
    } else if (optimalClusters <= 3) {
      return `Clear data structure with ${optimalClusters} distinct groups`;
    } else if (optimalClusters <= 7) {
      return `Complex structure with ${optimalClusters} identifiable clusters`;
    } else {
      return `Highly complex data with ${optimalClusters} potential groupings`;
    }
  }

  getClusteringQualityClass(quality?: string): string {
    switch (quality?.toLowerCase()) {
      case 'excellent': case 'very good': return 'quality-excellent';
      case 'good': case 'moderate': return 'quality-good';
      case 'fair': case 'poor': return 'quality-fair';
      default: return 'quality-unknown';
    }
  }

  formatClusteringQuality(quality?: string): string {
    return quality?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown';
  }

  getClusteringQualityExplanation(quality: string): string {
    switch (quality?.toLowerCase()) {
      case 'excellent':
        return 'Clusters are very well-separated and distinct. Ideal for dimensionality reduction.';
      case 'very good':
        return 'Clear cluster boundaries with minimal overlap. Good candidate for reduction.';
      case 'good':
        return 'Reasonable cluster separation. Dimensionality reduction should preserve structure.';
      case 'moderate':
        return 'Some cluster overlap present. Monitor cluster preservation after reduction.';
      case 'fair':
        return 'Clusters are somewhat overlapping. Careful validation needed after reduction.';
      case 'poor':
        return 'Weak cluster structure. Dimensionality reduction may blur group boundaries.';
      default:
        return 'Cluster quality assessment unavailable.';
    }
  }

  getSilhouetteExplanation(score: number): string {
    if (score >= 0.7) {
      return 'Excellent cluster separation. Strong, well-defined groups.';
    } else if (score >= 0.5) {
      return 'Good cluster structure. Reasonable separation between groups.';
    } else if (score >= 0.25) {
      return 'Moderate clustering. Some overlap between groups exists.';
    } else if (score >= 0) {
      return 'Weak clustering structure. Groups are not well-separated.';
    } else {
      return 'Poor clustering. Data points may be in wrong clusters.';
    }
  }

  getStabilityClass(stability: string): string {
    switch (stability?.toLowerCase()) {
      case 'high': case 'stable': return 'stability-high';
      case 'medium': case 'moderate': return 'stability-medium';
      case 'low': case 'unstable': return 'stability-low';
      default: return 'stability-unknown';
    }
  }

  getStabilityExplanation(stability: string): string {
    switch (stability?.toLowerCase()) {
      case 'high':
        return 'Clusters remain consistent across different data samples. Highly reliable structure.';
      case 'stable':
        return 'Good stability with minor variations. Structure is generally reliable.';
      case 'medium':
        return 'Moderate stability. Some variation in cluster assignments expected.';
      case 'moderate':
        return 'Reasonable consistency with some sensitivity to data changes.';
      case 'low':
        return 'Low stability. Cluster assignments may vary significantly.';
      case 'unstable':
        return 'Unstable clustering. Results may not be reproducible.';
      default:
        return 'Stability assessment unavailable.';
    }
  }

  getClusterCharacteristics(): any[] {
    return this.basicResults?.dimensionality_insights?.clustering_analysis?.cluster_characteristics || [];
  }

  getStrategicRecommendations(): Array<{priority: string, title: string, description: string, benefits?: string[]}> {
    const recommendations: Array<{priority: string, title: string, description: string, benefits?: string[]}> = [];
    const dimData = this.basicResults?.dimensionality_insights;
    
    if (!dimData) return recommendations;

    const pcaData = dimData.pca_analysis;
    const clusterData = dimData.clustering_analysis;

    // High Priority Recommendations
    if (pcaData?.dimensionality_reduction_potential === 'high') {
      recommendations.push({
        priority: 'high',
        title: 'Implement Immediate Dimensionality Reduction',
        description: `Your data shows excellent potential for dimensionality reduction. Implementing PCA can significantly improve performance while preserving data quality.`,
        benefits: [
          'Faster model training and inference',
          'Reduced computational costs',
          'Lower storage requirements',
          'Improved visualization capabilities'
        ]
      });
    }

    // Medium Priority Recommendations
    if (clusterData?.optimal_clusters && clusterData.optimal_clusters > 1) {
      recommendations.push({
        priority: 'medium',
        title: 'Leverage Cluster Structure for Optimization',
        description: `Your data has ${clusterData.optimal_clusters} distinct clusters. This structure can be used to optimize analysis and improve model performance.`,
        benefits: [
          'Better feature engineering opportunities',
          'Improved model interpretability',
          'Targeted analysis for each cluster',
          'Enhanced anomaly detection'
        ]
      });
    }

    // Strategic Planning
    if (pcaData?.total_components && pcaData.total_components > 50) {
      recommendations.push({
        priority: 'medium',
        title: 'Develop Systematic Dimensionality Strategy',
        description: `With ${pcaData.total_components} features, develop a comprehensive strategy for feature selection and dimensionality management.`,
        benefits: [
          'Consistent approach across projects',
          'Improved model maintenance',
          'Better resource utilization',
          'Enhanced team productivity'
        ]
      });
    }

    return recommendations;
  }

  getTechnicalRecommendations(): Array<{icon: string, method: string, description: string, steps?: string[]}> {
    const recommendations: Array<{icon: string, method: string, description: string, steps?: string[]}> = [];
    const dimData = this.basicResults?.dimensionality_insights;
    
    if (!dimData) return recommendations;

    // PCA Implementation
    if (dimData.pca_analysis?.dimensionality_reduction_potential !== 'low') {
      recommendations.push({
        icon: 'compress',
        method: 'Principal Component Analysis (PCA)',
        description: 'Reduce dimensionality while preserving maximum variance in your data.',
        steps: [
          'Standardize your features to unit variance',
          'Apply PCA transformation to training data',
          'Determine optimal number of components (95% variance)',
          'Transform test data using fitted PCA model',
          'Validate model performance on reduced dataset'
        ]
      });
    }

    // Clustering-based Approach
    if (dimData.clustering_analysis?.optimal_clusters && dimData.clustering_analysis.optimal_clusters > 1) {
      recommendations.push({
        icon: 'group_work',
        method: 'Cluster-Aware Dimensionality Reduction',
        description: 'Use cluster structure to guide feature selection and reduction.',
        steps: [
          'Identify and validate optimal cluster assignments',
          'Analyze feature importance within each cluster',
          'Apply cluster-specific dimensionality reduction',
          'Combine reduced representations',
          'Evaluate cluster preservation in reduced space'
        ]
      });
    }

    // Feature Selection
    recommendations.push({
      icon: 'tune',
      method: 'Feature Selection Techniques',
      description: 'Select most informative features using statistical methods.',
      steps: [
        'Calculate feature importance scores',
        'Apply correlation analysis to remove redundancy',
        'Use statistical tests for feature relevance',
        'Implement recursive feature elimination',
        'Cross-validate final feature set'
      ]
    });

    // Hybrid Approach
    if (dimData.pca_analysis && dimData.clustering_analysis) {
      recommendations.push({
        icon: 'merge',
        method: 'Hybrid PCA-Clustering Approach',
        description: 'Combine PCA and clustering insights for optimal dimensionality reduction.',
        steps: [
          'Apply initial PCA to reduce obvious redundancy',
          'Perform clustering on PCA-transformed data',
          'Refine component selection based on cluster preservation',
          'Validate final model on original cluster structure',
          'Document transformation pipeline for production'
        ]
      });
    }

    return recommendations;
  }

  // Math helper for templates
  Math = Math;

  // PCA Component Features Helper Methods
  getPCAComponentFeatures(): any[] {
    if (!this.basicResults?.dimensionality_insights?.pca_analysis?.component_features) {
      return [];
    }
    return this.basicResults.dimensionality_insights.pca_analysis.component_features;
  }

  getTopFeaturesForComponent(component: any): any[] {
    return component?.top_features || [];
  }

  getFeatureContributionClass(percentage: number): string {
    if (percentage >= 30) return 'high-contribution';
    if (percentage >= 20) return 'medium-contribution';
    if (percentage >= 10) return 'low-contribution';
    return 'minimal-contribution';
  }

  getFeatureContributionIcon(percentage: number): string {
    if (percentage >= 30) return 'trending_up';
    if (percentage >= 20) return 'trending_neutral';
    if (percentage >= 10) return 'trending_down';
    return 'remove';
  }

  getLoadingDirection(loading: number): string {
    return loading >= 0 ? 'positive' : 'negative';
  }

  getLoadingDirectionIcon(loading: number): string {
    return loading >= 0 ? 'north' : 'south';
  }

  getComponentContributionExplanation(component: any): string {
    if (!component?.top_features?.length) return '';
    
    const topFeature = component.top_features[0];
    const componentNum = component.component?.replace('PC', '') || '1';
    
    return `PC${componentNum} is primarily driven by ${topFeature.feature} (${topFeature.percentage.toFixed(1)}% contribution)`;
  }

  formatLoadingValue(loading: number): string {
    return loading.toFixed(3);
  }

  getVarianceInterpretation(variance: number): string {
    const percentage = variance * 100;
    if (percentage >= 50) return 'Dominant component - captures majority of data variation';
    if (percentage >= 25) return 'Major component - significant portion of data variation';
    if (percentage >= 10) return 'Important component - notable data variation';
    if (percentage >= 5) return 'Moderate component - meaningful variation';
    return 'Minor component - limited variation captured';
  }







}
