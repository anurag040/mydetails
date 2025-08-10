import { Component, computed, inject } from '@angular/core';
import { NgIf } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ThemeService } from '../../theme.service';

@Component({
  selector: 'app-theme-toggle',
  standalone: true,
  imports: [NgIf, MatIconModule, MatButtonModule, MatTooltipModule],
  template: `
    <button mat-icon-button (click)="toggle()" [matTooltip]="tooltip()"
            aria-label="Toggle theme">
      <mat-icon *ngIf="isDark(); else sun">dark_mode</mat-icon>
      <ng-template #sun><mat-icon>light_mode</mat-icon></ng-template>
    </button>
  `
})
export class ThemeToggleComponent {
  private theme = inject(ThemeService);

  isDark = () => this.theme.isDark();

  toggle() {
    this.theme.toggle();
  }

  tooltip = computed(() => this.isDark() ? 'Switch to light theme' : 'Switch to dark theme');
}