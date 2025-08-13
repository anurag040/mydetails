import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/generator',
    pathMatch: 'full'
  },
  {
    path: 'generator',
    loadComponent: () => import('./components/project-generator/project-generator.component')
      .then(m => m.ProjectGeneratorComponent)
  },
  {
    path: 'status/:sessionId',
    loadComponent: () => import('./components/generation-status/generation-status.component')
      .then(m => m.GenerationStatusComponent)
  },
  {
    path: 'download/:sessionId',
    loadComponent: () => import('./components/download-page/download-page.component')
      .then(m => m.DownloadPageComponent)
  },
  {
    path: '**',
    redirectTo: '/generator'
  }
];
