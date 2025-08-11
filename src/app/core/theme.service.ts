import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly dark = signal<boolean>(false);
  isDark = this.dark.asReadonly();

  constructor() {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') {
      this.dark.set(true);
      document.documentElement.dataset['theme'] = 'dark';
      document.body.classList.add('dark-theme');
    }
  }

  toggleTheme() {
    const next = !this.dark();
    this.dark.set(next);
  document.documentElement.dataset['theme'] = next ? 'dark' : 'light';
  document.body.classList.toggle('dark-theme', next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
  }
}
