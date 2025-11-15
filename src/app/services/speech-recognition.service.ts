import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

export type RecognitionStatus = 'idle' | 'listening' | 'error' | 'unsupported';

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
}

interface SpeechRecognitionResult {
  transcript: string;
  isFinal: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class SpeechRecognitionService {
  private recognition: any; // Web Speech API instance
  private isSupported = false;

  private recognizedTextSubject = new BehaviorSubject<string>('');
  private finalTextSubject = new Subject<string>();
  private statusSubject = new BehaviorSubject<RecognitionStatus>('idle');
  private errorMessageSubject = new BehaviorSubject<string>('');
  private isListeningSubject = new BehaviorSubject<boolean>(false);

  public recognizedText$ = this.recognizedTextSubject.asObservable();
  public finalText$ = this.finalTextSubject.asObservable();
  public status$ = this.statusSubject.asObservable();
  public errorMessage$ = this.errorMessageSubject.asObservable();
  public isListening$ = this.isListeningSubject.asObservable();

  constructor() {
    this.initializeRecognition();
  }

  private initializeRecognition(): void {
    // Check for browser support
    const SpeechRecognitionAPI =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognitionAPI) {
      console.warn('Speech Recognition API not supported in this browser');
      this.statusSubject.next('unsupported');
      this.isSupported = false;
      return;
    }

    this.isSupported = true;
    this.recognition = new SpeechRecognitionAPI();

    // Configure recognition
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';

    // Set up event handlers
    this.recognition.onstart = () => {
      this.statusSubject.next('listening');
      this.isListeningSubject.next(true);
      this.errorMessageSubject.next('');
    };

    this.recognition.onresult = (event: SpeechRecognitionEvent) => {
      let transcript = '';
      let isFinalResult = false;

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result: any = event.results[i];
        transcript += result[0].transcript;
        if (result.isFinal) {
          isFinalResult = true;
        }
      }

      // Update the display with current transcript (interim + final)
      this.recognizedTextSubject.next(transcript);

      // Emit only when the result is final
      if (isFinalResult && transcript.trim()) {
        this.finalTextSubject.next(transcript.trim());
      }
    };

    this.recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error:', event.error);
      this.statusSubject.next('error');
      this.isListeningSubject.next(false);

      const errorMessages: { [key: string]: string } = {
        'no-speech': 'No speech detected. Please try again.',
        'audio-capture': 'No microphone found. Ensure that it is connected.',
        'network': 'Network error. Please check your connection.',
        'permission-denied':
          'Microphone permission denied. Please enable it in your browser settings.',
        'not-allowed': 'Permission to use microphone was denied.',
      };

      const userFriendlyMessage =
        errorMessages[event.error] ||
        `An error occurred: ${event.error}. Please try again.`;
      this.errorMessageSubject.next(userFriendlyMessage);
    };

    this.recognition.onend = () => {
      this.statusSubject.next('idle');
      this.isListeningSubject.next(false);
    };
  }

  public startListening(): void {
    if (!this.isSupported) {
      console.warn('Speech Recognition API not supported');
      return;
    }

    // Clear previous text when starting a new recording
    this.recognizedTextSubject.next('');
    this.errorMessageSubject.next('');

    try {
      this.recognition.start();
    } catch (error) {
      console.error('Error starting recognition:', error);
    }
  }

  public stopListening(): void {
    if (!this.isSupported) {
      return;
    }

    try {
      this.recognition.stop();
    } catch (error) {
      console.error('Error stopping recognition:', error);
    }
  }

  public resetText(): void {
    this.recognizedTextSubject.next('');
    this.errorMessageSubject.next('');
  }

  public getIsSupported(): boolean {
    return this.isSupported;
  }

  public getRecognizedText(): string {
    return this.recognizedTextSubject.value;
  }

  public getStatus(): RecognitionStatus {
    return this.statusSubject.value;
  }
}
