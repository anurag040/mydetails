import { Component, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatStepperModule } from '@angular/material/stepper';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { GenerationService } from '../core/generation.service';
import { StackOption, ProjectBlueprintPayload } from '../models/project-blueprint';

// StackOption interface imported from shared models

@Component({
  selector: 'app-wizard',
  standalone: true,
  imports: [CommonModule, MatRadioModule, MatSelectModule, MatChipsModule, MatButtonModule, MatIconModule, MatStepperModule, ReactiveFormsModule],
  templateUrl: './wizard.component.html',
  styleUrls: ['./wizard.component.scss']
})
export class WizardComponent {
  baseStacks: StackOption[] = [
    { id: 'ng-spring', label: 'Angular + Spring Boot' },
    { id: 'ng-fastapi', label: 'Angular + Python FastAPI' },
    { id: 'react-node', label: 'React + Node (NestJS)' },
    { id: 'ng-dotnet', label: 'Angular + .NET 8' }
  ];
  databaseOptions: StackOption[] = [
    { id: 'postgres', label: 'PostgreSQL' },
    { id: 'mysql', label: 'MySQL' },
    { id: 'mongodb', label: 'MongoDB' },
    { id: 'redis', label: 'Redis (cache)' }
  ];
  authOptions: StackOption[] = [
    { id: 'azure-ad', label: 'Azure AD' },
    { id: 'okta', label: 'Okta' },
    { id: 'auth0', label: 'Auth0' },
    { id: 'oidc', label: 'Generic OIDC' }
  ];
  toolingOptions: StackOption[] = [
    { id: 'docker', label: 'Docker' },
    { id: 'github-actions', label: 'GitHub Actions CI' },
    { id: 'helm', label: 'Helm Charts' },
    { id: 'k8s', label: 'Kubernetes Manifests' }
  ];

  baseForm = this.fb.group({ baseStack: ['', Validators.required] });
  dbForm = this.fb.group({ databases: [[] as string[]] });
  metaForm = this.fb.group({ auth: [[] as string[]], tooling: [[] as string[]] });

  private prdFile = signal<File | null>(null);
  prdFileName = computed(() => this.prdFile()?.name || '');
  selectionChips = computed(() => {
    const chips: string[] = [];
    if (this.baseForm.value.baseStack) chips.push(this.labelFor(this.baseForm.value.baseStack));
  (this.dbForm.value.databases||[]).forEach((d: string) => chips.push(this.labelFor(d)));
  (this.metaForm.value.auth||[]).forEach((a: string) => chips.push(this.labelFor(a)));
  (this.metaForm.value.tooling||[]).forEach((t: string) => chips.push(this.labelFor(t)));
    if (this.prdFile()) chips.push('PRD:'+ this.prdFileName());
    return chips;
  });

  constructor(private fb: FormBuilder, private gen: GenerationService) {}

  onFile(evt: Event) {
    const input = evt.target as HTMLInputElement;
    if (input.files && input.files.length) {
      this.prdFile.set(input.files[0]);
    }
  }

  emitGenerate() {
    const payload: ProjectBlueprintPayload = {
      baseStack: this.baseForm.value.baseStack,
      databases: this.dbForm.value.databases || [],
      auth: this.metaForm.value.auth || [],
      tooling: this.metaForm.value.tooling || [],
      prdFileName: this.prdFileName() || null
    };
    // Placeholder: integrate generation API call here
    this.gen.generate(payload).then(() => {
      alert('Generation placeholder complete. Check console for payload.');
    });
  }

  private labelFor(id: string): string {
    const all = [...this.baseStacks, ...this.databaseOptions, ...this.authOptions, ...this.toolingOptions];
    return all.find(o => o.id === id)?.label || id;
  }
}
