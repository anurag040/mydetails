# Project Forge (Angular 16)

A polished, standalone Angular 16 front-end that acts as a "project of projects": choose stack, DBs, auth, extras, optional PRD upload, and generate (placeholder).

## Quick start
```bash
npm i
npm start   # runs ng serve
```
Then open http://localhost:4200

## Notes
- Theme toggle persists via localStorage.
- Final "Generate" button shows a snackbar and is ready to wire to your ZIP API (see commented code in `project-generator.component.ts`).
