import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';
import { SwiftDashboardComponent } from './swift-dashboard/swift-dashboard.component';

const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'swift', component: SwiftDashboardComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DashboardRoutingModule { }
