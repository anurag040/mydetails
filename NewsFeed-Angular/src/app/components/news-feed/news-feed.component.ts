import { Component, OnInit, AfterViewInit, OnDestroy } from '@angular/core';

export interface NewsItem {
  id: number;
  title: string;
  category: string;
  date: string;
  dateFormatted: string;
  author: string;
  views: string;
  shares: string;
  image: string;
  trending?: boolean;
}

@Component({
  selector: 'app-news-feed',
  templateUrl: './news-feed.component.html',
  styleUrls: ['./news-feed.component.scss']
})
export class NewsFeedComponent implements OnInit, AfterViewInit, OnDestroy {
  
  isLoading: boolean = false;
  currentSlide: number = 0;
  totalNewsCount: number = 247;
  todayNewsCount: number = 23;
  trendingCount: number = 8;
  currentFeatureImage: string = '';
  showFullArticle: boolean = false;
  // Dense hashtag cloud entries rendered over the feature image
  featureTagCloud: Array<{ text: string; rotate: number; opacity: number }> = [];
  // High-priority tags (stable order)
  preferredTags: string[] = ['#NACKS_Exceeded', '#P3inProgress', '#SwiftWorkingFine'];
  
  // Current main article data
  currentMainArticle: any = {
    title: 'Federal Reserve Settlement Activity Remains Stable During Off-Peak Period',
    category: 'Market Intelligence',
    date: '2025-08-30',
    dateFormatted: '30 Aug, 2025',
    author: 'BNY',
    views: '4,127',
    shares: '67',
    comments: '15'
  };
  
  // Full article content
  fullArticleContent: string = `
    <span style="color: #1976d2; font-weight: 600;">Federal Reserve payment activity</span> remained quiet through the recent settlement cycle, with <span style="color: #d32f2f; font-weight: 500;">no transactions reported</span>. This pattern is consistent with the typical slowdown during off-peak periods, when flows across the FED rails tend to subside.

    <span style="color: #388e3c; font-weight: 600;">SWIFT negative acknowledgments</span> were broadly stable, closely tracking <span style="color: #f57c00; font-weight: 500;">long-term averages</span>. The absence of irregular spikes indicated that settlement conditions across the SWIFT network remained <span style="color: #388e3c;">orderly and within expected norms</span>.

    <span style="color: #7b1fa2; font-weight: 600;">CHIPS rejects</span> registered a <span style="color: #f57c00; font-weight: 500;">modest increase</span> compared with recent trends, though volumes stayed comfortably <span style="color: #388e3c;">within tolerance levels</span>. Market participants regarded the movement as routine variability rather than a signal of systemic stress.

    <span style="color: #1976d2; font-weight: 600;">Federal Reserve rejects</span> followed a similar path, recording a <span style="color: #f57c00;">slight uptick</span> but remaining contained. Settlement flows continued <span style="color: #388e3c; font-weight: 500;">without disruption</span>, and <span style="color: #388e3c;">no client impact was reported</span>.

    Deposit and payment activity across both <span style="color: #7b1fa2; font-weight: 500;">CHIPS and FED channels</span> was largely absent during the most recent off-peak window. The quiet session aligned with <span style="color: #1976d2;">seasonal patterns</span> when settlement desks typically experience limited throughput.

    <span style="color: #2e7d32; font-weight: 700; font-size: 1.1em;">Overall, activity across the major payment rails remained stable.</span> Minor fluctuations in rejects were observed, but they fall within <span style="color: #388e3c; font-weight: 500;">normal operating ranges</span> and do not warrant escalation at this stage.

    Looking ahead, market participants expect activity to gradually pick up as we move into the next settlement cycle. The <span style="color: #1976d2; font-weight: 600;">Federal Reserve continues to monitor</span> all payment rail activities closely, ensuring <span style="color: #388e3c; font-weight: 500;">system stability</span> and efficient processing of all transactions.

    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); padding: 16px; border-radius: 8px; margin: 16px 0; border-left: 4px solid #1976d2;">
    <strong style="color: #1976d2; font-size: 1.1em;">Key metrics from the settlement period:</strong><br/>
    • <span style="color: #388e3c; font-weight: 600;">SWIFT acknowledgments: 99.7% success rate</span><br/>
    • <span style="color: #f57c00; font-weight: 600;">CHIPS processing: 0.03% reject rate</span> (within normal parameters)<br/>
    • <span style="color: #1976d2; font-weight: 600;">FED rail throughput: Minimal activity</span> as expected<br/>
    • <span style="color: #388e3c; font-weight: 600;">No system-wide incidents reported</span><br/>
    • <span style="color: #388e3c; font-weight: 600;">All settlement windows completed successfully</span>
    </div>

    <span style="color: #2e7d32; font-weight: 600; font-size: 1.05em;">The stability observed across all major payment infrastructure demonstrates the robustness of the current financial settlement system and the effectiveness of ongoing monitoring protocols.</span>
  `;

  excerptContent: string = `
    <span style="color: #1976d2; font-weight: 600;">Federal Reserve payment activity</span> remained quiet through the recent settlement cycle, with <span style="color: #d32f2f; font-weight: 500;">no transactions reported</span>. This pattern is consistent with the typical slowdown during off-peak periods, when flows across the FED rails tend to subside. <span style="color: #388e3c; font-weight: 600;">SWIFT negative acknowledgments</span> were broadly stable, closely tracking <span style="color: #f57c00; font-weight: 500;">long-term averages</span>.
  `;
  
  recentNews: NewsItem[] = [
    {
      id: 1,
      title: "BNY Mellon Reports Record Growth in Digital Asset Custody Services",
      category: "Business",
      date: "2025-08-30",
      dateFormatted: "30 Aug, 2025",
      author: "BNY Mellon Press",
      views: "3,247",
      shares: "89",
      image: "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=300&h=300&fit=crop", // BNY building
      trending: true
    },
    {
      id: 2,
      title: "Enhanced Security Protocols Launched for Institutional Banking Clients",
      category: "Security",
      date: "2025-08-29",
      dateFormatted: "29 Aug, 2025",
      author: "Security Operations",
      views: "2,834",
      shares: "67",
      image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=300&h=300&fit=crop", // Modern banking
      trending: true
    },
    {
      id: 3,
      title: "Federal Reserve Updates Impact BNY Mellon's Global Investment Services",
      category: "Regulation",
      date: "2025-08-28",
      dateFormatted: "28 Aug, 2025",
      author: "Regulatory Affairs",
      views: "4,156",
      shares: "123",
      image: "https://images.unsplash.com/photo-1568992687947-868a62a9f521?w=300&h=300&fit=crop" // Federal/banking
    },
    {
      id: 4,
      title: "AI-Powered Investment Analytics Platform Processes $2.1T in Assets",
      category: "Technology",
      date: "2025-08-27",
      dateFormatted: "27 Aug, 2025",
      author: "Innovation Team",
      views: "5,431",
      shares: "234",
      image: "https://images.unsplash.com/photo-1565373679256-3ad7fd8cc62d?w=300&h=300&fit=crop", // Financial tech
      trending: true
    },
    {
      id: 5,
      title: "Cross-Border Settlement Network Reduces Transaction Times by 75%",
      category: "Technology",
      date: "2025-08-26",
      dateFormatted: "26 Aug, 2025",
      author: "Global Operations",
      views: "2,923",
      shares: "78",
      image: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=300&h=300&fit=crop" // Banking operations
    }
  ];

  // Enhanced BNY-themed financial images pool
  private bnyImages = [
    "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=300&h=300&fit=crop", // Bank building exterior
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=300&h=300&fit=crop", // Modern office building
    "https://images.unsplash.com/photo-1568992687947-868a62a9f521?w=300&h=300&fit=crop", // Banking interior
    "https://images.unsplash.com/photo-1565373679256-3ad7fd8cc62d?w=300&h=300&fit=crop", // Financial data/charts
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=300&h=300&fit=crop", // Banking/vault
    "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=300&h=300&fit=crop", // Financial district
    "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=300&h=300&fit=crop", // Bank interior/lobby
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300&h=300&fit=crop", // Financial charts/analytics
    "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=300&h=300&fit=crop", // Financial/banking tech
    "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop", // Wall Street/financial district
    "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=300&h=300&fit=crop", // Corporate headquarters
    "https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=300&h=300&fit=crop", // Financial meeting
    "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=300&h=300&fit=crop", // Banking documents
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop", // Financial analysis
    "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=300&h=300&fit=crop"  // Investment services
  ];

  // Custom flower images that change over time
  private featureImages = [
    "https://lh3.googleusercontent.com/aida-public/AB6AXuDofr0MF66-z8jLOvhIXtjUz7pYLNjq_ukJJN-GtRo_SHVdv89o_v_rHBoguywFjj6CoFmqAVymhLMnpcX7cFDcKK52uoM128vUWDSpsuLsH-5Hq420ZmIVdVSpAlZ4EAqDSX8a3igbbyb6XrqZ2G-AFFp9zHWiNSz7Vyk-48sCFUw6KsRQDRzLNYZHPh2t2vqF-zQYlo9Cyfrrqs0yXrUV4IyEzUHRuCtrlOdG_z7SmIbnPINQVkJ9MZZIRlh5SHOv33xnvrxTCgQ", // Custom flower image 1
    "https://lh3.googleusercontent.com/aida-public/AB6AXuBfz50Upa0idQeescZprb1IJotqIqCpVdMJtP4JMidzebVd2INSROu_rK0_mIxlKHjmfzVN_u3YjjJYU9QymQ62-p9PnxqJebdrqQGVid4kZg09w9eND5DH7-b6zJ9pW--f-iOiQBviKJ9HF2KEn3NvCNr5WALOhSo4Q363dSughiWgltobhoSMys_8gKQaFGHhpWh2iny763Ny_AqUIpdwXVjO9wEO3Q1UZA_xqtx7XJ_JPRUr1x7gBB4kAlmAxeOSwJ2CYulZiIU"  // Custom flower image 3
  ];

  private gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)'
  ];

  private categoryColors = {
    'Business': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'Security': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'Technology': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'Regulation': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'Finance': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  };

  private categoryIcons = {
    'Business': '💼',
    'Security': '🛡️',
    'Technology': '🚀',
    'Regulation': '⚖️',
    'Finance': '💰'
  };

  private animationId: number = 0;
  private particles: any[] = [];
  private canvas: HTMLCanvasElement | null = null;
  private ctx: CanvasRenderingContext2D | null = null;

  constructor() { }

  ngOnInit(): void {
    this.initializeFeatureImages();
    this.initializeTagCloud();
    this.startImageRotation();
  }

  ngAfterViewInit(): void {
    this.initParticleSystem();
  }

  ngOnDestroy(): void {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
  }

  private initializeFeatureImages(): void {
    // Set random feature image
    this.currentFeatureImage = this.getRandomFeatureImage();
  }

  private initializeTagCloud(): void {
    // Build initial hashtag cloud
    this.buildTagCloud();
  }

  private startImageRotation(): void {
    // Simulate initial loading
    this.isLoading = true;
    setTimeout(() => {
      this.isLoading = false;
    }, 1000);
  }

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

  // Randomize BNY-themed images
  private randomizeImages(): void {
    // Set random feature image
    this.currentFeatureImage = this.getRandomFeatureImage();
    
    // Set random images for news items
    this.recentNews.forEach(news => {
      news.image = this.getRandomBnyImage();
    });
  // Refresh the tag cloud on image change
  this.buildTagCloud();
  }

  // Get random BNY-themed image
  getRandomBnyImage(): string {
    const randomIndex = Math.floor(Math.random() * this.bnyImages.length);
    return this.bnyImages[randomIndex];
  }

  // Get random feature image
  getRandomFeatureImage(): string {
    const randomIndex = Math.floor(Math.random() * this.featureImages.length);
    return this.featureImages[randomIndex];
  }

  // Slider functionality
  setActiveSlide(index: number): void {
    this.currentSlide = index;
    // Change feature image when clicking slider dots
    this.currentFeatureImage = this.getRandomFeatureImage();
    this.buildTagCloud();
  }

  // TrackBy for hashtag chips by index (fast)
  trackByTagIndex(index: number): number { return index; }

  // Build a visually rich tag cloud from status + domain tags
  private buildTagCloud(): void {
    const fallback = [
      '#Payments', '#Settlement', '#SWIFT', '#Stable', '#Monitoring', '#Compliance'
    ];
    const pool = (this.preferredTags && this.preferredTags.length > 0)
      ? this.preferredTags.slice()
      : fallback.slice();
  // Enforce exactly three tags for compact prominence
  const desired = Math.min(3, pool.length);
  const chosen = pool.slice(0, desired);
    this.featureTagCloud = chosen.map(text => ({
      text,
      rotate: Math.floor(Math.random() * 7) - 3,
      opacity: 0.6 + Math.random() * 0.25
    }));
  }

  // Style helpers
  getRandomGradient(): string {
    return this.gradients[Math.floor(Math.random() * this.gradients.length)];
  }

  getCategoryColor(category: string): string {
    return this.categoryColors[category as keyof typeof this.categoryColors] || this.categoryColors['Business'];
  }

  getCategoryIcon(category: string): string {
    return this.categoryIcons[category as keyof typeof this.categoryIcons] || '📰';
  }

  // Article actions
  readFullArticle(): void {
    this.showFullArticle = !this.showFullArticle;
    console.log('Toggling full article view:', this.showFullArticle);
  }

  getArticleContent(): string {
    return this.showFullArticle ? this.fullArticleContent : this.excerptContent;
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
    
    // Randomize images on refresh
    this.randomizeImages();
    
    // Simulate API call
    setTimeout(() => {
      this.isLoading = false;
      console.log('News refreshed with new BNY images!');
    }, 1500);
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
      comments: '0' // Default value
    };
    
    // Create content based on the news item
    const baseContent = `This is a detailed article about: ${item.title}. Published on ${item.dateFormatted} by ${item.author}. This article has received ${item.views} views and ${item.shares} shares from our readers.`;
    
    // Update excerpt and full content
    this.excerptContent = `<span style="color: #1976d2; font-weight: 600;">${item.title}</span> - ${baseContent.substring(0, 200)}...`;
    this.fullArticleContent = `<span style="color: #1976d2; font-weight: 600; font-size: 1.1em;">${item.title}</span><br/><br/>${baseContent}<br/><br/>
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); padding: 16px; border-radius: 8px; margin: 16px 0; border-left: 4px solid #1976d2;">
    <strong style="color: #1976d2;">Article Details:</strong><br/>
    • <span style="color: #388e3c; font-weight: 600;">Category: ${item.category}</span><br/>
    • <span style="color: #f57c00; font-weight: 600;">Author: ${item.author}</span><br/>
    • <span style="color: #1976d2; font-weight: 600;">Published: ${item.dateFormatted}</span><br/>
    • <span style="color: #388e3c; font-weight: 600;">Views: ${item.views}</span><br/>
    • <span style="color: #7b1fa2; font-weight: 600;">Shares: ${item.shares}</span>
    </div>`;
    
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
}
