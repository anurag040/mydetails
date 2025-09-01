import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, delay, map } from 'rxjs';
import { NewsItem, MainArticle, ArticleContent, NewsStats, TagCloudItem } from '../interfaces/news.interface';
import { NEWS_CONSTANTS } from '../constants/news.constants';

@Injectable({
  providedIn: 'root'
})
export class NewsService {
  private baseUrl = NEWS_CONSTANTS.API_ENDPOINTS.BASE_URL;

  constructor(private http: HttpClient) {}

  /**
   * Get the main featured article
   * TODO: Replace with actual HTTP call to your API
   */
  getMainArticle(): Observable<MainArticle> {
    // Mock API call - replace with actual HTTP request
    // return this.http.get<MainArticle>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.MAIN_ARTICLE}`);
    
    // For now, return mock data with simulated delay
    return of(NEWS_CONSTANTS.MAIN_ARTICLE).pipe(delay(300));
  }

  /**
   * Get article content (excerpt and full)
   * TODO: Replace with actual HTTP call to your API
   */
  getArticleContent(articleId?: number): Observable<ArticleContent> {
    // Mock API call - replace with actual HTTP request
    // return this.http.get<ArticleContent>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.MAIN_ARTICLE}/${articleId || 'current'}/content`);
    
    // For now, return mock data with simulated delay
    return of(NEWS_CONSTANTS.ARTICLE_CONTENT).pipe(delay(200));
  }

  /**
   * Get recent news items
   * TODO: Replace with actual HTTP call to your API
   */
  getRecentNews(): Observable<NewsItem[]> {
    // Mock API call - replace with actual HTTP request
    // return this.http.get<NewsItem[]>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}`);
    
    // For now, return mock data with simulated delay
    return of(NEWS_CONSTANTS.RECENT_NEWS).pipe(delay(500));
  }

  /**
   * Get news statistics
   * TODO: Replace with actual HTTP call to your API
   */
  getNewsStats(): Observable<NewsStats> {
    // Mock API call - replace with actual HTTP request
    // return this.http.get<NewsStats>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.STATS}`);
    
    // For now, return mock data with simulated delay
    return of(NEWS_CONSTANTS.NEWS_STATS).pipe(delay(200));
  }

  /**
   * Refresh news data
   * TODO: Replace with actual HTTP call to your API
   */
  refreshNews(): Observable<{ success: boolean; message: string }> {
    // Mock API call - replace with actual HTTP request
    // return this.http.post<{success: boolean, message: string}>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.REFRESH}`, {});
    
    // For now, simulate refresh with delay
    return of({ success: true, message: 'News refreshed successfully' }).pipe(delay(1500));
  }

  /**
   * Get a specific news item by ID
   * TODO: Replace with actual HTTP call to your API
   */
  getNewsById(id: number): Observable<NewsItem | null> {
    // Mock API call - replace with actual HTTP request
    // return this.http.get<NewsItem>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}/${id}`);
    
    // For now, find in mock data
    const newsItem = NEWS_CONSTANTS.RECENT_NEWS.find(item => item.id === id);
    return of(newsItem || null).pipe(delay(300));
  }

  /**
   * Generate tag cloud for feature article
   * TODO: This could be enhanced to call an API for dynamic tags
   */
  generateTagCloud(): Observable<TagCloudItem[]> {
    const fallback = ['#Payments', '#Settlement', '#SWIFT', '#Stable', '#Monitoring', '#Compliance'];
    const pool = NEWS_CONSTANTS.PREFERRED_TAGS.length > 0 
      ? NEWS_CONSTANTS.PREFERRED_TAGS.slice() 
      : fallback.slice();
    
    // Enforce exactly three tags for compact prominence
    const desired = Math.min(3, pool.length);
    const chosen = pool.slice(0, desired);
    
    const tagCloud = chosen.map(text => ({
      text,
      rotate: Math.floor(Math.random() * 7) - 3,
      opacity: 0.6 + Math.random() * 0.25
    }));

    return of(tagCloud).pipe(delay(100));
  }

  /**
   * Get random BNY-themed image
   */
  getRandomBnyImage(): string {
    const randomIndex = Math.floor(Math.random() * NEWS_CONSTANTS.BNY_IMAGES.length);
    return NEWS_CONSTANTS.BNY_IMAGES[randomIndex];
  }

  /**
   * Get random feature image
   */
  getRandomFeatureImage(): string {
    const randomIndex = Math.floor(Math.random() * NEWS_CONSTANTS.FEATURE_IMAGES.length);
    return NEWS_CONSTANTS.FEATURE_IMAGES[randomIndex];
  }

  /**
   * Get random gradient
   */
  getRandomGradient(): string {
    return NEWS_CONSTANTS.GRADIENTS[Math.floor(Math.random() * NEWS_CONSTANTS.GRADIENTS.length)];
  }

  /**
   * Get category color
   */
  getCategoryColor(category: string): string {
    return NEWS_CONSTANTS.CATEGORY_COLORS[category] || NEWS_CONSTANTS.CATEGORY_COLORS['Business'];
  }

  /**
   * Get category icon
   */
  getCategoryIcon(category: string): string {
    return NEWS_CONSTANTS.CATEGORY_ICONS[category] || '📰';
  }

  /**
   * Create article content for a news item when loaded in main view
   */
  createArticleContentForNewsItem(item: NewsItem): ArticleContent {
    const baseContent = `This is a detailed article about: ${item.title}. Published on ${item.dateFormatted} by ${item.author}. This article has received ${item.views} views and ${item.shares} shares from our readers.`;
    
    return {
      excerpt: `<span style="color: #1976d2; font-weight: 600;">${item.title}</span> - ${baseContent.substring(0, 200)}...`,
      full: `<span style="color: #1976d2; font-weight: 600; font-size: 1.1em;">${item.title}</span><br/><br/>${baseContent}<br/><br/>
      <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); padding: 16px; border-radius: 8px; margin: 16px 0; border-left: 4px solid #1976d2;">
      <strong style="color: #1976d2;">Article Details:</strong><br/>
      • <span style="color: #388e3c; font-weight: 600;">Category: ${item.category}</span><br/>
      • <span style="color: #f57c00; font-weight: 600;">Author: ${item.author}</span><br/>
      • <span style="color: #1976d2; font-weight: 600;">Published: ${item.dateFormatted}</span><br/>
      • <span style="color: #388e3c; font-weight: 600;">Views: ${item.views}</span><br/>
      • <span style="color: #7b1fa2; font-weight: 600;">Shares: ${item.shares}</span>
      </div>`
    };
  }

  // TODO: Add these methods when you integrate with your real API
  
  /**
   * Search news articles
   * TODO: Implement when you have backend API
   */
  // searchNews(query: string): Observable<NewsItem[]> {
  //   return this.http.get<NewsItem[]>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}/search?q=${query}`);
  // }

  /**
   * Get news by category
   * TODO: Implement when you have backend API
   */
  // getNewsByCategory(category: string): Observable<NewsItem[]> {
  //   return this.http.get<NewsItem[]>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}/category/${category}`);
  // }

  /**
   * Get trending news
   * TODO: Implement when you have backend API
   */
  // getTrendingNews(): Observable<NewsItem[]> {
  //   return this.http.get<NewsItem[]>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}/trending`);
  // }

  /**
   * Create new news article
   * TODO: Implement when you have backend API
   */
  // createNews(news: Partial<NewsItem>): Observable<NewsItem> {
  //   return this.http.post<NewsItem>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}`, news);
  // }

  /**
   * Update news article
   * TODO: Implement when you have backend API
   */
  // updateNews(id: number, news: Partial<NewsItem>): Observable<NewsItem> {
  //   return this.http.put<NewsItem>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}/${id}`, news);
  // }

  /**
   * Delete news article
   * TODO: Implement when you have backend API
   */
  // deleteNews(id: number): Observable<{success: boolean}> {
  //   return this.http.delete<{success: boolean}>(`${this.baseUrl}${NEWS_CONSTANTS.API_ENDPOINTS.NEWS}/${id}`);
  // }
}
