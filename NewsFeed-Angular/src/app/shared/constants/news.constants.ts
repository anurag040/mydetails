import { NewsItem, MainArticle, ArticleContent, NewsStats, CategoryColors, CategoryIcons } from '../interfaces/news.interface';

export const NEWS_CONSTANTS = {
  // Main article data
  MAIN_ARTICLE: {
    title: 'Federal Reserve Settlement Activity Remains Stable During Off-Peak Period',
    category: 'Market Intelligence',
    date: '2025-08-30',
    dateFormatted: '30 Aug, 2025',
    author: 'BNY',
    views: '4,127',
    shares: '67',
    comments: '15'
  } as MainArticle,

  // Article content
  ARTICLE_CONTENT: {
    excerpt: `
      <span style="color: #1976d2; font-weight: 600;">Federal Reserve payment activity</span> remained quiet through the recent settlement cycle, with <span style="color: #d32f2f; font-weight: 500;">no transactions reported</span>. This pattern is consistent with the typical slowdown during off-peak periods, when flows across the FED rails tend to subside. <span style="color: #388e3c; font-weight: 600;">SWIFT negative acknowledgments</span> were broadly stable, closely tracking <span style="color: #f57c00; font-weight: 500;">long-term averages</span>.
    `,
    full: `
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
    `
  } as ArticleContent,

  // Recent news data
  RECENT_NEWS: [
    {
      id: 1,
      title: "BNY Mellon Reports Record Growth in Digital Asset Custody Services",
      category: "Business",
      date: "2025-08-30",
      dateFormatted: "30 Aug, 2025",
      author: "BNY Mellon Press",
      views: "3,247",
      shares: "89",
      image: "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=300&h=300&fit=crop",
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
      image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=300&h=300&fit=crop",
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
      image: "https://images.unsplash.com/photo-1568992687947-868a62a9f521?w=300&h=300&fit=crop"
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
      image: "https://images.unsplash.com/photo-1565373679256-3ad7fd8cc62d?w=300&h=300&fit=crop",
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
      image: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=300&h=300&fit=crop"
    }
  ] as NewsItem[],

  // News statistics
  NEWS_STATS: {
    totalNewsCount: 247,
    todayNewsCount: 23,
    trendingCount: 8
  } as NewsStats,

  // Preferred tags for tag cloud
  PREFERRED_TAGS: ['#NACKS_Exceeded', '#P3inProgress', '#SwiftWorkingFine'],

  // BNY-themed images pool
  BNY_IMAGES: [
    "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1568992687947-868a62a9f521?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1565373679256-3ad7fd8cc62d?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
    "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=300&h=300&fit=crop"
  ],

  // Feature images for main content
  FEATURE_IMAGES: [
    "https://lh3.googleusercontent.com/aida-public/AB6AXuDofr0MF66-z8jLOvhIXtjUz7pYLNjq_ukJJN-GtRo_SHVdv89o_v_rHBoguywFjj6CoFmqAVymhLMnpcX7cFDcKK52uoM128vUWDSpsuLsH-5Hq420ZmIVdVSpAlZ4EAqDSX8a3igbbyb6XrqZ2G-AFFp9zHWiNSz7Vyk-48sCFUw6KsRQDRzLNYZHPh2t2vqF-zQYlo9Cyfrrqs0yXrUV4IyEzUHRuCtrlOdG_z7SmIbnPINQVkJ9MZZIRlh5SHOv33xnvrxTCgQ",
    "https://lh3.googleusercontent.com/aida-public/AB6AXuBfz50Upa0idQeescZprb1IJotqIqCpVdMJtP4JMidzebVd2INSROu_rK0_mIxlKHjmfzVN_u3YjjJYU9QymQ62-p9PnxqJebdrqQGVid4kZg09w9eND5DH7-b6zJ9pW--f-iOiQBviKJ9HF2KEn3NvCNr5WALOhSo4Q363dSughiWgltobhoSMys_8gKQaFGHhpWh2iny763Ny_AqUIpdwXVjO9wEO3Q1UZA_xqtx7XJ_JPRUr1x7gBB4kAlmAxeOSwJ2CYulZiIU"
  ],

  // CSS gradients for random colors
  GRADIENTS: [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)'
  ],

  // Category colors mapping
  CATEGORY_COLORS: {
    'Business': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'Security': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'Technology': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'Regulation': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'Finance': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  } as CategoryColors,

  // Category icons mapping
  CATEGORY_ICONS: {
    'Business': '💼',
    'Security': '🛡️',
    'Technology': '🚀',
    'Regulation': '⚖️',
    'Finance': '💰'
  } as CategoryIcons,

  // API endpoint configurations (for future integration)
  API_ENDPOINTS: {
    BASE_URL: '/api/v1',
    NEWS: '/news',
    MAIN_ARTICLE: '/main-article',
    STATS: '/stats',
    REFRESH: '/refresh'
  }
};
