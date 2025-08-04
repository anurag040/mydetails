import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Incident } from '../../shared/models/incident.model';

@Component({
  selector: 'app-incident-detail',
  templateUrl: './incident-detail.component.html',
  styleUrls: ['./incident-detail.component.scss']
})
export class IncidentDetailComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA) public incident: Incident,
    private dialogRef: MatDialogRef<IncidentDetailComponent>
  ) {}

  getSeverityIcon(severity: string): string {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'notification_important';
    }
  }

  getStatusClass(status: string): string {
    switch (status.toLowerCase()) {
      case 'open':
      case 'investigating':
        return 'status-open';
      case 'resolved':
      case 'closed':
        return 'status-resolved';
      case 'in progress':
      case 'monitoring':
        return 'status-progress';
      default:
        return 'status-unknown';
    }
  }

  getLastUpdated(): string {
    // Calculate time difference
    const now = new Date();
    const incidentDate = new Date(this.incident.date);
    const diffMs = now.getTime() - incidentDate.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 60) {
      return `${diffMins} minutes ago`;
    } else if (diffMins < 1440) {
      const hours = Math.floor(diffMins / 60);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
      const days = Math.floor(diffMins / 1440);
      return `${days} day${days > 1 ? 's' : ''} ago`;
    }
  }

  getPriority(severity: string): string {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'Critical';
      case 'medium':
        return 'High';
      case 'low':
        return 'Medium';
      default:
        return 'Low';
    }
  }

  getAffectedSystems(): string {
    // Mock affected systems based on incident type
    const systems = ['Payment Gateway', 'SWIFT Network', 'Fed Wire', 'CHIPS'];
    const affectedCount = Math.floor(Math.random() * 3) + 1;
    return `${affectedCount} system${affectedCount > 1 ? 's' : ''}`;
  }

  getDuration(): string {
    const now = new Date();
    const incidentDate = new Date(this.incident.date);
    const diffMs = now.getTime() - incidentDate.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 60) {
      return `${diffMins}m`;
    } else if (diffMins < 1440) {
      const hours = Math.floor(diffMins / 60);
      const mins = diffMins % 60;
      return `${hours}h ${mins}m`;
    } else {
      const days = Math.floor(diffMins / 1440);
      const hours = Math.floor((diffMins % 1440) / 60);
      return `${days}d ${hours}h`;
    }
  }

  getRecommendedActions(): Array<{icon: string, text: string}> {
    const baseActions = [
      { icon: 'refresh', text: 'Restart affected services' },
      { icon: 'monitoring', text: 'Increase monitoring frequency' },
      { icon: 'notification_important', text: 'Notify stakeholders' }
    ];

    const severityActions = {
      high: [
        { icon: 'emergency', text: 'Activate emergency response team' },
        { icon: 'support_agent', text: 'Contact vendor support immediately' }
      ],
      medium: [
        { icon: 'bug_report', text: 'Investigate root cause' },
        { icon: 'timeline', text: 'Update status page' }
      ],
      low: [
        { icon: 'schedule', text: 'Schedule maintenance window' },
        { icon: 'documentation', text: 'Update documentation' }
      ]
    };

    const severity = this.incident.severity.toLowerCase() as keyof typeof severityActions;
    return [...baseActions, ...(severityActions[severity] || [])];
  }

  acknowledgeIncident(): void {
    // Mock acknowledge action
    console.log('Incident acknowledged:', this.incident.title);
    // In a real app, this would call an API
  }

  escalateIncident(): void {
    // Mock escalate action
    console.log('Incident escalated:', this.incident.title);
    // In a real app, this would call an API and possibly close the dialog
  }
}