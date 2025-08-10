export const PROJECT_TYPES = [
  { id: 'ng-spring', label: 'Angular + Spring Boot' },
  { id: 'ng-fastapi', label: 'Angular + Python (FastAPI)' },
  { id: 'react-node', label: 'React + Node (Express)' },
  { id: 'vue-go', label: 'Vue + Go (Gin)' }
] as const;

export const ANGULAR_VERSIONS = [
  '12', '13', '14', '15', '16', '17', '18'
];
export const SPRING_BOOT_VERSIONS = ['3.1', '3.2', '3.3'];
export const PY_BACKENDS = ['FastAPI', 'Flask'];
export const NODE_BACKENDS = ['Express (JS)', 'Express (TS)', 'NestJS'];
export const GO_BACKENDS = ['Gin', 'Fiber'];

// Java versions for Spring Boot
export const JAVA_VERSIONS = ['17', '21', '22'];

// Python versions
export const PYTHON_VERSIONS = ['3.8', '3.9', '3.10', '3.11', '3.12'];

// Node.js versions  
export const NODE_VERSIONS = ['16.x', '18.x', '20.x', '21.x'];

// Go versions
export const GO_VERSIONS = ['1.19', '1.20', '1.21', '1.22'];

// Build tools
export const BUILD_TOOLS = ['Maven', 'Gradle'];

/** Expanded databases — multi-select */
export const DATABASES = [
  'PostgreSQL',
  'MySQL',
  'MariaDB',
  'SQL Server',
  'Oracle',
  'SQLite',
  'MongoDB',
  'Redis',
  'Elasticsearch',
  'Neo4j',
  'Cassandra',
  'DynamoDB',
  'Snowflake',
  'Vertica',
  'Amazon Redshift',
  'Google BigQuery'
];

export const AUTH_PROVIDERS = [
  'Microsoft Entra ID',
  'Azure AD B2C',
  'Okta',
  'Keycloak',
  'Generic OIDC',
  'None'
];

export const EXTRAS = [
  'Docker',
  'Docker Compose',
  'CI/CD (GitHub Actions)',
  'Unit Tests',
  'ESLint/Prettier'
];

export type Selection = {
  projectType?: string;
  angularVersion?: string;
  uiLibs?: string[];
  backendChoice?: string;
  backendVersionOrType?: string;
  backendTechVersion?: string; // e.g., Python 3.11, Node 18.x, Go 1.21
  buildTool?: string; // Maven, Gradle
  databases?: string[];
  auth?: string[];
  extras?: string[];
  prdFileName?: string;
};