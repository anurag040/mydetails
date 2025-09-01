import { Component, OnInit } from '@angular/core';

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
}

@Component({
  selector: 'app-news-feed',
  templateUrl: './news-feed.component.html',
  styleUrls: ['./news-feed.component.scss']
})
export class NewsFeedComponent implements OnInit {
  
  recentNews: NewsItem[] = [
    {
      id: 1,
      title: "Be a part of TechCrunch's Digital Startup Alley",
      category: "Business",
      date: "2025-08-30",
      dateFormatted: "30 August, 2025",
      author: "Payments Prism Team",
      views: "1,847",
      shares: "23",
      image: "https://picsum.photos/id/1080/300/300"
    },
    {
      id: 2,
      title: "This startup reworked its privacy-friendly sensors to help battle fraud",
      category: "Security",
      date: "2025-08-29",
      dateFormatted: "29 August, 2025",
      author: "Security Analyst",
      views: "2,334",
      shares: "67",
      image: "https://picsum.photos/id/1011/300/300"
    },
    {
      id: 3,
      title: "New regulations vote to halt facial recognition tech in financial services",
      category: "Regulation",
      date: "2025-08-28",
      dateFormatted: "28 August, 2025",
      author: "Compliance Team",
      views: "3,156",
      shares: "89",
      image: "https://picsum.photos/id/292/300/300"
    },
    {
      id: 4,
      title: "AI-powered payment systems reached 4.1M transactions in first month",
      category: "Technology",
      date: "2025-08-27",
      dateFormatted: "27 August, 2025",
      author: "Tech Reporter",
      views: "4,231",
      shares: "156",
      image: "https://picsum.photos/id/1005/300/300"
    }
  ];

  constructor() { }

  ngOnInit(): void {
  }
}
