import { Injectable } from '@angular/core';
import { Application } from '../types';

@Injectable({
  providedIn: 'root',
})
export class VoiceCommandService {
  constructor() {}

  /**
   * Find the best matching application from the voice input
   * Uses tokenization and fuzzy matching
   */
  findMatchingApplication(voiceInput: string, applications: Application[]): Application | null {
    if (!voiceInput || !voiceInput.trim()) {
      return null;
    }

    const cleanedInput = voiceInput.toLowerCase().trim();
    const tokens = this.tokenize(cleanedInput);

    // Remove common action words
    const actionWords = ['open', 'launch', 'start', 'run', 'show', 'display', 'go', 'to', 'access', 'view', 'check', 'use', 'take', 'me', 'the', 'use'];
    const filteredTokens = tokens.filter(
      (token) => !actionWords.includes(token) && token.length > 1
    );

    // If no meaningful tokens left after filtering, return null
    if (filteredTokens.length === 0) {
      return null;
    }

    // Score each application based on token matching
    let bestMatch: { app: Application; score: number } | null = null;

    for (const app of applications) {
      const score = this.calculateMatchScore(filteredTokens, app);

      if (score > 0 && (!bestMatch || score > bestMatch.score)) {
        bestMatch = { app, score };
      }
    }

    return bestMatch ? bestMatch.app : null;
  }

  /**
   * Tokenize a sentence into individual words
   */
  private tokenize(text: string): string[] {
    return text
      .split(/\s+/)
      .map((token) => token.toLowerCase())
      .filter((token) => token.length > 0);
  }

  /**
   * Calculate matching score between tokens and an application
   * Higher score = better match
   */
  private calculateMatchScore(tokens: string[], app: Application): number {
    let score = 0;

    const appNameLower = app.name.toLowerCase();
    const appCategoryLower = app.category.toLowerCase();
    const appNameWords = appNameLower.split(/\s+/);

    for (const token of tokens) {
      // Exact word match in app name (highest priority)
      if (appNameWords.includes(token)) {
        score += 100;
      } else if (appNameLower.includes(token)) {
        // Substring match in app name
        score += 60;
      }

      // Match in app category
      if (appCategoryLower.includes(token)) {
        score += 15;
      }

      // Fuzzy match for typos (Levenshtein distance)
      const distance = this.levenshteinDistance(token, appNameLower);
      if (distance <= 2) {
        score += Math.max(0, 40 - distance * 10);
      }

      // Check individual words in app name for similarity
      for (const word of appNameWords) {
        if (this.levenshteinDistance(token, word) <= 2) {
          score += Math.max(0, 35 - this.levenshteinDistance(token, word) * 10);
        }
      }
    }

    return score;
  }

  /**
   * Calculate Levenshtein distance for fuzzy matching
   * Handles typos like "trnsaction" vs "transaction"
   */
  private levenshteinDistance(a: string, b: string): number {
    const matrix: number[][] = [];

    for (let i = 0; i <= b.length; i++) {
      matrix[i] = [i];
    }

    for (let j = 0; j <= a.length; j++) {
      matrix[0][j] = j;
    }

    for (let i = 1; i <= b.length; i++) {
      for (let j = 1; j <= a.length; j++) {
        if (b.charAt(i - 1) === a.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }

    return matrix[b.length][a.length];
  }
}
