import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';
import { NgChartsModule } from 'ng2-charts';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TextFieldModule } from '@angular/cdk/text-field';
import { ApiService } from '../../services/api.service';
import { DatasetService } from '../../services/dataset.service';
import { DatasetInfo } from '../../models/api.models';

interface ChatMessage {
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  plotData?: any;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    FormsModule,
    NgChartsModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    TextFieldModule
  ],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit {
  currentDataset: DatasetInfo | null = null;
  messages: ChatMessage[] = [];
  currentQuery: string = '';
  selectedPlotType: string = '';
  selectedColumn: string = '';
  bollingerWindow: number = 20;
  isLoading: boolean = false;
  currentTime: Date = new Date();
  showChartOptions: boolean = false;

  bollingerBandChartOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { 
        display: true, 
        position: 'top',
        labels: {
          color: '#e0e0e0'
        }
      },
      title: { 
        display: true, 
        text: 'Bollinger Area Analysis',
        color: '#00ff88'
      }
    },
    scales: {
      x: { 
        title: { display: true, text: 'Data Points', color: '#e0e0e0' },
        ticks: { color: '#e0e0e0' },
        grid: { color: 'rgba(0, 255, 136, 0.1)' }
      },
      y: { 
        title: { display: true, text: 'Value', color: '#e0e0e0' },
        ticks: { color: '#e0e0e0' },
        grid: { color: 'rgba(0, 255, 136, 0.1)' }
      }
    }
  };

  lineTrendChartOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { 
        display: true, 
        position: 'top',
        labels: {
          color: '#e0e0e0'
        }
      },
      title: { 
        display: true, 
        text: 'Numeric Trends Analysis',
        color: '#00ff88'
      }
    },
    scales: {
      x: { 
        title: { display: true, text: 'Data Points', color: '#e0e0e0' },
        ticks: { color: '#e0e0e0' },
        grid: { color: 'rgba(0, 255, 136, 0.1)' }
      },
      y: { 
        title: { display: true, text: 'Values', color: '#e0e0e0' },
        ticks: { color: '#e0e0e0' },
        grid: { color: 'rgba(0, 255, 136, 0.1)' }
      }
    }
  };

  constructor(
    private apiService: ApiService,
    private datasetService: DatasetService
  ) {}

  ngOnInit() {
    this.datasetService.currentDataset$.subscribe(dataset => {
      this.currentDataset = dataset;
      if (dataset) {
        this.addWelcomeMessage();
      }
    });
  }

  private addWelcomeMessage() {
    this.messages = [{
      type: 'ai',
      content: `Hello! I'm your AI data assistant. I can help you analyze your dataset "${this.currentDataset?.filename}". Try asking: "summarize my data", "show me averages", "any missing values?", or "help" to see what I can do!`,
      timestamp: new Date()
    }];
  }

  sendMessage() {
    if (!this.currentQuery.trim() || !this.currentDataset || this.isLoading) return;

    // Add user message
    this.messages.push({
      type: 'user',
      content: this.currentQuery,
      timestamp: new Date()
    });

    const query = this.currentQuery;
    this.currentQuery = '';
    this.isLoading = true;

    // Handle plot requests
    if (this.selectedPlotType === 'bollinger_band' || this.selectedPlotType === 'line_trend') {
      console.log('🔍 DEBUG: Creating visualization with plot type:', this.selectedPlotType);
      this.apiService.talkToDataPlot(
        this.currentDataset.dataset_id,
        this.selectedPlotType,
        this.selectedColumn || undefined,
        this.bollingerWindow
      ).subscribe({
        next: (resp) => {
          const message: ChatMessage = {
            type: 'ai',
            content: resp.answer,
            timestamp: new Date(),
            plotData: resp.plot_data
          };
          this.messages.push(message);
          this.isLoading = false;
          this.resetForm();
        },
        error: (err) => {
          this.messages.push({
            type: 'ai',
            content: `❌ Error creating visualization: ${err.error?.detail || 'Failed to generate plot'}`,
            timestamp: new Date()
          });
          this.isLoading = false;
          this.resetForm();
        }
      });
    } else {
      // Handle regular Q&A
      this.apiService.talkToData(
        this.currentDataset.dataset_id,
        query,
        this.selectedColumn || undefined
      ).subscribe({
        next: (resp) => {
          this.messages.push({
            type: 'ai',
            content: resp.answer,
            timestamp: new Date()
          });
          this.isLoading = false;
          this.resetForm();
        },
        error: (err) => {
          this.messages.push({
            type: 'ai',
            content: `❌ Error: ${err.error?.detail || 'Failed to get answer'}`,
            timestamp: new Date()
          });
          this.isLoading = false;
          this.resetForm();
        }
      });
    }
  }

  private resetForm() {
    this.selectedPlotType = '';
    this.selectedColumn = '';
    this.bollingerWindow = 20;
  }

  createBollingerChart(plotData: any): any {
    return {
      labels: plotData.dates?.slice(0, 100) || Array.from({length: plotData.values?.length || 0}, (_, i) => i),
      datasets: [
        { 
          label: 'Upper Band', 
          data: plotData.upper?.slice(0, 100) || [], 
          borderColor: 'rgba(255, 102, 0, 0.8)', 
          backgroundColor: 'rgba(255, 102, 0, 0.2)',
          fill: '+1',
          tension: 0.4,
          pointRadius: 0,
          order: 1
        },
        { 
          label: 'Lower Band', 
          data: plotData.lower?.slice(0, 100) || [], 
          borderColor: 'rgba(255, 102, 0, 0.8)', 
          backgroundColor: 'rgba(255, 102, 0, 0.2)',
          fill: false,
          tension: 0.4,
          pointRadius: 0,
          order: 2
        },
        { 
          label: 'Moving Average', 
          data: plotData.ma?.slice(0, 100) || [], 
          borderColor: '#2196f3', 
          backgroundColor: 'transparent',
          fill: false,
          tension: 0.4,
          pointRadius: 0,
          borderWidth: 2,
          order: 3
        },
        { 
          label: 'Value', 
          data: plotData.values?.slice(0, 100) || [], 
          borderColor: '#00ff88', 
          backgroundColor: 'transparent',
          fill: false,
          tension: 0.4,
          pointRadius: 0,
          borderWidth: 2,
          order: 4
        }
      ]
    };
  }

  createLineTrendChart(plotData: any): any {
    const datasets = plotData.datasets?.map((dataset: any, index: number) => ({
      label: dataset.label,
      data: dataset.data?.slice(0, 100) || [],
      borderColor: dataset.color || (index === 0 ? '#00ff88' : '#ff6600'),
      backgroundColor: `${dataset.color || (index === 0 ? '#00ff88' : '#ff6600')}20`,
      fill: false,
      tension: 0.4,
      pointRadius: 2,
      pointHoverRadius: 4
    })) || [];

    return {
      labels: plotData.dates?.slice(0, 100) || Array.from({length: datasets[0]?.data?.length || 0}, (_, i) => i),
      datasets: datasets
    };
  }

  getChartData(plotData: any, isLineTrend: boolean = false): any {
    if (isLineTrend || plotData.datasets) {
      return this.createLineTrendChart(plotData);
    } else {
      return this.createBollingerChart(plotData);
    }
  }

  getChartOptions(plotData: any): any {
    if (plotData.datasets) {
      // Line trend chart - check if we have actual dates or just data points
      const hasRealDates = plotData.dates && plotData.dates.length > 0 && 
                          typeof plotData.dates[0] === 'string' && 
                          plotData.dates[0].includes('-');
      
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { 
            display: true, 
            position: 'top',
            labels: {
              color: '#e0e0e0'
            }
          },
          title: { 
            display: true, 
            text: 'Numeric Trend Analysis',
            color: '#00ff88'
          }
        },
        scales: {
          x: { 
            title: { 
              display: true, 
              text: hasRealDates ? 'Date' : 'Data Points', 
              color: '#e0e0e0' 
            },
            ticks: { color: '#e0e0e0' },
            grid: { color: 'rgba(0, 255, 136, 0.1)' }
          },
          y: { 
            title: { display: true, text: 'Values', color: '#e0e0e0' },
            ticks: { color: '#e0e0e0' },
            grid: { color: 'rgba(0, 255, 136, 0.1)' }
          }
        }
      };
    } else {
      // Bollinger band chart
      return this.bollingerBandChartOptions;
    }
  }

  formatTime(date: Date): string {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  trackByIndex(index: number, item: any): number {
    return index;
  }

  toggleChartOptions() {
    this.showChartOptions = !this.showChartOptions;
  }

  selectChart(type: string) {
    console.log('🔍 DEBUG: Chart type selected:', type);
    this.selectedPlotType = type;
    if (!type) {
      this.showChartOptions = false;
    }
  }

  getNumericColumns(): string[] {
    if (!this.currentDataset || !this.currentDataset.column_names) return [];
    
    // Return all columns and let backend validate which are numeric
    // This ensures we show actual column names from the dataset
    return this.currentDataset.column_names;
  }
}
