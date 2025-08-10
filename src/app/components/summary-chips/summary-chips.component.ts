import { Component, Input } from '@angular/core';
import { NgFor, NgIf } from '@angular/common';

@Component({
  selector: 'app-summary-chips',
  standalone: true,
  imports: [NgFor, NgIf],
  templateUrl: './summary-chips.component.html',
  styleUrls: ['./summary-chips.component.css']
})
export class SummaryChipsComponent {
  @Input() projectType?: string;
  @Input() angularVersion?: string;
  @Input() uiLibs: string[] = [];
  @Input() backendChoice?: string;
  @Input() backendVersionOrType?: string;
  @Input() backendTechVersion?: string;
  @Input() buildTool?: string;
  @Input() databases: string[] = [];
  @Input() auth: string[] = [];
  @Input() extras: string[] = [];
  @Input() prdFileName?: string;

  getBackendTechDisplay(): string {
    if (!this.backendTechVersion) return '';
    
    // Determine the tech type based on project type or backend choice
    if (this.projectType?.includes('Spring Boot') || this.backendChoice === 'Spring Boot') {
      return `Java ${this.backendTechVersion}`;
    } else if (this.projectType?.includes('Python') || this.backendChoice === 'Python') {
      return `Python ${this.backendTechVersion}`;
    } else if (this.projectType?.includes('Node') || this.backendChoice === 'Node') {
      return `Node ${this.backendTechVersion}`;
    } else if (this.projectType?.includes('Go') || this.backendChoice === 'Go') {
      return `Go ${this.backendTechVersion}`;
    }
    
    return this.backendTechVersion;
  }
}
