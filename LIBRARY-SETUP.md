# Creating an Angular Library for Project Generator

## Step 1: Generate Angular Library

```bash
ng generate library project-generator
```

## Step 2: Copy Component Files
Copy the component files to:
```
projects/project-generator/src/lib/
├── project-generator.component.ts
├── project-generator.component.html
├── project-generator.component.scss
└── public-api.ts
```

## Step 3: Update public-api.ts
```typescript
export * from './lib/project-generator.component';
export * from './lib/project-generator.service'; // if you have services
```

## Step 4: Build Library
```bash
ng build project-generator
```

## Step 5: Publish to NPM
```bash
cd dist/project-generator
npm publish
```

## Usage in Other Projects
```bash
npm install @yourcompany/project-generator
```

```typescript
import { ProjectGeneratorComponent } from '@yourcompany/project-generator';

@Component({
  imports: [ProjectGeneratorComponent]
})
export class AppComponent {}
```
