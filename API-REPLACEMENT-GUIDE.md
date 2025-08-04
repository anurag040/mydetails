# 🔄 API Replacement Guide

## Quick Start - Replace Mock API with Real API

### 1. Update API Base URL

**File:** `src/app/core/api.service.ts` (Line 13)

```typescript
// Current (line 13):
private readonly baseUrl = 'http://localhost:3000'; // Change this to your API URL

// Replace with your actual API URL:
private readonly baseUrl = 'https://your-api-domain.com'; 
```

### 2. Replace Mock Methods One by One

**Replace these methods in `api.service.ts`:**

#### A. Main Dashboard Summary
```typescript
// CURRENT MOCK METHOD:
getSummary(): Observable<Summary> {
  const summary = {
    swiftTransactions: this.mockData?.statistics?.totalTransactions || 15847,
    // ... mock data
  };
  return of(summary).pipe(delay(200));
}

// REPLACE WITH:
getSummary(): Observable<Summary> {
  return this.http.get<Summary>(`${this.baseUrl}/api/summary`);
}
```

#### B. SWIFT Transactions List
```typescript
// CURRENT MOCK METHOD:
getSwiftTransactions(limit: number = 50, offset: number = 0): Observable<SwiftTransaction[]> {
  // ... mock data from JSON file
}

// REPLACE WITH:
getSwiftTransactions(limit: number = 50, offset: number = 0): Observable<SwiftTransaction[]> {
  return this.http.get<SwiftTransaction[]>(`${this.baseUrl}/api/swift/transactions?limit=${limit}&offset=${offset}`);
}
```

#### C. SWIFT Statistics
```typescript
// CURRENT MOCK METHOD:
getSwiftStatistics(): Observable<SwiftStatistics> {
  const stats = this.mockData?.statistics || this.getFallbackData().statistics;
  return of(stats).pipe(delay(250));
}

// REPLACE WITH:
getSwiftStatistics(): Observable<SwiftStatistics> {
  return this.http.get<SwiftStatistics>(`${this.baseUrl}/api/swift/statistics`);
}
```

#### D. SWIFT Alerts
```typescript
// CURRENT MOCK METHOD:
getSwiftAlerts(): Observable<SwiftAlert[]> {
  const alerts = this.mockData?.alerts || [];
  return of(alerts).pipe(delay(150));
}

// REPLACE WITH:
getSwiftAlerts(): Observable<SwiftAlert[]> {
  return this.http.get<SwiftAlert[]>(`${this.baseUrl}/api/swift/alerts`);
}
```

#### E. Real-time Metrics
```typescript
// CURRENT MOCK METHOD:
getRealtimeSwiftMetrics(): Observable<any> {
  const metrics = {
    // ... simulated random data
  };
  return of(metrics).pipe(delay(100));
}

// REPLACE WITH:
getRealtimeSwiftMetrics(): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/api/swift/realtime-metrics`);
}
```

### 3. Test Each Replacement

1. **Replace one method at a time**
2. **Test the dashboard after each change**
3. **Keep mock methods commented out for easy rollback**

### 4. Remove Mock Data (When All APIs Work)

When all your real APIs are working:

1. **Remove mock data loading:**
   ```typescript
   constructor(private http: HttpClient) {
     // Remove this line:
     // this.loadMockData();
   }
   ```

2. **Delete mock data file:** `src/assets/mock-data/swift-data.json`

3. **Remove mock methods:** `loadMockData()`, `getFallbackData()`

### 5. Expected API Response Formats

Your backend APIs should return data in these formats:

#### `/api/summary` Response:
```json
{
  "swiftTransactions": 15847,
  "nattedSwiftMessages": 12635,
  "fedPayments": 5000,
  "chipsPayments": 3000,
  "chipsDeposits": 2000,
  "timestamp": "2025-08-04T11:26:16.292Z"
}
```

#### `/api/swift/transactions` Response:
```json
[
  {
    "id": "TXN-SW-240801-001",
    "messageType": "MT103",
    "senderBIC": "CHASUS33XXX",
    "receiverBIC": "DEUTDEFFXXX",
    "amount": 150000.00,
    "currency": "USD",
    "status": "Completed",
    "priority": "Normal",
    "timestamp": "2025-08-01T08:15:23.123Z",
    // ... see swift-data.json for complete structure
  }
]
```

See `src/assets/mock-data/swift-data.json` for complete data structure examples.

### 6. API Endpoints Your Backend Should Implement

- `GET /api/summary` - Dashboard summary
- `GET /api/swift/transactions` - SWIFT transaction list
- `GET /api/swift/transactions/:id` - Single transaction
- `GET /api/swift/statistics` - Network statistics
- `GET /api/swift/alerts` - Active alerts
- `GET /api/swift/realtime-metrics` - Real-time metrics
- `GET /api/incidents` - Incident list

### 7. Testing Your APIs

Use browser dev tools or Postman to test your APIs:
```bash
# Test summary endpoint
curl http://your-api-domain.com/api/summary

# Test SWIFT transactions
curl http://your-api-domain.com/api/swift/transactions?limit=10
```

---

**The mock system will continue working until you replace each method, so you can do this gradually and test each endpoint individually.**
