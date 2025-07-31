// Global type declarations for missing browser types

// Extend the global namespace to include RequestPriority
declare global {
  type RequestPriority = 'high' | 'low' | 'auto';
}

export {};
