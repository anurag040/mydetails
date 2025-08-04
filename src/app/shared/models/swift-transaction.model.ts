export interface SwiftTransaction {
  id: string;
  messageType: string; // MT103, MT202, MT950, etc.
  senderBIC: string;
  receiverBIC: string;
  amount: number;
  currency: string;
  status: 'Pending' | 'Processing' | 'Completed' | 'Failed' | 'Rejected';
  priority: 'Normal' | 'High' | 'Urgent';
  timestamp: string;
  settledTimestamp?: string;
  processingTime?: number; // in milliseconds
  fees: number;
  reference: string;
  valueDate: string;
  description: string;
  country: string;
  network: 'SWIFT' | 'SWIFT_GPI';
  gpiUETR?: string; // Unique End-to-End Transaction Reference for GPI
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

export interface SwiftStatistics {
  totalTransactions: number;
  completedTransactions: number;
  pendingTransactions: number;
  failedTransactions: number;
  totalVolume: number;
  averageProcessingTime: number;
  successRate: number;
  networkUptime: number;
  peakThroughput: number;
  currentThroughput: number;
  topCurrencies: Array<{
    currency: string;
    count: number;
    volume: number;
  }>;
  topCountries: Array<{
    country: string;
    count: number;
    volume: number;
  }>;
  messageTypeBreakdown: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
  hourlyTrends: Array<{
    hour: number;
    transactions: number;
    volume: number;
  }>;
}

export interface SwiftAlert {
  id: string;
  type: 'High Volume' | 'Processing Delay' | 'Network Issue' | 'Compliance Alert' | 'Fee Anomaly';
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  message: string;
  timestamp: string;
  resolved: boolean;
  affectedTransactions: number;
  estimatedImpact: string;
}
