import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HeaderComponent } from './components/header/header.component';
import { NewsFeedComponent } from './components/news-feed/news-feed.component';
import { IncidentsComponent } from './components/incidents/incidents.component';
import { PaymentsInsightsComponent } from './components/payments-insights/payments-insights.component';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    NewsFeedComponent,
    IncidentsComponent,
    PaymentsInsightsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
