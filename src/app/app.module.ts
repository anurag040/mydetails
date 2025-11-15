import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AppComponent } from './app.component';
import { HeaderComponent } from './components/header/header.component';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { FilterPanelComponent } from './components/filter-panel/filter-panel.component';
import { AppGridComponent } from './components/app-grid/app-grid.component';
import { AppTileComponent } from './components/app-tile/app-tile.component';
import { FavoritesRowComponent } from './components/favorites-row/favorites-row.component';
import { RecentlyAccessedRowComponent } from './components/recently-accessed-row/recently-accessed-row.component';
import { VoiceInputComponent } from './components/voice-input/voice-input.component';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    SidebarComponent,
    FilterPanelComponent,
    AppGridComponent,
    AppTileComponent,
    FavoritesRowComponent,
    RecentlyAccessedRowComponent,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    ReactiveFormsModule,
    FormsModule,
    CommonModule,
    VoiceInputComponent,
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
