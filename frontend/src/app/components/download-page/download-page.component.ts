import { Component, inject, signal, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgIf, NgFor } from '@angular/common';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';

import { ProjectGenerationService, ProjectBlueprint } from '../../services/project-generation.service';

@Component({
  selector: 'app-download-page',
  standalone: true,
  imports: [
    NgIf, NgFor,
    MatCardModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule,
    MatDividerModule, MatChipsModule
  ],
  template: `
    <div class="download-container">
      <mat-card class="download-card">
        <mat-card-header>
          <mat-card-title>
            <mat-icon>download</mat-icon>
            Download Generated Project
          </mat-card-title>
          <mat-card-subtitle *ngIf="sessionId()">
            Session: {{ sessionId() }}
          </mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <!-- Project Information -->
          <div class="project-info" *ngIf="projectBlueprint()">
            <h3>Project Details</h3>
            <div class="info-row">
              <span class="label">Name:</span>
              <span>{{ projectBlueprint()?.projectName || 'Generated Project' }}</span>
            </div>
            <div class="info-row">
              <span class="label">Description:</span>
              <span>{{ projectBlueprint()?.description || 'AI-generated project from PRD' }}</span>
            </div>
            <mat-divider></mat-divider>
          </div>

          <!-- Download Options -->
          <div class="download-section">
            <h3>Download Files</h3>
            <p>Your project has been successfully generated. Download the frontend and backend ZIP files below:</p>

            <div class="download-options">
              <!-- Backend Download -->
              <div class="download-option">
                <div class="option-header">
                  <mat-icon>code</mat-icon>
                  <div class="option-details">
                    <h4>Backend Code</h4>
                    <p>Spring Boot application with REST APIs, database configuration, and business logic</p>
                  </div>
                </div>
                <div class="option-actions">
                  <button 
                    mat-raised-button 
                    color="primary" 
                    [disabled]="isDownloadingBackend()"
                    (click)="downloadBackend()">
                    <mat-spinner diameter="20" *ngIf="isDownloadingBackend()"></mat-spinner>
                    <mat-icon *ngIf="!isDownloadingBackend()">download</mat-icon>
                    {{ isDownloadingBackend() ? 'Downloading...' : 'Download Backend' }}
                  </button>
                </div>
              </div>

              <mat-divider></mat-divider>

              <!-- Frontend Download -->
              <div class="download-option">
                <div class="option-header">
                  <mat-icon>web</mat-icon>
                  <div class="option-details">
                    <h4>Frontend Code</h4>
                    <p>Angular application with components, services, and complete UI implementation</p>
                  </div>
                </div>
                <div class="option-actions">
                  <button 
                    mat-raised-button 
                    color="primary" 
                    [disabled]="isDownloadingFrontend()"
                    (click)="downloadFrontend()">
                    <mat-spinner diameter="20" *ngIf="isDownloadingFrontend()"></mat-spinner>
                    <mat-icon *ngIf="!isDownloadingFrontend()">download</mat-icon>
                    {{ isDownloadingFrontend() ? 'Downloading...' : 'Download Frontend' }}
                  </button>
                </div>
              </div>

              <mat-divider></mat-divider>

              <!-- Download Both -->
              <div class="download-option">
                <div class="option-header">
                  <mat-icon>download_for_offline</mat-icon>
                  <div class="option-details">
                    <h4>Download Both</h4>
                    <p>Download both frontend and backend ZIP files at once</p>
                  </div>
                </div>
                <div class="option-actions">
                  <button 
                    mat-raised-button 
                    color="accent" 
                    [disabled]="isDownloadingBoth()"
                    (click)="downloadBoth()">
                    <mat-spinner diameter="20" *ngIf="isDownloadingBoth()"></mat-spinner>
                    <mat-icon *ngIf="!isDownloadingBoth()">download_for_offline</mat-icon>
                    {{ isDownloadingBoth() ? 'Downloading...' : 'Download Both' }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Instructions -->
          <div class="instructions-section">
            <h3>Next Steps</h3>
            <div class="instructions">
              <div class="instruction-item">
                <mat-icon>folder_open</mat-icon>
                <div>
                  <strong>1. Extract Files</strong>
                  <p>Extract the downloaded ZIP files to your desired project directory</p>
                </div>
              </div>

              <div class="instruction-item">
                <mat-icon>play_arrow</mat-icon>
                <div>
                  <strong>2. Backend Setup</strong>
                  <p>Navigate to backend folder and run: <code>mvn spring-boot:run</code></p>
                </div>
              </div>

              <div class="instruction-item">
                <mat-icon>web</mat-icon>
                <div>
                  <strong>3. Frontend Setup</strong>
                  <p>Navigate to frontend folder and run: <code>npm install && ng serve</code></p>
                </div>
              </div>

              <div class="instruction-item">
                <mat-icon>open_in_browser</mat-icon>
                <div>
                  <strong>4. Access Application</strong>
                  <p>Open <code>http://localhost:4200</code> in your browser</p>
                </div>
              </div>
            </div>
          </div>
        </mat-card-content>

        <mat-card-actions>
          <button mat-button (click)="goToStatus()">
            <mat-icon>visibility</mat-icon>
            View Status
          </button>
          <button mat-button (click)="startNewGeneration()">
            <mat-icon>add</mat-icon>
            Generate New Project
          </button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`
    .download-container {
      max-width: 900px;
      margin: 2rem auto;
      padding: 1rem;
    }

    .download-card {
      width: 100%;
    }

    .project-info {
      margin-bottom: 2rem;
    }

    .info-row {
      display: flex;
      justify-content: space-between;
      padding: 0.5rem 0;
    }

    .label {
      font-weight: 500;
      color: rgba(0, 0, 0, 0.7);
      min-width: 100px;
    }

    .download-section h3 {
      margin-bottom: 1rem;
    }

    .download-options {
      margin: 1rem 0;
    }

    .download-option {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem 0;
    }

    .option-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      flex: 1;
    }

    .option-details h4 {
      margin: 0 0 0.25rem 0;
      font-size: 1.1rem;
    }

    .option-details p {
      margin: 0;
      color: rgba(0, 0, 0, 0.7);
      font-size: 0.9rem;
    }

    .option-actions {
      margin-left: 1rem;
    }

    .instructions-section {
      margin-top: 2rem;
    }

    .instructions {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .instruction-item {
      display: flex;
      align-items: flex-start;
      gap: 1rem;
    }

    .instruction-item mat-icon {
      margin-top: 0.25rem;
      color: #1976d2;
    }

    .instruction-item strong {
      display: block;
      margin-bottom: 0.25rem;
    }

    .instruction-item p {
      margin: 0;
      color: rgba(0, 0, 0, 0.7);
    }

    code {
      background-color: #f5f5f5;
      padding: 0.2rem 0.4rem;
      border-radius: 3px;
      font-family: 'Courier New', monospace;
      font-size: 0.9em;
    }

    @media (max-width: 600px) {
      .download-container {
        margin: 1rem;
        padding: 0.5rem;
      }

      .download-option {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
      }

      .option-actions {
        margin-left: 0;
        width: 100%;
      }

      .option-actions button {
        width: 100%;
      }

      .info-row {
        flex-direction: column;
        gap: 0.25rem;
      }
    }
  `]
})
export class DownloadPageComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private projectService = inject(ProjectGenerationService);
  private snackBar = inject(MatSnackBar);

  sessionId = signal<string | null>(null);
  projectBlueprint = signal<ProjectBlueprint | null>(null);
  
  isDownloadingBackend = signal<boolean>(false);
  isDownloadingFrontend = signal<boolean>(false);
  isDownloadingBoth = signal<boolean>(false);

  ngOnInit() {
    // Get session ID from route
    const sessionId = this.route.snapshot.paramMap.get('sessionId');
    if (sessionId) {
      this.sessionId.set(sessionId);
      this.loadProjectBlueprint(sessionId);
    } else {
      this.router.navigate(['/generator']);
    }
  }

  private loadProjectBlueprint(sessionId: string) {
    this.projectService.getProjectBlueprint(sessionId).subscribe({
      next: (blueprint) => {
        this.projectBlueprint.set(blueprint);
      },
      error: (error) => {
        console.error('Failed to load project blueprint:', error);
        // Continue anyway, blueprint is optional for download
      }
    });
  }

  downloadBackend() {
    const sessionId = this.sessionId();
    if (!sessionId) return;

    this.isDownloadingBackend.set(true);
    
    this.projectService.downloadBackendZip(sessionId).subscribe({
      next: (blob) => {
        this.projectService.downloadFile(blob, `${sessionId}-backend.zip`);
        this.snackBar.open('Backend download completed!', 'OK', { duration: 3000 });
        this.isDownloadingBackend.set(false);
      },
      error: (error) => {
        console.error('Backend download failed:', error);
        this.snackBar.open('Backend download failed. Please try again.', 'OK', { duration: 5000 });
        this.isDownloadingBackend.set(false);
      }
    });
  }

  downloadFrontend() {
    const sessionId = this.sessionId();
    if (!sessionId) return;

    this.isDownloadingFrontend.set(true);
    
    this.projectService.downloadFrontendZip(sessionId).subscribe({
      next: (blob) => {
        this.projectService.downloadFile(blob, `${sessionId}-frontend.zip`);
        this.snackBar.open('Frontend download completed!', 'OK', { duration: 3000 });
        this.isDownloadingFrontend.set(false);
      },
      error: (error) => {
        console.error('Frontend download failed:', error);
        this.snackBar.open('Frontend download failed. Please try again.', 'OK', { duration: 5000 });
        this.isDownloadingFrontend.set(false);
      }
    });
  }

  downloadBoth() {
    this.isDownloadingBoth.set(true);
    
    // Download both files sequentially
    this.downloadBackend();
    setTimeout(() => {
      this.downloadFrontend();
      this.isDownloadingBoth.set(false);
    }, 1000);
  }

  goToStatus() {
    const sessionId = this.sessionId();
    if (sessionId) {
      this.router.navigate(['/status', sessionId]);
    }
  }

  startNewGeneration() {
    this.router.navigate(['/generator']);
  }
}
