# Data Analysis Platform

A comprehensive full-stack data analysis platform combining advanced statistical analysis, AI-powered insights, and academic-grade validation systems.

## 🚀 Key Features

### 📊 **Comprehensive Statistical Analysis (17 Analysis Types)**
- **Basic Statistics**: Descriptive stats, correlation analysis, distribution analysis
- **Data Quality Analysis**: Missing data patterns, duplicates detection, type integrity validation
- **Advanced Analytics**: Outlier detection, multicollinearity assessment, dimensionality insights
- **Model Readiness**: Baseline sanity checks, drift analysis, bias/fairness detection
- **Documentation**: Automated data dictionary generation and reproducibility tracking

### 💬 **Talk to My Data - AI-Powered Conversational Interface**
- Natural language data queries with context awareness
- ChatGPT-like interface for statistical analysis
- Real-time visualization generation based on queries
- Intelligent pattern recognition and insights

### 🎯 **Analysis Matrix - Quality Assurance System**
- Real-time tracking of all statistical analyses
- Academic-grade validation with 85%+ accuracy scores
- Four-dimensional quality scoring (Statistical Accuracy, Completeness, Consistency, Efficiency)
- Comprehensive validation reports and recommendations

### 📈 **Advanced Analytics Engine**
- **Machine Learning**: Clustering analysis, PCA, anomaly detection
- **Statistical Modeling**: Regression analysis, time series forecasting
- **Feature Engineering**: AI-generated transformation suggestions
- **Visualization**: Dynamic Chart.js integration with interactive dashboards

## 🏗️ Architecture

### Frontend (Angular 16)
```
frontend/core_model/
├── src/app/components/
│   ├── file-upload/           # Drag-and-drop file upload
│   ├── statistics-dashboard/   # 17 statistical analysis types
│   ├── chat/                  # Talk to Data interface
│   ├── analysis-matrix/       # Quality assurance dashboard
│   └── analysis-metrics/      # Validation metrics display
├── src/app/services/
│   ├── api.service.ts         # Backend API integration
│   ├── dataset.service.ts     # Dataset management
│   └── analysis.service.ts    # Statistical analysis service
└── src/app/models/            # TypeScript interfaces
```

**Technology Stack:**
- Angular 16 with TypeScript 5.0
- Angular Material Design
- Chart.js with ng2-charts for visualizations
- RxJS for reactive programming
- SCSS with modern CSS Grid/Flexbox

### Backend (Python FastAPI)
```
backend/
├── app/api/endpoints/
│   ├── upload.py              # File upload and dataset management
│   ├── statistics.py          # 17 statistical analysis endpoints
│   ├── chat.py                # AI chat system
│   ├── talk_to_data.py        # Natural language data queries
│   ├── analysis_matrix.py     # Quality assurance system
│   ├── clustering.py          # ML clustering analysis
│   └── analysis.py            # Advanced analytics
├── app/services/
│   ├── statistics_calculator.py           # Core statistical engine
│   ├── comprehensive_analysis_validator.py # Validation framework
│   ├── llm_service.py                     # AI/LLM integration
│   ├── analysis_matrix_service.py         # Quality tracking
│   └── file_handler.py                    # Data processing
└── app/models/                # Pydantic models and schemas
```

**Technology Stack:**
- FastAPI with async/await support
- pandas, numpy, scipy for data processing
- scikit-learn, statsmodels for ML/statistics
- OpenAI GPT-4 for AI features
- Pydantic for data validation

## 📋 Prerequisites

- **Node.js**: 18+ (for Angular frontend)
- **Python**: 3.8+ (for FastAPI backend)
- **OpenAI API Key**: Required for AI features

## 🛠️ Quick Start

### 1. Complete Setup (Automated)
```bash
# Clone the repository
git clone <repository-url>
cd angular_core

# Run automated setup
setup.bat
```

### 2. Manual Setup

**Backend Setup:**
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env
# Add your OpenAI API key to .env file
```

**Frontend Setup:**
```bash
cd frontend/core_model

# Install dependencies
npm install
```

### 3. Start the Application

**Option A: Use Batch Files (Windows)**
```bash
# Terminal 1: Start backend
start-backend.bat

# Terminal 2: Start frontend
start-frontend.bat
```

**Option B: Manual Start**
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend/core_model
ng serve --port 4200
```

### 4. Access the Application
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🌐 API Endpoints

### Data Management
```http
POST /api/v1/upload           # Upload dataset (CSV, Excel, JSON)
GET  /api/v1/datasets         # List all datasets
GET  /api/v1/dataset/{id}     # Get dataset information
DELETE /api/v1/dataset/{id}   # Delete dataset
```

### Statistical Analysis
```http
POST /api/v1/statistics/basic     # 17 basic analysis types
POST /api/v1/statistics/advanced  # Advanced ML analysis
GET  /api/v1/statistics/options/basic    # Available basic options
GET  /api/v1/statistics/options/advanced # Available advanced options
GET  /api/v1/statistics/{id}/summary     # Quick dataset summary
```

### AI-Powered Features
```http
POST /api/v1/chat                    # Chat with your data
GET  /api/v1/chat/{id}/history       # Get chat history
POST /api/v1/chat/suggestions        # Get suggested questions
POST /api/v1/talk-to-data           # Natural language queries
```

### Quality Assurance
```http
POST /api/v1/statistics/{id}/validate           # Validate analysis accuracy
GET  /api/v1/statistics/{id}/validation-metrics # Get validation metrics
GET  /api/v1/analysis-matrix/{id}              # Get analysis matrix
POST /api/v1/record-analysis/{id}              # Record analysis event
```

### Advanced Analytics
```http
POST /api/v1/clustering/analyze     # Clustering analysis
POST /api/v1/regression/analyze     # Regression analysis
POST /api/v1/analysis/full          # Comprehensive analysis
POST /api/v1/analysis/insights      # Generate AI insights
```

## 📊 Usage Examples

### Basic Workflow
1. **Upload Data**: Drag and drop CSV/Excel file
2. **Run Analysis**: Select from 17 analysis types
3. **View Results**: Interactive charts and statistical summaries
4. **Chat with Data**: Ask questions in natural language
5. **Validate Quality**: Check analysis accuracy scores

### Talk to Data Examples
```
"What's the correlation between sales and marketing spend?"
"Show me outliers in the revenue column"
"Calculate IQR for all numeric columns"
"Find missing data patterns"
"Generate a summary of my dataset"
```

### Analysis Matrix Features
- Real-time quality scoring for all analyses
- Academic-grade validation (Statistical Accuracy: 35%, Completeness: 25%, Consistency: 25%, Efficiency: 15%)
- Detailed methodology explanations
- Improvement recommendations

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
CORS_ORIGINS=["http://localhost:4200", "http://127.0.0.1:4200"]
```

### Angular Environment
```typescript
// frontend/core_model/src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1'
};
```

## 📈 17 Statistical Analysis Types

### Data Quality Analysis
1. **Missing Data Analysis** - Pattern detection and MCAR testing
2. **Missing Value Report** - Comprehensive imputation strategies  
3. **Duplicates Check** - Full and partial duplicate detection
4. **Type Integrity Validation** - Data consistency validation

### Descriptive Analytics
5. **Descriptive Statistics** - Mean, median, quartiles, distribution metrics
6. **Correlation Analysis** - Pearson/Spearman correlation matrices
7. **Distribution Analysis** - Normality tests, skewness, kurtosis
8. **Univariate Summaries** - Column-specific profiling

### Advanced Analytics
9. **Outlier Detection** - Multi-method ensemble approach
10. **Multicollinearity Assessment** - VIF analysis and recommendations
11. **Dimensionality Insights** - PCA and clustering analysis
12. **Feature Engineering Ideas** - AI-generated transformation suggestions

### Model Readiness
13. **Baseline Model Sanity** - Data readiness assessment
14. **Drift/Stability Analysis** - Statistical stability indicators
15. **Bias/Fairness Flags** - Algorithmic bias detection

### Documentation
16. **Documentation Summary** - Automated data dictionary
17. **Reproducibility Info** - Environment and audit trail

## 🧪 Quality Assurance

### Validation Framework
- **Statistical Accuracy (35%)**: Validates numerical claims against ground truth
- **Analysis Completeness (25%)**: Measures coverage across analysis domains
- **Logical Consistency (25%)**: Contradiction detection and alignment
- **Response Efficiency (15%)**: Performance and user experience metrics

### Quality Scores
- **85%+**: Excellent quality, academic-grade results
- **70-84%**: Good quality, minor improvements suggested
- **<70%**: Needs improvement, detailed recommendations provided

## 🚀 Deployment

### Development
```bash
# Backend development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development server  
ng serve --port 4200
```

### Production Build
```bash
# Frontend production build
cd frontend/core_model
ng build --configuration production

# Backend production server
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs (auto-generated OpenAPI)
- **Project Documentation**: See `PROJECT_DOCUMENTATION.md`
- **Technical Guide**: See `DataAnalysisPlatform_Documentation.md`
- **Architecture Guide**: See `Chapter5_ProjectArtifacts_Comprehensive.md`

## 🆘 Support

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the `/docs` folder for detailed guides
- **API Reference**: Interactive docs at `/docs` endpoint

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏆 Key Differentiators

- **Academic-Grade Validation**: First platform with comprehensive AI analysis validation
- **17 Analysis Types**: Most comprehensive statistical coverage in a single platform
- **Natural Language Interface**: Advanced AI-powered data conversations
- **Real-Time Quality Assurance**: Continuous analysis tracking and validation
- **Enterprise-Ready**: Modern architecture with scalability and security built-in

---

**Built with ❤️ for data scientists, analysts, and researchers**
