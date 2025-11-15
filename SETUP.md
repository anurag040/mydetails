# Angular Setup & Migration Guide

## What Changed

✅ **Converted from React to Angular 18**
- Replaced React components with Angular components
- Migrated from Vite to Angular CLI
- Kept all styling (Tailwind + glassmorphism effects)
- Maintained all 70 applications and features
- Preserved localStorage persistence for favorites/recent access

## Installation Steps

### 1. Install Node Dependencies
```bash
npm install
```

This will install:
- Angular 18 framework
- Angular CLI & DevKit
- TypeScript 5.4
- Tailwind CSS 4
- All required dependencies

### 2. Start Development Server
```bash
npm start
# or
npm run dev
```

The app will open at `http://localhost:4200`

### 3. Build for Production
```bash
npm run build:prod
```

Output: `dist/payments-hub/`

## Project Architecture

### Services Layer
- `ApplicationService`: Centralized app data management
  - CRUD operations (add, remove, update, get applications)
  - Filtering & searching logic
  - localStorage persistence for favorites & recent access
  - Role-based application filtering

### Components Layer
- `AppComponent`: Main root component
- `HeaderComponent`: Search & user profile
- `SidebarComponent`: Navigation with 4 main views
- `FilterPanelComponent`: Role filtering + sort options
- `AppGridComponent`: Responsive grid layout (1-6 columns)
- `AppTileComponent`: Individual application card
- `FavoritesRowComponent`: Horizontal favorites section
- `RecentlyAccessedRowComponent`: Horizontal recently accessed section

### Types
```typescript
interface Application {
  id: string;
  name: string;
  category: string;
  icon: string;
  color: string; // Tailwind gradient
  roles: string[];
  isFavorite?: boolean;
  lastAccessed?: Date;
}
```

## Key Features Implemented

✅ **Responsive Design**
- Mobile: 1 column
- Tablet: 3 columns  
- Desktop: 4-6 columns (depending on screen)

✅ **Role-Based Filtering**
- All, Operations, Production Services, Management, Reporting Analyst, Ops Analyst

✅ **Search**
- Real-time search across app names & categories

✅ **Favorites**
- Pin/unpin applications
- Dedicated favorites view
- Horizontal pinned favorites row on home
- Persisted to localStorage

✅ **Recently Accessed**
- Auto-tracked when launching app
- Chronologically sorted
- Horizontal scrolling row on home
- Persisted to localStorage

✅ **Sorting**
- Show All, Recently Accessed, Favorites, Most Used

✅ **Glassmorphism Styling**
- Semi-transparent cards with blur effect
- Subtle neon borders
- Gradient backgrounds
- Smooth hover animations

## Adding More Applications

Edit `src/app/data/applications.ts`:

```typescript
export const applications: Application[] = [
  // Existing 70 apps...
  
  // Add new app like this:
  {
    id: '71',
    name: 'New App Name',
    category: 'Category Name',
    icon: '🚀',
    color: 'from-purple-500 to-pink-500',
    roles: ['Operations', 'Management'],
    isFavorite: false,
    lastAccessed: undefined
  }
];
```

The grid automatically adapts to any number of applications!

## Managing Applications Programmatically

```typescript
import { ApplicationService } from './services/application.service';

export class MyComponent {
  constructor(private appService: ApplicationService) {}

  addApp() {
    this.appService.addApplication(newApp);
  }

  removeApp(id: string) {
    this.appService.removeApplication(id);
  }

  updateApp(id: string, updates: Partial<Application>) {
    this.appService.updateApplication(id, updates);
  }

  toggleFav(id: string) {
    this.appService.toggleFavorite(id);
  }

  getRecent(limit = 10) {
    return this.appService.getRecentApplications(limit);
  }

  getFavorites() {
    return this.appService.getFavoriteApplications();
  }

  getByRole(role: RoleFilter) {
    return this.appService.getApplicationsByRole(role);
  }

  search(query: string) {
    return this.appService.searchApplications(query);
  }
}
```

## Customization Guide

### Change Color Scheme

1. Update `tailwind.config.ts`:
```typescript
theme: {
  extend: {
    colors: {
      'brand': '#your-color',
    }
  }
}
```

2. Update component templates to use new colors

### Add New Role

1. Update `src/app/types/index.ts`:
```typescript
export type RoleFilter = '... | 'NewRole';
```

2. Update `filter-panel.component.ts`:
```typescript
roles: RoleFilter[] = ['...', 'NewRole'];
```

3. Add applications with new role in `applications.ts`

### Change Grid Columns

Edit `app-grid.component.html` grid classes:
```html
<div class="grid gap-4 grid-cols-1 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
```

Change the numbers to adjust columns per breakpoint.

## Performance Tips

1. **Use TrackBy**: Already implemented in *ngFor loops
2. **Lazy Load Routes**: Add Angular routing module for code splitting
3. **Optimize Images**: Replace emoji icons with SVG for smaller bundle
4. **Tree Shake**: Unused code is automatically removed in production builds

## Deployment

### Build for Production
```bash
npm run build:prod
```

### Deploy to Various Platforms

**Vercel**
```bash
vercel deploy
```

**Netlify**
```bash
netlify deploy --prod --dir=dist/payments-hub
```

**GitHub Pages**
```bash
npm run build:prod
# Then push dist/ folder to gh-pages branch
```

**Traditional Server**
```bash
# Copy dist/payments-hub/* to your web server
# Configure server to redirect all routes to index.html for SPA routing
```

## Troubleshooting

### Port 4200 already in use
```bash
ng serve --port 4300
```

### Module not found errors
```bash
rm -rf node_modules package-lock.json
npm install
npm start
```

### Tailwind styles not applying
1. Save any file in `src/`
2. Dev server should hot-reload
3. If not, restart: `npm start`

### Build size too large
Check with:
```bash
ng build --stats-json
npm install -g webpack-bundle-analyzer
webpack-bundle-analyzer dist/payments-hub/stats.json
```

## Next Steps

1. **Install dependencies**: `npm install`
2. **Start dev server**: `npm start`
3. **Try the features**: Search, filter, add favorites, check recent
4. **Customize**: Add your apps, update colors, adjust layout
5. **Deploy**: Build and deploy to your platform

## Available Commands

```bash
npm start              # Start dev server
npm run dev            # Alternative start
npm run build          # Build for development
npm run build:prod     # Optimized production build
npm run watch          # Watch mode build
npm run ng             # Run Angular CLI
```

## Documentation Files

- `README.md` - Main documentation
- `SETUP.md` - This file
- `src/app/services/application.service.ts` - Service documentation
- Component files have inline documentation

## Support & Questions

- Check README.md for detailed API documentation
- Review ApplicationService for all available methods
- Check component templates for HTML structure
- Inspect types/index.ts for data structure

---

**Ready to build? Run `npm install && npm start`**
