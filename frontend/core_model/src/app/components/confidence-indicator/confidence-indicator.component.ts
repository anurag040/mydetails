import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatExpansionModule } from '@angular/material/expansion';

export interface ConfidenceData {
  score: number;
  explanation: string;
  factors: string[];
  model_used?: string;
  analysis_type?: string;
}

@Component({
  selector: 'app-confidence-indicator',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatTooltipModule,
    MatProgressBarModule,
    MatExpansionModule
  ],
  templateUrl: './confidence-indicator.component.html',
  styleUrls: ['./confidence-indicator.component.scss']
})
export class ConfidenceIndicatorComponent implements OnInit {
  @Input() confidence: ConfidenceData | null = null;
  @Input() showDetails: boolean = true;
  @Input() compact: boolean = false;

  confidencePercentage: number = 0;
  confidenceLevel: string = '';
  confidenceColor: string = '';
  confidenceIcon: string = '';

  ngOnInit() {
    if (this.confidence) {
      this.calculateConfidenceMetrics();
    }
  }

  private calculateConfidenceMetrics() {
    if (!this.confidence) return;

    this.confidencePercentage = Math.round(this.confidence.score * 100);
    
    // Determine confidence level and styling
    if (this.confidencePercentage >= 90) {
      this.confidenceLevel = 'Excellent';
      this.confidenceColor = '#4caf50';
      this.confidenceIcon = 'verified';
    } else if (this.confidencePercentage >= 80) {
      this.confidenceLevel = 'High';
      this.confidenceColor = '#8bc34a';
      this.confidenceIcon = 'check_circle';
    } else if (this.confidencePercentage >= 70) {
      this.confidenceLevel = 'Good';
      this.confidenceColor = '#ffc107';
      this.confidenceIcon = 'info';
    } else if (this.confidencePercentage >= 60) {
      this.confidenceLevel = 'Moderate';
      this.confidenceColor = '#ff9800';
      this.confidenceIcon = 'warning';
    } else {
      this.confidenceLevel = 'Low';
      this.confidenceColor = '#f44336';
      this.confidenceIcon = 'error';
    }
  }

  getConfidenceDescription(): string {
    switch (this.confidenceLevel) {
      case 'Excellent':
        return 'Very reliable insights with minimal uncertainty';
      case 'High':
        return 'Reliable insights with good statistical foundation';
      case 'Good':
        return 'Generally reliable with some limitations';
      case 'Moderate':
        return 'Reasonable insights but consider data quality';
      case 'Low':
        return 'Limited reliability, review data and methodology';
      default:
        return 'Confidence assessment unavailable';
    }
  }

  getProgressBarColor(): string {
    return this.confidenceColor;
  }
}
