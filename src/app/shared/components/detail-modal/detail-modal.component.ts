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
    elements: { point: { radius: 0 } },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.07)' },
        ticks: { color: '#a3adc8' }
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.07)' },
        ticks: { color: '#a3adc8' }
      }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1f2330',
        titleColor: '#e3e9ff',
        bodyColor: '#a3adc8',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1
      }
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
    const pointCount = 48; // 48 hours of data
    const base = this.getCurrentValue();
    const data: number[] = [];

    for (let i = 0; i < pointCount; i++) {
      const noise = Math.sin(i / 8) * 20 + Math.random() * 40 - 20;
      const trend = i * 2; // Slight upward trend
      const value = base + noise + trend;
      data.push(parseFloat(value.toFixed(0)));
    }

    this.chartData = {
      labels: Array.from({ length: pointCount }, (_, i) => {
        const hour = (new Date().getHours() - pointCount + i + 24) % 24;
        return `${hour.toString().padStart(2, '0')}:00`;
      }),
      datasets: [
        {
          label: this.metricName,
          data: data,
          borderWidth: 3,
          tension: 0.4,
          pointRadius: 2,
          pointHoverRadius: 6,
          borderColor: '#00fff7',
          backgroundColor: 'rgba(0, 255, 247, 0.1)',
          fill: true,
          pointBackgroundColor: '#00fff7',
          pointBorderColor: '#0f111a',
          pointBorderWidth: 2
        }
      ]
    };
  }

  private generateInsights(): void {
    const metricLower = this.metricName.toLowerCase();
    const baseInsights = [
      `Volume ${this.getTrendClass() === 'positive' ? 'increased' : 'decreased'} by ${this.getTrendPercentage()}% vs last 24h`,
      `Peak activity observed at ${this.getPeakTime()}`,
      `Average processing time: ${this.getAvgProcessingTime()}ms`,
      `Success rate maintained at ${this.getSuccessRate()}%`
    ];

    if (metricLower.includes('swift')) {
      this.insights = [
        ...baseInsights,
        'SWIFT network connectivity stable',
        'Message formatting compliance: 100%',
        'No regulatory flags detected'
      ];
    } else if (metricLower.includes('fed')) {
      this.insights = [
        ...baseInsights,
        'Federal Reserve connectivity optimal',
        'Settlement times within SLA',
        'Reserve requirements met'
      ];
    } else if (metricLower.includes('chips')) {
      this.insights = [
        ...baseInsights,
        'CHIPS network performance normal',
        'Liquidity levels adequate',
        'Transaction priorities processed correctly'
      ];
    } else {
      this.insights = baseInsights;
    }
  }
}