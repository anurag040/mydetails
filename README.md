# Core Model

A full-stack web application for advanced data analysis with AI-powered insights.

## 🚀 Features

- **File Upload**: Support for CSV, Excel, and JSON files
- **Basic Statistics**: Descriptive stats, correlations, distributions, missing data analysis
- **Advanced Statistics**: Regression, clustering, PCA, time series, anomaly detection
- **Talk to Data**: AI-powered natural language queries using OpenAI GPT
- **Validation System**: Academic-grade validation of AI analysis results
- **Interactive Dashboard**: Modern Angular UI with Material Design

## 🏗️ Architecture

### Frontend (Angular 16)
- **Framework**: Angular 16 with TypeScript
- **UI Library**: Angular Material
- **Charts**: Chart.js with ng2-charts
- **File Upload**: Custom file upload with drag-and-drop
- **State Management**: Services with RxJS

### Backend (Python FastAPI)
- **Framework**: FastAPI with async support
- **Data Processing**: pandas, numpy, scikit-learn
- **AI Integration**: OpenAI GPT-4 for insights
- **Validation**: Custom LLM analysis validation system
- **APIs**: RESTful APIs with automatic OpenAPI documentation

## 📋 Prerequisites

- **Node.js**: 18+ (for Angular)
- **Python**: 3.8+ (for FastAPI backend)
- **OpenAI API Key**: Required for AI features

## 🛠️ Installation

### 1. Clone and Setup

```bash
git clone <repository>
cd core-model
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file and add your OpenAI API key
```

### 3. Frontend Setup

```bash
cd frontend/core_model

# Install dependencies
npm install

# Start development server
ng serve
```

### 4. Start the Application

**Backend (Terminal 1):**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend/core_model
ng serve --port 4200
```

## 🌐 Usage

1. **Open Browser**: Navigate to `http://localhost:4200`
2. **Upload Data**: Use the "Upload Data" tab to upload your dataset
3. **Basic Analysis**: View descriptive statistics and correlations
4. **Advanced Analysis**: Perform ML-based analysis and clustering
5. **Talk to Data**: Ask natural language questions about your data

## 📊 API Endpoints

### Upload
- `POST /api/v1/upload` - Upload dataset
- `GET /api/v1/datasets` - List all datasets
- `GET /api/v1/dataset/{id}` - Get dataset info
- `DELETE /api/v1/dataset/{id}` - Delete dataset

### Statistics
- `POST /api/v1/statistics/basic` - Basic statistical analysis
- `POST /api/v1/statistics/advanced` - Advanced ML analysis
- `GET /api/v1/statistics/options/basic` - Available basic options
- `GET /api/v1/statistics/options/advanced` - Available advanced options

### Analysis
- `POST /api/v1/analysis/full` - Comprehensive LLM analysis
- `POST /api/v1/analysis/insights` - Generate targeted insights
- `GET /api/v1/analysis/{id}/validation` - Get validation metrics

### Chat
- `POST /api/v1/chat` - Chat with your data
- `GET /api/v1/chat/{id}/history` - Get chat history
- `POST /api/v1/chat/suggestions` - Get suggested questions

## 🔧 Configuration

### Environment Variables (.env)

```bash
OPENAI_API_KEY=your_openai_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
CORS_ORIGINS=["http://localhost:4200", "http://127.0.0.1:4200"]
```

### Angular Environment

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1'
};
```

## 📈 Analysis Features

### Basic Statistics
- Descriptive statistics (mean, median, std, etc.)
- Correlation matrix analysis
- Distribution analysis with normality tests
- Missing data patterns and recommendations

### Advanced Statistics
- Linear and polynomial regression
- K-means and hierarchical clustering
- Principal Component Analysis (PCA)
- Time series analysis and forecasting
- Anomaly detection using Isolation Forest

### AI-Powered Insights
- Natural language data exploration
- Pattern discovery and trend analysis
- Business recommendations
- Academic-grade validation metrics

## 🧪 Validation System

The platform includes a sophisticated validation system that measures:

- **Statistical Accuracy**: Correctness of statistical claims
- **Missing Data Accuracy**: Proper handling of data quality issues
- **Insight Relevance**: Contextual appropriateness of insights
- **Completeness**: Coverage of all important aspects
- **Consistency**: Internal logical consistency

Each analysis receives a composite score and detailed justifications.

## 🚀 Deployment

### Docker Deployment (Coming Soon)

```bash
docker-compose up -d
```

### Manual Deployment

1. **Backend**: Deploy FastAPI with gunicorn or uvicorn
2. **Frontend**: Build with `ng build --prod` and serve with nginx
3. **Environment**: Set production environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder for detailed API documentation
- **Issues**: Open an issue on GitHub
- **Email**: contact@dataanalysisplatform.com

## 🏆 Acknowledgments

- OpenAI for GPT-4 API
- Angular and Material Design teams
- FastAPI and Python data science community
- All contributors and testers

---

**Built with ❤️ for data scientists and analysts**
