import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../core/api.service';
import { Incident } from '../../shared/models/incident.model';
import { MatDialog } from '@angular/material/dialog';
import { IncidentDetailComponent } from '../incident-detail/incident-detail.component';

@Component({
  selector: 'app-incident-list',
  templateUrl: './incident-list.component.html',
  styleUrls: ['./incident-list.component.scss']
})
export class IncidentListComponent implements OnInit {
  incidents: Incident[] = [];
  loading = true;

  constructor(private api: ApiService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.loading = true;
    this.api.getIncidents().subscribe(list => {
      this.incidents = list;
      this.loading = false;
    });
  }

  openDetail(incident: Incident) {
    this.dialog.open(IncidentDetailComponent, {
      width: '600px',
      maxWidth: '90vw',
      data: incident,
      panelClass: 'premium-dialog'
    });
  }

  getIncidentsByType(severity: string): Incident[] {
    return this.incidents.filter(incident => 
      incident.severity.toLowerCase() === severity.toLowerCase()
    );
  }

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
}