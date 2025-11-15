import { Application } from '../types';

export const applications: Application[] = [
  // Operations
  { id: '1', name: 'PayFlow Manager', category: 'Operations', icon: '💰', color: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)', roles: ['Operations', 'Ops Analyst'], isFavorite: true, lastAccessed: new Date('2025-11-15T10:30:00') },
  { id: '2', name: 'Transaction Monitor', category: 'Operations', icon: '📊', color: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)', roles: ['Operations', 'Ops Analyst'], isFavorite: true, lastAccessed: new Date('2025-11-15T09:15:00') },
  { id: '3', name: 'Settlement Hub', category: 'Operations', icon: '🔄', color: 'linear-gradient(135deg, #22c55e 0%, #14b8a6 100%)', roles: ['Operations'], lastAccessed: new Date('2025-11-14T16:45:00') },
  { id: '4', name: 'Batch Processor', category: 'Operations', icon: '⚙️', color: 'linear-gradient(135deg, #f97316 0%, #ef4444 100%)', roles: ['Operations', 'Production Services'] },
  { id: '5', name: 'Reconciliation Tool', category: 'Operations', icon: '✅', color: 'linear-gradient(135deg, #6366f1 0%, #3b82f6 100%)', roles: ['Operations', 'Ops Analyst'], isFavorite: true },
  { id: '6', name: 'Payment Gateway', category: 'Operations', icon: '🚀', color: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', roles: ['Operations', 'Production Services'] },
  { id: '7', name: 'Fraud Detection', category: 'Operations', icon: '🛡️', color: 'linear-gradient(135deg, #ef4444 0%, #ec4899 100%)', roles: ['Operations', 'Ops Analyst'], lastAccessed: new Date('2025-11-15T08:00:00') },
  { id: '8', name: 'Chargeback Manager', category: 'Operations', icon: '⚠️', color: 'linear-gradient(135deg, #eab308 0%, #f97316 100%)', roles: ['Operations'] },

  // Production Services
  { id: '9', name: 'API Gateway', category: 'Production Services', icon: '🔌', color: 'linear-gradient(135deg, #14b8a6 0%, #22c55e 100%)', roles: ['Production Services'], isFavorite: true },
  { id: '10', name: 'Service Monitor', category: 'Production Services', icon: '📡', color: 'linear-gradient(135deg, #3b82f6 0%, #a855f7 100%)', roles: ['Production Services'] },
  { id: '11', name: 'Load Balancer', category: 'Production Services', icon: '⚖️', color: 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)', roles: ['Production Services'] },
  { id: '12', name: 'Database Manager', category: 'Production Services', icon: '💾', color: 'linear-gradient(135deg, #22c55e 0%, #06b6d4 100%)', roles: ['Production Services', 'Operations'] },
  { id: '13', name: 'Log Analyzer', category: 'Production Services', icon: '📝', color: 'linear-gradient(135deg, #f97316 0%, #eab308 100%)', roles: ['Production Services'] },
  { id: '14', name: 'Performance Monitor', category: 'Production Services', icon: '📈', color: 'linear-gradient(135deg, #ec4899 0%, #a855f7 100%)', roles: ['Production Services'] },
  { id: '15', name: 'Deployment Console', category: 'Production Services', icon: '🚢', color: 'linear-gradient(135deg, #06b6d4 0%, #14b8a6 100%)', roles: ['Production Services'] },
  { id: '16', name: 'Health Dashboard', category: 'Production Services', icon: '❤️', color: 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)', roles: ['Production Services', 'Operations'] },

  // Management
  { id: '17', name: 'Executive Dashboard', category: 'Management', icon: '📊', color: 'linear-gradient(135deg, #9333ea 0%, #1e40af 100%)', roles: ['Management'], isFavorite: true },
  { id: '18', name: 'Strategy Planner', category: 'Management', icon: '🎯', color: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)', roles: ['Management'] },
  { id: '19', name: 'Team Analytics', category: 'Management', icon: '👥', color: 'linear-gradient(135deg, #1e40af 0%, #0369a1 100%)', roles: ['Management'] },
  { id: '20', name: 'Budget Tracker', category: 'Management', icon: '💵', color: 'linear-gradient(135deg, #15803d 0%, #0d9488 100%)', roles: ['Management'] },
  { id: '21', name: 'KPI Monitor', category: 'Management', icon: '🎲', color: 'linear-gradient(135deg, #be185d 0%, #be123c 100%)', roles: ['Management'], isFavorite: true },
  { id: '22', name: 'Resource Planner', category: 'Management', icon: '📅', color: 'linear-gradient(135deg, #b45309 0%, #dc2626 100%)', roles: ['Management'] },
  { id: '23', name: 'Risk Dashboard', category: 'Management', icon: '⚡', color: 'linear-gradient(135deg, #ca8a04 0%, #b45309 100%)', roles: ['Management'] },
  { id: '24', name: 'Compliance Portal', category: 'Management', icon: '📋', color: 'linear-gradient(135deg, #0d9488 0%, #0369a1 100%)', roles: ['Management'] },

  // Reporting Analyst
  { id: '25', name: 'Report Builder', category: 'Analytics', icon: '📑', color: 'linear-gradient(135deg, #3b82f6 0%, #4f46e5 100%)', roles: ['Reporting Analyst'], isFavorite: true },
  { id: '26', name: 'Data Warehouse', category: 'Analytics', icon: '🏢', color: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)', roles: ['Reporting Analyst'] },
  { id: '27', name: 'BI Dashboard', category: 'Analytics', icon: '📊', color: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', roles: ['Reporting Analyst', 'Management'] },
  { id: '28', name: 'Metrics Explorer', category: 'Analytics', icon: '🔍', color: 'linear-gradient(135deg, #22c55e 0%, #14b8a6 100%)', roles: ['Reporting Analyst'] },
  { id: '29', name: 'Custom Reports', category: 'Analytics', icon: '📈', color: 'linear-gradient(135deg, #f97316 0%, #ef4444 100%)', roles: ['Reporting Analyst'] },
  { id: '30', name: 'Trend Analyzer', category: 'Analytics', icon: '📉', color: 'linear-gradient(135deg, #ec4899 0%, #a855f7 100%)', roles: ['Reporting Analyst'] },
  { id: '31', name: 'Export Manager', category: 'Analytics', icon: '💼', color: 'linear-gradient(135deg, #6366f1 0%, #3b82f6 100%)', roles: ['Reporting Analyst'] },
  { id: '32', name: 'Schedule Reports', category: 'Analytics', icon: '⏰', color: 'linear-gradient(135deg, #14b8a6 0%, #22c55e 100%)', roles: ['Reporting Analyst'] },

  // Ops Analyst
  { id: '33', name: 'Incident Tracker', category: 'Analytics', icon: '🚨', color: 'linear-gradient(135deg, #ef4444 0%, #ec4899 100%)', roles: ['Ops Analyst'], isFavorite: true },
  { id: '34', name: 'Queue Monitor', category: 'Analytics', icon: '📬', color: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)', roles: ['Ops Analyst'] },
  { id: '35', name: 'Error Logger', category: 'Analytics', icon: '❌', color: 'linear-gradient(135deg, #f97316 0%, #ef4444 100%)', roles: ['Ops Analyst'] },
  { id: '36', name: 'Alert Manager', category: 'Analytics', icon: '🔔', color: 'linear-gradient(135deg, #eab308 0%, #f97316 100%)', roles: ['Ops Analyst'] },
  { id: '37', name: 'Audit Trail', category: 'Analytics', icon: '🔐', color: 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)', roles: ['Ops Analyst', 'Operations'] },
  { id: '38', name: 'Workflow Monitor', category: 'Analytics', icon: '🔄', color: 'linear-gradient(135deg, #22c55e 0%, #14b8a6 100%)', roles: ['Ops Analyst'] },
  { id: '39', name: 'SLA Dashboard', category: 'Analytics', icon: '⏱️', color: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', roles: ['Ops Analyst'] },
  { id: '40', name: 'Quality Metrics', category: 'Analytics', icon: '✨', color: 'linear-gradient(135deg, #ec4899 0%, #a855f7 100%)', roles: ['Ops Analyst'] },

  // Additional Applications (to reach 65-70)
  { id: '41', name: 'Google Analytics', category: 'Third-Party', icon: '🔵', color: 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)', roles: ['Reporting Analyst', 'Management'], url: 'https://analytics.google.com/' },
  { id: '42', name: 'Salesforce', category: 'Third-Party', icon: '☁️', color: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', roles: ['Management', 'Operations'], url: 'https://login.salesforce.com/' },
  { id: '43', name: 'Slack', category: 'Communication', icon: '💬', color: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)', roles: ['All'], url: 'https://slack.com/app' },
  { id: '44', name: 'Jira', category: 'Project Management', icon: '📋', color: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)', roles: ['Operations', 'Production Services'], url: 'https://www.atlassian.com/software/jira' },
  { id: '45', name: 'Confluence', category: 'Documentation', icon: '📚', color: 'linear-gradient(135deg, #6366f1 0%, #3b82f6 100%)', roles: ['All'], url: 'https://www.atlassian.com/software/confluence' },
  { id: '46', name: 'Tableau', category: 'Analytics', icon: '📊', color: 'linear-gradient(135deg, #f97316 0%, #ef4444 100%)', roles: ['Reporting Analyst', 'Management'], url: 'https://www.tableau.com/' },
  { id: '47', name: 'Power BI', category: 'Analytics', icon: '⚡', color: 'linear-gradient(135deg, #eab308 0%, #f97316 100%)', roles: ['Reporting Analyst', 'Management'], url: 'https://app.powerbi.com/' },
  { id: '48', name: 'Zendesk', category: 'Support', icon: '🎧', color: 'linear-gradient(135deg, #22c55e 0%, #14b8a6 100%)', roles: ['Operations'], url: 'https://www.zendesk.com/' },
  { id: '49', name: 'GitHub', category: 'Development', icon: '🐙', color: 'linear-gradient(135deg, #1f2937 0%, #111827 100%)', roles: ['Production Services'], url: 'https://github.com/' },
  { id: '50', name: 'Jenkins', category: 'CI/CD', icon: '🔨', color: 'linear-gradient(135deg, #7c2d12 0%, #9a3412 100%)', roles: ['Production Services'], url: 'https://www.jenkins.io/' },

  { id: '51', name: 'Datadog', category: 'Monitoring', icon: '🐕', color: 'linear-gradient(135deg, #7c3aed 0%, #be185d 100%)', roles: ['Production Services'], url: 'https://app.datadoghq.com/' },
  { id: '52', name: 'New Relic', category: 'Monitoring', icon: '🔬', color: 'linear-gradient(135deg, #14b8a6 0%, #06b6d4 100%)', roles: ['Production Services'], url: 'https://login.newrelic.com/' },
  { id: '53', name: 'Splunk', category: 'Analytics', icon: '🔍', color: 'linear-gradient(135deg, #15803d 0%, #047857 100%)', roles: ['Ops Analyst', 'Production Services'], url: 'https://www.splunk.com/' },
  { id: '54', name: 'PagerDuty', category: 'Incident', icon: '📟', color: 'linear-gradient(135deg, #22c55e 0%, #14b8a6 100%)', roles: ['Ops Analyst', 'Production Services'], url: 'https://www.pagerduty.com/' },
  { id: '55', name: 'Terraform', category: 'Infrastructure', icon: '🏗️', color: 'linear-gradient(135deg, #7c3aed 0%, #6366f1 100%)', roles: ['Production Services'], url: 'https://developer.hashicorp.com/terraform' },
  { id: '56', name: 'Kubernetes', category: 'Orchestration', icon: '☸️', color: 'linear-gradient(135deg, #1e40af 0%, #06b6d4 100%)', roles: ['Production Services'], url: 'https://kubernetes.io/' },
  { id: '57', name: 'Docker', category: 'Containers', icon: '🐋', color: 'linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%)', roles: ['Production Services'], url: 'https://www.docker.com/' },
  { id: '58', name: 'Postman', category: 'API Testing', icon: '📮', color: 'linear-gradient(135deg, #f97316 0%, #ef4444 100%)', roles: ['Production Services', 'Operations'], url: 'https://www.postman.com/' },
  { id: '59', name: 'Grafana', category: 'Visualization', icon: '📈', color: 'linear-gradient(135deg, #b45309 0%, #dc2626 100%)', roles: ['Production Services', 'Ops Analyst'], url: 'https://grafana.com/' },
  { id: '60', name: 'Prometheus', category: 'Monitoring', icon: '🔥', color: 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)', roles: ['Production Services'], url: 'https://prometheus.io/' },

  { id: '61', name: 'Snowflake', category: 'Data Platform', icon: '❄️', color: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', roles: ['Reporting Analyst'], url: 'https://app.snowflake.com/' },
  { id: '62', name: 'MongoDB', category: 'Database', icon: '🍃', color: 'linear-gradient(135deg, #15803d 0%, #065f46 100%)', roles: ['Production Services'], url: 'https://www.mongodb.com/' },
  { id: '63', name: 'Redis', category: 'Cache', icon: '🔴', color: 'linear-gradient(135deg, #7c2d12 0%, #431407 100%)', roles: ['Production Services'], url: 'https://redis.io/' },
  { id: '64', name: 'Elasticsearch', category: 'Search', icon: '🔎', color: 'linear-gradient(135deg, #eab308 0%, #14b8a6 100%)', roles: ['Production Services', 'Ops Analyst'], url: 'https://www.elastic.co/elasticsearch/' },
  { id: '65', name: 'Kafka', category: 'Messaging', icon: '📨', color: 'linear-gradient(135deg, #1f2937 0%, #111827 100%)', roles: ['Production Services'], url: 'https://kafka.apache.org/' },
  { id: '66', name: 'RabbitMQ', category: 'Queue', icon: '🐰', color: 'linear-gradient(135deg, #f97316 0%, #b45309 100%)', roles: ['Production Services'], url: 'https://www.rabbitmq.com/' },
  { id: '67', name: 'Apache Airflow', category: 'Workflow', icon: '🌪️', color: 'linear-gradient(135deg, #14b8a6 0%, #06b6d4 100%)', roles: ['Production Services', 'Ops Analyst'], url: 'https://airflow.apache.org/' },
  { id: '68', name: 'Looker', category: 'Analytics', icon: '👁️', color: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)', roles: ['Reporting Analyst', 'Management'], url: 'https://looker.com/' },
  { id: '69', name: 'Segment', category: 'Data Pipeline', icon: '🔗', color: 'linear-gradient(135deg, #22c55e 0%, #0d9488 100%)', roles: ['Reporting Analyst'], url: 'https://segment.com/' },
  { id: '70', name: 'Auth0', category: 'Security', icon: '🔒', color: 'linear-gradient(135deg, #b45309 0%, #dc2626 100%)', roles: ['Production Services', 'Operations'], url: 'https://auth0.com/' },
];
