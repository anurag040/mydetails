import { NgModule } from '@angular/core';
import { DashboardComponent } from './dashboard/dashboard.component';
import { SwiftDashboardComponent } from './swift-dashboard/swift-dashboard.component';
import { DashboardRoutingModule } from './dashboard-routing.module';
import { SharedModule } from '../shared/shared.module';

@NgModule({
  declarations: [DashboardComponent, SwiftDashboardComponent],
  imports: [SharedModule, DashboardRoutingModule],
  exports: [DashboardComponent, SwiftDashboardComponent]
})
export class DashboardModule {}