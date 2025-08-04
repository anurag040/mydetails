import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule } from '@angular/material/dialog';
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatTableModule } from '@angular/material/table';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatMenuModule } from '@angular/material/menu';
import { MatOptionModule } from '@angular/material/core';

import { NgChartsModule } from 'ng2-charts';

import { MetricCardComponent } from './components/metric-card/metric-card.component';
import { DetailModalComponent } from './components/detail-modal/detail-modal.component';

@NgModule({
  declarations: [MetricCardComponent, DetailModalComponent],
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatDialogModule,
    MatTabsModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatTableModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    MatMenuModule,
    MatOptionModule,
    NgChartsModule
  ],
  exports: [
    CommonModule,
    RouterModule,
    FormsModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatDialogModule,
    MatTabsModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatTableModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    MatMenuModule,
    MatOptionModule,
    NgChartsModule,
    MetricCardComponent,
    DetailModalComponent
  ]
})
export class SharedModule {}