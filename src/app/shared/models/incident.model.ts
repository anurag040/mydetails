export type Severity = 'High' | 'Medium' | 'Low';
export type Status = 'Open' | 'Resolved' | 'In Progress';

export interface Incident {
  id: number;
  title: string;
  severity: Severity;
  status: Status;
  date: string;
  description: string;
}