import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Application } from '../../types/index';

@Component({
  selector: 'app-grid',
  templateUrl: './app-grid.component.html',
  styleUrls: ['./app-grid.component.css'],
})
export class AppGridComponent {
  @Input() applications: Application[] = [];
  @Input() title: string = 'Applications';
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
