import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule } from '@angular/material/dialog';
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { NgChartsModule } from 'ng2-charts';

import { MetricCardComponent } from './components/metric-card/metric-card.component';
import { DetailModalComponent } from './components/detail-modal/detail-modal.component';

@NgModule({
  declarations: [MetricCardComponent, DetailModalComponent],
  imports: [
    CommonModule,
    RouterModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatDialogModule,
    MatTabsModule,
    MatProgressSpinnerModule,
    NgChartsModule
  ],
  exports: [
    CommonModule,
    RouterModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatDialogModule,
    MatTabsModule,
    MatProgressSpinnerModule,
    NgChartsModule,
    MetricCardComponent,
    DetailModalComponent
  ]
})
export class SharedModule {}