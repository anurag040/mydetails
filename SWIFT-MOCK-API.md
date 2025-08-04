# SWIFT Transaction Mock API Documentation

This mock API system provides realistic SWIFT transaction data for development and testing purposes.

## Overview

The mock API includes:
- **Detailed SWIFT Transaction Models**: Complete transaction objects with compliance, routing, and metadata
- **Real-time Statistics**: Network performance, throughput, and volume metrics
- **Alert System**: Compliance alerts, processing delays, and network issues
- **Comprehensive Filtering**: By status, currency, date range, and more

## Data Structure

### SwiftTransaction Model
```typescript
interface SwiftTransaction {
  id: string;                    // Unique transaction ID
  messageType: string;           // MT103, MT202, MT950, etc.
  senderBIC: string;            // Bank Identifier Code
  receiverBIC: string;          // Receiving bank BIC
  amount: number;               // Transaction amount
  currency: string;             // Currency code (USD, EUR, etc.)
  status: 'Pending' | 'Processing' | 'Completed' | 'Failed' | 'Rejected';
  priority: 'Normal' | 'High' | 'Urgent';
  timestamp: string;            // ISO timestamp
  settledTimestamp?: string;    // Settlement time (if completed)
  processingTime?: number;      // Processing time in milliseconds
  fees: number;                 // Transaction fees
  reference: string;            // Transaction reference
  valueDate: string;            // Value date
  description: string;          // Transaction description
  country: string;              // Destination country
  network: 'SWIFT' | 'SWIFT_GPI'; // Network type
  gpiUETR?: string;            // GPI transaction reference
  compliance: {
    amlStatus: 'Cleared' | 'Pending' | 'Flagged';
    sanctionsCheck: 'Passed' | 'Pending' | 'Failed';
    kycStatus: 'Verified' | 'Pending' | 'Required';
  };
  routing: {
    intermediaryBanks: string[];
    expectedHops: number;
    actualHops: number;
  };
}
```

## API Methods

### Basic Operations
```typescript
// Get summary statistics (used by main dashboard)
getSummary(): Observable<Summary>

// Get paginated transactions
getSwiftTransactions(limit: number = 50, offset: number = 0): Observable<SwiftTransaction[]>

// Get specific transaction by ID
getSwiftTransaction(id: string): Observable<SwiftTransaction | null>

// Get comprehensive statistics
getSwiftStatistics(): Observable<SwiftStatistics>

// Get active alerts
getSwiftAlerts(): Observable<SwiftAlert[]>
```

### Filtering Methods
```typescript
// Filter by transaction status
getSwiftTransactionsByStatus(status: string): Observable<SwiftTransaction[]>

// Filter by currency
getSwiftTransactionsByCurrency(currency: string): Observable<SwiftTransaction[]>

// Filter by date range
getSwiftTransactionsByDateRange(startDate: string, endDate: string): Observable<SwiftTransaction[]>

// Get real-time metrics (updates every 5 seconds)
getRealtimeSwiftMetrics(): Observable<any>
```

## Usage Examples

### 1. Load All SWIFT Data
```typescript
// In your component
async loadSwiftData() {
  try {
    const [transactions, statistics, alerts] = await Promise.all([
      this.api.getSwiftTransactions(20).toPromise(),
      this.api.getSwiftStatistics().toPromise(),
      this.api.getSwiftAlerts().toPromise()
    ]);
    
    this.transactions = transactions || [];
    this.statistics = statistics || null;
    this.alerts = alerts || [];
  } catch (error) {
    console.error('Error loading SWIFT data:', error);
  }
}
```

### 2. Filter Transactions
```typescript
// Get only failed transactions
this.api.getSwiftTransactionsByStatus('Failed').subscribe(failedTxns => {
  console.log('Failed transactions:', failedTxns);
});

// Get USD transactions only
this.api.getSwiftTransactionsByCurrency('USD').subscribe(usdTxns => {
  console.log('USD transactions:', usdTxns);
});

// Get transactions from last 24 hours
const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
const now = new Date().toISOString();
this.api.getSwiftTransactionsByDateRange(yesterday, now).subscribe(recentTxns => {
  console.log('Recent transactions:', recentTxns);
});
```

### 3. Real-time Updates
```typescript
// Set up real-time metrics updates
startRealtimeUpdates() {
  this.realtimeSubscription = interval(5000).subscribe(() => {
    this.api.getRealtimeSwiftMetrics().subscribe(metrics => {
      this.currentThroughput = metrics.currentThroughput;
      this.networkLatency = metrics.networkLatency;
      this.successRate = metrics.successRate;
      // Update your UI with real-time data
    });
  });
}
```

### 4. Transaction Details
```typescript
// Get specific transaction details
viewTransactionDetail(transactionId: string) {
  this.api.getSwiftTransaction(transactionId).subscribe(transaction => {
    if (transaction) {
      // Open detail modal or navigate to detail page
      this.dialog.open(DetailModalComponent, {
        data: { transaction, statistics: this.statistics }
      });
    }
  });
}
```

## File Locations

- **Mock Data**: `src/assets/mock-data/swift-data.json`
- **Models**: `src/app/shared/models/swift-transaction.model.ts`
- **API Service**: `src/app/core/api.service.ts`
- **SWIFT Dashboard**: `src/app/dashboard/swift-dashboard/`

## Replacing with Real API

To replace the mock API with your real backend:

1. **Update the base URL** in the API service
2. **Replace mock methods** with HTTP calls:

```typescript
// Replace this mock method:
getSwiftTransactions(limit: number = 50): Observable<SwiftTransaction[]> {
  return of(this.mockData.swiftTransactions.slice(0, limit)).pipe(delay(300));
}

// With a real HTTP call:
getSwiftTransactions(limit: number = 50): Observable<SwiftTransaction[]> {
  return this.http.get<SwiftTransaction[]>(`${this.baseUrl}/api/swift/transactions?limit=${limit}`);
}
```

3. **Update environment configuration**:
```typescript
// environment.ts
export const environment = {
  production: false,
  apiUrl: 'https://your-api-domain.com'
};
```

## Features Included

### Dashboard Features
- ✅ Real-time metrics display
- ✅ Transaction history table
- ✅ Advanced filtering (status, currency, date range)
- ✅ Alert monitoring
- ✅ Responsive design
- ✅ Export functionality
- ✅ Detail modals

### Mock Data Features
- ✅ 6 sample transactions with realistic data
- ✅ Complete compliance and routing information
- ✅ Various transaction statuses and priorities
- ✅ Multiple currencies (USD, EUR, GBP, CHF)
- ✅ Different message types (MT103, MT202, MT950)
- ✅ Network statistics and trends
- ✅ Active alerts with severity levels

## Navigation

- **Main Dashboard**: `http://localhost:4200/dashboard`
- **SWIFT Details**: `http://localhost:4200/dashboard/swift`

The SWIFT dashboard provides a comprehensive view of all SWIFT transaction data, real-time metrics, alerts, and detailed filtering capabilities. You can easily test the interface and then replace the mock service methods with your actual API endpoints.

## Testing the Mock API

1. Navigate to the SWIFT dashboard
2. Use the filters to test different data views
3. Click on transactions to see detailed information
4. Watch real-time metrics update every 5 seconds
5. Export data to see the JSON structure
6. Test mobile responsiveness

This mock system provides a complete foundation that mimics a production SWIFT monitoring system, making it easy to develop and test your UI before connecting to real backend services.
