# News Feed API Integration Guide

This document provides instructions on how to integrate your backend API with the Angular News Feed application.

## Overview

The application has been refactored to use a service-based architecture with the following structure:

- **Constants**: All hardcoded data moved to `src/app/shared/constants/news.constants.ts`
- **Interfaces**: Type definitions in `src/app/shared/interfaces/news.interface.ts`
- **Service**: API service in `src/app/shared/services/news.service.ts`
- **Component**: Updated to use the service in `src/app/components/news-feed/news-feed.component.ts`

## Quick Start

1. **Update API Base URL**: In `news.constants.ts`, update the `API_ENDPOINTS.BASE_URL` to point to your backend.

2. **Enable HTTP Calls**: In `news.service.ts`, uncomment the HTTP calls and comment out the mock responses.

3. **Customize Data**: Modify the constants in `news.constants.ts` to match your data structure.

## API Endpoints Structure

Your backend should implement these endpoints:

### Required Endpoints

```typescript
// Base URL configuration
const API_BASE = 'https://your-api.com/api/v1';

// GET /api/v1/main-article
// Returns the featured article for the main content area
interface MainArticleResponse {
  title: string;
  category: string;
  date: string;         // ISO date string
  dateFormatted: string; // Human readable date
  author: string;
  views: string;
  shares: string;
  comments: string;
}

// GET /api/v1/main-article/{id}/content
// Returns the article content (excerpt and full text)
interface ArticleContentResponse {
  excerpt: string; // HTML content for preview
  full: string;    // HTML content for full article
}

// GET /api/v1/news
// Returns list of recent news items
interface NewsResponse {
  id: number;
  title: string;
  category: string;
  date: string;
  dateFormatted: string;
  author: string;
  views: string;
  shares: string;
  comments?: string;
  image: string;
  trending?: boolean;
}[]

// GET /api/v1/stats
// Returns news statistics for the dashboard
interface StatsResponse {
  totalNewsCount: number;
  todayNewsCount: number;
  trendingCount: number;
}

// POST /api/v1/refresh
// Triggers a news refresh and returns success status
interface RefreshResponse {
  success: boolean;
  message: string;
}
```

## Step-by-Step Integration

### Step 1: Update Constants (Optional)

```typescript
// In src/app/shared/constants/news.constants.ts
export const NEWS_CONSTANTS = {
  // Update API endpoints
  API_ENDPOINTS: {
    BASE_URL: 'https://your-api.com/api/v1', // Update this
    NEWS: '/news',
    MAIN_ARTICLE: '/main-article',
    STATS: '/stats',
    REFRESH: '/refresh'
  },
  
  // Update other constants as needed
  PREFERRED_TAGS: ['#YourTag1', '#YourTag2', '#YourTag3'],
  // ... rest of your custom data
};
```

### Step 2: Enable HTTP Calls in Service

```typescript
// In src/app/shared/services/news.service.ts

// Replace this mock call:
// return of(NEWS_CONSTANTS.MAIN_ARTICLE).pipe(delay(300));

// With this HTTP call:
getMainArticle(): Observable<MainArticle> {
  return this.http.get<MainArticle>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.MAIN_ARTICLE}`);
}

// Do the same for all other methods:
getRecentNews(): Observable<NewsItem[]> {
  return this.http.get<NewsItem[]>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}`);
}

getNewsStats(): Observable<NewsStats> {
  return this.http.get<NewsStats>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.STATS}`);
}

refreshNews(): Observable<{ success: boolean; message: string }> {
  return this.http.post<{success: boolean, message: string}>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.REFRESH}`, {});
}
```

### Step 3: Handle Authentication (If Required)

```typescript
// In src/app/shared/services/news.service.ts
// Add authentication headers if needed

private getHttpOptions() {
  return {
    headers: new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.getAuthToken()}` // Add if needed
    })
  };
}

getMainArticle(): Observable<MainArticle> {
  return this.http.get<MainArticle>(
    `${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.MAIN_ARTICLE}`,
    this.getHttpOptions()
  );
}
```

### Step 4: Error Handling

The component already includes basic error handling. You can enhance it:

```typescript
// In src/app/shared/services/news.service.ts
import { catchError, retry } from 'rxjs/operators';
import { throwError } from 'rxjs';

getMainArticle(): Observable<MainArticle> {
  return this.http.get<MainArticle>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.MAIN_ARTICLE}`)
    .pipe(
      retry(2), // Retry failed requests 2 times
      catchError(this.handleError)
    );
}

private handleError(error: any) {
  console.error('API Error:', error);
  return throwError(() => new Error('Something went wrong; please try again later.'));
}
```

## Optional Enhancements

### Search Functionality
```typescript
// Uncomment and implement in news.service.ts
searchNews(query: string): Observable<NewsItem[]> {
  return this.http.get<NewsItem[]>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}/search?q=${query}`);
}
```

### Category Filtering
```typescript
getNewsByCategory(category: string): Observable<NewsItem[]> {
  return this.http.get<NewsItem[]>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}/category/${category}`);
}
```

### CRUD Operations
```typescript
createNews(news: Partial<NewsItem>): Observable<NewsItem> {
  return this.http.post<NewsItem>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}`, news);
}

updateNews(id: number, news: Partial<NewsItem>): Observable<NewsItem> {
  return this.http.put<NewsItem>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}/${id}`, news);
}

deleteNews(id: number): Observable<{success: boolean}> {
  return this.http.delete<{success: boolean}>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}/${id}`);
}
```

## Testing

1. **Mock Data**: Keep the current mock implementation for development
2. **Environment Variables**: Use Angular environments to switch between mock and real API
3. **API Testing**: Test each endpoint individually before full integration

## Environment Configuration

```typescript
// In src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'https://localhost:3000/api/v1',
  useMockData: true // Set to false when ready for real API
};

// In src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://your-production-api.com/api/v1',
  useMockData: false
};
```

Then update the service:
```typescript
// In news.service.ts
import { environment } from '../../../environments/environment';

constructor(private http: HttpClient) {
  this.baseUrl = environment.apiUrl;
}

getMainArticle(): Observable<MainArticle> {
  if (environment.useMockData) {
    return of(NEWS_CONSTANTS.MAIN_ARTICLE).pipe(delay(300));
  }
  return this.http.get<MainArticle>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.MAIN_ARTICLE}`);
}
```

## Benefits of This Architecture

✅ **Easy Integration**: Simply uncomment HTTP calls and update endpoints  
✅ **Type Safety**: Full TypeScript interfaces for all data structures  
✅ **Centralized Data**: All constants in one place for easy modification  
✅ **Reusable Service**: Service can be used by other components  
✅ **Error Handling**: Built-in error handling and loading states  
✅ **Mock Support**: Can easily switch between mock and real data  
✅ **Future Ready**: Prepared for advanced features like caching, retry logic, etc.

Your API integration is now ready! Simply update the service methods to call your real endpoints instead of returning mock data.
