// File: src/app/shared/components/metric-card/metric-card.component.ts
import { Component, Input } from '@angular/core';
import { ChartConfiguration, ChartOptions } from 'chart.js';
import { BreakpointObserver } from '@angular/cdk/layout';

@Component({
  selector: 'app-metric-card',
  templateUrl: './metric-card.component.html',
  styleUrls: ['./metric-card.component.scss']
})
export class MetricCardComponent {
  @Input() title = '';
  @Input() subtitle = ''; // e.g., "Today"
  @Input() value: number | null = null;
  @Input() delta: number = 0;
  @Input() previousValue: number | null = null;
  @Input() averagePerHour: number | null = null;
  @Input() peakTime: string | null = null;
  @Input() lastUpdated: string | null = null;
  @Input() sparkline: number[] = [];
  @Input() dense = false;
  
  // Enhanced trend inputs
  @Input() yesterdayValue: number | null | undefined = null;
  @Input() changeAmount: number | null | undefined = null;
  @Input() changePercent: number | null | undefined = null;
  @Input() trendDirection: 'up' | 'down' | 'stable' = 'stable';

  isMobile = false;

  constructor(private breakpoint: BreakpointObserver) {
    this.breakpoint.observe(['(max-width: 768px)']).subscribe(r => {
      this.isMobile = r.matches;
    });
  }

  get deltaSign() {
    return this.delta >= 0 ? '+' : '';
  }

  get changeSign() {
    if (!this.changePercent && this.changePercent !== 0) return '';
    return this.changePercent >= 0 ? '+' : '';
  }

  get formattedChangeAmount(): string {
    if (!this.changeAmount && this.changeAmount !== 0) return '';
    const sign = this.changeAmount >= 0 ? '+' : '';
    return `${sign}${Math.abs(this.changeAmount).toLocaleString()}`;
  }

  get trendIcon(): string {
    switch (this.trendDirection) {
      case 'up': return 'trending_up';
      case 'down': return 'trending_down';
      default: return 'trending_flat';
    }
  }

  get trendClass(): string {
    switch (this.trendDirection) {
      case 'up': return 'trend-positive';
      case 'down': return 'trend-negative';
      default: return 'trend-neutral';
    }
  }

  // New methods for enhanced card design
  getCardCategory(): string {
    const titleLower = this.title.toLowerCase();
    if (titleLower.includes('swift')) return 'swift';
    if (titleLower.includes('fed')) return 'fed';
    if (titleLower.includes('chips')) return 'chips';
    if (titleLower.includes('payment')) return 'payment';
    if (titleLower.includes('deposit')) return 'deposit';
    if (titleLower.includes('message')) return 'message';
    return 'default';
  }

  getCardIcon(): string {
    const titleLower = this.title.toLowerCase();
    if (titleLower.includes('swift')) return 'swap_horiz';
    if (titleLower.includes('fed')) return 'account_balance';
    if (titleLower.includes('chips')) return 'credit_card';
    if (titleLower.includes('payment')) return 'payments';
    if (titleLower.includes('deposit')) return 'savings';
    if (titleLower.includes('message')) return 'message';
    if (titleLower.includes('transaction')) return 'receipt_long';
    return 'analytics';
  }

  get sparklineChartData(): ChartConfiguration<'line'>['data'] {
    const labels = this.sparkline.map(() => '');
    return {
      labels,
      datasets: [
        {
          data: this.sparkline,
          borderWidth: 2,
          tension: 0.4,
          pointRadius: 0,
          borderColor: this.delta >= 0 ? '#2affb0' : '#ff6b6b',
          backgroundColor: this.delta >= 0 
            ? 'rgba(42, 255, 176, 0.1)' 
            : 'rgba(255, 107, 107, 0.1)',
          fill: true
        }
      ]
    };
  }

  sparklineOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    elements: { point: { radius: 0 } },
    scales: {
      x: { display: false },
      y: { display: false }
    },
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false }
    },
    interaction: {
      intersect: false,
      mode: 'index'
    }
  };
}