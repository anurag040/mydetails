import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { NewsFeedComponent } from './components/news-feed/news-feed.component';
import { IncidentsComponent } from './components/incidents/incidents.component';
import { PaymentsInsightsComponent } from './components/payments-insights/payments-insights.component';

const routes: Routes = [
  { path: '', component: NewsFeedComponent, pathMatch: 'full' },
  { path: 'incidents', component: IncidentsComponent },
  // Canonical route for Payments Insights
  { path: 'payments-insights', component: PaymentsInsightsComponent },
  // Redirect legacy/split paths to canonical
  { path: 'payments', redirectTo: 'payments-insights', pathMatch: 'full' },
  { path: 'insights', redirectTo: 'payments-insights', pathMatch: 'full' },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
