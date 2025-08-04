import { Component, OnInit, OnDestroy } from '@angular/core';
import { ApiService } from '../../core/api.service';
import { SwiftTransaction, SwiftStatistics, SwiftAlert } from '../../shared/models/swift-transaction.model';
import { MatDialog } from '@angular/material/dialog';
import { DetailModalComponent } from '../../shared/components/detail-modal/detail-modal.component';
import { interval, Subscription } from 'rxjs';

@Component({
  selector: 'app-swift-dashboard',
  templateUrl: './swift-dashboard.component.html',
  styleUrls: ['./swift-dashboard.component.scss']
})
export class SwiftDashboardComponent implements OnInit, OnDestroy {
  transactions: SwiftTransaction[] = [];
  statistics: SwiftStatistics | null = null;
  alerts: SwiftAlert[] = [];
  realtimeMetrics: any = null;
  loading = true;
  selectedTimeRange = '24h';
  selectedCurrency = 'ALL';
  selectedStatus = 'ALL';

  private realtimeSubscription?: Subscription;

  displayedColumns: string[] = ['id', 'messageType', 'amount', 'currency', 'status', 'priority', 'timestamp', 'actions'];
  
  currencies = ['ALL', 'USD', 'EUR', 'GBP', 'CHF', 'JPY'];
  statuses = ['ALL', 'Completed', 'Processing', 'Pending', 'Failed', 'Rejected'];
  timeRanges = [
    { value: '1h', label: 'Last Hour' },
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' }
  ];

  constructor(
    private api: ApiService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.loadSwiftData();
    this.startRealtimeUpdates();
  }

  ngOnDestroy() {
    if (this.realtimeSubscription) {
      this.realtimeSubscription.unsubscribe();
    }
  }

  loadSwiftData() {
    this.loading = true;
    
    // Load all SWIFT data
    Promise.all([
      this.api.getSwiftTransactions(20).toPromise(),
      this.api.getSwiftStatistics().toPromise(),
      this.api.getSwiftAlerts().toPromise()
    ]).then(([transactions, statistics, alerts]) => {
      this.transactions = transactions || [];
      this.statistics = statistics || null;
      this.alerts = alerts || [];
      this.loading = false;
      this.applyFilters();
    }).catch(error => {
      console.error('Error loading SWIFT data:', error);
      this.loading = false;
    });
  }

  startRealtimeUpdates() {
    // Update realtime metrics every 5 seconds
    this.realtimeSubscription = interval(5000).subscribe(() => {
      this.api.getRealtimeSwiftMetrics().subscribe(metrics => {
        this.realtimeMetrics = metrics;
      });
    });

    // Get initial metrics
    this.api.getRealtimeSwiftMetrics().subscribe(metrics => {
      this.realtimeMetrics = metrics;
    });
  }

  applyFilters() {
    let filtered = [...this.transactions];

    if (this.selectedCurrency !== 'ALL') {
      filtered = filtered.filter(t => t.currency === this.selectedCurrency);
    }

    if (this.selectedStatus !== 'ALL') {
      filtered = filtered.filter(t => t.status === this.selectedStatus);
    }

    // Apply time range filter
    const now = new Date();
    let startTime: Date;
    
    switch (this.selectedTimeRange) {
      case '1h':
        startTime = new Date(now.getTime() - 60 * 60 * 1000);
        break;
      case '24h':
        startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        break;
      case '7d':
        startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case '30d':
        startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      default:
        startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    }

    filtered = filtered.filter(t => new Date(t.timestamp) >= startTime);
    
    this.transactions = filtered;
  }

  onFilterChange() {
    this.applyFilters();
  }

  onTimeRangeChange() {
    this.applyFilters();
  }

  onCurrencyChange() {
    this.applyFilters();
  }

  onStatusChange() {
    this.applyFilters();
  }

  refreshData() {
    this.loadSwiftData();
  }

  viewTransactionDetail(transaction: SwiftTransaction) {
    this.dialog.open(DetailModalComponent, {
      width: '900px',
      maxWidth: '95vw',
      data: { 
        metric: 'SWIFT Transaction Detail',
        transaction: transaction,
        statistics: this.statistics
      },
      panelClass: 'detail-modal-panel'
    });
  }

  getStatusClass(status: string): string {
    switch (status.toLowerCase()) {
      case 'completed': return 'status-completed';
      case 'processing': return 'status-processing';
      case 'pending': return 'status-pending';
      case 'failed': 
      case 'rejected': return 'status-failed';
      default: return 'status-unknown';
    }
  }

  getPriorityClass(priority: string): string {
    switch (priority.toLowerCase()) {
      case 'urgent': return 'priority-urgent';
      case 'high': return 'priority-high';
      case 'normal': return 'priority-normal';
      default: return 'priority-normal';
    }
  }

  getComplianceStatus(transaction: SwiftTransaction): string {
    const { amlStatus, sanctionsCheck, kycStatus } = transaction.compliance;
    
    if (sanctionsCheck === 'Failed' || amlStatus === 'Flagged') {
      return 'High Risk';
    }
    if (sanctionsCheck === 'Pending' || amlStatus === 'Pending' || kycStatus === 'Required') {
      return 'Under Review';
    }
    return 'Cleared';
  }

  exportData() {
    const dataStr = JSON.stringify(this.transactions, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `swift-transactions-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  formatCurrency(amount: number, currency: string): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2
    }).format(amount);
  }

  formatProcessingTime(timeMs: number): string {
    if (timeMs < 1000) return `${timeMs}ms`;
    if (timeMs < 60000) return `${(timeMs / 1000).toFixed(1)}s`;
    return `${(timeMs / 60000).toFixed(1)}m`;
  }
}
