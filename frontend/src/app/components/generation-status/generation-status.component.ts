import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgIf, NgFor, NgClass } from '@angular/common';
import { Subscription } from 'rxjs';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';

import { ProjectGenerationService, GenerationSession } from '../../services/project-generation.service';

@Component({
  selector: 'app-generation-status',
  standalone: true,
  imports: [
    NgIf, NgFor, NgClass,
    MatCardModule, MatButtonModule, MatProgressSpinnerModule, MatProgressBarModule,
    MatIconModule, MatChipsModule, MatDividerModule
  ],
  template: `
    <div class="status-container">
      <mat-card class="status-card">
        <mat-card-header>
          <mat-card-title>
            <mat-icon>auto_awesome</mat-icon>
            Project Generation Status
          </mat-card-title>
          <mat-card-subtitle *ngIf="sessionId()">
            Session: {{ sessionId() }}
          </mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <div class="status-section" *ngIf="currentStatus()">
            <!-- Status Display -->
            <div class="status-display">
              <div class="status-icon" [ngClass]="getStatusClass()">
                <mat-icon>{{ getStatusIcon() }}</mat-icon>
              </div>
              <div class="status-text">
                <h3>{{ getStatusLabel() }}</h3>
                <p *ngIf="currentStatus()?.message">{{ currentStatus()?.message }}</p>
                <p *ngIf="currentStatus()?.error" class="error-text">{{ currentStatus()?.error }}</p>
              </div>
            </div>

            <!-- Progress Bar -->
            <mat-progress-bar 
              *ngIf="isInProgress()" 
              mode="indeterminate" 
              class="progress-bar">
            </mat-progress-bar>

            <!-- Generation Details -->
            <div class="details-section" *ngIf="currentStatus()">
              <mat-divider></mat-divider>
              
              <div class="detail-row" *ngIf="currentStatus()?.startTime">
                <span class="label">Started:</span>
                <span>{{ formatTime(currentStatus()!.startTime!) }}</span>
              </div>

              <div class="detail-row" *ngIf="currentStatus()?.duration">
                <span class="label">Duration:</span>
                <span>{{ formatDuration(currentStatus()!.duration!) }}</span>
              </div>

              <div class="detail-row" *ngIf="currentStatus()?.agentResults">
                <span class="label">Agents:</span>
                <span>{{ currentStatus()?.successfulAgents }} / {{ currentStatus()?.agentResults }} completed</span>
              </div>
            </div>

            <!-- Agent Progress -->
            <div class="agents-section" *ngIf="showAgentProgress()">
              <h4>AI Agents Progress:</h4>
              <div class="agent-chips">
                <mat-chip-set>
                  <mat-chip *ngFor="let agent of getAgentList()">
                    <mat-icon>{{ agent.icon }}</mat-icon>
                    {{ agent.name }}
                  </mat-chip>
                </mat-chip-set>
              </div>
            </div>
          </div>

          <!-- Loading State -->
          <div class="loading-section" *ngIf="!currentStatus()">
            <mat-spinner></mat-spinner>
            <p>Loading status...</p>
          </div>
        </mat-card-content>

        <mat-card-actions>
          <!-- Actions based on status -->
          <div class="actions" *ngIf="currentStatus()">
            <!-- In Progress Actions -->
            <ng-container *ngIf="isInProgress()">
              <button mat-raised-button color="warn" (click)="cancelGeneration()">
                <mat-icon>stop</mat-icon>
                Cancel Generation
              </button>
              <button mat-button (click)="refreshStatus()">
                <mat-icon>refresh</mat-icon>
                Refresh
              </button>
            </ng-container>

            <!-- Completed Actions -->
            <ng-container *ngIf="currentStatus()?.status === 'COMPLETED'">
              <button mat-raised-button color="primary" (click)="goToDownloadPage()">
                <mat-icon>download</mat-icon>
                Download Files
              </button>
              <button mat-button (click)="startNewGeneration()">
                <mat-icon>add</mat-icon>
                New Generation
              </button>
            </ng-container>

            <!-- Failed Actions -->
            <ng-container *ngIf="currentStatus()?.status === 'FAILED'">
              <button mat-raised-button color="primary" (click)="startNewGeneration()">
                <mat-icon>refresh</mat-icon>
                Try Again
              </button>
            </ng-container>

            <!-- Cancelled Actions -->
            <ng-container *ngIf="currentStatus()?.status === 'CANCELLED'">
              <button mat-raised-button color="primary" (click)="startNewGeneration()">
                <mat-icon>add</mat-icon>
                Start New
              </button>
            </ng-container>
          </div>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`
    .status-container {
      max-width: 800px;
      margin: 2rem auto;
      padding: 1rem;
    }

    .status-card {
      width: 100%;
    }

    .status-display {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .status-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      
      &.processing { background-color: #e3f2fd; color: #1976d2; }
      &.generating { background-color: #fff3e0; color: #f57c00; }
      &.completed { background-color: #e8f5e8; color: #388e3c; }
      &.failed { background-color: #ffebee; color: #d32f2f; }
      &.cancelled { background-color: #f3e5f5; color: #7b1fa2; }
    }

    .status-text h3 {
      margin: 0 0 0.5rem 0;
      font-size: 1.5rem;
    }

    .status-text p {
      margin: 0;
      color: rgba(0, 0, 0, 0.7);
    }

    .error-text {
      color: #d32f2f !important;
    }

    .progress-bar {
      margin: 1rem 0;
    }

    .details-section {
      margin-top: 1rem;
    }

    .detail-row {
      display: flex;
      justify-content: space-between;
      padding: 0.5rem 0;
    }

    .label {
      font-weight: 500;
      color: rgba(0, 0, 0, 0.7);
    }

    .agents-section {
      margin-top: 1rem;
    }

    .agents-section h4 {
      margin-bottom: 0.5rem;
    }

    .agent-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .loading-section {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem;
    }

    .actions {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }

    @media (max-width: 600px) {
      .status-container {
        margin: 1rem;
        padding: 0.5rem;
      }

      .status-display {
        flex-direction: column;
        text-align: center;
      }

      .detail-row {
        flex-direction: column;
        gap: 0.25rem;
      }

      .actions {
        flex-direction: column;
      }
    }
  `]
})
export class GenerationStatusComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private projectService = inject(ProjectGenerationService);
  private snackBar = inject(MatSnackBar);

  sessionId = signal<string | null>(null);
  currentStatus = signal<GenerationSession | null>(null);

  private statusSubscription?: Subscription;
  private pollingSubscription?: Subscription;

  ngOnInit() {
    // Get session ID from route
    const sessionId = this.route.snapshot.paramMap.get('sessionId');
    if (sessionId) {
      this.sessionId.set(sessionId);
      this.startStatusPolling(sessionId);
    } else {
      this.router.navigate(['/generator']);
    }
  }

  ngOnDestroy() {
    this.stopPolling();
  }

  private startStatusPolling(sessionId: string) {
    // Get initial status
    this.refreshStatus();

    // Start polling
    this.pollingSubscription = this.projectService.pollGenerationStatus(sessionId, 3000).subscribe({
      next: (status) => {
        this.currentStatus.set(status);
      },
      error: (error) => {
        console.error('Status polling error:', error);
        this.snackBar.open('Failed to get status updates', 'OK', { duration: 3000 });
      },
      complete: () => {
        console.log('Status polling completed');
      }
    });
  }

  private stopPolling() {
    this.statusSubscription?.unsubscribe();
    this.pollingSubscription?.unsubscribe();
  }

  refreshStatus() {
    const sessionId = this.sessionId();
    if (!sessionId) return;

    this.statusSubscription = this.projectService.getGenerationStatus(sessionId).subscribe({
      next: (status) => {
        this.currentStatus.set(status);
      },
      error: (error) => {
        console.error('Status refresh error:', error);
        this.snackBar.open('Failed to refresh status', 'OK', { duration: 3000 });
      }
    });
  }

  isInProgress(): boolean {
    const status = this.currentStatus()?.status;
    return status === 'PROCESSING' || status === 'GENERATING';
  }

  showAgentProgress(): boolean {
    return this.currentStatus()?.status === 'GENERATING';
  }

  getStatusClass(): string {
    const status = this.currentStatus()?.status;
    return status?.toLowerCase() || '';
  }

  getStatusIcon(): string {
    const status = this.currentStatus()?.status;
    switch (status) {
      case 'PROCESSING': return 'upload';
      case 'GENERATING': return 'settings';
      case 'COMPLETED': return 'check_circle';
      case 'FAILED': return 'error';
      case 'CANCELLED': return 'cancel';
      default: return 'help';
    }
  }

  getStatusLabel(): string {
    const status = this.currentStatus()?.status;
    switch (status) {
      case 'PROCESSING': return 'Processing PRD';
      case 'GENERATING': return 'Generating Project';
      case 'COMPLETED': return 'Generation Complete';
      case 'FAILED': return 'Generation Failed';
      case 'CANCELLED': return 'Generation Cancelled';
      default: return 'Unknown Status';
    }
  }

  getAgentList() {
    return [
      { name: 'PRD Analyst', icon: 'description' },
      { name: 'Database', icon: 'storage' },
      { name: 'Backend Code', icon: 'code' },
      { name: 'Frontend Code', icon: 'web' },
      { name: 'DevOps', icon: 'cloud' },
      { name: 'QA Testing', icon: 'bug_report' },
      { name: 'Integration', icon: 'integration_instructions' }
    ];
  }

  formatTime(timestamp: number): string {
    return new Date(timestamp).toLocaleString();
  }

  formatDuration(duration: number): string {
    const seconds = Math.floor(duration / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${remainingSeconds}s`;
  }

  cancelGeneration() {
    const sessionId = this.sessionId();
    if (!sessionId) return;

    this.projectService.cancelGeneration(sessionId).subscribe({
      next: (status) => {
        this.currentStatus.set(status);
        this.stopPolling();
        this.snackBar.open('Generation cancelled', 'OK', { duration: 3000 });
      },
      error: (error) => {
        console.error('Cancel error:', error);
        this.snackBar.open('Failed to cancel generation', 'OK', { duration: 3000 });
      }
    });
  }

  goToDownloadPage() {
    const sessionId = this.sessionId();
    if (sessionId) {
      this.router.navigate(['/download', sessionId]);
    }
  }

  startNewGeneration() {
    this.router.navigate(['/generator']);
  }
}
