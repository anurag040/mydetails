import { Component } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { ThemeToggleComponent } from './components/theme-toggle/theme-toggle.component';
import { ProjectGeneratorComponent } from './components/project-generator/project-generator.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MatToolbarModule, MatIconModule, ThemeToggleComponent, ProjectGeneratorComponent],
  templateUrl: './app.component.html'
})
export class AppComponent {}
