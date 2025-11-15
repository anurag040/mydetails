import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Application } from '../../types/index';

@Component({
  selector: 'app-tile',
  templateUrl: './app-tile.component.html',
  styleUrls: ['./app-tile.component.css'],
})
export class AppTileComponent {
  @Input() application!: Application;
  @Output() toggleFavorite = new EventEmitter<string>();
  @Output() launch = new EventEmitter<Application>();

  onToggleFavorite(event: Event): void {
    event.stopPropagation();
    this.toggleFavorite.emit(this.application.id);
  }

  onLaunch(): void {
    this.launch.emit(this.application);
  }
}
