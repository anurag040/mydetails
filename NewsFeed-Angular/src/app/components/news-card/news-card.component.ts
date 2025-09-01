import { Component, Input } from '@angular/core';

export interface NewsItem {
  id: string;
  title: string;
  excerpt: string;
  content: string;
  imageUrl?: string;
  publishedAt: Date;
  author: string;
  source: string;
  category: string;
  featured: boolean;
  url?: string;
}

export interface IntelligenceTag {
  label: string;
  type: 'critical' | 'warning' | 'info' | 'success';
}

@Component({
  selector: 'app-news-card',
  templateUrl: './news-card.component.html',
  styleUrls: ['./news-card.component.scss']
})
export class NewsCardComponent {
  @Input() newsItem!: NewsItem;
  @Input() isFeatured: boolean = false;
  
  isBookmarked: boolean = false;

  getStatusColor(): 'green' | 'yellow' | 'red' {
    // Determine status based on article characteristics
    if (this.newsItem.featured) return 'green';
    if (this.newsItem.category.toLowerCase().includes('alert') || 
        this.newsItem.title.toLowerCase().includes('alert')) return 'red';
    return 'yellow';
  }

  getStatusText(): string {
    const color = this.getStatusColor();
    switch (color) {
      case 'green': return 'Verified';
      case 'red': return 'Critical';
      case 'yellow': return 'Processing';
      default: return 'Active';
    }
  }

  getIntelligenceTags(): IntelligenceTag[] {
    const tags: IntelligenceTag[] = [];
    
    // Generate intelligence tags based on content analysis
    if (this.newsItem.title.toLowerCase().includes('payment') || 
        this.newsItem.excerpt?.toLowerCase().includes('payment')) {
      tags.push({ label: 'Payment Intelligence', type: 'info' });
    }
    
    if (this.newsItem.title.toLowerCase().includes('fraud') || 
        this.newsItem.excerpt?.toLowerCase().includes('fraud')) {
      tags.push({ label: 'Fraud Detection', type: 'critical' });
    }
    
    if (this.newsItem.title.toLowerCase().includes('trend') || 
        this.newsItem.excerpt?.toLowerCase().includes('trend')) {
      tags.push({ label: 'Market Trend', type: 'success' });
    }
    
    if (this.newsItem.category.toLowerCase().includes('finance') || 
        this.newsItem.category.toLowerCase().includes('fintech')) {
      tags.push({ label: 'FinTech Insight', type: 'warning' });
    }
    
    return tags.slice(0, 2); // Limit to 2 tags for clean UI
  }

  onImageError(event: any): void {
    // Hide image container if image fails to load
    const imageContainer = event.target.closest('.card-image');
    if (imageContainer) {
      imageContainer.style.display = 'none';
    }
  }

  readArticle(): void {
    // Navigate to full article or open in new tab
    if (this.newsItem.url) {
      window.open(this.newsItem.url, '_blank');
    } else {
      // Implement internal article view navigation
      console.log('Reading article:', this.newsItem.title);
    }
  }

  shareArticle(): void {
    // Implement sharing functionality
    if (navigator.share && this.newsItem.url) {
      navigator.share({
        title: this.newsItem.title,
        text: this.newsItem.excerpt,
        url: this.newsItem.url
      }).catch(err => console.error('Error sharing:', err));
    } else {
      // Fallback: copy to clipboard
      const shareText = `${this.newsItem.title}
${this.newsItem.url || ''}`;
      navigator.clipboard.writeText(shareText).then(() => {
        console.log('Article link copied to clipboard');
      });
    }
  }

  toggleBookmark(): void {
    this.isBookmarked = !this.isBookmarked;
    // Implement bookmark persistence logic here
    console.log(`Article ${this.isBookmarked ? 'bookmarked' : 'unbookmarked'}:`, this.newsItem.title);
  }
}
