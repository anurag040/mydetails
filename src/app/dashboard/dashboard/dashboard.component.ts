import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../core/api.service';
import { Summary } from '../../shared/models/summary.model';
import { MatDialog } from '@angular/material/dialog';
import { DetailModalComponent } from '../../shared/components/detail-modal/detail-modal.component';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  summary?: Summary;
  loading = true;
  isLoading = false;
  isOnline = true;

  constructor(private api: ApiService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.loadDashboardData();
    // Simulate real-time updates
    setInterval(() => {
      this.isOnline = Math.random() > 0.1; // 90% uptime simulation
    }, 30000);
  }

  loadDashboardData(): void {
    this.api.getSummary().subscribe(s => {
      this.summary = s;
      this.loading = false;
    });
  }

  refreshData(): void {
    this.isLoading = true;
    setTimeout(() => {
      this.loadDashboardData();
      this.isLoading = false;
    }, 1500);
  }

  openDetail(metric: string) {
    this.dialog.open(DetailModalComponent, {
      width: '800px',
      maxWidth: '90vw',
      data: { metric, summary: this.summary },
      panelClass: 'detail-modal-panel'
    });
  }

  // Quick stats calculations
  getSuccessRate(): number {
    if (!this.summary) return 0;
    const total = this.summary.swiftTransactions + this.summary.fedPayments + 
                 this.summary.chipsPayments + this.summary.chipsDeposits;
    return Math.round((total * 0.998)); // Simulate 99.8% success rate
  }

  getProcessingTime(): number {
    return Math.round(120 + (Math.random() * 50)); // Simulate 120-170ms processing time
  }

  getTotalVolume(): number {
    if (!this.summary) return 0;
    const totalTransactions = this.summary.swiftTransactions + this.summary.fedPayments + 
                            this.summary.chipsPayments + this.summary.chipsDeposits;
    return Math.round(totalTransactions * 2.5); // Simulate volume multiplier
  }

  getActiveAlerts(): number {
    return Math.floor(Math.random() * 3); // Simulate 0-2 active alerts
  }

  // New methods for enhanced dashboard
  getCurrentTime(): string {
    return new Date().toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  }

  getNetworkHealth(): number {
    return Math.round(95 + (Math.random() * 5)); // Simulate 95-100% network health
  }

  getThroughput(): number {
    return Math.round(850 + (Math.random() * 300)); // Simulate 850-1150 transactions per second
  }

  exportData(): void {
    console.log('Exporting dashboard data...');
    // Implement data export functionality
  }

  configureAlerts(): void {
    console.log('Opening alert configuration...');
    // Implement alert configuration functionality
  }
}