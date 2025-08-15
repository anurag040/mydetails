from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from app.services.file_handler import FileHandler
from app.services.llm_service import LLMService

router = APIRouter()
file_handler = FileHandler()
llm_service = LLMService()

class TalkToDataRequest(BaseModel):
    dataset_id: str
    query: str
    plot_type: Optional[str] = None
    column: Optional[str] = None
    window: Optional[int] = 20

class TalkToDataResponse(BaseModel):
    answer: str
    plot_data: Optional[Dict[str, Any]] = None

@router.post("/talk-to-data", response_model=TalkToDataResponse)
async def talk_to_data(request: TalkToDataRequest):
    df = await file_handler.load_dataset(request.dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    query = request.query.strip()
    
    try:
        # Use AI-powered generic analysis
        answer = await analyze_data_with_ai(df, query)
        return TalkToDataResponse(answer=answer)
    
    except Exception as e:
        print(f"❌ DEBUG: Error in talk_to_data: {str(e)}")
        return TalkToDataResponse(answer=f"❌ Error processing your question: {str(e)}")

async def analyze_data_with_ai(df: pd.DataFrame, query: str) -> str:
    """Generic AI-powered data analysis that can handle any question"""
    
    # Create dataset summary for context
    summary = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
        "sample_data": df.head(3).to_dict('records') if len(df) > 0 else []
    }
    
    # Check for specific statistical operations and handle them directly
    query_lower = query.lower()
    
    # Handle IQR requests
    if 'iqr' in query_lower or 'interquartile' in query_lower:
        return calculate_iqr_for_columns(df, query)
    
    # Handle other statistical operations
    if any(stat in query_lower for stat in ['mean', 'median', 'std', 'variance', 'correlation', 'min', 'max']):
        return calculate_statistics(df, query)
    
    # Handle data description requests
    if any(word in query_lower for word in ['describe', 'summary', 'overview', 'analyze']):
        return generate_data_description(df, query)
    
    # Handle missing data queries
    if 'missing' in query_lower or 'null' in query_lower or 'nan' in query_lower:
        return analyze_missing_data(df, query)
    
    # Handle outlier detection
    if 'outlier' in query_lower:
        return detect_outliers(df, query)
    
    # For other queries, try to create a general analysis
    return await create_ai_response(df, query, summary)

def calculate_iqr_for_columns(df: pd.DataFrame, query: str) -> str:
    """Calculate IQR for numeric columns"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        return "❌ No numeric columns found for IQR calculation."
    
    results = []
    results.append("📊 **Interquartile Range (IQR) Analysis:**\n")
    
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        median = df[col].median()
        
        results.append(f"**{col}:**")
        results.append(f"  • Q1 (25th percentile): {q1:.2f}")
        results.append(f"  • Q3 (75th percentile): {q3:.2f}")
        results.append(f"  • IQR: {iqr:.2f}")
        results.append(f"  • Median: {median:.2f}")
        results.append("")
    
    # Add interpretation
    results.append("💡 **What IQR means:**")
    results.append("- IQR shows the range where the middle 50% of your data falls")
    results.append("- Lower IQR = less variation, Higher IQR = more variation")
    results.append("- Values beyond Q1 - 1.5×IQR or Q3 + 1.5×IQR are potential outliers")
    
    return "\n".join(results)

def calculate_statistics(df: pd.DataFrame, query: str) -> str:
    """Calculate various statistics based on query"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        return "❌ No numeric columns found for statistical analysis."
    
    query_lower = query.lower()
    results = []
    
    if 'correlation' in query_lower:
        results.append("📈 **Correlation Analysis:**\n")
        corr_matrix = df[numeric_cols].corr()
        
        # Find strong correlations (> 0.7 or < -0.7)
        strong_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_corrs.append(f"{corr_matrix.columns[i]} ↔ {corr_matrix.columns[j]}: {corr_val:.3f}")
        
        if strong_corrs:
            results.append("**Strong correlations found:**")
            for corr in strong_corrs:
                results.append(f"  • {corr}")
        else:
            results.append("No strong correlations (>0.7) found between columns.")
        
        return "\n".join(results)
    
    # General statistics
    results.append("📊 **Statistical Summary:**\n")
    for col in numeric_cols:
        stats = df[col].describe()
        results.append(f"**{col}:**")
        results.append(f"  • Mean: {stats['mean']:.2f}")
        results.append(f"  • Median: {df[col].median():.2f}")
        results.append(f"  • Std Dev: {stats['std']:.2f}")
        results.append(f"  • Min: {stats['min']:.2f}")
        results.append(f"  • Max: {stats['max']:.2f}")
        results.append("")
    
    return "\n".join(results)

def generate_data_description(df: pd.DataFrame, query: str) -> str:
    """Generate a comprehensive data description"""
    rows, cols = df.shape
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    results = []
    results.append("📋 **Dataset Overview:**\n")
    results.append(f"• **Size:** {rows:,} rows × {cols} columns")
    results.append(f"• **Numeric columns:** {len(numeric_cols)} ({', '.join(numeric_cols[:3])}{'...' if len(numeric_cols) > 3 else ''})")
    results.append(f"• **Categorical columns:** {len(categorical_cols)} ({', '.join(categorical_cols[:3])}{'...' if len(categorical_cols) > 3 else ''})")
    results.append("")
    
    # Missing data analysis
    missing_data = df.isnull().sum()
    if missing_data.any():
        results.append("⚠️ **Missing Data:**")
        for col, missing in missing_data[missing_data > 0].items():
            percentage = (missing / len(df)) * 100
            results.append(f"  • {col}: {missing} missing ({percentage:.1f}%)")
        results.append("")
    
    # Data types
    results.append("🔢 **Column Details:**")
    for col in df.columns:
        dtype = str(df[col].dtype)
        unique_vals = df[col].nunique()
        results.append(f"  • **{col}:** {dtype}, {unique_vals} unique values")
    
    return "\n".join(results)

def analyze_missing_data(df: pd.DataFrame, query: str) -> str:
    """Analyze missing data in the dataset"""
    missing_data = df.isnull().sum()
    total_missing = missing_data.sum()
    
    if total_missing == 0:
        return "✅ **No missing data found!** Your dataset is complete."
    
    results = []
    results.append(f"⚠️ **Missing Data Analysis:**\n")
    results.append(f"• **Total missing values:** {total_missing}")
    results.append(f"• **Percentage of dataset:** {(total_missing / (len(df) * len(df.columns))) * 100:.1f}%")
    results.append("")
    
    results.append("**Missing values by column:**")
    for col, missing in missing_data[missing_data > 0].items():
        percentage = (missing / len(df)) * 100
        results.append(f"  • **{col}:** {missing} missing ({percentage:.1f}%)")
    
    return "\n".join(results)

def detect_outliers(df: pd.DataFrame, query: str) -> str:
    """Detect outliers using IQR method"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        return "❌ No numeric columns found for outlier detection."
    
    results = []
    results.append("🔍 **Outlier Detection (IQR Method):**\n")
    
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outlier_count = len(outliers)
        
        results.append(f"**{col}:**")
        results.append(f"  • Range for normal values: {lower_bound:.2f} to {upper_bound:.2f}")
        results.append(f"  • Outliers found: {outlier_count}")
        if outlier_count > 0:
            percentage = (outlier_count / len(df)) * 100
            results.append(f"  • Percentage of data: {percentage:.1f}%")
        results.append("")
    
    return "\n".join(results)

async def create_ai_response(df: pd.DataFrame, query: str, summary: dict) -> str:
    """Use AI to create response for complex queries"""
    # For now, provide a helpful fallback
    return f"""🤖 **I can help you analyze your data!** Here are some things you can ask me:

📊 **Statistical Analysis:**
- "Find IQR for each column" ✅
- "Calculate correlation between columns"
- "Show me basic statistics"
- "What's the mean and median?"
- "Detect outliers in my data"

📋 **Data Exploration:**
- "Describe my dataset"
- "Show me missing data"
- "What are the data types?"

📈 **Visualizations:**
- Use the chart buttons above for Bollinger Bands and Line Trends

**Your dataset:** {summary['shape'][0]} rows × {summary['shape'][1]} columns
**Columns:** {', '.join(summary['columns'][:5])}{'...' if len(summary['columns']) > 5 else ''}

💡 **Try asking:** "Find IQR for each column" or "Show me correlations"!"""

# Keep the existing plot functionality
@router.post("/talk-to-data/plot", response_model=TalkToDataResponse)
async def talk_to_data_plot(request: TalkToDataRequest):
    print(f"🔍 DEBUG: Received plot request - plot_type: {request.plot_type}, dataset_id: {request.dataset_id}")
    print(f"🔍 DEBUG: Request details - column: {request.column}, window: {request.window}")
    
    try:
        df = await file_handler.load_dataset(request.dataset_id)
        if df is None:
            print("❌ DEBUG: Dataset not found")
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        print(f"📊 DEBUG: Dataset loaded - shape: {df.shape}, columns: {list(df.columns)}")
        
        if request.plot_type == "bollinger_band":
            print("📈 DEBUG: Processing Bollinger Band request")
            
            # Find appropriate column for Bollinger Bands
            if request.column and request.column in df.columns:
                col = request.column
                print(f"🎯 DEBUG: Using specified column: {col}")
            else:
                # Find first numeric column or first close/open column
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                close_cols = [c for c in df.columns if 'close' in c.lower()]
                open_cols = [c for c in df.columns if 'open' in c.lower()]
                
                if close_cols:
                    col = close_cols[0]
                    print(f"🎯 DEBUG: Using close column: {col}")
                elif open_cols:
                    col = open_cols[0]
                    print(f"🎯 DEBUG: Using open column: {col}")
                elif numeric_cols:
                    col = numeric_cols[0]
                    print(f"🎯 DEBUG: Using first numeric column: {col}")
                else:
                    print(f"❌ DEBUG: No suitable numeric columns found")
                    return TalkToDataResponse(answer="❌ No numeric columns found for Bollinger Band analysis.")
            
            try:
                window = request.window or 20
                print(f"📊 DEBUG: Using window size: {window}, column: {col}")
                
                # Clean and convert data to numeric, handling any non-numeric values
                s = pd.to_numeric(df[col], errors='coerce').fillna(method='ffill').fillna(0)
                print(f"📈 DEBUG: Data converted - length: {len(s)}, sample: {s.head().tolist()}")
                
                # Calculate Bollinger Bands
                ma = s.rolling(window=window).mean()
                std = s.rolling(window=window).std()
                upper = ma + 2 * std
                lower = ma - 2 * std
                
                # Check for date column (case insensitive)
                date_col = None
                for col_name in df.columns:
                    if col_name.lower() == 'date':
                        date_col = col_name
                        break
                
                plot_data = {
                    "dates": df[date_col].tolist() if date_col else list(range(len(df))),
                    "ma": ma.fillna(0).tolist(),
                    "upper": upper.fillna(0).tolist(),
                    "lower": lower.fillna(0).tolist(),
                    "values": s.tolist()
                }
                print("✅ DEBUG: Bollinger Band data prepared successfully")
                return TalkToDataResponse(answer=f"📈 Bollinger Band analysis created for '{col}' column with {window}-period moving average.", plot_data=plot_data)
            
            except Exception as e:
                print(f"❌ DEBUG: Bollinger Band error: {str(e)}")
                import traceback
                traceback.print_exc()
                return TalkToDataResponse(answer=f"❌ Error creating Bollinger Band: {str(e)}")
        
        elif request.plot_type == "line_trend":
            print("📊 DEBUG: Processing Line Trend request")
            try:
                # Find open and close columns
                open_cols = [col for col in df.columns if "open" in col.lower()]
                close_cols = [col for col in df.columns if "close" in col.lower()]
                
                print(f"📈 DEBUG: Found open columns: {open_cols}")
                print(f"📉 DEBUG: Found close columns: {close_cols}")
                
                if not open_cols and not close_cols:
                    print("❌ DEBUG: No open or close columns found")
                    return TalkToDataResponse(answer="❌ No 'open' or 'close' columns found for trend analysis.")
                
                plot_data = {
                    "dates": df["Date"].tolist() if "Date" in df.columns else list(range(len(df))),
                    "datasets": []
                }
                print(f"📅 DEBUG: Date column exists: {'Date' in df.columns}")
                
                if open_cols:
                    open_col = open_cols[0]
                    print(f"📈 DEBUG: Processing open column: {open_col}")
                    # Clean data and handle NaN values
                    open_data = df[open_col].fillna(method='ffill').fillna(0)
                    # Convert to float and then to list to handle any data type issues
                    try:
                        open_data = pd.to_numeric(open_data, errors='coerce').fillna(0).tolist()
                        print(f"✅ DEBUG: Open data processed - length: {len(open_data)}, sample: {open_data[:3]}")
                    except Exception as e:
                        print(f"⚠️ DEBUG: Open data conversion fallback - error: {e}")
                        open_data = open_data.tolist()
                        
                    plot_data["datasets"].append({
                        "label": f"Open ({open_col})",
                        "data": open_data,
                        "color": "#00ff88"
                    })
                
                if close_cols:
                    close_col = close_cols[0]
                    print(f"📉 DEBUG: Processing close column: {close_col}")
                    # Clean data and handle NaN values
                    close_data = df[close_col].fillna(method='ffill').fillna(0)
                    # Convert to float and then to list to handle any data type issues
                    try:
                        close_data = pd.to_numeric(close_data, errors='coerce').fillna(0).tolist()
                        print(f"✅ DEBUG: Close data processed - length: {len(close_data)}, sample: {close_data[:3]}")
                    except Exception as e:
                        print(f"⚠️ DEBUG: Close data conversion fallback - error: {e}")
                        close_data = close_data.tolist()
                        
                    plot_data["datasets"].append({
                        "label": f"Close ({close_col})",
                        "data": close_data,
                        "color": "#ff6600"
                    })
                
                answer = f"📈 Trend chart created for {len(plot_data['datasets'])} series. "
                if open_cols and close_cols:
                    answer += f"Showing open vs close price movements over time."
                elif open_cols:
                    answer += f"Showing opening price trend."
                else:
                    answer += f"Showing closing price trend."
                
                print(f"✅ DEBUG: Line trend data prepared - datasets: {len(plot_data['datasets'])}")
                return TalkToDataResponse(answer=answer, plot_data=plot_data)
            
            except Exception as e:
                print(f"❌ DEBUG: Line trend error: {str(e)}")
                import traceback
                traceback.print_exc()
                return TalkToDataResponse(answer=f"❌ Error creating line trend: {str(e)}")
        
        else:
            print(f"❌ DEBUG: Unsupported plot type: {request.plot_type}")
            return TalkToDataResponse(answer="Plot type not supported.")
    
    except Exception as e:
        print(f"❌ DEBUG: General error in talk_to_data_plot: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
