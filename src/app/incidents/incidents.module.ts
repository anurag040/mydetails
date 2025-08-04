import { NgModule } from '@angular/core';
import { IncidentListComponent } from './incident-list/incident-list.component';
import { IncidentDetailComponent } from './incident-detail/incident-detail.component';
import { SharedModule } from '../shared/shared.module';

@NgModule({
  declarations: [IncidentListComponent, IncidentDetailComponent],
  imports: [SharedModule],
  exports: [IncidentListComponent]
})
export class IncidentsModule {}