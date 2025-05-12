import { Component, OnInit, ViewChildren, QueryList, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Video } from '../../services/video.service';

@Component({
  selector: 'app-video-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './video-list.component.html',
  styleUrls: ['./video-list.component.scss'],
})
export class VideoListComponent implements OnInit {
  @ViewChildren('videoPreview') videoPreviews!: QueryList<ElementRef<HTMLVideoElement>>;
  videos: Video[] = [];
  activePreviews: boolean[] = [];
  searchQuery: string = '';

  constructor(private router: Router) {}

  ngOnInit(): void {
    this.loadVideosFromDirectory();
  }

  async loadVideosFromDirectory() {
    try {
      // This is a placeholder - in a real Electron app you would use the filesystem API
      // For a web app, you would need a backend service to serve these files
      const videoFiles = await this.getVideoFiles();
      
      this.videos = videoFiles.map((file, index) => ({
        id: index,
        title: file.name.replace(/\.[^/.]+$/, ""), // Remove file extension
        fileUrl: file.url,
        channel: 'My Screen Recordings',
        channelIcon: 'EFM.png',
        views: Math.floor(Math.random() * 10000000),
        uploadTime: this.randomUploadTime(),
        duration: this.randomDuration(),
        likes: Math.floor(Math.random() * 10000), // Mock likes count
        comments: [] // Initialize with an empty array for comments
      }));
      
      this.activePreviews = new Array(this.videos.length).fill(false);
    } catch (error) {
      console.error('Error loading videos:', error);
    }
  }

  // This is a mock implementation - you'll need to replace it with actual file access
  private async getVideoFiles(): Promise<{name: string, url: string}[]> {
    // In a real Electron app, you would use:
    // const files = await window.electronAPI.readDirectory('C:/Users/Anurag/Videos/Screen Recordings');
    
    // For demonstration, we'll return mock data
    return [
      { name: 'Recording1.mp4', url: 'Screen Recording 2025-02-15 201140.mp4' },
      { name: 'Recording2.mp4', url: 'Screen Recording 2025-02-16 150055.mp4' },
      // Add more files as needed
    ];
  }

  // Keep all other existing methods the same...
  filteredVideos(): Video[] {
    return this.videos.filter(video =>
      video.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
      (video.channel || '').toLowerCase().includes(this.searchQuery.toLowerCase())
    );
  }

  startPreview(index: number) {
    const videoElements = this.videoPreviews.toArray();
    if (videoElements[index]) {
      const videoEl = videoElements[index].nativeElement;
      videoEl.currentTime = 0;
      videoEl.play()
        .then(() => this.activePreviews[index] = true)
        .catch(err => {
          console.error('Error playing video preview:', err);
          this.activePreviews[index] = false;
        });
    }
  }

  stopPreview(index: number) {
    const videoElements = this.videoPreviews.toArray();
    if (videoElements[index]) {
      videoElements[index].nativeElement.pause();
      this.activePreviews[index] = false;
    }
  }

  play(id: number) {
    this.router.navigate(['/videos', id]);
  }

  openSettings(video: Video) {
    alert(`Settings for video: ${video.title}`);
  }

  getVideoPoster(video: Video): string {
    return '';
  }

  getChannelIcon(video: Video): string {
    return video.channelIcon || 'EFM.png';
  }

  getChannelName(video: Video): string {
    return video.channel || 'EFM Community';
  }

  getViewCount(video: Video): string {
    const views = video.views || Math.floor(Math.random() * 10000000);
    return this.formatViews(views);
  }

  getUploadTime(video: Video): string {
    return video.uploadTime || this.randomUploadTime();
  }

  getDuration(video: Video): string {
    return video.duration || this.randomDuration();
  }

  private formatViews(views: number): string {
    if (views >= 1_000_000) return `${(views / 1_000_000).toFixed(1)}M`;
    if (views >= 1_000) return `${(views / 1_000).toFixed(1)}K`;
    return views.toString();
  }

  private randomUploadTime(): string {
    const times = ['1 hour', '2 days', '1 week', '3 months', '1 year'];
    return times[Math.floor(Math.random() * times.length)];
  }

  private randomDuration(): string {
    const minutes = Math.floor(Math.random() * 60) + 1;
    const seconds = Math.floor(Math.random() * 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }
}