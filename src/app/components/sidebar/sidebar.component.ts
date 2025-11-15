import { Component, Input, Output, EventEmitter } from '@angular/core';

interface SidebarItem {
  id: string;
  icon: string;
  label: string;
  tooltip: string;
}

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css'],
})
export class SidebarComponent {
  @Input() currentView: string = 'home';
  @Output() viewChange = new EventEmitter<string>();
  @Output() voiceToggle = new EventEmitter<boolean>();

  isVoiceActive = false;

  sidebarItems: SidebarItem[] = [
    { id: 'home', icon: '🏠', label: 'Home', tooltip: 'Home' },
    { id: 'dashboard', icon: '📊', label: 'Dashboard', tooltip: 'Dashboard' },
    {
      id: 'favorites',
      icon: '⭐',
      label: 'Favorites',
      tooltip: 'Favorites',
    },
    { id: 'settings', icon: '⚙️', label: 'Settings', tooltip: 'Settings' },
  ];

  onItemClick(itemId: string): void {
    this.viewChange.emit(itemId);
  }

  onVoiceClick(): void {
    this.isVoiceActive = !this.isVoiceActive;
    this.voiceToggle.emit(this.isVoiceActive);
  }

  isActive(itemId: string): boolean {
    return this.currentView === itemId;
  }
}
