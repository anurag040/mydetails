import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { delay, map } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { Summary } from '../shared/models/summary.model';
import { Incident } from '../shared/models/incident.model';
import { SwiftTransaction, SwiftStatistics, SwiftAlert } from '../shared/models/swift-transaction.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  // TODO: Replace this with your actual API URL
  private readonly baseUrl = 'http://localhost:3000'; // Change this to your API URL
  private mockData: any = null;

  constructor(private http: HttpClient) {
    // Remove this line when switching to real API
    this.loadMockData();
  }

  private async loadMockData() {
    try {
      this.mockData = await this.http.get('/assets/mock-data/swift-data.json').toPromise();
    } catch (error) {
      console.warn('Could not load mock data, using fallback data');
      this.mockData = this.getFallbackData();
    }
  }

  private getFallbackData() {
    return {
      swiftTransactions: [],
      statistics: {
        totalTransactions: 15847,
        completedTransactions: 14523,
        pendingTransactions: 892,
        failedTransactions: 432,
        totalVolume: 2847592385.50,
        averageProcessingTime: 87532,
        successRate: 91.64,
        networkUptime: 99.8,
        peakThroughput: 1250,
        currentThroughput: 834,
        topCurrencies: [],
        topCountries: [],
        messageTypeBreakdown: [],
        hourlyTrends: []
      },
      alerts: []
    };
  }
  getSummary(): Observable<Summary> {
    // Enhanced summary using SWIFT statistics with trend data
    const currentSwift = this.mockData?.statistics?.totalTransactions || 15847;
    const currentNetted = Math.round(currentSwift * 0.75);
    const currentFed = 5000;
    const currentChips = 3000;
    const currentDeposits = 2000;

    // Calculate trend data with realistic yesterday values
    const createTrend = (current: number, yesterdayVariation: number): any => {
      const yesterday = Math.round(current * (1 + yesterdayVariation));
      const change = current - yesterday;
      const changePercent = yesterday > 0 ? (change / yesterday) * 100 : 0;
      return {
        current,
        yesterday,
        change,
        changePercent: Math.round(changePercent * 10) / 10,
        trend: change > 0 ? 'up' : change < 0 ? 'down' : 'stable'
      };
    };

    const summary = {
      swiftTransactions: currentSwift,
      nattedSwiftMessages: currentNetted,
      fedPayments: currentFed,
      chipsPayments: currentChips,
      chipsDeposits: currentDeposits,
      timestamp: new Date().toISOString(),
      trends: {
        swiftTransactions: createTrend(currentSwift, -0.008),    // +0.8% vs yesterday
        nattedSwiftMessages: createTrend(currentNetted, 0.015),  // -1.5% vs yesterday
        fedPayments: createTrend(currentFed, -0.012),            // +1.2% vs yesterday
        chipsPayments: createTrend(currentChips, -0.011),        // +1.1% vs yesterday
        chipsDeposits: createTrend(currentDeposits, 0.006)       // -0.6% vs yesterday
      }
    };
    
    return of(summary).pipe(delay(200));
  }

  // SWIFT Transaction Methods
  getSwiftTransactions(limit: number = 50, offset: number = 0): Observable<SwiftTransaction[]> {
    if (!this.mockData) {
      return of([]).pipe(delay(300));
    }
    
    const transactions = this.mockData.swiftTransactions.slice(offset, offset + limit);
    return of(transactions).pipe(delay(300));
  }

  getSwiftTransaction(id: string): Observable<SwiftTransaction | null> {
    if (!this.mockData) {
      return of(null).pipe(delay(200));
    }
    
    const transaction = this.mockData.swiftTransactions.find((t: SwiftTransaction) => t.id === id);
    return of(transaction || null).pipe(delay(200));
  }

  getSwiftStatistics(): Observable<SwiftStatistics> {
    const stats = this.mockData?.statistics || this.getFallbackData().statistics;
    return of(stats).pipe(delay(250));
  }

  getSwiftAlerts(): Observable<SwiftAlert[]> {
    const alerts = this.mockData?.alerts || [];
    return of(alerts).pipe(delay(150));
  }

  // Filter transactions by various criteria
  getSwiftTransactionsByStatus(status: string): Observable<SwiftTransaction[]> {
    if (!this.mockData) {
      return of([]).pipe(delay(300));
    }
    
    const filtered = this.mockData.swiftTransactions.filter(
      (t: SwiftTransaction) => t.status.toLowerCase() === status.toLowerCase()
    );
    return of(filtered).pipe(delay(300));
  }

  getSwiftTransactionsByCurrency(currency: string): Observable<SwiftTransaction[]> {
    if (!this.mockData) {
      return of([]).pipe(delay(300));
    }
    
    const filtered = this.mockData.swiftTransactions.filter(
      (t: SwiftTransaction) => t.currency === currency
    );
    return of(filtered).pipe(delay(300));
  }

  getSwiftTransactionsByDateRange(startDate: string, endDate: string): Observable<SwiftTransaction[]> {
    if (!this.mockData) {
      return of([]).pipe(delay(300));
    }
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    const filtered = this.mockData.swiftTransactions.filter((t: SwiftTransaction) => {
      const txDate = new Date(t.timestamp);
      return txDate >= start && txDate <= end;
    });
    
    return of(filtered).pipe(delay(300));
  }

  // Real-time data simulation
  getRealtimeSwiftMetrics(): Observable<any> {
    const metrics = {
      currentThroughput: Math.floor(800 + Math.random() * 400), // 800-1200 TPS
      networkLatency: Math.floor(20 + Math.random() * 30), // 20-50ms
      successRate: 99.2 + Math.random() * 0.8, // 99.2-100%
      processingTime: Math.floor(80 + Math.random() * 40), // 80-120ms average
      activeConnections: Math.floor(150 + Math.random() * 50), // 150-200 connections
      queueDepth: Math.floor(Math.random() * 20), // 0-20 queued messages
      timestamp: new Date().toISOString()
    };
    
    return of(metrics).pipe(delay(100));
  }

  // Simulate API endpoints that you would replace with real ones
  
  /**
   * Example of how to replace with real API:
   * 
   * getRealSwiftTransactions(): Observable<SwiftTransaction[]> {
   *   return this.http.get<SwiftTransaction[]>(`${this.baseUrl}/api/swift/transactions`);
   * }
   * 
   * getRealSwiftStatistics(): Observable<SwiftStatistics> {
   *   return this.http.get<SwiftStatistics>(`${this.baseUrl}/api/swift/statistics`);
   * }
   */

  getIncidents(): Observable<Incident[]> {
    const incidents: Incident[] = [
      {
        id: 1,
        title: 'Payment Gateway Timeout',
        severity: 'High',
        status: 'Open',
        date: '2025-08-01T10:15:00Z',
        description: 'Timeouts observed in the payment gateway causing delays in SWIFT processing.'
      },
      {
        id: 2,
        title: 'Delayed SWIFT Message',
        severity: 'Medium',
        status: 'Resolved',
        date: '2025-07-30T08:30:00Z',
        description: 'One of the SWIFT messages was delayed due to intermediate network latency.'
      }
    ];
    return of(incidents).pipe(delay(200));
  }
}