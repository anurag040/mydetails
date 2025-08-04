export interface Summary {
  swiftTransactions: number;
  nattedSwiftMessages: number;
  fedPayments: number;
  chipsPayments: number;
  chipsDeposits: number;
  timestamp?: string;
}