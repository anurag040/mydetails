export interface NewsItem {
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
}

export interface MainArticle {
  title: string;
  category: string;
  date: string;
  dateFormatted: string;
  author: string;
  views: string;
  shares: string;
  comments: string;
}

export interface ArticleContent {
  excerpt: string;
  full: string;
}

export interface TagCloudItem {
  text: string;
  rotate: number;
  opacity: number;
}

export interface NewsStats {
  totalNewsCount: number;
  todayNewsCount: number;
  trendingCount: number;
}

export interface CategoryColors {
  [key: string]: string;
}

export interface CategoryIcons {
  [key: string]: string;
}
