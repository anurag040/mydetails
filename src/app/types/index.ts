export interface Application {
  id: string;
  name: string;
  category: string;
  icon: string;
  color: string;
  roles: string[];
  isFavorite?: boolean;
  lastAccessed?: Date;
  description?: string;
  url?: string;
}

export type RoleFilter = 'All' | 'Operations' | 'Production Services' | 'Management' | 'Reporting Analyst' | 'Ops Analyst';

export type SortFilter = 'all' | 'recent' | 'favorites' | 'most-used';
