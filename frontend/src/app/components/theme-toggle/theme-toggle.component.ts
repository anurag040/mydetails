import { Component, inject } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { ThemeService } from '../../theme.service';

@Component({
  selector: 'app-theme-toggle',
  standalone: true,
  imports: [MatIconModule, MatButtonModule],
  template: `
    <button mat-icon-button (click)="toggleTheme()">
      <mat-icon>{{ isDarkMode ? 'light_mode' : 'dark_mode' }}</mat-icon>
    </button>
  `
})
export class ThemeToggleComponent {
  private themeService = inject(ThemeService);
  
  get isDarkMode(): boolean {
    return this.themeService.isDark();
  }

  toggleTheme(): void {
    this.themeService.toggle();
  }
}