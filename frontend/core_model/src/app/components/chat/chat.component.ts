import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TextFieldModule } from '@angular/cdk/text-field';
import { NgChartsModule } from 'ng2-charts';
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
    FormsModule,
    MatIconModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatTooltipModule,
    TextFieldModule,
    NgChartsModule
  ],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit {
  currentDataset: DatasetInfo | null = null;
  messages: ChatMessage[] = [];
  currentQuery: string = '';
  showChartOptions = false;
  selectedPlotType = '';
  selectedColumn = '';
  bollingerWindow = 20;
  showAnalysisMatrix = false;
  isLoading: boolean = false;
  isTyping: boolean = false;
  currentTime: Date = new Date();
  errorMessage: string = '';
  retryCount: number = 0;
  maxRetries: number = 3;

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

    // Clear any previous errors
    this.errorMessage = '';
    this.retryCount = 0;

    // Add user message
    this.messages.push({
      type: 'user',
      content: this.currentQuery,
      timestamp: new Date()
    });

    const query = this.currentQuery;
    this.currentQuery = '';
    this.isLoading = true;
    this.isTyping = true;

    // Add typing indicator
    this.addTypingIndicator();

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
          this.removeTypingIndicator();
          const message: ChatMessage = {
            type: 'ai',
            content: resp.answer,
            timestamp: new Date(),
            plotData: resp.plot_data
          };
          this.messages.push(message);
          this.isLoading = false;
          this.isTyping = false;
          this.resetForm();
          this.scrollToBottom();
        },
        error: (err) => {
          this.removeTypingIndicator();
          this.handleError(err, 'visualization', query);
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
          this.removeTypingIndicator();
          this.messages.push({
            type: 'ai',
            content: resp.answer,
            timestamp: new Date()
          });
          this.isLoading = false;
          this.isTyping = false;
          this.resetForm();
          this.scrollToBottom();
        },
        error: (err) => {
          this.removeTypingIndicator();
          this.handleError(err, 'analysis', query);
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

  toggleAnalysisMatrix() {
    this.showAnalysisMatrix = !this.showAnalysisMatrix;
    // Reset chart selection when showing matrix
    if (this.showAnalysisMatrix) {
      this.selectedPlotType = '';
      this.showChartOptions = false;
    }
  }

  selectChart(type: string) {
    console.log('🔍 DEBUG: Chart type selected:', type);
    this.selectedPlotType = type;
    if (!type) {
      this.showChartOptions = false;
    }
    
    // Don't auto-render immediately - wait for column selection
    // Charts will render when user selects a column from dropdown
  }

  getNumericColumns(): string[] {
    if (!this.currentDataset || !this.currentDataset.column_names) return [];
    
    // Return all columns and let backend validate which are numeric
    // This ensures we show actual column names from the dataset
    return this.currentDataset.column_names;
  }

  // Handle column dropdown change
  onColumnChange(column: string) {
    console.log('🔍 DEBUG: Column changed to:', column);
    this.selectedColumn = column;
    
    // Auto-render chart when column is selected
    if (this.selectedPlotType && (this.selectedPlotType === 'bollinger_band' || this.selectedPlotType === 'line_trend')) {
      this.renderChartWithSettings();
    }
  }

  // Handle Bollinger window change
  onWindowChange(window: number) {
    console.log('🔍 DEBUG: Window changed to:', window);
    this.bollingerWindow = window;
    
    // Auto-render Bollinger chart when window changes
    if (this.selectedPlotType === 'bollinger_band') {
      this.renderChartWithSettings();
    }
  }

  // Render chart with current settings
  private renderChartWithSettings() {
    if (!this.currentDataset || this.isLoading) return;
    
    console.log('🎯 DEBUG: Rendering chart with settings:', {
      type: this.selectedPlotType,
      column: this.selectedColumn,
      window: this.bollingerWindow
    });
    
    // Add user message to show what was generated
    let chartDescription = '';
    if (this.selectedPlotType === 'bollinger_band') {
      chartDescription = `Bollinger Bands${this.selectedColumn ? ` for ${this.selectedColumn}` : ''} (${this.bollingerWindow}-period)`;
    } else if (this.selectedPlotType === 'line_trend') {
      chartDescription = `Line Chart${this.selectedColumn ? ` for ${this.selectedColumn}` : ' for all columns'}`;
    }
    
    this.messages.push({
      type: 'user',
      content: chartDescription,
      timestamp: new Date()
    });
    
    this.isLoading = true;
    this.isTyping = true;
    
    // Add typing indicator
    this.messages.push({
      type: 'ai',
      content: 'typing-indicator',
      timestamp: new Date()
    });
    
    // Call the plot API directly
    this.apiService.talkToDataPlot(
      this.currentDataset.dataset_id,
      this.selectedPlotType,
      this.selectedColumn || undefined,
      this.selectedPlotType === 'bollinger_band' ? this.bollingerWindow : undefined
    ).subscribe({
      next: (resp) => {
        // Remove typing indicator
        const typingIndex = this.messages.findIndex(msg => msg.content === 'typing-indicator');
        if (typingIndex !== -1) {
          this.messages.splice(typingIndex, 1);
        }
        
        const message: ChatMessage = {
          type: 'ai',
          content: resp.answer,
          timestamp: new Date(),
          plotData: resp.plot_data
        };
        this.messages.push(message);
        this.isLoading = false;
        this.isTyping = false;
        
        // Scroll to bottom
        setTimeout(() => {
          const container = document.querySelector('.messages-area');
          if (container) {
            container.scrollTop = container.scrollHeight;
          }
        }, 100);
      },
      error: (err) => {
        // Remove typing indicator
        const typingIndex = this.messages.findIndex(msg => msg.content === 'typing-indicator');
        if (typingIndex !== -1) {
          this.messages.splice(typingIndex, 1);
        }
        
        this.isLoading = false;
        this.isTyping = false;
        
        const errorDetail = err.error?.detail || err.message || 'Unknown error occurred';
        this.messages.push({
          type: 'ai',
          content: `❌ **Error generating chart:** ${errorDetail}`,
          timestamp: new Date()
        });
      }
    });
  }

  clearError() {
    this.errorMessage = '';
    this.retryCount = 0;
  }

  // Auto-render chart when chart type is selected
  private autoRenderChart(chartType: string) {
    if (!this.currentDataset || this.isLoading) return;
    
    let query = '';
    if (chartType === 'bollinger_band') {
      query = 'Generate Bollinger Bands chart';
    } else if (chartType === 'line_trend') {
      query = 'Show line trend chart';
    }
    
    if (query) {
      // Add user message to show what was auto-generated
      this.messages.push({
        type: 'user',
        content: query + (this.selectedColumn ? ` for ${this.selectedColumn}` : ''),
        timestamp: new Date()
      });
      
      this.isLoading = true;
      this.isTyping = true;
      // Add typing indicator manually
      this.messages.push({
        type: 'ai',
        content: 'typing-indicator',
        timestamp: new Date()
      });
      
      // Generate chart using existing sendMessage logic
      const originalQuery = this.currentQuery;
      this.currentQuery = query;
      
      // Handle plot requests using existing logic
      this.apiService.talkToData(
        this.currentDataset.dataset_id,
        query,
        this.selectedColumn || undefined
      ).subscribe({
        next: (resp) => {
          // Remove typing indicator manually
          const typingIndex = this.messages.findIndex(msg => msg.content === 'typing-indicator');
          if (typingIndex !== -1) {
            this.messages.splice(typingIndex, 1);
          }
          
          const message: ChatMessage = {
            type: 'ai',
            content: resp.answer,
            timestamp: new Date(),
            plotData: resp.plot_data
          };
          this.messages.push(message);
          this.isLoading = false;
          this.isTyping = false;
          
          // Scroll to bottom manually
          setTimeout(() => {
            const container = document.querySelector('.messages-area');
            if (container) {
              container.scrollTop = container.scrollHeight;
            }
          }, 100);
        },
        error: (err) => {
          this.removeTypingIndicator();
          this.handleError(err, 'visualization', query);
        }
      });
      
      this.currentQuery = originalQuery;
    }
  }

  // Quick action methods
  askQuickQuestion(question: string) {
    if (this.isLoading || !this.currentDataset) return;
    
    this.currentQuery = question;
    this.sendMessage();
  }

  // Format AI response with HTML
  formatAIResponse(content: string): string {
    if (!content) return '';
    
    // Don't format user messages
    if (!content.includes('**') && !content.includes('###') && !content.includes('•')) {
      return this.escapeHtml(content);
    }
    
    let formatted = content;
    
    // Convert markdown headers to HTML
    formatted = formatted.replace(/### (.*?)$/gm, '<h4 class="response-header">$1</h4>');
    formatted = formatted.replace(/## (.*?)$/gm, '<h3 class="response-header">$1</h3>');
    formatted = formatted.replace(/# (.*?)$/gm, '<h2 class="response-header">$1</h2>');
    
    // Convert bold text
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong class="response-bold">$1</strong>');
    
    // Convert bullet points
    formatted = formatted.replace(/^• (.*?)$/gm, '<div class="response-bullet">• $1</div>');
    
    // Convert code blocks (inline)
    formatted = formatted.replace(/`([^`]+)`/g, '<code class="response-code">$1</code>');
    
    // Convert horizontal rules
    formatted = formatted.replace(/^---$/gm, '<hr class="response-divider">');
    
    // Convert line breaks to proper HTML
    formatted = formatted.replace(/\n\n/g, '<br><br>');
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Handle emoji spacing
    formatted = formatted.replace(/([📊📈📋⚠️✅🔍💡🎯⚡🟢🟡🔴💰🤖])/g, '<span class="response-emoji">$1</span>');
    
    return formatted;
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Retry last query
  retryLastQuery() {
    if (this.retryCount >= this.maxRetries || this.isLoading) return;
    
    this.retryCount++;
    this.errorMessage = '';
    
    // Get the last user message to retry
    const lastUserMessage = [...this.messages].reverse().find(msg => msg.type === 'user');
    if (lastUserMessage) {
      this.currentQuery = lastUserMessage.content;
      this.sendMessage();
    }
  }

  // Typing indicator methods
  private addTypingIndicator() {
    // Remove any existing typing indicator
    this.removeTypingIndicator();
    
    // Add new typing indicator
    this.messages.push({
      type: 'ai',
      content: 'typing-indicator',
      timestamp: new Date()
    });
  }

  private removeTypingIndicator() {
    // Remove typing indicator message
    const typingIndex = this.messages.findIndex(msg => msg.content === 'typing-indicator');
    if (typingIndex !== -1) {
      this.messages.splice(typingIndex, 1);
    }
  }

  // Scroll to bottom
  private scrollToBottom() {
    setTimeout(() => {
      const container = document.querySelector('.messages-area');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }, 100);
  }

  // Error handling
  private handleError(err: any, context: string, originalQuery: string) {
    this.isLoading = false;
    this.isTyping = false;
    
    const errorDetail = err.error?.detail || err.message || 'Unknown error occurred';
    this.errorMessage = errorDetail;
    
    // Determine if error is retryable
    const isRetryable = this.isRetryableError(err);
    
    let errorContent = `❌ **Error during ${context}:** ${errorDetail}`;
    
    if (isRetryable && this.retryCount < this.maxRetries) {
      errorContent += `\n\n🔄 **Retry available** (${this.retryCount + 1}/${this.maxRetries})`;
    } else if (this.retryCount >= this.maxRetries) {
      errorContent += `\n\n⚠️ **Maximum retries reached.** Please try a different query or check your connection.`;
    }
    
    this.messages.push({
      type: 'ai',
      content: errorContent,
      timestamp: new Date()
    });
    
    this.resetForm();
    this.scrollToBottom();
  }

  private isRetryableError(err: any): boolean {
    const status = err.status;
    const errorMessage = (err.error?.detail || err.message || '').toLowerCase();
    
    // Network errors, timeouts, and server errors are retryable
    return status >= 500 || status === 0 || 
           errorMessage.includes('timeout') || 
           errorMessage.includes('network') ||
           errorMessage.includes('connection');
  }

  getInputPlaceholder(): string {
    if (!this.currentDataset) {
      return 'Upload a dataset to start chatting...';
    }
    
    if (this.messages.length === 0) {
      return 'Ask me anything about your data...';
    }
    
    return 'Continue the conversation...';
  }

}
