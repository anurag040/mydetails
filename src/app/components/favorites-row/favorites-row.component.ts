import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Application } from '../../types/index';

@Component({
  selector: 'app-favorites-row',
  templateUrl: './favorites-row.component.html',
  styleUrls: ['./favorites-row.component.css'],
})
export class FavoritesRowComponent {
  @Input() applications: Application[] = [];
  @Output() toggleFavorite = new EventEmitter<string>();
  @Output() launchApp = new EventEmitter<Application>();

  onToggleFavorite(id: string): void {
    this.toggleFavorite.emit(id);
  }

  onLaunchApp(app: Application): void {
    this.launchApp.emit(app);
  }

  trackByAppId(_index: number, app: Application): string {
    return app.id;
  }
}
