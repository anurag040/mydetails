# Architect Forge - Project Generator UI

Angular 16 standalone-component based wizard for configuring a full-stack project blueprint. Provides theme toggling (light/dark), multi-step selection of base stack, databases, authentication providers, and DevOps tooling, plus PRD file upload and a placeholder for backend ZIP generation.

## Features
- Angular 16 + Standalone Components
- Material Design theming with custom neon-inspired dark mode and clean light mode
- Theme toggle persisted in localStorage
- Stepper wizard (Base Stack -> Databases -> Auth & DevOps -> Review)
- Multi-select dropdowns, radio options, chip summaries
- PRD file upload placeholder
- Generate action with payload logged to console (replace with real API call)

## Moving Components Into Another App
`ThemeService` (in `src/app/core/theme.service.ts`) and `WizardComponent` (in `src/app/wizard/wizard.component.ts`) are standalone and can be copied directly. Ensure Material modules imported match your target app and styles in `styles.scss` are merged (CSS variables + global styling).

## Development

Install dependencies and run the dev server:

```powershell
npm install
npm start
```

Open `http://localhost:4200`.

## Replace Generate Placeholder
Inside `wizard.component.ts`, replace `emitGenerate()` logic with an HTTP call to your backend that returns a Blob ZIP. Then trigger a client-side download.

Example snippet:
```ts
this.http.post('/api/generate', payload, { responseType: 'blob' })
  .subscribe(zip => saveAs(zip, 'project-blueprint.zip'));
```

Include `HttpClientModule` if you add that.

## License
MIT
