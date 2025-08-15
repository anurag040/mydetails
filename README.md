# Core Model

A full-stack web application for advanced data analysis with AI-powered insights.

## 🚀 Features

- **File Upload**: Support for CSV, Excel, and JSON files
- **Basic Statistics**: Descriptive stats, correlations, distributions, missing data analysis
- **Advanced Statistics**: Regression, clustering, PCA, time series, anomaly detection
- **Talk to My Data**: AI-powered natural language data analysis with ChatGPT-like interface
- **Interactive Visualizations**: Dynamic charts including Bollinger Bands and trend analysis
- **Validation System**: Academic-grade validation of AI analysis results
- **Interactive Dashboard**: Modern Angular UI with Material Design

## 💬 Talk to My Data Feature

### Overview

The "Talk to My Data" feature transforms your dataset into an interactive AI-powered assistant that understands natural language queries and provides comprehensive statistical analysis, insights, and visualizations. Built with a ChatGPT-like interface, this feature makes data analysis accessible to both technical and non-technical users.

### 🎯 Core Capabilities

#### **Statistical Analysis Engine**
- **Interquartile Range (IQR) Analysis**: Complete quartile analysis with beautiful visual summaries
- **Descriptive Statistics**: Mean, median, standard deviation, variance calculations
- **Correlation Analysis**: Identify relationships between variables with strength indicators
- **Missing Data Analysis**: Comprehensive missing value detection and impact assessment
- **Outlier Detection**: IQR-based outlier identification with statistical boundaries
- **Data Quality Assessment**: Complete dataset health check and recommendations

#### **Natural Language Processing**
- **Intelligent Query Understanding**: Recognizes statistical terms, column names, and analysis requests
- **Context-Aware Responses**: Maintains conversation context for follow-up questions
- **Smart Pattern Recognition**: Automatically detects query intent (statistics, visualization, exploration)
- **Flexible Query Formats**: Accepts formal statistical language or casual conversational queries

#### **Advanced Visualizations**
- **Financial Data Visualizations**:
  - **Bollinger Bands**: Technical analysis with moving averages and confidence intervals
  - **Open/Close Trend Analysis**: Multi-series line charts for price movement analysis
  - **Volume Analysis**: Trading volume patterns and correlations
- **Dynamic Chart Generation**: Real-time chart creation based on data characteristics
- **Interactive Chart Controls**: User-selectable chart types and parameters

### 🛠️ Technical Implementation

#### **Backend Architecture**
- **FastAPI Endpoints**: RESTful APIs for chat and visualization requests
- **Pandas Integration**: Advanced data manipulation and statistical calculations
- **NumPy Processing**: High-performance numerical computations
- **Claude 3.7 AI Integration**: Natural language understanding and response generation
- **Modular Analysis Functions**: Specialized functions for different statistical operations

#### **Frontend Features**
- **ChatGPT-like Interface**: Modern chat UI with user and AI message bubbles
- **Real-time Responses**: Instant feedback with loading indicators
- **Chart Integration**: Embedded Chart.js visualizations within chat responses
- **Responsive Design**: Mobile-friendly interface with Material Design components
- **Theme Consistency**: Dark theme with neon accent colors for modern appeal

### 📊 Usage Examples

#### **Basic Queries**
```
✅ "Find IQR for each column"
✅ "Show me basic statistics"
✅ "What's the correlation between Open and Close?"
✅ "Describe my dataset"
✅ "Show me missing data"
```

#### **Advanced Analysis**
```
✅ "Detect outliers in my data"
✅ "Calculate coefficient of variation for all columns"
✅ "What's the typical daily price spread?"
✅ "Show volume trading patterns"
✅ "Analyze price volatility"
```

#### **Visualization Requests**
```
✅ "Create Bollinger Bands for Close price"
✅ "Show Open vs Close trend analysis"
✅ "Generate line chart for price movements"
✅ "Display volume analysis chart"
```

### 🎨 User Interface Features

#### **Chat Interface Components**
- **Message History**: Persistent conversation history with timestamps
- **User Input Field**: Multi-line text input with Enter-to-send functionality
- **Visualization Options**: Quick-select buttons for common chart types
- **Response Formatting**: Rich text responses with markdown support
- **Chart Embedding**: Inline charts within chat responses

#### **Visual Design Elements**
- **Modern Chat Bubbles**: Distinct styling for user vs AI messages
- **Loading Animations**: Elegant loading indicators during processing
- **Chart Containers**: Styled containers with headers and context information
- **Responsive Layout**: Adaptive design for different screen sizes
- **Accessibility Features**: High contrast colors and keyboard navigation

### 🔧 Configuration and Customization

#### **Backend Configuration**
```python
# Statistical Analysis Settings
DEFAULT_IQR_PRECISION = 2  # Decimal places for IQR calculations
CORRELATION_THRESHOLD = 0.7  # Strong correlation threshold
OUTLIER_METHOD = "IQR"  # Outlier detection method
BOLLINGER_DEFAULT_WINDOW = 20  # Default Bollinger Band period
```

#### **Frontend Configuration**
```typescript
// Chat Interface Settings
AUTO_SCROLL = true  // Auto-scroll to latest messages
MESSAGE_TIMESTAMP = true  // Show message timestamps
CHART_ANIMATION = true  // Enable chart animations
MAX_CHART_POINTS = 100  // Limit chart data points for performance
```

### 📈 Advanced Statistical Features

#### **Financial Data Analysis**
- **Price Analysis**: Open, High, Low, Close (OHLC) statistical summaries
- **Volume Analysis**: Trading volume patterns and distribution analysis
- **Volatility Metrics**: Standard deviation, coefficient of variation calculations
- **Trend Analysis**: Moving averages and trend direction identification
- **Technical Indicators**: Bollinger Bands with customizable periods

#### **Data Quality Assessment**
- **Completeness Analysis**: Missing data percentage and patterns
- **Consistency Checks**: Data type validation and format verification
- **Outlier Impact**: Assessment of outlier effects on statistical measures
- **Distribution Analysis**: Normality tests and distribution characteristics

#### **Comparative Analysis**
- **Column Comparisons**: Side-by-side statistical comparisons
- **Stability Rankings**: Identification of most/least volatile variables
- **Correlation Matrices**: Complete correlation analysis with visualization
- **Performance Metrics**: Coefficient of variation and relative stability measures

### 🚀 Performance Optimizations

#### **Data Processing**
- **Efficient Pandas Operations**: Optimized statistical calculations
- **Chunked Processing**: Large dataset handling with memory management
- **Caching Mechanisms**: Statistical result caching for repeated queries
- **Asynchronous Processing**: Non-blocking API responses

#### **Frontend Performance**
- **Chart Data Limiting**: Maximum data points for smooth rendering
- **Lazy Loading**: Progressive loading of chat history
- **Debounced Input**: Optimized user input handling
- **Memory Management**: Efficient chart cleanup and garbage collection

### 🔐 Security and Validation

#### **Data Security**
- **File Upload Validation**: Secure file type and size validation
- **Input Sanitization**: Protection against malicious query inputs
- **API Rate Limiting**: Prevents abuse of statistical analysis endpoints
- **Error Handling**: Comprehensive error management and user feedback

#### **Result Validation**
- **Statistical Accuracy**: Verification of mathematical calculations
- **Range Validation**: Ensuring results are within expected bounds
- **Consistency Checks**: Cross-validation of related statistical measures
- **Academic Standards**: Compliance with statistical best practices

### 💡 Future Enhancements

#### **Planned Features**
- **Machine Learning Integration**: Automated model suggestions and training
- **Export Capabilities**: PDF and Excel report generation
- **Collaborative Features**: Shared analysis sessions and comments
- **Custom Visualizations**: User-defined chart types and layouts
- **API Integration**: Connect to external data sources and APIs

#### **AI Improvements**
- **Advanced NLP**: Better understanding of complex statistical queries
- **Predictive Analytics**: Forecasting and trend prediction capabilities
- **Automated Insights**: Proactive identification of data patterns
- **Multi-language Support**: Support for non-English queries

### 🏆 Best Practices

#### **For Users**
- Start with simple queries like "describe my dataset" to understand your data structure
- Use specific column names in queries for targeted analysis
- Combine statistical queries with visualizations for comprehensive insights
- Review IQR analysis to understand data distribution and outliers

#### **For Developers**
- Extend statistical functions in the backend for domain-specific analysis
- Customize chart types and styling for different data types
- Implement caching for frequently requested statistical calculations
- Add validation for new statistical methods and calculations

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
