import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { AnalysisMatrixComponent } from '../analysis-matrix/analysis-matrix.component';
import { DatasetService } from '../../services/dataset.service';
import { DatasetInfo } from '../../models/api.models';

@Component({
  selector: 'app-analysis-metrics',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    AnalysisMatrixComponent
  ],
  templateUrl: './analysis-metrics.component.html',
  styleUrls: ['./analysis-metrics.component.scss']
})
export class AnalysisMetricsComponent implements OnInit {
  currentDataset: DatasetInfo | null = null;

  constructor(private datasetService: DatasetService) { }

  ngOnInit(): void {
    // Subscribe to current dataset
    this.datasetService.currentDataset$.subscribe(dataset => {
      this.currentDataset = dataset;
    });
  }
}
