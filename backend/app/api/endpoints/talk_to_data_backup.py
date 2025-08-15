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
    
    # Enhanced Q&A logic
    query = request.query.lower()
    answer = "Sorry, I can't answer that yet."
    
    try:
        # Data summary and analysis
        if "summarize" in query or "summary" in query or "analyze" in query:
            rows, cols = df.shape
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            answer = f"📊 Dataset Summary: {rows:,} rows × {cols} columns. "
            
            # Check for specific financial columns
            financial_cols = []
            for col in df.columns:
                col_lower = col.lower()
                if any(term in col_lower for term in ['open', 'close', 'high', 'low', 'price', 'volume']):
                    financial_cols.append(col)
            
            if financial_cols:
                answer += f"Financial columns detected: {', '.join(financial_cols)}. "
            
            if numeric_cols:
                answer += f"Numeric columns ({len(numeric_cols)}): {', '.join(numeric_cols[:3])}{'...' if len(numeric_cols) > 3 else ''}. "
            
            if categorical_cols:
                answer += f"Categorical columns ({len(categorical_cols)}): {', '.join(categorical_cols[:3])}{'...' if len(categorical_cols) > 3 else ''}."
            
            # Add specific column mentions if requested
            if "open" in query and any("open" in col.lower() for col in df.columns):
                open_cols = [col for col in df.columns if "open" in col.lower()]
                if open_cols and df[open_cols[0]].dtype in ['int64', 'float64']:
                    open_stats = f" Open column stats: min={df[open_cols[0]].min():.2f}, max={df[open_cols[0]].max():.2f}, avg={df[open_cols[0]].mean():.2f}."
                    answer += open_stats
            
            if "close" in query and any("close" in col.lower() for col in df.columns):
                close_cols = [col for col in df.columns if "close" in col.lower()]
                if close_cols and df[close_cols[0]].dtype in ['int64', 'float64']:
                    close_stats = f" Close column stats: min={df[close_cols[0]].min():.2f}, max={df[close_cols[0]].max():.2f}, avg={df[close_cols[0]].mean():.2f}."
                    answer += close_stats
        
        # Statistical queries
        elif "average" in query or "mean" in query:
            if request.column and request.column in df.columns:
                if df[request.column].dtype in ['int64', 'float64']:
                    avg = df[request.column].mean()
                    answer = f"📈 Average of {request.column}: {avg:.2f}"
                else:
                    answer = f"❌ Column '{request.column}' is not numeric."
            else:
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    means = df[numeric_cols].mean()
                    answer = f"📈 Averages: " + ", ".join([f"{col}: {val:.2f}" for col, val in means.head(3).items()])
                else:
                    answer = "❌ No numeric columns found for average calculation."
        
        elif "max" in query or "maximum" in query:
            if request.column and request.column in df.columns:
                if df[request.column].dtype in ['int64', 'float64']:
                    mx = df[request.column].max()
                    answer = f"📈 Maximum of {request.column}: {mx}"
                else:
                    answer = f"❌ Column '{request.column}' is not numeric."
            else:
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    maxs = df[numeric_cols].max()
                    answer = f"📈 Maximums: " + ", ".join([f"{col}: {val}" for col, val in maxs.head(3).items()])
        
        elif "min" in query or "minimum" in query:
            if request.column and request.column in df.columns:
                if df[request.column].dtype in ['int64', 'float64']:
                    mn = df[request.column].min()
                    answer = f"📈 Minimum of {request.column}: {mn}"
                else:
                    answer = f"❌ Column '{request.column}' is not numeric."
            else:
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    mins = df[numeric_cols].min()
                    answer = f"📈 Minimums: " + ", ".join([f"{col}: {val}" for col, val in mins.head(3).items()])
        
        # Data shape and structure
        elif "shape" in query or "size" in query or "dimension" in query:
            rows, cols = df.shape
            answer = f"📏 Dataset shape: {rows:,} rows × {cols} columns"
        
        elif "column" in query and ("name" in query or "list" in query):
            cols = df.columns.tolist()
            answer = f"📋 Columns ({len(cols)}): {', '.join(cols[:5])}{'...' if len(cols) > 5 else ''}"
        
        elif "missing" in query or "null" in query or "nan" in query:
            missing = df.isnull().sum()
            missing_cols = missing[missing > 0]
            if len(missing_cols) > 0:
                answer = f"❓ Missing values: " + ", ".join([f"{col}: {val}" for col, val in missing_cols.head(3).items()])
            else:
                answer = "✅ No missing values found in the dataset."
        
        elif "duplicate" in query:
            duplicates = df.duplicated().sum()
            answer = f"🔄 Duplicate rows: {duplicates}"
        
        elif "data type" in query or "dtype" in query:
            types = df.dtypes.value_counts()
            answer = f"🏷️ Data types: " + ", ".join([f"{dtype}: {count} columns" for dtype, count in types.items()])
        
        # Correlation queries
        elif "correlation" in query or "correlated" in query:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) >= 2:
                corr_matrix = df[numeric_cols].corr()
                high_corr = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7:
                            high_corr.append(f"{corr_matrix.columns[i]} & {corr_matrix.columns[j]}: {corr_val:.2f}")
                
                if high_corr:
                    answer = f"🔗 High correlations found: " + ", ".join(high_corr[:3])
                else:
                    answer = "📊 No strong correlations (>0.7) found between numeric columns."
            else:
                answer = "❌ Need at least 2 numeric columns for correlation analysis."
        
        # Trend and visualization requests
        elif any(term in query for term in ["trend", "graph", "chart", "plot", "line", "show"]) and any(term in query for term in ["open", "close"]):
            # This should trigger a plot request, suggest using visualization
            open_cols = [col for col in df.columns if "open" in col.lower()]
            close_cols = [col for col in df.columns if "close" in col.lower()]
            
            if open_cols or close_cols:
                found_cols = open_cols + close_cols
                answer = f"📈 I found these columns: {', '.join(found_cols)}. To create a trend chart, select '📊 Line Trend (Open/Close)' from the Visualization dropdown above, then send your message again!"
            else:
                answer = f"❌ No 'open' or 'close' columns found. Available columns: {', '.join(df.columns.tolist()[:5])}{'...' if len(df.columns) > 5 else ''}"
        
        # Specific column queries (open, close, high, low, etc.)
        elif any(term in query for term in ["open", "close", "high", "low", "volume", "price"]):
            target_terms = [term for term in ["open", "close", "high", "low", "volume", "price"] if term in query]
            found_cols = []
            stats_info = []
            
            for term in target_terms:
                matching_cols = [col for col in df.columns if term.lower() in col.lower()]
                if matching_cols:
                    col = matching_cols[0]  # Take first match
                    found_cols.append(col)
                    if df[col].dtype in ['int64', 'float64']:
                        stats = f"{col}: min={df[col].min():.2f}, max={df[col].max():.2f}, avg={df[col].mean():.2f}"
                        stats_info.append(stats)
            
            if found_cols:
                answer = f"📈 Found columns: {', '.join(found_cols)}. "
                if stats_info:
                    answer += "Statistics: " + "; ".join(stats_info)
            else:
                answer = f"❌ No columns found matching: {', '.join(target_terms)}. Available columns: {', '.join(df.columns.tolist()[:5])}{'...' if len(df.columns) > 5 else ''}"
        
        # Help and capabilities
        elif "help" in query or "what can you do" in query:
            answer = ("🤖 I can help you with: data summaries, statistics (mean/max/min), "
                     "data shape, column info, missing values, duplicates, correlations, "
                     "and create Bollinger Band visualizations. Try asking 'summarize my data' or 'show correlations'!")
        
        else:
            # Default enhanced response
            answer = ("🤔 I didn't understand that question. Try asking about: "
                     "'summarize my data', 'show me averages', 'any missing values?', "
                     "'data shape', 'column names', or 'help'.")
    
    except Exception as e:
        answer = f"❌ Error processing your question: {str(e)}"
    
    return TalkToDataResponse(answer=answer)

@router.post("/talk-to-data/plot", response_model=TalkToDataResponse)
async def talk_to_data_plot(request: TalkToDataRequest):
    print(f"🔍 DEBUG: Received plot request - plot_type: {request.plot_type}, dataset_id: {request.dataset_id}")
    print(f"🔍 DEBUG: Request details - column: {request.column}, window: {request.window}")
    
    try:
        df = await file_handler.load_dataset(request.dataset_id)
        if df is None:
            print(f"❌ DEBUG: Dataset not found for ID: {request.dataset_id}")
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
                # Handle open/close trend visualization
                open_cols = [col for col in df.columns if "open" in col.lower()]
                close_cols = [col for col in df.columns if "close" in col.lower()]
                print(f"🔍 DEBUG: Found columns - open: {open_cols}, close: {close_cols}")
                
                if not open_cols and not close_cols:
                    print("❌ DEBUG: No open/close columns found")
                    return TalkToDataResponse(answer="❌ No 'open' or 'close' columns found for trend analysis.")
                
                plot_data = {
                    "dates": df["date"].tolist() if "date" in df.columns else list(range(len(df))),
                    "datasets": []
                }
                print(f"📅 DEBUG: Date column exists: {'date' in df.columns}")
                
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
