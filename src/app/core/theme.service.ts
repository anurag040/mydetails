import { Injectable } from '@angular/core';

const STORAGE_KEY = 'theme-preference';

@Injectable({
  providedIn: 'root',
})
export class ThemeService {
  isDark: boolean;

  constructor() {
    const saved = localStorage.getItem(STORAGE_KEY);
    this.isDark = saved ? saved === 'dark' : true; // default dark
    this.apply(this.isDark);
  }

  toggle() {
    this.isDark = !this.isDark;
    localStorage.setItem(STORAGE_KEY, this.isDark ? 'dark' : 'light');
    this.apply(this.isDark);
  }

  apply(dark: boolean) {
    document.body.classList.toggle('dark-theme', dark);
    document.body.classList.toggle('light-theme', !dark);
  }
}