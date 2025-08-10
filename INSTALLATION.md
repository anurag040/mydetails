# Project Generator Component - Installation Guide

## Dependencies Required

Install these packages in your Angular project:

```bash
npm install @angular/material @angular/cdk @angular/animations
npm install @angular/forms @angular/common @angular/common/http
```

## Angular Material Setup

1. **Add Angular Material to your project:**
```bash
ng add @angular/material
```

2. **Import Material Theme** in your `styles.scss`:
```scss
@import '@angular/material/prebuilt-themes/indigo-pink.css';
```

## Component Usage

### **Option A: Standalone Component (Recommended)**
```typescript
import { ProjectGeneratorComponent } from './components/project-generator/project-generator.component';

@Component({
  // ... your component
  imports: [ProjectGeneratorComponent], // Add to imports array
})
export class YourComponent {
  // Use <app-project-generator></app-project-generator> in template
}
```

### **Option B: Module-based Project**
```typescript
// In your module
import { ProjectGeneratorComponent } from './components/project-generator/project-generator.component';

@NgModule({
  declarations: [], // Don't add here for standalone components
  imports: [
    ProjectGeneratorComponent, // Add to imports
    // ... other imports
  ]
})
export class YourModule { }
```

## File Structure in Your Project

```
src/
├── app/
│   ├── components/
│   │   └── project-generator/
│   │       ├── project-generator.component.ts
│   │       ├── project-generator.component.html
│   │       └── project-generator.component.scss
│   └── ...
└── ...
```

## Usage in Template

```html
<app-project-generator></app-project-generator>
```

## Customization

### **Change Component Selector**
If you want a different selector, modify the component:

```typescript
@Component({
  selector: 'your-project-generator', // Change this
  // ... rest of config
})
```

### **Customize Themes**
The component supports light/dark themes. You can modify the SCSS variables:

```scss
.project-generator {
  --bg-primary: #your-color;
  --accent-primary: #your-accent;
  // ... other variables
}
```

### **Backend Integration**
Update the API endpoint in the component:

```typescript
const POST_URL = 'https://your-api.com/project-generator/generate';
```

## API Requirements

Your backend should accept:
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Fields:**
  - `config`: JSON blob with project configuration
  - `prd`: Optional file upload
- **Response:** ZIP file blob

## Configuration Interface

```typescript
interface ProjectConfig {
  springBootVersion: string;
  angularVersion: string;
  groupId: string;
  artifactId: string;
  applicationName: string;
  databases: DbOption[];
  authentication: AuthOption[];
  deployment: DeploymentOption[];
  includeTests: boolean;
  includeSwagger: boolean;
  includeActuator: boolean;
  includeDocker: boolean;
  prdFile: File | null;
}
```
