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
    """Calculate IQR for numeric columns with beautiful web-friendly formatting"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        return "❌ No numeric columns found for IQR calculation."
    
    results = []
    results.append("📊 **IQR Analysis Results**\n")
    
    # Process each column
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        median = df[col].median()
        
        # Calculate coefficient of variation
        cv = (df[col].std() / df[col].mean()) * 100 if df[col].mean() != 0 else 0
        
        # Format numbers based on scale
        if 'volume' in col.lower() or q1 > 1000:
            q1_str = f"{q1:,.0f}"
            q3_str = f"{q3:,.0f}"
            iqr_str = f"{iqr:,.0f}"
            median_str = f"{median:,.0f}"
        else:
            q1_str = f"{q1:.2f}"
            q3_str = f"{q3:.2f}"
            iqr_str = f"{iqr:.2f}"
            median_str = f"{median:.2f}"
        
        # Variation level indicator
        if cv < 10:
            variation = "🟢 Low"
        elif cv < 25:
            variation = "🟡 Medium"
        else:
            variation = "🔴 High"
        
        results.append(f"**{col}:**")
        results.append(f"• Q1: {q1_str}  •  Q3: {q3_str}  •  IQR: {iqr_str}")
        results.append(f"• Median: {median_str}  •  Variation: {variation} ({cv:.1f}%)")
        results.append("")
    
    # Add simple explanation
    results.append("💡 **What this means:**")
    results.append("• **IQR** = Range containing the middle 50% of your data")
    results.append("• **Lower values** = More consistent data")
    results.append("• **Higher values** = More spread out data")
    
    return "\n".join(results)

def calculate_statistics(df: pd.DataFrame, query: str) -> str:
    
    # Price columns section (if any)
    if price_cols:
        results.append("### 💰 **Price Analysis**")
        for col in price_cols:
            data = iqr_data[col]
            results.append(f"**{col}:**")
            results.append(f"  • Q1: **{data['q1']:.2f}** | Q3: **{data['q3']:.2f}** | IQR: **{data['iqr']:.2f}**")
            results.append(f"  • Median: **{data['median']:.2f}** | Variation: **{data['cv']:.1f}%**")
            results.append("")
    
    # Volume columns section (if any)
    if volume_cols:
        results.append("### 📊 **Volume Analysis**")
        for col in volume_cols:
            data = iqr_data[col]
            results.append(f"**{col}:**")
            results.append(f"  • Q1: **{data['q1']:,.0f}** | Q3: **{data['q3']:,.0f}** | IQR: **{data['iqr']:,.0f}**")
            results.append(f"  • Median: **{data['median']:,.0f}** | Variation: **{data['cv']:.1f}%**")
            results.append("")
    
    # Other numeric columns section (if any)
    if other_cols:
        results.append("### � **Other Numeric Columns**")
        for col in other_cols:
            data = iqr_data[col]
            results.append(f"**{col}:**")
            results.append(f"  • Q1: **{data['q1']:.2f}** | Q3: **{data['q3']:.2f}** | IQR: **{data['iqr']:.2f}**")
            results.append(f"  • Median: **{data['median']:.2f}** | Variation: **{data['cv']:.1f}%**")
            results.append("")
    
    # Summary insights
    results.append("---")
    results.append("### 🔍 **Key Insights**")
    
    # Find most and least stable columns
    if len(numeric_cols) > 1:
        most_stable = min([(col, data['cv']) for col, data in iqr_data.items()], key=lambda x: x[1])
        most_volatile = max([(col, data['cv']) for col, data in iqr_data.items()], key=lambda x: x[1])
        
        results.append(f"🎯 **Most Stable:** `{most_stable[0]}` ({most_stable[1]:.1f}% variation)")
        results.append(f"⚡ **Most Volatile:** `{most_volatile[0]}` ({most_volatile[1]:.1f}% variation)")
    else:
        col_name, cv = list(iqr_data.items())[0][0], list(iqr_data.items())[0][1]['cv']
        results.append(f"📈 **Single Column:** `{col_name}` has {cv:.1f}% variation")
    
    # Price range insights (for financial data)
    if price_cols and len(price_cols) >= 2:
        high_col = next((col for col in price_cols if 'high' in col.lower()), None)
        low_col = next((col for col in price_cols if 'low' in col.lower()), None)
        if high_col and low_col:
            high_q3 = iqr_data[high_col]['q3']
            low_q1 = iqr_data[low_col]['q1']
            results.append(f"📊 **Price Range:** Typical range from `{low_q1:.2f}` to `{high_q3:.2f}`")
    
    # Volume insights (if applicable)
    if volume_cols:
        vol_col = volume_cols[0]
        vol_median = iqr_data[vol_col]['median']
        results.append(f"📈 **Trading Activity:** Median volume of `{vol_median:,.0f}` units")
    
    results.append("")
    results.append("### 💡 **Understanding IQR**")
    results.append("• **IQR (Interquartile Range)** = Q3 - Q1 (middle 50% of data)")
    results.append("• **Lower variation** = More consistent values")
    results.append("• **Higher variation** = More spread in the data")
    results.append("• **Outliers** = Values beyond Q1 - 1.5×IQR or Q3 + 1.5×IQR")
    
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
- Use the chart buttons above for statistical visualizations and trend analysis

**Your dataset:** {summary['shape'][0]} rows × {summary['shape'][1]} columns
**Columns:** {', '.join(summary['columns'][:5])}{'...' if len(summary['columns']) > 5 else ''}

💡 **Try asking:** "Find IQR for each column" or "Show me correlations"!"""

# Keep the existing plot functionality
@router.post("/talk-to-data/plot", response_model=TalkToDataResponse)
async def talk_to_data_plot(request: TalkToDataRequest):
    print(f"🔍 DEBUG: Received plot request - plot_type: {request.plot_type}, dataset_id: {request.dataset_id}")
    print(f"🔍 DEBUG: Request details - column: '{request.column}', window: {request.window}")
    print(f"🔍 DEBUG: Column is None: {request.column is None}, Column is empty: {request.column == ''}")
    
    try:
        df = await file_handler.load_dataset(request.dataset_id)
        if df is None:
            print("❌ DEBUG: Dataset not found")
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        print(f"📊 DEBUG: Dataset loaded - shape: {df.shape}, columns: {list(df.columns)}")
        
        if request.plot_type == "bollinger_band":
            print("📈 DEBUG: Processing Bollinger Area request")
            
            # Find appropriate column for Bollinger Area
            if request.column and request.column.strip():
                # Try exact match first
                if request.column in df.columns:
                    col = request.column
                    print(f"🎯 DEBUG: Using user-specified column (exact match): {col}")
                else:
                    # Try case-insensitive match
                    matching_cols = [c for c in df.columns if c.lower() == request.column.lower()]
                    if matching_cols:
                        col = matching_cols[0]
                        print(f"🎯 DEBUG: Using user-specified column (case-insensitive match): {col}")
                    else:
                        print(f"⚠️ DEBUG: Column '{request.column}' not found in dataset. Available columns: {list(df.columns)}")
                        col = None
            else:
                col = None
            
            if not col:
                print(f"🔍 DEBUG: No valid column specified (column='{request.column}'), auto-selecting...")
                # Auto-select column when none specified
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                close_cols = [c for c in df.columns if 'close' in c.lower()]
                open_cols = [c for c in df.columns if 'open' in c.lower()]
                
                if close_cols:
                    col = close_cols[0]
                    print(f"🎯 DEBUG: Auto-selected close column: {col}")
                elif open_cols:
                    col = open_cols[0]
                    print(f"🎯 DEBUG: Auto-selected open column: {col}")
                elif numeric_cols:
                    col = numeric_cols[0]
                    print(f"🎯 DEBUG: Auto-selected first numeric column: {col}")
                else:
                    print(f"❌ DEBUG: No suitable numeric columns found")
                    return TalkToDataResponse(answer="❌ No numeric columns found for Bollinger Area analysis.")
            
            try:
                window = request.window or 20
                print(f"📊 DEBUG: Using window size: {window}, column: {col}")
                
                # Clean and convert data to numeric, handling any non-numeric values
                s = pd.to_numeric(df[col], errors='coerce').fillna(method='ffill').fillna(0)
                print(f"📈 DEBUG: Data converted - length: {len(s)}, sample: {s.head().tolist()}")
                
                # Calculate Bollinger Area
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
                print("✅ DEBUG: Bollinger Area data prepared successfully")
                return TalkToDataResponse(answer=f"📈 Bollinger Area analysis created for '{col}' column with {window}-period moving average.", plot_data=plot_data)
            
            except Exception as e:
                print(f"❌ DEBUG: Bollinger Area error: {str(e)}")
                import traceback
                traceback.print_exc()
                return TalkToDataResponse(answer=f"❌ Error creating Bollinger Area: {str(e)}")
        
        elif request.plot_type == "line_trend":
            print("📊 DEBUG: Processing Line Trend request")
            try:
                # Find numeric columns for trend analysis (generic approach)
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                print(f"📈 DEBUG: Found numeric columns: {numeric_cols}")
                
                if not numeric_cols:
                    print("❌ DEBUG: No numeric columns found")
                    return TalkToDataResponse(answer="❌ No numeric columns found for trend analysis.")
                
                # Check if user specified a column
                if request.column and request.column.strip():
                    # Try exact match first
                    if request.column in df.columns:
                        selected_cols = [request.column]
                        print(f"🎯 DEBUG: Using user-specified column: {request.column}")
                    else:
                        # Try case-insensitive match
                        matching_cols = [c for c in df.columns if c.lower() == request.column.lower()]
                        if matching_cols:
                            selected_cols = [matching_cols[0]]
                            print(f"🎯 DEBUG: Using user-specified column (case-insensitive): {matching_cols[0]}")
                        else:
                            print(f"⚠️ DEBUG: Column '{request.column}' not found, using all numeric columns")
                            selected_cols = numeric_cols[:3]  # Fallback to first 3
                else:
                    # Use first 2-3 numeric columns for trend analysis when no specific column requested
                    selected_cols = numeric_cols[:3]  # Limit to max 3 columns for readability
                    print(f"🎯 DEBUG: No column specified, using first {len(selected_cols)} numeric columns")
                
                plot_data = {
                    "dates": df[df.columns[0]].tolist() if len(df.columns) > 0 else list(range(len(df))),
                    "datasets": []
                }
                print(f"📅 DEBUG: Using first column as x-axis: {df.columns[0] if len(df.columns) > 0 else 'index'}")
                
                # Create color palette for multiple lines
                colors = ["#00ff88", "#ff6600", "#00aaff", "#ff3366", "#88ff00"]
                
                for i, col in enumerate(selected_cols):
                    print(f"� DEBUG: Processing column: {col}")
                    # Clean data and handle NaN values
                    col_data = df[col].fillna(method='ffill').fillna(0)
                    # Convert to float and then to list to handle any data type issues
                    try:
                        col_data = pd.to_numeric(col_data, errors='coerce').fillna(0).tolist()
                        print(f"✅ DEBUG: {col} data processed - length: {len(col_data)}, sample: {col_data[:3]}")
                    except Exception as e:
                        print(f"⚠️ DEBUG: {col} data conversion fallback - error: {e}")
                        col_data = col_data.tolist()
                        
                    plot_data["datasets"].append({
                        "label": col,
                        "data": col_data,
                        "color": colors[i % len(colors)]
                    })
                
                if len(selected_cols) == 1:
                    answer = f"📈 Trend chart created for '{selected_cols[0]}' column."
                else:
                    answer = f"📈 Trend chart created for {len(plot_data['datasets'])} numeric columns: {', '.join(selected_cols)}."
                
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
