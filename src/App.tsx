import { useState, useMemo } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { FilterPanel } from './components/FilterPanel';
import { FavoritesRow } from './components/FavoritesRow';
import { RecentlyAccessedRow } from './components/RecentlyAccessedRow';
import { AppGrid } from './components/AppGrid';
import { StyleGuide } from './components/StyleGuide';
import { applications as initialApps } from './data/applications';
import { Application, RoleFilter, SortFilter } from './types';

export default function App() {
  const [currentView, setCurrentView] = useState('home');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState<RoleFilter>('All');
  const [selectedSort, setSelectedSort] = useState<SortFilter>('all');
  const [apps, setApps] = useState<Application[]>(initialApps);

  const handleToggleFavorite = (id: string) => {
    setApps((prevApps) =>
      prevApps.map((app) =>
        app.id === id ? { ...app, isFavorite: !app.isFavorite } : app
      )
    );
  };

  const filteredApps = useMemo(() => {
    let filtered = apps;

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
        break;
    }

    return filtered;
  }, [apps, searchQuery, selectedRole, selectedSort]);

  const showFavoritesRow = currentView === 'home' && selectedSort === 'all' && !searchQuery;
  const showRecentRow = currentView === 'home' && selectedSort === 'all' && !searchQuery;

  return (
    <div className="min-h-screen bg-[#141414]">
      {/* Header */}
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      {/* Sidebar */}
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />

      {/* Main Content - Fixed padding to prevent overlap */}
      <main className="ml-[72px] pt-[68px]">
        <div className="px-8 py-8 max-w-[2000px]">
          {currentView === 'style-guide' ? (
            <StyleGuide />
          ) : currentView === 'favorites' ? (
            <div className="space-y-8">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">
                  Favorite Applications
                </h1>
                <p className="text-base text-gray-400">Quick access to your most used applications</p>
              </div>
              <AppGrid
                apps={apps.filter((app) => app.isFavorite)}
                title="All Favorites"
                onToggleFavorite={handleToggleFavorite}
              />
            </div>
          ) : (
            <div className="space-y-8">
              {/* Filter Panel */}
              <FilterPanel
                selectedRole={selectedRole}
                onRoleChange={setSelectedRole}
                selectedSort={selectedSort}
                onSortChange={setSelectedSort}
              />

              {/* Favorites Row */}
              {showFavoritesRow && (
                <FavoritesRow apps={apps} onToggleFavorite={handleToggleFavorite} />
              )}

              {/* Recently Accessed Row */}
              {showRecentRow && (
                <RecentlyAccessedRow apps={apps} onToggleFavorite={handleToggleFavorite} />
              )}

              {/* All Applications Grid */}
              <AppGrid
                apps={filteredApps}
                title={
                  selectedSort === 'all'
                    ? 'All Applications'
                    : selectedSort === 'recent'
                    ? 'Recently Accessed'
                    : selectedSort === 'favorites'
                    ? 'Favorite Applications'
                    : 'Most Used Applications'
                }
                onToggleFavorite={handleToggleFavorite}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
