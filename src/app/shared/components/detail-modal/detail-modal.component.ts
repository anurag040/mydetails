import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ChartConfiguration, ChartOptions } from 'chart.js';
import { Summary } from '../../models/summary.model';

interface Alert {
  severity: 'high' | 'medium' | 'low';
  icon: string;
  title: string;
  message: string;
  time: string;
}

@Component({
  selector: 'app-detail-modal',
  templateUrl: './detail-modal.component.html',
  styleUrls: ['./detail-modal.component.scss']
})
export class DetailModalComponent implements OnInit {
  metricName!: string;
  chartData!: ChartConfiguration<'line'>['data'];
  chartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    elements: { 
      point: { radius: 0 },
      line: { tension: 0.4 }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.07)' },
        ticks: { color: '#a3adc8', maxTicksLimit: 8 }
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.07)' },
        ticks: { color: '#a3adc8' }
      }
    },
    plugins: {
      legend: { 
        display: true,
        position: 'top',
        labels: {
          color: '#a3adc8',
          usePointStyle: true,
          pointStyle: 'line',
          font: { size: 10 }
        }
      },
      tooltip: {
        backgroundColor: '#1f2330',
        titleColor: '#e3e9ff',
        bodyColor: '#a3adc8',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        mode: 'index',
        intersect: false
      }
    },
    interaction: {
      mode: 'index',
      intersect: false
    }
  };

  insights: string[] = [];
  timePeriods = ['1H', '6H', '24H', '7D'];
  selectedPeriod = '24H';

  constructor(@Inject(MAT_DIALOG_DATA) public data: { metric: string; summary?: Summary }) {}

  ngOnInit(): void {
    this.metricName = this.data.metric;
    this.generateSyntheticChart();
    this.generateInsights();
  }

  // Update chart when period changes
  onPeriodChange(period: string): void {
    this.selectedPeriod = period;
    this.generateSyntheticChart();
  }

  // Icon and category methods
  getMetricCategory(): string {
    const metricLower = this.metricName.toLowerCase();
    if (metricLower.includes('swift')) return 'swift';
    if (metricLower.includes('fed')) return 'fed';
    if (metricLower.includes('chips')) return 'chips';
    return 'default';
  }

  getMetricIcon(): string {
    const metricLower = this.metricName.toLowerCase();
    if (metricLower.includes('swift')) return 'swap_horiz';
    if (metricLower.includes('fed')) return 'account_balance';
    if (metricLower.includes('chips')) return 'credit_card';
    if (metricLower.includes('payment')) return 'payments';
    if (metricLower.includes('deposit')) return 'savings';
    if (metricLower.includes('message')) return 'message';
    return 'analytics';
  }

  // Data methods
  getCurrentValue(): number {
    return Math.floor(Math.random() * 1000) + 500;
  }

  getTrendClass(): string {
    return Math.random() > 0.5 ? 'positive' : 'negative';
  }

  getTrendIcon(): string {
    return this.getTrendClass() === 'positive' ? 'trending_up' : 'trending_down';
  }

  getTrendPercentage(): number {
    return parseFloat((Math.random() * 10 + 1).toFixed(1));
  }

  getAveragePerHour(): number {
    return Math.floor(Math.random() * 50) + 20;
  }

  getPeakTime(): string {
    const hours = ['9:30 AM', '10:15 AM', '11:45 AM', '1:20 PM', '2:45 PM', '3:30 PM'];
    return hours[Math.floor(Math.random() * hours.length)];
  }

  getGrowthRate(): number {
    return parseFloat((Math.random() * 20 - 5).toFixed(1));
  }

  getSuccessRate(): number {
    return parseFloat((98 + Math.random() * 2).toFixed(1));
  }

  getAvgProcessingTime(): number {
    return Math.floor(Math.random() * 100) + 80;
  }

  getTotalVolume(): number {
    return parseFloat((Math.random() * 500 + 100).toFixed(1));
  }

  // Insights methods
  getInsightIcon(insight: string): string {
    if (insight.includes('up') || insight.includes('increase')) return 'trending_up';
    if (insight.includes('down') || insight.includes('decrease')) return 'trending_down';
    if (insight.includes('spike') || insight.includes('peak')) return 'timeline';
    if (insight.includes('latency') || insight.includes('performance')) return 'speed';
    return 'info';
  }

  // Alerts methods
  hasAlerts(): boolean {
    return Math.random() > 0.7; // 30% chance of having alerts
  }

  getAlerts(): Alert[] {
    const alerts: Alert[] = [
      {
        severity: 'medium',
        icon: 'warning',
        title: 'Processing Delay',
        message: 'Average processing time increased by 15%',
        time: '5 minutes ago'
      },
      {
        severity: 'low',
        icon: 'info',
        title: 'Volume Spike',
        message: 'Transaction volume above average for this time',
        time: '12 minutes ago'
      }
    ];
    return alerts.slice(0, Math.floor(Math.random() * 2) + 1);
  }

  // Action methods
  exportData(): void {
    console.log('Exporting data for:', this.metricName);
    // Implement export functionality
  }

  setAlert(): void {
    console.log('Setting alert for:', this.metricName);
    // Implement alert setting functionality
  }

  private generateSyntheticChart() {
    // Determine data points based on selected period
    let pointCount: number;
    let labelFormat: (index: number) => string;

    switch (this.selectedPeriod) {
      case '1H':
        pointCount = 60; // 60 minutes
        labelFormat = (i) => {
          const minute = (new Date().getMinutes() - pointCount + i + 60) % 60;
          return `${minute.toString().padStart(2, '0')}m`;
        };
        break;
      case '6H':
        pointCount = 36; // 6 hours in 10-minute intervals
        labelFormat = (i) => {
          const totalMinutes = (new Date().getHours() * 60 + new Date().getMinutes()) - (pointCount * 10) + (i * 10);
          const hour = Math.floor(totalMinutes / 60) % 24;
          const minute = totalMinutes % 60;
          return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
        };
        break;
      case '7D':
        pointCount = 168; // 7 days in hourly intervals
        labelFormat = (i) => {
          const daysAgo = Math.floor((pointCount - i) / 24);
          const hour = (new Date().getHours() - (pointCount - i) + 24 * 7) % 24;
          return daysAgo === 0 ? `${hour}h` : `${daysAgo}d`;
        };
        break;
      default: // 24H
        pointCount = 48; // 48 hours in 30-minute intervals
        labelFormat = (i) => {
          const hour = (new Date().getHours() - pointCount + i + 24) % 24;
          return `${hour.toString().padStart(2, '0')}:00`;
        };
    }

    const base = this.getCurrentValue();
    const data: number[] = [];
    const movingAverage: number[] = [];
    const upperBand: number[] = [];
    const lowerBand: number[] = [];
    const period = Math.min(20, Math.floor(pointCount / 3)); // Adaptive period based on data length
    const standardDeviations = 2; // 2 standard deviations

    // Generate base data with some volatility
    for (let i = 0; i < pointCount; i++) {
      const noise = Math.sin(i / 8) * 15 + Math.random() * 30 - 15;
      const trend = i * (this.selectedPeriod === '7D' ? 0.5 : 1.5); // Different trends for different periods
      const value = base + noise + trend;
      data.push(parseFloat(value.toFixed(0)));
    }

    // Calculate Bollinger Bands
    for (let i = 0; i < pointCount; i++) {
      if (i >= period - 1) {
        // Calculate moving average
        const slice = data.slice(i - period + 1, i + 1);
        const avg = slice.reduce((sum, val) => sum + val, 0) / period;
        movingAverage[i] = avg;

        // Calculate standard deviation
        const squaredDiffs = slice.map(val => Math.pow(val - avg, 2));
        const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / period;
        const stdDev = Math.sqrt(variance);

        // Calculate upper and lower bands
        upperBand[i] = avg + (standardDeviations * stdDev);
        lowerBand[i] = avg - (standardDeviations * stdDev);
      } else {
        // For early data points, use simple average
        const slice = data.slice(0, i + 1);
        const avg = slice.reduce((sum, val) => sum + val, 0) / slice.length;
        movingAverage[i] = avg;
        upperBand[i] = avg + (data[i] * 0.1);
        lowerBand[i] = avg - (data[i] * 0.1);
      }
    }

    this.chartData = {
      labels: Array.from({ length: pointCount }, (_, i) => labelFormat(i)),
      datasets: [
        {
          label: 'Upper Band',
          data: upperBand,
          borderWidth: 1,
          tension: 0.4,
          pointRadius: 0,
          borderColor: 'rgba(255, 72, 219, 0.6)',
          backgroundColor: 'transparent',
          fill: false,
          borderDash: [3, 3]
        },
        {
          label: 'Moving Average',
          data: movingAverage,
          borderWidth: 2,
          tension: 0.4,
          pointRadius: 0,
          borderColor: '#00fff7',
          backgroundColor: 'transparent',
          fill: false
        },
        {
          label: 'Lower Band',
          data: lowerBand,
          borderWidth: 1,
          tension: 0.4,
          pointRadius: 0,
          borderColor: 'rgba(255, 72, 219, 0.6)',
          backgroundColor: 'rgba(0, 255, 247, 0.1)',
          fill: '+1', // Fill between this line and the upper band
          borderDash: [3, 3]
        },
        {
          label: this.metricName,
          data: data,
          borderWidth: 2,
          tension: 0.4,
          pointRadius: this.selectedPeriod === '1H' ? 0 : 1,
          pointHoverRadius: 4,
          borderColor: '#ffffff',
          backgroundColor: '#ffffff',
          fill: false,
          pointBackgroundColor: '#ffffff',
          pointBorderColor: '#00fff7',
          pointBorderWidth: 1,
          order: 1 // Ensure this line is drawn on top
        }
      ]
    };
  }

  private generateInsights(): void {
    const metricLower = this.metricName.toLowerCase();
    const currentValue = this.getCurrentValue();
    const trend = this.getTrendClass();
    
    // Generate Bollinger Band insights
    const bollingerInsights = [
      `Current value ${trend === 'positive' ? 'above' : 'below'} moving average`,
      `Price volatility ${Math.random() > 0.5 ? 'increasing' : 'decreasing'} based on band width`,
      `${Math.random() > 0.7 ? 'Breakout' : 'Consolidation'} pattern detected in recent data`,
      `Band squeeze indicates ${Math.random() > 0.5 ? 'potential volatility increase' : 'stable trading range'}`
    ];
    
    const baseInsights = [
      `Volume ${trend === 'positive' ? 'increased' : 'decreased'} by ${this.getTrendPercentage()}% vs last 24h`,
      `Peak activity observed at ${this.getPeakTime()}`,
      `Average processing time: ${this.getAvgProcessingTime()}ms`,
      `Success rate maintained at ${this.getSuccessRate()}%`,
      ...bollingerInsights.slice(0, 2) // Add 2 Bollinger insights
    ];

    if (metricLower.includes('swift')) {
      this.insights = [
        ...baseInsights,
        'SWIFT network connectivity stable',
        'Message formatting compliance: 100%',
        'Technical indicators suggest continued upward momentum'
      ];
    } else if (metricLower.includes('fed')) {
      this.insights = [
        ...baseInsights,
        'Federal Reserve connectivity optimal',
        'Settlement times within SLA',
        'Bollinger bands indicate healthy volatility range'
      ];
    } else if (metricLower.includes('chips')) {
      this.insights = [
        ...baseInsights,
        'CHIPS network performance normal',
        'Liquidity levels adequate',
        'Price action respecting technical support levels'
      ];
    } else {
      this.insights = [...baseInsights, ...bollingerInsights.slice(2)];
    }
  }
}