# AI-Driven Project Generator

A sophisticated project generator that converts Product Requirements Documents (PRD) into functional code using Spring AI multi-agent orchestration.

## 🏗️ Architecture

### Frontend (Angular)
- Interactive stepper UI for configuration
- PRD file upload (PDF/TXT)
- Real-time generation progress
- ZIP file download for generated projects

### Backend (Spring Boot + Spring AI)
- Multi-agent orchestration system
- PRD analysis and blueprint generation
- Autonomous code generation
- Project structure creation and ZIP packaging

## 🤖 AI Agents

1. **PRD Analyst Agent** - Parses and analyzes requirements
2. **System Architect Agent** - Designs system architecture
3. **Frontend Code Agent** - Generates Angular components
4. **Backend Code Agent** - Generates Spring Boot services
5. **Database Agent** - Generates schema and repositories
6. **DevOps Agent** - Generates deployment configurations
7. **QA Agent** - Generates tests
8. **Integration Agent** - Combines and validates components

## 📁 Project Structure

```
ai-project-generator/
├── frontend/                 # Angular application
├── backend/                  # Spring Boot application
├── shared/                   # Shared utilities and types
└── docs/                     # Documentation
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Java 17+
- OpenAI API key

### Setup
1. Clone the repository
2. Configure OpenAI API key
3. Start backend: `cd backend && ./mvnw spring-boot:run`
4. Start frontend: `cd frontend && npm start`

## 🎯 Output
- **Frontend ZIP**: Complete Angular project in `src/app/` structure
- **Backend ZIP**: Complete Spring Boot project in `src/main/` structure
