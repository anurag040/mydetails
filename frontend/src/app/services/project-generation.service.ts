import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpEvent, HttpEventType } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { Selection } from '../project-types';

export interface GenerationSession {
  sessionId: string;
  status: 'PROCESSING' | 'GENERATING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  message?: string;
  error?: string;
  startTime?: number;
  endTime?: number;
  duration?: number;
  agentResults?: number;
  successfulAgents?: number;
}

export interface ProjectBlueprint {
  projectName: string;
  description: string;
  // Add other blueprint properties as needed
}

@Injectable({
  providedIn: 'root'
})
export class ProjectGenerationService {
  private http = inject(HttpClient);
  
  private readonly baseUrl = 'http://localhost:8080/api/projects';
  
  // Current session tracking
  private currentSessionSubject = new BehaviorSubject<string | null>(null);
  public currentSession$ = this.currentSessionSubject.asObservable();
  
  private generationStatusSubject = new BehaviorSubject<GenerationSession | null>(null);
  public generationStatus$ = this.generationStatusSubject.asObservable();

  /**
   * Upload PRD file and start processing
   */
  uploadPRD(file: File, projectName?: string): Observable<GenerationSession> {
    const formData = new FormData();
    formData.append('file', file);
    if (projectName) {
      formData.append('projectName', projectName);
    }

    return this.http.post<GenerationSession>(`${this.baseUrl}/upload-prd`, formData).pipe(
      map(response => {
        this.currentSessionSubject.next(response.sessionId);
        this.generationStatusSubject.next(response);
        return response;
      }),
      catchError(error => {
        console.error('PRD upload failed:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Generate project directly without PRD upload
   */
  generateDirectProject(config: Selection): Observable<GenerationSession> {
    return this.http.post<GenerationSession>(`${this.baseUrl}/generate`, config).pipe(
      map(response => {
        this.currentSessionSubject.next(response.sessionId);
        this.generationStatusSubject.next(response);
        return response;
      }),
      catchError(error => {
        console.error('Direct project generation failed:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Start project generation with configuration
   */
  generateProject(sessionId: string, config: Selection): Observable<GenerationSession> {
    return this.http.post<GenerationSession>(`${this.baseUrl}/generate/${sessionId}`, config).pipe(
      map(response => {
        this.generationStatusSubject.next(response);
        return response;
      }),
      catchError(error => {
        console.error('Project generation failed:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Get generation status for a session
   */
  getGenerationStatus(sessionId: string): Observable<GenerationSession> {
    return this.http.get<GenerationSession>(`${this.baseUrl}/status/${sessionId}`).pipe(
      map(response => {
        this.generationStatusSubject.next(response);
        return response;
      }),
      catchError(error => {
        console.error('Failed to get status:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Poll generation status periodically
   */
  pollGenerationStatus(sessionId: string, intervalMs: number = 2000): Observable<GenerationSession> {
    return new Observable(observer => {
      const interval = setInterval(() => {
        this.getGenerationStatus(sessionId).subscribe({
          next: status => {
            observer.next(status);
            
            // Stop polling if generation is complete, failed, or cancelled
            if (['COMPLETED', 'FAILED', 'CANCELLED'].includes(status.status)) {
              clearInterval(interval);
              observer.complete();
            }
          },
          error: error => {
            clearInterval(interval);
            observer.error(error);
          }
        });
      }, intervalMs);

      // Cleanup function
      return () => {
        clearInterval(interval);
      };
    });
  }

  /**
   * Download combined project ZIP file
   */
  downloadProjectZip(sessionId: string): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/download/${sessionId}`, {
      responseType: 'blob'
    }).pipe(
      catchError(error => {
        console.error('Project download failed:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Download backend ZIP file
   */
  downloadBackendZip(sessionId: string): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/download/backend/${sessionId}`, {
      responseType: 'blob'
    }).pipe(
      catchError(error => {
        console.error('Backend download failed:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Download frontend ZIP file
   */
  downloadFrontendZip(sessionId: string): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/download/frontend/${sessionId}`, {
      responseType: 'blob'
    }).pipe(
      catchError(error => {
        console.error('Frontend download failed:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Get project blueprint
   */
  getProjectBlueprint(sessionId: string): Observable<ProjectBlueprint> {
    return this.http.get<ProjectBlueprint>(`${this.baseUrl}/blueprint/${sessionId}`).pipe(
      catchError(error => {
        console.error('Blueprint retrieval failed:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Cancel generation
   */
  cancelGeneration(sessionId: string): Observable<GenerationSession> {
    return this.http.post<GenerationSession>(`${this.baseUrl}/cancel/${sessionId}`, {}).pipe(
      map(response => {
        this.generationStatusSubject.next(response);
        return response;
      }),
      catchError(error => {
        console.error('Cancellation failed:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Trigger file download
   */
  downloadFile(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  /**
   * Clear current session
   */
  clearSession(): void {
    this.currentSessionSubject.next(null);
    this.generationStatusSubject.next(null);
  }

  /**
   * Get current session ID
   */
  getCurrentSessionId(): string | null {
    return this.currentSessionSubject.value;
  }

  /**
   * Health check
   */
  healthCheck(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }
}
