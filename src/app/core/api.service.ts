import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';
import { Summary } from '../shared/models/summary.model';
import { Incident } from '../shared/models/incident.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  getSummary(): Observable<Summary> {
    return of({
      swiftTransactions: 15000,
      nattedSwiftMessages: 12000,
      fedPayments: 5000,
      chipsPayments: 3000,
      chipsDeposits: 2000,
      timestamp: new Date().toISOString()
    }).pipe(delay(200));
  }

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