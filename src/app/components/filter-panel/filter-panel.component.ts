import { Component, Input, Output, EventEmitter } from '@angular/core';
import { RoleFilter, SortFilter } from '../../types/index';

@Component({
  selector: 'app-filter-panel',
  templateUrl: './filter-panel.component.html',
  styleUrls: ['./filter-panel.component.css'],
})
export class FilterPanelComponent {
  @Input() selectedRole: RoleFilter = 'All';
  @Input() selectedSort: SortFilter = 'all';
  @Output() roleChange = new EventEmitter<RoleFilter>();
  @Output() sortChange = new EventEmitter<SortFilter>();

  roles: RoleFilter[] = [
    'All',
    'Operations',
    'Production Services',
    'Management',
    'Reporting Analyst',
    'Ops Analyst',
  ];

  sortOptions: { value: SortFilter; label: string }[] = [
    { value: 'all', label: 'Show All' },
    { value: 'recent', label: 'Recently Accessed' },
    { value: 'favorites', label: 'Favorites' },
    { value: 'most-used', label: 'Most Used' },
  ];

  onRoleSelect(role: RoleFilter): void {
    this.roleChange.emit(role);
  }

  onSortSelect(sort: SortFilter): void {
    this.sortChange.emit(sort);
  }
}
