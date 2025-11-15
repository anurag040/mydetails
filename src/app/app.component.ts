import { Component, OnInit, OnDestroy } from '@angular/core';
import { ApplicationService } from './services/application.service';
import { SpeechRecognitionService } from './services/speech-recognition.service';
import { VoiceCommandService } from './services/voice-command.service';
import { Application, RoleFilter, SortFilter } from './types/index';
import { Subject, Subscription } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit, OnDestroy {
  currentView: string = 'home';
  searchQuery: string = '';
  selectedRole: RoleFilter = 'All';
  selectedSort: SortFilter = 'all';
  allApps: Application[] = [];
  filteredApps: Application[] = [];
  isVoiceActive = false;
  voiceMessage: string = '';
  voiceMessageTimeout: any;
  private voiceSub?: Subscription;

  private destroy$ = new Subject<void>();

  constructor(
    private appService: ApplicationService,
    private speechRecognitionService: SpeechRecognitionService,
    private voiceCommandService: VoiceCommandService
  ) {}

  ngOnInit(): void {
    console.log('AppComponent initializing...');
    this.allApps = this.appService.getApplications();
    console.log('Loaded applications:', this.allApps);
    console.log('Total apps:', this.allApps.length);
    this.filterApps();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.isVoiceActive) {
      this.speechRecognitionService.stopListening();
    }
    if (this.voiceSub) {
      this.voiceSub.unsubscribe();
      this.voiceSub = undefined;
    }
  }

  onSearchChange(query: string): void {
    this.searchQuery = query;
    this.filterApps();
  }

  onVoiceToggle(isActive: boolean): void {
    this.isVoiceActive = isActive;

    if (isActive) {
      // Start listening and auto-launch matching app
      this.speechRecognitionService.startListening();
      // Ensure no duplicate subscriptions
      if (this.voiceSub) {
        this.voiceSub.unsubscribe();
        this.voiceSub = undefined;
      }

      // Use only final transcript to decide actions
      this.voiceSub = this.speechRecognitionService.finalText$
        .subscribe((text) => {
          const finalText = text.trim();
          if (!finalText) {
            return;
          }

          // Try to find matching application using final text
          const matchedApp = this.voiceCommandService.findMatchingApplication(
            finalText,
            this.allApps
          );

          if (matchedApp) {
            console.log('Opening app:', matchedApp.name);
            this.onLaunchApp(matchedApp);
            this.showVoiceMessage(`Opening ${matchedApp.name}...`, 3000);
          } else {
            this.showVoiceMessage('Sorry, I couldn\'t understand that. Please try again.', 4000);
            console.log('No matching app found for:', finalText);
          }

          // Stop listening and clean up after a final result
          this.speechRecognitionService.stopListening();
          this.isVoiceActive = false;
          if (this.voiceSub) {
            this.voiceSub.unsubscribe();
            this.voiceSub = undefined;
          }
        });
    } else {
      // Stop listening
      this.speechRecognitionService.stopListening();
      this.speechRecognitionService.resetText();
      if (this.voiceSub) {
        this.voiceSub.unsubscribe();
        this.voiceSub = undefined;
      }
    }
  }

  private showVoiceMessage(message: string, duration: number = 3000): void {
    this.voiceMessage = message;
    
    // Clear previous timeout if exists
    if (this.voiceMessageTimeout) {
      clearTimeout(this.voiceMessageTimeout);
    }

    // Auto-clear message after duration
    this.voiceMessageTimeout = setTimeout(() => {
      this.voiceMessage = '';
    }, duration);
  }

  onVoiceSearch(query: string): void {
    this.searchQuery = query;
    this.selectedRole = 'All';
    this.selectedSort = 'all';
    this.filterApps();
  }

  onRoleChange(role: RoleFilter): void {
    this.selectedRole = role;
    this.filterApps();
  }

  onSortChange(sort: SortFilter): void {
    this.selectedSort = sort;
    this.filterApps();
  }

  onViewChange(view: string): void {
    this.currentView = view;
  }

  onToggleFavorite(id: string): void {
    this.appService.toggleFavorite(id);
    this.allApps = this.appService.getApplications();
    this.filterApps();
  }

  onLaunchApp(app: Application): void {
    this.appService.updateLastAccessed(app.id);
    this.allApps = this.appService.getApplications();
    console.log('onLaunchApp called with:', app);
    if (app.url) {
      window.open(app.url, '_blank');
    } else {
      window.open(`#/app/${app.id}`, '_blank');
    }
  }

  private filterApps(): void {
    this.filteredApps = this.appService.filterApplications(
      this.allApps,
      this.searchQuery,
      this.selectedRole,
      this.selectedSort
    );
  }

  get showFavoritesRow(): boolean {
    return (
      this.currentView === 'home' &&
      this.selectedSort === 'all' &&
      !this.searchQuery
    );
  }

  get showRecentRow(): boolean {
    return (
      this.currentView === 'home' &&
      this.selectedSort === 'all' &&
      !this.searchQuery
    );
  }

  get favoriteApps(): Application[] {
    return this.allApps.filter((app) => app.isFavorite);
  }

  get recentApps(): Application[] {
    return this.allApps
      .filter((app) => app.lastAccessed)
      .sort(
        (a, b) =>
          (b.lastAccessed?.getTime() || 0) - (a.lastAccessed?.getTime() || 0)
      )
      .slice(0, 6);
  }
}
