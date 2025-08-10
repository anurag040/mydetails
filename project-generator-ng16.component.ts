import { Component, ChangeDetectionStrategy, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpEventType } from '@angular/common/http';
import { Subject, takeUntil } from 'rxjs';

// Angular Material
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { MatExpansionModule } from '@angular/material/expansion';

export type DbOption = 'Vertica' | 'Snowflake' | 'Oracle' | 'PostgreSQL' | 'MySQL' | 'MongoDB';
export type AuthOption = 'JWT' | 'OAuth2' | 'Basic' | 'LDAP';
export type DeploymentOption = 'Docker' | 'Kubernetes' | 'AWS' | 'Azure' | 'GCP';

export interface ProjectConfig {
  springBootVersion: string;
  angularVersion: string;
  groupId: string;
  artifactId: string;
  applicationName: string;
  databases: DbOption[];
  authentication: AuthOption[];
  deployment: DeploymentOption[];
  includeTests: boolean;
  includeSwagger: boolean;
  includeActuator: boolean;
  includeDocker: boolean;
  prdFile: File | null;
}

@Component({
  selector: 'app-project-generator',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    HttpClientModule,
    // Material
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatButtonModule,
    MatIconModule,
    MatSlideToggleModule,
    MatSnackBarModule,
    MatProgressBarModule,
    MatTooltipModule,
    MatDividerModule,
    MatExpansionModule,
  ],
  templateUrl: './project-generator.component.html',
  styleUrls: ['./project-generator.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectGeneratorComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  // Theme (replaced signal with regular property)
  isDark = false;

  // Configuration Options
  springBootVersions = [
    { value: '3.3.3', label: '3.3.3 (Latest)', recommended: true },
    { value: '3.2.8', label: '3.2.8 (LTS)', recommended: true },
    { value: '3.1.12', label: '3.1.12', recommended: false },
    { value: '2.7.18', label: '2.7.18 (Legacy)', recommended: false }
  ];

  angularVersions = [
    { value: '16', label: 'Angular 16 (LTS)', recommended: true },
    { value: '17', label: 'Angular 17 (Latest)', recommended: true },
    { value: '15', label: 'Angular 15', recommended: false }
  ];

  databases: DbOption[] = ['Vertica', 'Snowflake', 'Oracle', 'PostgreSQL', 'MySQL', 'MongoDB'];
  authenticationOptions: AuthOption[] = ['JWT', 'OAuth2', 'Basic', 'LDAP'];
  deploymentOptions: DeploymentOption[] = ['Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP'];

  // Form with enhanced validation
  form = this.fb.group({
    springBootVersion: ['', Validators.required],
    angularVersion: ['', Validators.required],
    groupId: [
      '',
      [
        Validators.required,
        Validators.pattern(/^[a-z]+(\.[a-z][a-z0-9]*)+$/),
        Validators.minLength(3)
      ],
    ],
    artifactId: [
      '',
      [
        Validators.required,
        Validators.pattern(/^[a-z][a-z0-9\-]*$/),
        Validators.minLength(2),
        Validators.maxLength(50)
      ],
    ],
    applicationName: [
      '',
      [
        Validators.required,
        Validators.pattern(/^[A-Za-z][A-Za-z0-9 _\-]{2,}$/),
        Validators.minLength(3),
        Validators.maxLength(100)
      ],
    ],
    databases: [<DbOption[]>[], Validators.required],
    authentication: [<AuthOption[]>['JWT']], // Default to JWT
    deployment: [<DeploymentOption[]>['Docker']], // Default to Docker
    includeTests: [true],
    includeSwagger: [true],
    includeActuator: [true],
    includeDocker: [true],
    prdFile: [<File | null>null],
  });

  // Upload state (replaced signals with regular properties)
  isSubmitting = false;
  uploadProgress: number | null = null;

  // UI State (replaced signals with regular properties)
  panelOpenState = {
    basic: true,
    advanced: false,
    optional: false
  };

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private snack: MatSnackBar
  ) {}

  ngOnInit() {
    // Initialize component
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // Convenience getters
  get f() { return this.form.controls; }

  // Computed properties (replaced computed() with getters)
  get isValid(): boolean {
    return this.form.valid;
  }

  get isDirty(): boolean {
    return this.form.dirty;
  }

  get selectedDatabasesCount(): number {
    return (this.f.databases.value || []).length;
  }

  get selectedAuthCount(): number {
    return (this.f.authentication.value || []).length;
  }

  get selectedDeploymentCount(): number {
    return (this.f.deployment.value || []).length;
  }

  togglePanel(panel: 'basic' | 'advanced' | 'optional') {
    this.panelOpenState = {
      ...this.panelOpenState,
      [panel]: !this.panelOpenState[panel]
    };
  }

  onToggleTheme(dark: boolean) {
    this.isDark = dark;
  }

  onPRDSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input?.files?.[0] ?? null;

    if (file && file.size > 30 * 1024 * 1024) { // 30 MB guard
      this.snack.open('PRD file is too large (max 30MB).', 'Close', { 
        duration: 3000,
        panelClass: ['warning-snackbar']
      });
      this.form.patchValue({ prdFile: null });
      input.value = '';
      return;
    }

    this.form.patchValue({ prdFile: file });
    this.form.markAsDirty();
    
    if (file) {
      this.snack.open(`PRD file "${file.name}" uploaded successfully!`, 'Close', { 
        duration: 2000,
        panelClass: ['success-snackbar']
      });
    }
  }

  removeDb(db: DbOption) {
    const selected = (this.f.databases.value || []) as DbOption[];
    this.f.databases.setValue(selected.filter(d => d !== db));
    this.form.markAsDirty();
  }

  removeAuth(auth: AuthOption) {
    const selected = (this.f.authentication.value || []) as AuthOption[];
    this.f.authentication.setValue(selected.filter(a => a !== auth));
    this.form.markAsDirty();
  }

  removeDeployment(deployment: DeploymentOption) {
    const selected = (this.f.deployment.value || []) as DeploymentOption[];
    this.f.deployment.setValue(selected.filter(d => d !== deployment));
    this.form.markAsDirty();
  }

  clearPRD(inputEl: HTMLInputElement) {
    this.form.patchValue({ prdFile: null });
    inputEl.value = '';
    this.snack.open('PRD file removed', 'Close', { duration: 2000 });
  }

  getVersionIcon(version: string, type: 'spring' | 'angular'): string {
    if (type === 'spring') {
      return this.springBootVersions.find(v => v.value === version)?.recommended ? 'verified' : 'info';
    } else {
      return this.angularVersions.find(v => v.value === version)?.recommended ? 'verified' : 'info';
    }
  }

  getVersionColor(version: string, type: 'spring' | 'angular'): 'primary' | 'accent' | 'warn' {
    if (type === 'spring') {
      return this.springBootVersions.find(v => v.value === version)?.recommended ? 'primary' : 'accent';
    } else {
      return this.angularVersions.find(v => v.value === version)?.recommended ? 'primary' : 'accent';
    }
  }

  onGenerate() {
    if (!this.form.valid) {
      this.form.markAllAsTouched();
      this.snack.open('Please fix validation errors before generating the project.', 'Close', { 
        duration: 4000,
        panelClass: ['error-snackbar']
      });
      return;
    }

    const POST_URL = '/api/project-generator/generate'; // TODO: replace with real URL

    const { prdFile, ...config } = this.form.getRawValue();
    const formData = new FormData();
    formData.append('config', new Blob([JSON.stringify(config)], { type: 'application/json' }));
    if (prdFile) formData.append('prd', prdFile);

    this.isSubmitting = true;
    this.uploadProgress = 0;

    this.http.post(POST_URL, formData, {
      observe: 'events',
      reportProgress: true,
      responseType: 'blob', // expect ZIP blob
    })
    .pipe(takeUntil(this.destroy$))
    .subscribe({
      next: (event) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          const pct = Math.round((event.loaded / event.total) * 100);
          this.uploadProgress = pct;
        }
        if (event.type === HttpEventType.Response) {
          this.isSubmitting = false;
          this.uploadProgress = null;

          const zipBlob = event.body as Blob;
          if (zipBlob && zipBlob.size > 0) {
            const url = window.URL.createObjectURL(zipBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${config.artifactId}-project.zip`;
            a.click();
            window.URL.revokeObjectURL(url);
            
            this.snack.open('🚀 Project generated successfully! Download started.', 'Close', { 
              duration: 4000,
              panelClass: ['success-snackbar']
            });
            this.form.markAsPristine();
          } else {
            this.snack.open('Generation completed, but no file returned. Check server response.', 'Close', { 
              duration: 4000,
              panelClass: ['warning-snackbar']
            });
          }
        }
      },
      error: (err) => {
        console.error('Project generation error:', err);
        this.isSubmitting = false;
        this.uploadProgress = null;
        
        const errorMessage = err.error?.message || 'Failed to generate project. Please try again.';
        this.snack.open(`❌ ${errorMessage}`, 'Close', { 
          duration: 5000,
          panelClass: ['error-snackbar']
        });
      }
    });
  }

  // Helper methods for template
  getErrorMessage(controlName: string): string {
    const control = this.form.get(controlName);
    if (!control || !control.errors || !control.touched) return '';

    const errors = control.errors;
    
    if (errors['required']) return `${this.getFieldLabel(controlName)} is required.`;
    if (errors['pattern']) return this.getPatternError(controlName);
    if (errors['minLength']) return `${this.getFieldLabel(controlName)} must be at least ${errors['minLength'].requiredLength} characters.`;
    if (errors['maxLength']) return `${this.getFieldLabel(controlName)} must be less than ${errors['maxLength'].requiredLength} characters.`;
    
    return 'Invalid input.';
  }

  private getFieldLabel(controlName: string): string {
    const labels: { [key: string]: string } = {
      springBootVersion: 'Spring Boot Version',
      angularVersion: 'Angular Version',
      groupId: 'Group ID',
      artifactId: 'Artifact ID',
      applicationName: 'Application Name',
      databases: 'Databases',
      authentication: 'Authentication',
      deployment: 'Deployment'
    };
    return labels[controlName] || controlName;
  }

  private getPatternError(controlName: string): string {
    const patterns: { [key: string]: string } = {
      groupId: 'Use lowercase dot-separated format (e.g., com.mycompany.app)',
      artifactId: 'Use lowercase letters, numbers, and dashes only (must start with a letter)',
      applicationName: 'Start with a letter; letters, numbers, spaces, dashes, underscores allowed'
    };
    return patterns[controlName] || 'Invalid format.';
  }
}
