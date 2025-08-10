import { Component, ChangeDetectionStrategy, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpEventType } from '@angular/common/http';

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

type DbOption = 'Vertica' | 'Snowflake' | 'Oracle';

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
  ],
  templateUrl: './project-generator.component.html',
  styleUrls: ['./project-generator.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectGeneratorComponent {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private snack = inject(MatSnackBar);

  // Theme
  isDark = signal<boolean>(false);

  // Options
  springBootVersions = ['3.3.3', '3.2.8', '3.1.12', '2.7.18'];
  angularVersions = ['17', '16', '15'];
  databases: DbOption[] = ['Vertica', 'Snowflake', 'Oracle'];

  // Form (PRD optional, DB multi-select required)
  form = this.fb.group({
    springBootVersion: ['', Validators.required],
    angularVersion: ['', Validators.required],
    groupId: [
      '',
      [
        Validators.required,
        // com.mycompany.app (lowercase, dot-separated)
        Validators.pattern(/^[a-z]+(\.[a-z][a-z0-9]*)+$/),
      ],
    ],
    artifactId: [
      '',
      [
        Validators.required,
        // project-generator (lowercase, numbers, dashes)
        Validators.pattern(/^[a-z][a-z0-9\-]*$/),
      ],
    ],
    applicationName: [
      '',
      [
        Validators.required,
        // Start letter; letters/numbers/space/_/-
        Validators.pattern(/^[A-Za-z][A-Za-z0-9 _\-]{2,}$/),
      ],
    ],
    databases: [<DbOption[]>[], Validators.required], // multi-select required
    prdFile: [<File | null>null],                     // optional
  });

  // Convenience
  get f() { return this.form.controls; }

  // Derived
  isValid = computed(() => this.form.valid);
  isDirty = computed(() => this.form.dirty);

  // Upload state
  isSubmitting = signal(false);
  uploadProgress = signal<number | null>(null);

  onToggleTheme(dark: boolean) {
    this.isDark.set(dark);
  }

  onPRDSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input?.files?.[0] ?? null;

    if (file && file.size > 30 * 1024 * 1024) { // 30 MB guard
      this.snack.open('PRD file is too large (max 30MB).', 'Close', { duration: 3000 });
      this.form.patchValue({ prdFile: null });
      input.value = '';
      return;
    }

    this.form.patchValue({ prdFile: file });
    this.form.markAsDirty();
  }

  removeDb(db: DbOption) {
    const selected = (this.f.databases.value || []) as DbOption[];
    this.f.databases.setValue(selected.filter(d => d !== db));
    this.form.markAsDirty();
  }

  clearPRD(inputEl: HTMLInputElement) {
    this.form.patchValue({ prdFile: null });
    inputEl.value = '';
  }

  // Placeholder POST – replace `POST_URL` with your backend endpoint.
  // Sends multipart/form-data: JSON "config" + (optional) PRD file
  onGenerate() {
    if (!this.form.valid) {
      this.form.markAllAsTouched();
      this.snack.open('Please fix validation errors before generating the project.', 'Close', { duration: 3000 });
      return;
    }

    const POST_URL = '/api/project-generator/generate'; // TODO: replace with real URL

    const { prdFile, ...rest } = this.form.getRawValue();
    const formData = new FormData();
    formData.append('config', new Blob([JSON.stringify(rest)], { type: 'application/json' }));
    if (prdFile) formData.append('prd', prdFile);

    this.isSubmitting.set(true);
    this.uploadProgress.set(0);

    this.http.post(POST_URL, formData, {
      observe: 'events',
      reportProgress: true,
      responseType: 'blob', // expect ZIP blob
    })
    .subscribe({
      next: (event) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          const pct = Math.round((event.loaded / event.total) * 100);
          this.uploadProgress.set(pct);
        }
        if (event.type === HttpEventType.Response) {
          this.isSubmitting.set(false);
          this.uploadProgress.set(null);

          const zipBlob = event.body as Blob;
          if (zipBlob && zipBlob.size > 0) {
            const url = window.URL.createObjectURL(zipBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${rest.artifactId}-project.zip`;
            a.click();
            window.URL.revokeObjectURL(url);
            this.snack.open('Project generated successfully!', 'Close', { duration: 3000 });
            this.form.markAsPristine();
          } else {
            this.snack.open('Generation completed, but no file returned. Check server response.', 'Close', { duration: 4000 });
          }
        }
      },
      error: (err) => {
        console.error(err);
        this.isSubmitting.set(false);
        this.uploadProgress.set(null);
        this.snack.open('Failed to generate project. Please try again.', 'Close', { duration: 4000 });
      }
    });
  }
}



###############
<div class="generator-shell" [class.dark-theme]="isDark()">
  <mat-card class="header-card">
    <div class="header-row">
      <div class="title">
        <mat-icon>construction</mat-icon>
        <h1>Project Generator</h1>
        <span class="subtitle">Configure → Upload PRD (optional) → Generate a ZIP</span>
      </div>

      <div class="actions">
        <mat-slide-toggle
          (change)="onToggleTheme($event.checked)"
          [checked]="isDark()"
          aria-label="Toggle dark mode">
          Dark mode
        </mat-slide-toggle>
      </div>
    </div>

    <div class="status-row">
      <mat-chip-set class="status-chips">
        <mat-chip [disabled]="!isValid()" selected color="primary">
          {{ isValid() ? 'All checks passed' : 'Fill required fields' }}
        </mat-chip>
        <mat-chip *ngIf="isDirty() && !isSubmitting()">Unsaved changes</mat-chip>
      </mat-chip-set>

      <div class="progress" *ngIf="isSubmitting()">
        <mat-progress-bar mode="determinate" *ngIf="uploadProgress() !== null" [value]="uploadProgress()!"></mat-progress-bar>
      </div>
    </div>
  </mat-card>

  <mat-card class="form-card">
    <form [formGroup]="form" class="form-grid" (ngSubmit)="onGenerate()">

      <!-- Versions -->
      <div class="grid two">
        <mat-form-field appearance="outline">
          <mat-label>Spring Boot Version</mat-label>
          <mat-select formControlName="springBootVersion" required>
            <mat-option *ngFor="let v of springBootVersions" [value]="v">{{ v }}</mat-option>
          </mat-select>
          <mat-error *ngIf="f.springBootVersion.touched && f.springBootVersion.invalid">
            Please select a Spring Boot version.
          </mat-error>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Angular Version</mat-label>
          <mat-select formControlName="angularVersion" required>
            <mat-option *ngFor="let v of angularVersions" [value]="v">{{ v }}</mat-option>
          </mat-select>
          <mat-error *ngIf="f.angularVersion.touched && f.angularVersion.invalid">
            Please select an Angular version.
          </mat-error>
        </mat-form-field>
      </div>

      <!-- Chips reflecting single-selects -->
      <div class="chip-bar">
        <mat-chip-set>
          <mat-chip *ngIf="f.springBootVersion.value" color="primary" selected>
            Spring Boot: {{ f.springBootVersion.value }}
          </mat-chip>
          <mat-chip *ngIf="f.angularVersion.value" color="accent" selected>
            Angular: {{ f.angularVersion.value }}
          </mat-chip>
        </mat-chip-set>
      </div>

      <!-- Identifiers -->
      <div class="grid three">
        <mat-form-field appearance="outline">
          <mat-label>Group ID</mat-label>
          <input matInput formControlName="groupId" placeholder="e.g., com.mycompany.app" required>
          <mat-error *ngIf="f.groupId.touched && f.groupId.hasError('required')">Group ID is required.</mat-error>
          <mat-error *ngIf="f.groupId.touched && f.groupId.hasError('pattern')">
            Use lowercase dot-separated package format (e.g., com.mycompany.app).
          </mat-error>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Artifact ID</mat-label>
          <input matInput formControlName="artifactId" placeholder="e.g., project-generator" required>
          <mat-error *ngIf="f.artifactId.touched && f.artifactId.hasError('required')">Artifact ID is required.</mat-error>
          <mat-error *ngIf="f.artifactId.touched && f.artifactId.hasError('pattern')">
            Lowercase, numbers, and dashes only (must start with a letter).
          </mat-error>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Application Name</mat-label>
          <input matInput formControlName="applicationName" placeholder="e.g., Project Generator" required>
          <mat-error *ngIf="f.applicationName.touched && f.applicationName.hasError('required')">Application name is required.</mat-error>
          <mat-error *ngIf="f.applicationName.touched && f.applicationName.hasError('pattern')">
            Start with a letter; letters, numbers, spaces, dashes, underscores allowed (min 3 chars).
          </mat-error>
        </mat-form-field>
      </div>

      <!-- Databases multi-select with chips inside trigger -->
      <mat-form-field appearance="outline">
        <mat-label>Databases</mat-label>
        <mat-select formControlName="databases" multiple required>
          <mat-select-trigger>
            <ng-container *ngIf="(f.databases.value || []).length; else noneSelected">
              <mat-chip-set class="inline-chips">
                <mat-chip *ngFor="let db of f.databases.value" [removable]="true" (removed)="removeDb(db)">
                  {{ db }}
                  <button matChipRemove aria-label="Remove database">
                    <mat-icon>close</mat-icon>
                  </button>
                </mat-chip>
              </mat-chip-set>
            </ng-container>
            <ng-template #noneSelected>Choose one or more…</ng-template>
          </mat-select-trigger>

          <mat-option *ngFor="let db of databases" [value]="db">{{ db }}</mat-option>
        </mat-select>
        <mat-hint>Select one or more (Vertica, Snowflake, Oracle)</mat-hint>
        <mat-error *ngIf="f.databases.touched && f.databases.invalid">
          Please select at least one database.
        </mat-error>
      </mat-form-field>

      <!-- PRD Upload (optional) + Generate -->
      <div class="grid two">
        <div class="file-field">
          <mat-form-field appearance="outline" class="file-input">
            <mat-label>Upload PRD (optional)</mat-label>
            <input matInput [value]="f.prdFile.value?.name || ''" placeholder="Select a PRD file" readonly>
            <button
              mat-icon-button
              matSuffix
              color="primary"
              (click)="fileInput.click()"
              aria-label="Choose file">
              <mat-icon>upload_file</mat-icon>
            </button>
            <mat-hint *ngIf="!f.prdFile.value">You can skip this and generate without a PRD.</mat-hint>
          </mat-form-field>

          <input
            #fileInput
            type="file"
            class="hidden"
            (change)="onPRDSelected($event)"
            accept=".pdf,.doc,.docx,.md,.txt,.json" />
          <button mat-stroked-button *ngIf="f.prdFile.value" (click)="clearPRD(fileInput)">
            <mat-icon>delete</mat-icon>
            Clear PRD
          </button>
        </div>

        <div class="generate-cta">
          <button mat-raised-button color="primary" [disabled]="!form.valid || isSubmitting()" type="submit">
            <mat-icon>rocket_launch</mat-icon>
            Generate Project
          </button>
          <div class="tiny-note">This will POST your config + optional PRD and download a ZIP.</div>
        </div>
      </div>
    </form>
  </mat-card>

  <mat-card class="preview-card">
    <h3>Summary</h3>
    <div class="summary-grid">
      <div>
        <strong>Spring Boot</strong>
        <div>{{ f.springBootVersion.value || '—' }}</div>
      </div>
      <div>
        <strong>Angular</strong>
        <div>{{ f.angularVersion.value || '—' }}</div>
      </div>
      <div>
        <strong>Group ID</strong>
        <div>{{ f.groupId.value || '—' }}</div>
      </div>
      <div>
        <strong>Artifact ID</strong>
        <div>{{ f.artifactId.value || '—' }}</div>
      </div>
      <div>
        <strong>App Name</strong>
        <div>{{ f.applicationName.value || '—' }}</div>
      </div>
      <div>
        <strong>Databases</strong>
        <div>
          <mat-chip-set *ngIf="(f.databases.value || []).length; else noDb">
            <mat-chip *ngFor="let d of f.databases.value" color="primary" selected>{{ d }}</mat-chip>
          </mat-chip-set>
          <ng-template #noDb>—</ng-template>
        </div>
      </div>
      <div class="full">
        <strong>PRD</strong>
        <div>{{ f.prdFile.value?.name || '—' }}</div>
      </div>
    </div>
  </mat-card>
</div>
##############################
/* Component-scoped light/dark token setup */
.generator-shell {
  --bg: #0b0f14;
  --card: #0f141a;
  --text: #e8edf3;
  --muted: #a7b0ba;
  --border: #1e2a36;

  &.dark-theme {
    background: var(--bg);
    color: var(--text);

    .mat-mdc-card {
      background: var(--card);
      color: var(--text);
      border: 1px solid var(--border);
    }

    .mat-mdc-form-field-subscript-wrapper,
    .mat-mdc-form-field-error {
      color: #ff8a80;
    }
  }

  /* Light theme */
  &:not(.dark-theme) {
    --bg: #f7f9fc;
    --card: #ffffff;
    --text: #243447;
    --muted: #5b6b7c;
    --border: #e6ecf1;

    background: var(--bg);
    color: var(--text);

    .mat-mdc-card {
      background: var(--card);
      color: var(--text);
      border: 1px solid var(--border);
    }
  }

  padding: 24px;
  min-height: 100svh;
}

.header-card {
  margin: 0 auto 20px;
  max-width: 1200px;

  .header-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 16px;
    align-items: center;

    .title {
      display: grid;
      grid-template-columns: 32px 1fr;
      gap: 12px;
      align-items: center;

      h1 {
        margin: 0;
        font-weight: 700;
        letter-spacing: 0.2px;
      }
      .subtitle {
        grid-column: 2 / -1;
        color: var(--muted);
        font-size: 0.95rem;
      }
      mat-icon {
        font-size: 28px;
        height: 28px;
        width: 28px;
      }
    }
  }

  .status-row {
    margin-top: 14px;
    display: flex;
    gap: 10px;
    align-items: center;

    .status-chips {
      display: flex;
      gap: 8px;
      align-items: center;
    }

    .progress {
      flex: 1;
    }
  }
}

.form-card,
.preview-card {
  margin: 0 auto 20px;
  max-width: 1200px;
}

.form-grid {
  display: grid;
  gap: 18px;
}

.grid.two {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

.grid.three {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;

  @media (max-width: 1100px) {
    grid-template-columns: 1fr 1fr;
  }
  @media (max-width: 700px) {
    grid-template-columns: 1fr;
  }
}

.chip-bar {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: -8px;
}

.inline-chips .mat-mdc-chip {
  margin-right: 6px;
}

.file-field {
  display: flex;
  align-items: center;
  gap: 12px;

  .file-input {
    flex: 1;
  }

  .hidden {
    display: none;
  }
}

.generate-cta {
  display: grid;
  align-content: start;
  gap: 6px;

  .tiny-note {
    color: var(--muted);
    font-size: 0.85rem;
  }
}

.preview-card {
  h3 {
    margin-top: 0;
    font-weight: 700;
  }

  .summary-grid {
    display: grid;
    gap: 12px;
    grid-template-columns: repeat(3, minmax(0, 1fr));

    .full {
      grid-column: 1 / -1;
    }

    @media (max-width: 900px) {
      grid-template-columns: 1fr 1fr;
    }
    @media (max-width: 600px) {
      grid-template-columns: 1fr;
    }
  }
}

/* Subtle card lift */
.mat-mdc-card {
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}


