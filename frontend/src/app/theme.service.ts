import { Injectable, inject } from '@angular/core';
import { DOCUMENT } from '@angular/common';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private doc: Document = inject(DOCUMENT);

  constructor() {
    // Start in dark so the neon is visible right away.
    this.setDark(true);
  }

  setDark(on: boolean) {
    const root = this.doc.documentElement; // <html>
    root.classList.toggle('theme-dark', on);
  }

  toggle() {
    const root = this.doc.documentElement;
    const isDark = root.classList.contains('theme-dark');
    this.setDark(!isDark);
  }

  isDark(): boolean {
    return this.doc.documentElement.classList.contains('theme-dark');
  }
}