export interface MetricTrend {
  current: number;
  yesterday: number;
  change: number;
  changePercent: number;
  trend: 'up' | 'down' | 'stable';
}

export interface Summary {
  swiftTransactions: number;
  nattedSwiftMessages: number;
  fedPayments: number;
  chipsPayments: number;
  chipsDeposits: number;
  timestamp?: string;
  
  // Enhanced trend data
  trends?: {
    swiftTransactions: MetricTrend;
    nattedSwiftMessages: MetricTrend;
    fedPayments: MetricTrend;
    chipsPayments: MetricTrend;
    chipsDeposits: MetricTrend;
  };
}