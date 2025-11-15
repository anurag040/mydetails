import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css'],
})
export class HeaderComponent {
  @Input() searchQuery: string = '';
  @Output() searchChange = new EventEmitter<string>();

  userRole = 'Operations Analyst';
  userInitials = 'JD';

  onSearchChange(value: string): void {
    this.searchChange.emit(value);
  }

  onProfileClick(): void {
    console.log('Profile clicked');
  }
}
