import { Component, inject, signal, computed, ViewChild } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { NgFor, NgIf } from '@angular/common';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelectModule, MatSelect } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatChipsModule } from '@angular/material/chips';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatStepperModule, MatStepperIntl, MatStepper } from '@angular/material/stepper';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';

import {
  PROJECT_TYPES, ANGULAR_VERSIONS, SPRING_BOOT_VERSIONS,
  PY_BACKENDS, NODE_BACKENDS, GO_BACKENDS,
  JAVA_VERSIONS, PYTHON_VERSIONS, NODE_VERSIONS, GO_VERSIONS,
  BUILD_TOOLS, DATABASES, AUTH_PROVIDERS, EXTRAS, Selection
} from '../../project-types';
import { SummaryChipsComponent } from '../summary-chips/summary-chips.component';

/** Hide the small “Editable” badge cleanly */
class CustomStepperIntl extends MatStepperIntl {
  override editableLabel = '';
  constructor() {
    super();
    setTimeout(() => this.changes.next());
  }
}

@Component({
  selector: 'app-project-generator',
  standalone: true,
  imports: [
    ReactiveFormsModule, NgFor, NgIf,
    MatButtonModule, MatCardModule, MatRadioModule, MatSelectModule, MatInputModule,
    MatChipsModule, MatCheckboxModule, MatIconModule, MatSnackBarModule,
    MatStepperModule, MatDividerModule, MatFormFieldModule,
    SummaryChipsComponent
  ],
  providers: [{ provide: MatStepperIntl, useClass: CustomStepperIntl }],
  templateUrl: './project-generator.component.html',
  styleUrls: ['./project-generator.component.css']
})
export class ProjectGeneratorComponent {
  private fb = inject(FormBuilder);
  private snack = inject(MatSnackBar);

  @ViewChild('stepper') stepper!: MatStepper;

  // Data sources
  projectTypes = PROJECT_TYPES;
  angularVersions = ANGULAR_VERSIONS;
  springVersions = SPRING_BOOT_VERSIONS;
  javaVersions = JAVA_VERSIONS;
  pyBackends = PY_BACKENDS;
  pythonVersions = PYTHON_VERSIONS;
  nodeBackends = NODE_BACKENDS;
  nodeVersions = NODE_VERSIONS;
  goBackends = GO_BACKENDS;
  goVersions = GO_VERSIONS;
  buildTools = BUILD_TOOLS;
  databases = DATABASES;
  authProviders = AUTH_PROVIDERS;
  extras = EXTRAS;

  // Forms
  projectTypeForm = this.fb.group({ projectType: ['', Validators.required] });
  frontendForm   = this.fb.group({ angularVersion: ['16', Validators.required], uiLibs: [[] as string[]] });
  backendForm    = this.fb.group({ 
    backendChoice: [''], 
    backendVersionOrType: [''],
    backendTechVersion: [''],
    buildTool: ['']
  });
  dbForm         = this.fb.group({ databases: [[] as string[]] });
  authForm       = this.fb.group({ auth: [[] as string[]] });
  extrasForm     = this.fb.group({ extras: [[] as string[]] });
  prdForm        = this.fb.group({ prd: [null as File | null] });

  // UI helpers
  prdFileName = signal<string | undefined>(undefined);
  projectTypeValue = signal<string>('');
  formUpdateTrigger = signal<number>(0); // Trigger for form reactivity
  trackByVal = (_: number, v: string) => v;

  // Derived selection
  projectType = computed(() => this.projectTypeValue());
  selection = computed<Selection>(() => {
    // This will make the computed reactive to form changes
    this.formUpdateTrigger();
    
    return {
      projectType: this.projectType(),
      angularVersion: this.frontendForm.getRawValue().angularVersion || undefined,
      uiLibs: this.frontendForm.getRawValue().uiLibs || [],
      backendChoice: this.backendForm.getRawValue().backendChoice || undefined,
      backendVersionOrType: this.backendForm.getRawValue().backendVersionOrType || undefined,
      backendTechVersion: this.backendForm.getRawValue().backendTechVersion || undefined,
      buildTool: this.backendForm.getRawValue().buildTool || undefined,
      databases: this.dbForm.getRawValue().databases || [],
      auth: this.authForm.getRawValue().auth || [],
      extras: this.extrasForm.getRawValue().extras || [],
      prdFileName: this.prdFileName()
    };
  });

  constructor() {
    // Set up reactivity for all forms
    this.setupFormReactivity();
    
    // keep backendChoice in sync with project type and set default versions
    this.projectTypeForm.valueChanges.subscribe((val: any) => {
      const t = val.projectType || '';
      this.projectTypeValue.set(t); // Update the signal
      let label = '';
      let defaultFramework = '';
      let defaultVersion = '';
      
      if (t?.includes('Spring Boot')) {
        label = 'Spring Boot';
        defaultFramework = '3.3'; // Default Spring Boot version
        defaultVersion = '21'; // Default Java version
      } else if (t?.includes('Python')) {
        label = 'Python';
        defaultFramework = 'FastAPI'; // Default Python framework
        defaultVersion = '3.11'; // Default Python version
      } else if (t?.includes('Node')) {
        label = 'Node';
        defaultFramework = 'Express (TS)'; // Default Node framework
        defaultVersion = '20.x'; // Default Node version
      } else if (t?.includes('Go')) {
        label = 'Go';
        defaultFramework = 'Gin'; // Default Go framework
        defaultVersion = '1.21'; // Default Go version
      }
      
      this.backendForm.patchValue({ 
        backendChoice: label,
        backendVersionOrType: defaultFramework,
        backendTechVersion: defaultVersion,
        buildTool: t?.includes('Spring Boot') ? 'Maven' : ''
      });
    });
    this.frontendForm.get('angularVersion')?.enable({ emitEvent: false });
  }

  private setupFormReactivity() {
    // Subscribe to all form changes to trigger reactivity
    this.frontendForm.valueChanges.subscribe(() => {
      this.formUpdateTrigger.update(val => val + 1);
    });
    
    this.backendForm.valueChanges.subscribe(() => {
      this.formUpdateTrigger.update(val => val + 1);
    });
    
    this.dbForm.valueChanges.subscribe(() => {
      this.formUpdateTrigger.update(val => val + 1);
    });
    
    this.authForm.valueChanges.subscribe(() => {
      this.formUpdateTrigger.update(val => val + 1);
    });
    
    this.extrasForm.valueChanges.subscribe(() => {
      this.formUpdateTrigger.update(val => val + 1);
    });
    
    this.prdForm.valueChanges.subscribe(() => {
      this.formUpdateTrigger.update(val => val + 1);
    });
  }

  backendChoice(): string | undefined {
    return this.backendForm.value.backendChoice || undefined;
  }

  toggleExtra(extra: string, on: boolean) {
    const list = new Set(this.extrasForm.value.extras || []);
    on ? list.add(extra) : list.delete(extra);
    this.extrasForm.patchValue({ extras: Array.from(list) });
    // Trigger update for immediate reactivity
    this.formUpdateTrigger.update(val => val + 1);
  }

  isExtraSelected(extra: string): boolean {
    return (this.extrasForm.value.extras || []).includes(extra);
  }

  getBackendTechDisplay(): string {
    const backendTechVersion = this.selection().backendTechVersion;
    const projectType = this.selection().projectType;
    const backendChoice = this.selection().backendChoice;
    
    if (!backendTechVersion) return '';
    
    // Determine the tech type based on project type or backend choice
    if (projectType?.includes('Spring Boot') || backendChoice === 'Spring Boot') {
      return `Java ${backendTechVersion}`;
    } else if (projectType?.includes('Python') || backendChoice === 'Python') {
      return `Python ${backendTechVersion}`;
    } else if (projectType?.includes('Node') || backendChoice === 'Node') {
      return `Node ${backendTechVersion}`;
    } else if (projectType?.includes('Go') || backendChoice === 'Go') {
      return `Go ${backendTechVersion}`;
    }
    
    return backendTechVersion;
  }

  onFile(evt: Event) {
    const input = evt.target as HTMLInputElement;
    const file = input.files?.[0];
    this.prdForm.patchValue({ prd: file || null });
    this.prdFileName.set(file ? file.name : undefined);
  }

  // Close multiple select dropdown
  closeMultiSelect(selectRef: MatSelect) {
    // Remove any empty values that might have been added by the close button
    this.cleanupFormArrays();
    selectRef.close();
  }

  private cleanupFormArrays() {
    // Clean up UI libs
    const uiLibs = this.frontendForm.get('uiLibs')?.value || [];
    this.frontendForm.patchValue({ 
      uiLibs: uiLibs.filter((lib: string) => lib && lib.trim() !== '') 
    });

    // Clean up databases
    const databases = this.dbForm.get('databases')?.value || [];
    this.dbForm.patchValue({ 
      databases: databases.filter((db: string) => db && db.trim() !== '') 
    });

    // Clean up auth
    const auth = this.authForm.get('auth')?.value || [];
    this.authForm.patchValue({ 
      auth: auth.filter((a: string) => a && a.trim() !== '') 
    });
  }

  goStart() {
    // Reset all forms
    this.projectTypeForm.reset({ projectType: '' });
    this.frontendForm.reset({ angularVersion: '16', uiLibs: [] });
    this.backendForm.reset({ backendChoice: '', backendVersionOrType: '', backendTechVersion: '', buildTool: '' });
    this.dbForm.reset({ databases: [] });
    this.authForm.reset({ auth: [] });
    this.extrasForm.reset({ extras: [] });
    this.prdForm.reset({ prd: null });
    
    // Reset signals
    this.projectTypeValue.set('');
    this.prdFileName.set(undefined);
    
    // Reset stepper to first step
    if (this.stepper) {
      this.stepper.reset();
    }
  }

  generate() {
    const payload = { ...this.selection() };
    this.snack.open('Generate clicked — wire this to your ZIP API.', 'OK', { duration: 3000 });
  }
}