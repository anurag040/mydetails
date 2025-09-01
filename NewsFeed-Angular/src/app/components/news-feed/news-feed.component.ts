import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject, takeUntil, forkJoin } from 'rxjs';
import { NewsService } from '../../shared/services/news.service';
import { NewsItem, MainArticle, ArticleContent, NewsStats, TagCloudItem } from '../../shared/interfaces/news.interface';

@Component({
  selector: 'app-news-feed',
  templateUrl: './news-feed.component.html'
})
export class NewsFeedComponent implements OnInit, OnDestroy {
  
  private destroy$ = new Subject<void>();
  
  isLoading: boolean = false;
  currentSlide: number = 0;
  totalNewsCount: number = 0;
  todayNewsCount: number = 0;
  trendingCount: number = 0;
  currentFeatureImage: string = '';
  showFullArticle: boolean = false;
  
  // Dense hashtag cloud entries rendered over the feature image
  featureTagCloud: TagCloudItem[] = [];
  
  // Current main article data
  currentMainArticle: MainArticle = {} as MainArticle;
  
  // Article content
  currentArticleContent: ArticleContent = { excerpt: '', full: '' };
  
  // Recent news list
  recentNews: NewsItem[] = [];

  private animationId: number = 0;
  private particles: any[] = [];
  private canvas: HTMLCanvasElement | null = null;
  private ctx: CanvasRenderingContext2D | null = null;

  constructor(private newsService: NewsService) { }

  ngOnInit(): void {
    this.loadAllData();
    this.initializeFeatureImages();
    this.startImageRotation();
  }

  ngAfterViewInit(): void {
    this.initParticleSystem();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
  }

  private loadAllData(): void {
    this.isLoading = true;
    
    // Load all data in parallel using forkJoin
    forkJoin({
      mainArticle: this.newsService.getMainArticle(),
      articleContent: this.newsService.getArticleContent(),
      recentNews: this.newsService.getRecentNews(),
      newsStats: this.newsService.getNewsStats(),
      tagCloud: this.newsService.generateTagCloud()
    }).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (data) => {
        this.currentMainArticle = data.mainArticle;
        this.currentArticleContent = data.articleContent;
        this.recentNews = data.recentNews;
        this.totalNewsCount = data.newsStats.totalNewsCount;
        this.todayNewsCount = data.newsStats.todayNewsCount;
        this.trendingCount = data.newsStats.trendingCount;
        this.featureTagCloud = data.tagCloud;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading news data:', error);
        this.isLoading = false;
      }
    });
  }

  private initializeFeatureImages(): void {
    // Set random feature image
    this.currentFeatureImage = this.newsService.getRandomFeatureImage();
  }

  private initializeTagCloud(): void {
    // Tag cloud is now loaded via service in loadAllData()
  }

  private startImageRotation(): void {
    // Simulate initial loading - this is now handled in loadAllData()
  }

  // Randomize BNY-themed images
  private randomizeImages(): void {
    // Set random feature image
    this.currentFeatureImage = this.newsService.getRandomFeatureImage();
    
    // Set random images for news items
    this.recentNews.forEach(news => {
      news.image = this.newsService.getRandomBnyImage();
    });
    
    // Refresh the tag cloud
    this.newsService.generateTagCloud()
      .pipe(takeUntil(this.destroy$))
      .subscribe(tagCloud => {
        this.featureTagCloud = tagCloud;
      });
  }

  // Get random BNY-themed image
  getRandomBnyImage(): string {
    return this.newsService.getRandomBnyImage();
  }

  // Get random feature image
  getRandomFeatureImage(): string {
    return this.newsService.getRandomFeatureImage();
  }

  // Slider functionality
  setActiveSlide(index: number): void {
    this.currentSlide = index;
    // Change feature image when clicking slider dots
    this.currentFeatureImage = this.newsService.getRandomFeatureImage();
    this.newsService.generateTagCloud()
      .pipe(takeUntil(this.destroy$))
      .subscribe(tagCloud => {
        this.featureTagCloud = tagCloud;
      });
  }

  // TrackBy for hashtag chips by index (fast)
  trackByTagIndex(index: number): number { return index; }

  // Build a visually rich tag cloud from status + domain tags - now handled by service
  private buildTagCloud(): void {
    this.newsService.generateTagCloud()
      .pipe(takeUntil(this.destroy$))
      .subscribe(tagCloud => {
        this.featureTagCloud = tagCloud;
      });
  }

  // Style helpers - delegate to service
  getRandomGradient(): string {
    return this.newsService.getRandomGradient();
  }

  getCategoryColor(category: string): string {
    return this.newsService.getCategoryColor(category);
  }

  getCategoryIcon(category: string): string {
    return this.newsService.getCategoryIcon(category);
  }

  // Article actions
  readFullArticle(): void {
    this.showFullArticle = !this.showFullArticle;
    console.log('Toggling full article view:', this.showFullArticle);
  }

  getArticleContent(): string {
    return this.showFullArticle ? this.currentArticleContent.full : this.currentArticleContent.excerpt;
  }

  getReadButtonText(): string {
    return this.showFullArticle ? 'Show Less' : 'Read Full Article';
  }

  shareArticle(): void {
    console.log('Sharing article...');
    // Implement share functionality
    if (navigator.share) {
      navigator.share({
        title: 'The Payments Industry is Transforming',
        text: 'Check out this article about AI-powered financial intelligence platforms',
        url: window.location.href
      });
    }
  }

  // News list actions
  refreshNews(): void {
    this.isLoading = true;
    console.log('Refreshing news...');
    
    this.newsService.refreshNews()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          if (response.success) {
            // Randomize images on refresh
            this.randomizeImages();
            // Reload all data
            this.loadAllData();
            console.log('News refreshed successfully!');
          }
        },
        error: (error) => {
          console.error('Error refreshing news:', error);
          this.isLoading = false;
        }
      });
  }

  onNewsItemClick(item: NewsItem, event: Event): void {
    event.preventDefault();
    console.log('News item clicked:', item.title);
    // Implement navigation to news article
  }

  // Load news item in main view
  loadNewsInMain(item: NewsItem): void {
    console.log('Loading news in main view:', item.title);
    
    // Update current main article
    this.currentMainArticle = {
      title: item.title,
      category: item.category,
      date: item.date,
      dateFormatted: item.dateFormatted,
      author: item.author,
      views: item.views,
      shares: item.shares,
      comments: item.comments || '0' // Default value
    };
    
    // Create content based on the news item using service
    this.currentArticleContent = this.newsService.createArticleContentForNewsItem(item);
    
    // Reset to excerpt view
    this.showFullArticle = false;
    
    // Randomize feature image
    this.randomizeImages();
    
    // Scroll to top to show the main article
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  viewAllNews(): void {
    console.log('Viewing all news...');
    // Implement navigation to all news page
  }

  // Mobile swipe handlers
  onSwipeLeft(): void {
    console.log('Swiped left');
    // Implement swipe functionality
  }

  onSwipeRight(): void {
    console.log('Swiped right');
    // Implement swipe functionality
  }

  // Utility functions
  trackByNewsId(index: number, item: NewsItem): number {
    return item.id;
  }

  highlightSearchTerm(text: string): string {
    // For now, just return the text as-is
    // In a real app, you'd highlight search terms
    return text;
  }

  // =================== PARTICLE SYSTEM METHODS ===================
  // These methods handle the 3D text animation in the feature area

  private initParticleSystem(): void {
    this.canvas = document.getElementById('threejs-canvas') as HTMLCanvasElement;
    if (!this.canvas) return;

    this.ctx = this.canvas.getContext('2d');
    if (!this.ctx) return;

    // Set canvas size
    const container = this.canvas.parentElement;
    if (container) {
      this.canvas.width = container.offsetWidth;
      this.canvas.height = container.offsetHeight;
    }

    this.createLetterParticles();
    this.animate();
  }

  private createLetterParticles(): void {
    const letters = ['P', 'A', 'Y', 'M', 'E', 'N', 'T', 'S', 'P', 'R', 'I', 'S', 'M'];
    const letterPositions = this.getLetterPositions();
    
    this.particles = [];
    
    letters.forEach((letter, letterIndex) => {
      const letterPos = letterPositions[letterIndex];
      const particleCount = 50; // Reduced from 200 to 50
      
      // Create letter shape using particle positions
      const letterShape = this.getLetterShape(letter);
      
      for (let i = 0; i < particleCount; i++) {
        const shapePoint = letterShape[i % letterShape.length];
        const particle = {
          letter: letter,
          letterIndex: letterIndex,
          originalX: letterPos.x + shapePoint.x,
          originalY: letterPos.y + shapePoint.y,
          x: letterPos.x + shapePoint.x,
          y: letterPos.y + shapePoint.y,
          z: 0,
          vx: 0,
          vy: 0,
          vz: 0,
          size: 2,
          opacity: 0.8,
          phase: Math.random() * Math.PI * 2,
          forming: false,
          formProgress: 1,
          exploding: false,
          explodeTime: 0,
          color: this.getDistinctColor(letterIndex),
          hovered: false
        };
        this.particles.push(particle);
      }
    });
    
    // Add mouse event listeners
    this.addMouseListeners();
  }

  private getLetterPositions(): Array<{x: number, y: number}> {
    if (!this.canvas) return [];
    
    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;
    const letterSpacing = Math.max(35, Math.min(65, this.canvas.width / 12)); // Better spacing that utilizes available width
    
    // Compact vertical spacing for smaller canvas
    const verticalSpacing = this.canvas.height < 200 ? 25 : 35;
    
    // PAYMENTS positions (8 letters)
    const paymentsStart = centerX - (7 * letterSpacing) / 2;
    const paymentsY = centerY - verticalSpacing;
    
    // PRISM positions (5 letters)  
    const prismStart = centerX - (4 * letterSpacing) / 2;
    const prismY = centerY + verticalSpacing;
    
    return [
      // PAYMENTS
      {x: paymentsStart + 0 * letterSpacing, y: paymentsY},
      {x: paymentsStart + 1 * letterSpacing, y: paymentsY},
      {x: paymentsStart + 2 * letterSpacing, y: paymentsY},
      {x: paymentsStart + 3 * letterSpacing, y: paymentsY},
      {x: paymentsStart + 4 * letterSpacing, y: paymentsY},
      {x: paymentsStart + 5 * letterSpacing, y: paymentsY},
      {x: paymentsStart + 6 * letterSpacing, y: paymentsY},
      {x: paymentsStart + 7 * letterSpacing, y: paymentsY},
      // PRISM
      {x: prismStart + 0 * letterSpacing, y: prismY},
      {x: prismStart + 1 * letterSpacing, y: prismY},
      {x: prismStart + 2 * letterSpacing, y: prismY},
      {x: prismStart + 3 * letterSpacing, y: prismY},
      {x: prismStart + 4 * letterSpacing, y: prismY}
    ];
  }

  private getDistinctColor(letterIndex: number): string {
    const colors = [
      '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57',
      '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43',
      '#dda0dd', '#98d8c8', '#f7dc6f'
    ];
    return colors[letterIndex % colors.length];
  }

  private getLetterShape(letter: string): Array<{x: number, y: number}> {
    const points: Array<{x: number, y: number}> = [];
    
    // Create a simple grid of points for each letter - particles will render the actual letter
    for (let i = 0; i < 25; i++) {
      const x = (i % 5) * 4 - 8; // 5x5 grid, centered
      const y = Math.floor(i / 5) * 4 - 8;
      points.push({x, y});
    }
    
    return points;
  }

  private addMouseListeners(): void {
    if (!this.canvas) return;
    
    // Mouse events for desktop
    this.canvas.addEventListener('mousemove', (event) => {
      this.handleInteraction(event.clientX, event.clientY);
    });
    
    // Touch events for mobile
    this.canvas.addEventListener('touchstart', (event) => {
      event.preventDefault();
      const touch = event.touches[0];
      this.handleInteraction(touch.clientX, touch.clientY);
    });
    
    this.canvas.addEventListener('touchmove', (event) => {
      event.preventDefault();
      const touch = event.touches[0];
      this.handleInteraction(touch.clientX, touch.clientY);
    });
  }

  private handleInteraction(clientX: number, clientY: number): void {
    if (!this.canvas) return;
    
    const rect = this.canvas.getBoundingClientRect();
    const interactionX = clientX - rect.left;
    const interactionY = clientY - rect.top;
    
    this.particles.forEach(particle => {
      const distance = Math.sqrt(
        Math.pow(particle.x - interactionX, 2) + 
        Math.pow(particle.y - interactionY, 2)
      );
      
      if (distance < 100) { // Increased radius for mobile
        particle.hovered = true;
        if (!particle.exploding) {
          this.explodeParticle(particle);
        }
      }
    });
  }

  private explodeParticle(particle: any): void {
    particle.exploding = true;
    particle.explodeTime = Date.now();
    particle.vx = (Math.random() - 0.5) * 15;
    particle.vy = (Math.random() - 0.5) * 15;
    particle.vz = (Math.random() - 0.5) * 10;
  }

  private getThemeColor(): string {
    // Get CSS variable for current theme accent color
    const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
    return accent || '#3b82f6';
  }

  private animate(): void {
    if (!this.ctx || !this.canvas) return;

    // Theme-adaptive background
    const bgColor = getComputedStyle(document.documentElement).getPropertyValue('--bg') || '#0a0a0a';
    this.ctx.fillStyle = bgColor;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    const time = Date.now();

    this.particles.forEach(particle => {
      if (particle.exploding) {
        const explodeDuration = time - particle.explodeTime;
        
        if (explodeDuration < 2000) { // Reduced to 2 seconds
          particle.x += particle.vx;
          particle.y += particle.vy;
          particle.vy += 0.2; // Simple gravity
          particle.vx *= 0.98; // Simple drag
          particle.opacity = Math.max(0, 0.8 - (explodeDuration / 2000));
        } else {
          // Quick reset
          particle.exploding = false;
          particle.hovered = false;
          particle.x = particle.originalX;
          particle.y = particle.originalY;
          particle.vx = 0;
          particle.vy = 0;
          particle.opacity = 0.8;
        }
      } else {
        // Simple floating
        particle.x = particle.originalX + Math.sin(time * 0.001 + particle.phase) * 1;
        particle.y = particle.originalY + Math.cos(time * 0.0008 + particle.phase) * 0.5;
      }

      // Simple 2D rendering - no 3D projection
      if (this.ctx && particle.opacity > 0.1) {
        this.ctx.save();
        this.ctx.translate(particle.x, particle.y);
        
        // Draw letter-shaped background using large font
        this.ctx.fillStyle = `${particle.color}${Math.floor(particle.opacity * 255).toString(16).padStart(2, '0')}`;
        this.ctx.font = `bold 32px Arial`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.strokeStyle = `${particle.color}${Math.floor(particle.opacity * 255).toString(16).padStart(2, '0')}`;
        this.ctx.lineWidth = 8;
        
        // Draw letter outline as background shape
        this.ctx.strokeText(particle.letter, 0, 0);
        this.ctx.fillText(particle.letter, 0, 0);
        
        // Draw smaller white letter on top for contrast
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = `bold 20px Arial`;
        this.ctx.shadowColor = 'rgba(0,0,0,0.7)';
        this.ctx.shadowBlur = 3;
        
        this.ctx.fillText(particle.letter, 0, 0);
        this.ctx.restore();
      }
    });

    this.animationId = requestAnimationFrame(() => this.animate());
  }
}
