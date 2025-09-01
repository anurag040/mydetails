import { Component, OnInit, Inject, HostListener } from '@angular/core';
import { DOCUMENT } from '@angular/common';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {

  selectedTheme = 'light';
  showThemeDropdown = false;
  
  themes = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'graphite', label: 'Graphite' },
    { value: 'forest', label: 'Forest' },
    { value: 'noir', label: 'Noir' }
  ];

  constructor(@Inject(DOCUMENT) private document: Document) {}

  ngOnInit(): void {
    // Load saved theme or default to light
  const savedTheme = localStorage.getItem('theme') || 'light';
  const allowed = new Set(this.themes.map(t => t.value));
  const themeToApply = allowed.has(savedTheme) ? savedTheme : 'light';
  this.selectedTheme = themeToApply;
  this.applyTheme(themeToApply);
  }

  toggleThemeDropdown(): void {
    this.showThemeDropdown = !this.showThemeDropdown;
  }

  selectTheme(theme: string): void {
    this.selectedTheme = theme;
    this.applyTheme(theme);
    this.showThemeDropdown = false;
    localStorage.setItem('theme', theme);
  }

  getSelectedThemeLabel(): string {
    const theme = this.themes.find(t => t.value === this.selectedTheme);
    return theme ? theme.label : 'Theme';
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.theme-selector')) {
      this.showThemeDropdown = false;
    }
  }

  private applyTheme(theme: string): void {
    const body = this.document.body;
    // Remove all theme classes
    body.classList.remove(
      'dark', 'orange-white', 'purple-white', 'neon-black',
      'bloom', 'oceanic', 'ember', 'solar',
      'graphite', 'forest', 'noir'
    );
    // Add selected theme class (if not light)
    if (theme !== 'light') {
      body.classList.add(theme);
    }
  }
}
