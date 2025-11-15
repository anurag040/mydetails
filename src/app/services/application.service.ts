import { Injectable } from '@angular/core';
import { Application, RoleFilter, SortFilter } from '../types';
import { applications as initialApps } from '../data/applications';

@Injectable({
  providedIn: 'root',
})
export class ApplicationService {
  private applications: Application[] = [];
  private readonly FAVORITES_KEY = 'payments_hub_favorites';
  private readonly RECENT_KEY = 'payments_hub_recent';

  constructor() {
    this.initializeApplications();
  }

  private initializeApplications(): void {
    // Deep copy the applications and convert date strings back to Date objects
    this.applications = initialApps.map((app: Application) => ({
      ...app,
      lastAccessed: app.lastAccessed instanceof Date ? app.lastAccessed : (app.lastAccessed ? new Date(app.lastAccessed as any) : undefined)
    }));
    console.log('Initialized applications:', this.applications.length);
    this.loadFavoritesFromStorage();
    this.loadRecentAccessedFromStorage();
  }

  private loadFavoritesFromStorage(): void {
    const favoriteIds = localStorage.getItem(this.FAVORITES_KEY);
    if (favoriteIds) {
      const ids = JSON.parse(favoriteIds) as string[];
      this.applications.forEach((app) => {
        app.isFavorite = ids.includes(app.id);
      });
    }
  }

  private loadRecentAccessedFromStorage(): void {
    const recent = localStorage.getItem(this.RECENT_KEY);
    if (recent) {
      const recentData = JSON.parse(recent) as {
        id: string;
        timestamp: number;
      }[];
      this.applications.forEach((app) => {
        const recentItem = recentData.find((r) => r.id === app.id);
        if (recentItem) {
          app.lastAccessed = new Date(recentItem.timestamp);
        }
      });
    }
  }

  private saveFavoritesToStorage(): void {
    const favoriteIds = this.applications
      .filter((app) => app.isFavorite)
      .map((app) => app.id);
    localStorage.setItem(this.FAVORITES_KEY, JSON.stringify(favoriteIds));
  }

  private saveRecentAccessedToStorage(): void {
    const recent = this.applications
      .filter((app) => app.lastAccessed)
      .map((app) => ({
        id: app.id,
        timestamp: app.lastAccessed!.getTime(),
      }));
    localStorage.setItem(this.RECENT_KEY, JSON.stringify(recent));
  }

  getApplications(): Application[] {
    // Return a deep copy but preserve Date objects
    return this.applications.map((app: Application) => ({
      ...app,
      lastAccessed: app.lastAccessed instanceof Date ? new Date(app.lastAccessed) : undefined
    }));
  }

  getApplicationById(id: string): Application | undefined {
    return this.applications.find((app) => app.id === id);
  }

  toggleFavorite(id: string): void {
    const app = this.applications.find((a) => a.id === id);
    if (app) {
      app.isFavorite = !app.isFavorite;
      this.saveFavoritesToStorage();
    }
  }

  updateLastAccessed(id: string): void {
    const app = this.applications.find((a) => a.id === id);
    if (app) {
      app.lastAccessed = new Date();
      this.saveRecentAccessedToStorage();
    }
  }

  addApplication(app: Application): void {
    const exists = this.applications.find((a) => a.id === app.id);
    if (!exists) {
      this.applications.push(app);
    }
  }

  removeApplication(id: string): void {
    const index = this.applications.findIndex((a) => a.id === id);
    if (index >= 0) {
      this.applications.splice(index, 1);
    }
  }

  updateApplication(id: string, updates: Partial<Application>): void {
    const app = this.applications.find((a) => a.id === id);
    if (app) {
      Object.assign(app, updates);
    }
  }

  filterApplications(
    apps: Application[],
    searchQuery: string,
    selectedRole: RoleFilter,
    selectedSort: SortFilter
  ): Application[] {
    let filtered = [...apps];

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(
        (app) =>
          app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          app.category.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by role
    if (selectedRole !== 'All') {
      filtered = filtered.filter((app) => app.roles.includes(selectedRole));
    }

    // Filter by sort option
    switch (selectedSort) {
      case 'recent':
        filtered = filtered.filter((app) => app.lastAccessed);
        filtered.sort((a, b) => {
          if (!a.lastAccessed || !b.lastAccessed) return 0;
          return b.lastAccessed.getTime() - a.lastAccessed.getTime();
        });
        break;
      case 'favorites':
        filtered = filtered.filter((app) => app.isFavorite);
        break;
      case 'most-used':
        filtered = filtered.filter((app) => app.lastAccessed);
        filtered.sort((a, b) => {
          if (!a.lastAccessed || !b.lastAccessed) return 0;
          return b.lastAccessed.getTime() - a.lastAccessed.getTime();
        });
        break;
    }

    return filtered;
  }

  searchApplications(query: string): Application[] {
    if (!query) return this.applications;

    const lower = query.toLowerCase();
    return this.applications.filter(
      (app) =>
        app.name.toLowerCase().includes(lower) ||
        app.category.toLowerCase().includes(lower)
    );
  }

  getApplicationsByRole(role: RoleFilter): Application[] {
    if (role === 'All') return this.applications;
    return this.applications.filter((app) => app.roles.includes(role));
  }

  getRecentApplications(limit: number = 10): Application[] {
    return [...this.applications]
      .filter((app) => app.lastAccessed)
      .sort(
        (a, b) =>
          (b.lastAccessed?.getTime() || 0) - (a.lastAccessed?.getTime() || 0)
      )
      .slice(0, limit);
  }

  getFavoriteApplications(): Application[] {
    return this.applications.filter((app) => app.isFavorite);
  }

  getApplicationCount(): number {
    return this.applications.length;
  }
}
