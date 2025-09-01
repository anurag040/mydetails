import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HeaderComponent } from './components/header/header.component';
import { NewsFeedComponent } from './components/news-feed/news-feed.component';
import { NewsCardComponent } from './components/news-card/news-card.component';
import { IncidentsComponent } from './components/incidents/incidents.component';
import { PaymentsInsightsComponent } from './components/payments-insights/payments-insights.component';
import { PaintSplashPillComponent } from './components/paint-splash-pill/paint-splash-pill.component';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    NewsFeedComponent,
  NewsCardComponent,
  IncidentsComponent,
  PaymentsInsightsComponent,
  PaintSplashPillComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
