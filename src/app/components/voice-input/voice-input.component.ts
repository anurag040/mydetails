import { Component, OnInit, OnDestroy, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SpeechRecognitionService, RecognitionStatus } from '../../services/speech-recognition.service';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

type VoiceInputState = 'idle' | 'listening' | 'review' | 'confirmed';

@Component({
  selector: 'app-voice-input',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './voice-input.component.html',
  styleUrls: ['./voice-input.component.scss'],
})
export class VoiceInputComponent implements OnInit, OnDestroy {
  @Output() voiceSearch = new EventEmitter<string>();

  currentState: VoiceInputState = 'idle';
  recognizedText = '';
  confirmedText = '';
  status: RecognitionStatus = 'idle';
  errorMessage = '';
  isListening = false;
  isSupported = false;

  private destroy$ = new Subject<void>();

  constructor(private speechRecognitionService: SpeechRecognitionService) {}

  ngOnInit(): void {
    this.isSupported = this.speechRecognitionService.getIsSupported();

    // Subscribe to recognized text
    this.speechRecognitionService.recognizedText$
      .pipe(takeUntil(this.destroy$))
      .subscribe((text) => {
        this.recognizedText = text;
      });

    // Subscribe to status
    this.speechRecognitionService.status$
      .pipe(takeUntil(this.destroy$))
      .subscribe((status) => {
        this.status = status;
        this.updateStateBasedOnStatus();
      });

    // Subscribe to error messages
    this.speechRecognitionService.errorMessage$
      .pipe(takeUntil(this.destroy$))
      .subscribe((message) => {
        this.errorMessage = message;
      });

    // Subscribe to listening state
    this.speechRecognitionService.isListening$
      .pipe(takeUntil(this.destroy$))
      .subscribe((isListening) => {
        this.isListening = isListening;
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private updateStateBasedOnStatus(): void {
    if (this.status === 'listening') {
      this.currentState = 'listening';
    } else if (this.status === 'idle' && this.recognizedText) {
      this.currentState = 'review';
    } else if (this.status === 'idle' && !this.recognizedText) {
      this.currentState = 'idle';
    }
  }

  onMicButtonClick(): void {
    if (!this.isSupported) {
      return;
    }

    if (this.currentState === 'idle') {
      this.speechRecognitionService.startListening();
    } else if (this.currentState === 'listening') {
      this.speechRecognitionService.stopListening();
    }
  }

  onConfirm(): void {
    this.confirmedText = this.recognizedText;
    this.currentState = 'confirmed';
    console.log('Confirmed text:', this.confirmedText);
    // Emit the voice search query to parent component
    this.voiceSearch.emit(this.confirmedText);
  }

  onRetry(): void {
    this.recognizedText = '';
    this.errorMessage = '';
    this.currentState = 'idle';
    this.speechRecognitionService.resetText();
  }

  onStartNewRecording(): void {
    this.confirmedText = '';
    this.recognizedText = '';
    this.errorMessage = '';
    this.currentState = 'idle';
    this.speechRecognitionService.resetText();
  }

  get statusMessage(): string {
    if (!this.isSupported) {
      return 'Voice input is not supported in this browser.';
    }

    if (this.status === 'error') {
      return this.errorMessage || 'An error occurred. Please try again.';
    }

    switch (this.currentState) {
      case 'idle':
        return 'Click the microphone button and start speaking.';
      case 'listening':
        return 'Listening... Speak now!';
      case 'review':
      case 'confirmed':
        return '';
      default:
        return '';
    }
  }

  get micButtonLabel(): string {
    if (!this.isSupported || this.status === 'error') {
      return '🎤';
    }

    return this.isListening ? '⏹️ Stop' : '🎤 Speak';
  }

  get isMicButtonDisabled(): boolean {
    return !this.isSupported || this.status === 'error' || this.currentState === 'confirmed';
  }

  get isConfirmButtonDisabled(): boolean {
    return !this.recognizedText.trim();
  }
}
