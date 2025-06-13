import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import os
import numpy as np
import seaborn as sns
from dataset_manager import DatasetManager
from main import CoreModel
from scipy import stats
from sklearn.decomposition import PCA
import mlflow
import mlflow.sklearn
import json

# Configure MLflow
tracking_uri = os.path.abspath("mlruns")
os.environ["MLFLOW_TRACKING_URI"] = f"file:///{tracking_uri}"
mlflow.set_tracking_uri(f"file:///{tracking_uri}")
os.makedirs(tracking_uri, exist_ok=True)
os.makedirs("temp/mlflow_artifacts", exist_ok=True)

# Set up MLflow experiment with explicit artifact location
artifact_root = os.path.abspath("mlruns/artifacts")
client = mlflow.tracking.MlflowClient()
if not any(exp.name == "LLM_Data_Analysis" for exp in client.search_experiments()):
    mlflow.create_experiment("LLM_Data_Analysis", artifact_location=f"file:///{artifact_root}")
mlflow.set_experiment("LLM_Data_Analysis")
st.sidebar.write(f"MLflow tracking directory: {tracking_uri}")

# Initialize DatasetManager and CoreModel
manager = DatasetManager()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API Key is not set in environment variables.")
    st.stop()
core_model = CoreModel(api_key)

# MLflow UI Access (Always visible)
st.sidebar.subheader("MLflow Tracking & Visualization")
st.sidebar.write("View and compare all analysis runs:")

if st.sidebar.button("Launch MLflow UI (localhost:5000)", key="sidebar_mlflow_button"):
    import subprocess
    try:
        # Get absolute path for MLflow tracking
        tracking_uri = os.path.abspath("mlruns")
        tracking_uri_posix = tracking_uri.replace('\\', '/')
        # Launch MLflow UI with proper environment variable
        powershell_command = (
            f'$env:MLFLOW_TRACKING_URI="file:///{tracking_uri_posix}"; '
            'write-host "MLflow UI starting with tracking URI: $env:MLFLOW_TRACKING_URI"; '
            'mlflow ui'
        )
        subprocess.Popen(
            ["powershell.exe", "-NoExit", "-Command", powershell_command],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        st.sidebar.success("MLflow UI launched! Open http://localhost:5000 in your browser")
        st.sidebar.info("Note: You need to analyze a dataset before seeing any results in MLflow.")
    except Exception as e:
        st.sidebar.error(f"Failed to launch MLflow UI: {e}")

st.sidebar.markdown("[Open MLflow UI](http://localhost:5000)")

# Streamlit UI
st.title("Intelligent Data Analysis Using LLMs")

# LLM Selection
st.subheader("Select an LLM")
# Map display names to OpenAI model IDs, including GPT-4o Mini option
llm_display_to_id = {
    "OpenAI GPT-4": "gpt-4",
    "OpenAI GPT-4o": "gpt-4o",
    "OpenAI GPT-4o Mini": "gpt-4o-mini"
}
# Display the options for selection
selected_display = st.selectbox("Choose an LLM for analysis:", list(llm_display_to_id.keys()))

if st.button("Confirm LLM Selection"):
    # Retrieve the model ID from the mapping and set it in CoreModel
    model_id = llm_display_to_id[selected_display]
    core_model.set_llm(model_id)
    st.success(f"You have selected {selected_display}. Proceed with the analysis.")

# File Upload
uploaded_file = st.file_uploader("Upload your dataset (CSV, JSON, or Excel)", type=["csv", "json", "xlsx"])

# Function to load data
def load_data(file, chunk_size=None):
    """Load data from uploaded file with optional chunking."""
    file_type = file.name.split('.')[-1].lower()
    try:
        if file_type == 'csv':
            if chunk_size:
                # Read in chunks for large CSV files
                chunks = []
                for chunk in pd.read_csv(file, chunksize=chunk_size):
                    chunks.append(chunk)
                return pd.concat(chunks, ignore_index=True)
            return pd.read_csv(file)
        elif file_type == 'xlsx' or file_type == 'xls':
            return pd.read_excel(file)
        elif file_type == 'json':
            return pd.read_json(file)
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

# File Upload and Initial Processing
if uploaded_file:
    try:
        import time
        start_time = time.time()
        MAX_PROCESSING_TIME = 120  # 2 minutes max

        # Check File Size
        file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
        st.write(f"Uploaded file size: {file_size:.2f} MB")

        if file_size == 0:
            st.error("The uploaded file is empty. Please upload a valid dataset.")
            st.stop()

        # Set chunk size based on file size
        if file_size > 100:
            CHUNK_SIZE = 10_000  # Optimize chunk size for better performance
            st.info(f"Processing in chunks of {CHUNK_SIZE:,} rows due to large file size")
        else:
            CHUNK_SIZE = None

        # Track processing time for each step
        processing_times = {}
        
        def track_time(step_name):
            step_start = time.time()
            return lambda: processing_times.update({step_name: time.time() - step_start})

        # Load data with progress
        data_timer = track_time("Data Loading")
        with st.spinner('Loading data...'):
            if CHUNK_SIZE:
                df = load_data(uploaded_file, CHUNK_SIZE)
                st.info(f"Processing first {CHUNK_SIZE:,} rows due to large file size")
            else:
                df = load_data(uploaded_file)

        if df is None or df.empty:
            st.error("Unable to load the dataset. Please check the file format.")
            st.stop()

        # Display dataset preview
        st.subheader("Dataset Preview")
        st.write(df.head())

        # Clean and validate data
        def clean_and_validate_data(df):
            import numpy as np
            import pandas as pd

            df_cleaned = df.copy()

            # 🔹 Drop likely index columns
            likely_index_cols = []
            for col in df_cleaned.columns:
                col_lower = col.lower()
                if col_lower in ['index', 'id', 'serial', 'sno', 'serial_number'] or \
                   (df_cleaned[col].dtype.kind in 'iuf' and df_cleaned[col].is_monotonic_increasing):
                    likely_index_cols.append(col)

            df_cleaned.drop(columns=likely_index_cols, inplace=True, errors='ignore')

            # 🔹 Convert 'Date' to datetime
            if 'Date' in df_cleaned.columns and not pd.api.types.is_datetime64_any_dtype(df_cleaned['Date']):
                df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'], errors='coerce')

            # 🔹 Detect constant columns (like 'Currency'), but do not drop them
            nunique = df_cleaned.nunique(dropna=False)
            constant_cols = nunique[nunique == 1].index.tolist()
            # Do not drop constant columns, just detect them
            # if constant_cols:
            #     st.info(f"Dropped constant columns: {', '.join(constant_cols)}")
            #     df_cleaned.drop(columns=constant_cols, inplace=True)

            # 🔹 Format numeric columns
            numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                col_lower = col.lower()
                if any(term in col_lower for term in ['price', 'amount', 'value', 'cost']):
                    df_cleaned[col] = df_cleaned[col].round(2)
                elif any(term in col_lower for term in ['ratio', 'rate', 'percentage']):
                    df_cleaned[col] = df_cleaned[col].round(4)
                elif col_lower == 'volume':
                    df_cleaned[col] = df_cleaned[col].round(0)

            return df_cleaned

        cleaning_timer = track_time("Data Cleaning")
        df = clean_and_validate_data(df)
        cleaning_timer()

        # Force conversion of all columns that look numeric to numeric dtype, but skip datetime columns
        # Only force numeric conversion on columns that are likely numeric (object columns that look like numbers)
        for col in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                # Only convert if all non-null values look like numbers
                non_null = df[col].dropna()
                if not non_null.empty and non_null.apply(lambda x: isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.', '', 1).isdigit())).all():
                    df[col] = pd.to_numeric(df[col], errors='coerce')

        # Handle NaT in datetime columns by dropping rows with NaT
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df = df[df[col].notna()]

        # Use robust datetime serialization for all .to_json() calls
        # Get LLM feedback on data quality
        # Patch constant object-type columns that may be misrepresented by Pandas as having count=0
        desc = df.describe(include='all')
        profile_constant_cols = {}
        for col in df.columns:
            if df[col].nunique(dropna=False) == 1:
                non_nulls = df[col].dropna()
                if not non_nulls.empty:
                    value = non_nulls.iloc[0]
                    desc.loc['count', col] = df.shape[0]
                    desc.loc['unique', col] = 1
                    desc.loc['top', col] = value
                    desc.loc['freq', col] = df.shape[0]
                    profile_constant_cols[col] = value
                else:
                    profile_constant_cols[col] = None

        stats_json = desc.to_json(date_format='iso')
        validation_prompt = f"""
You are a data quality expert analyzing diverse datasets. Provide general observations about:

1. Data Types: Note any unexpected data types or columns that might need conversion
2. Missing Values: Identify columns with significant missing data
3. Constant Columns: Report any columns with constant values (including all nulls)
4. Numeric Ranges: Note any numeric columns with unusual ranges
5. Potential Issues: Highlight any obvious data quality issues

For constant columns, suggest whether they should be:
- Kept (if they serve a purpose like schema conformity)
- Dropped (if truly redundant)

Dataset statistics:
{stats_json}

Constant columns detected:
{json.dumps(profile_constant_cols)}
"""
        validation_feedback = core_model.generate_insights(validation_prompt)
        st.subheader("Data Quality Analysis")
        st.write(validation_feedback)

        # Display cleaned statistics
        st.subheader("Basic Statistics")
        stats_display = df.describe()
        
        # Format display of statistics
        def format_stats(stats_df):
            formatted = stats_df.copy()
            for col in stats_df.columns:
                if 'year' in col.lower():
                    formatted[col] = formatted[col].astype(int)
                elif any(term in col.lower() for term in ['price', 'amount', 'value']):
                    formatted[col] = formatted[col].round(2)
                elif any(term in col.lower() for term in ['ratio', 'rate']):
                    formatted[col] = formatted[col].round(4)
                else:
                    formatted[col] = formatted[col].round(2)
            return formatted
        
        st.write(format_stats(stats_display))

        # Get LLM insights on the statistics
        stats_insights = core_model.generate_insights(f"Analyze these statistics and provide key insights: {df.describe().to_json(date_format='iso')}")
        st.write("Statistical Insights:")
        st.write(stats_insights)

        # Process data in parallel for large files
        if file_size > 100:
            from concurrent.futures import ThreadPoolExecutor
            import numpy as np
            
            def process_chunk(chunk_df):
                stats_df = chunk_df.describe()
                corr_df = chunk_df.select_dtypes(include=[np.number]).corr() if len(chunk_df.columns) > 1 else None
                ts_analysis = core_model.perform_time_series_analysis(chunk_df)
                return {
                    'stats': stats_df,
                    'correlation': corr_df,
                    'time_series': ts_analysis
                }

            chunks = np.array_split(df, max(1, len(df) // CHUNK_SIZE))
            parallel_timer = track_time("Parallel Processing")
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(process_chunk, chunks))
            parallel_timer()

            # Combine results
            stats = pd.concat([r['stats'] for r in results]).groupby(level=0).mean()
            correlations = [r['correlation'] for r in results if r['correlation'] is not None]
            correlation = pd.concat(correlations).groupby(level=0).mean() if correlations else None
            
            # Combine time series analysis
            ts_results = {}
            for r in results:
                if r['time_series']:
                    for key, value in r['time_series'].items():
                        if key not in ts_results:
                            ts_results[key] = value
                        else:
                            # Merge time series results
                            for metric in ['trend', 'seasonal', 'resid']:
                                ts_results[key][metric].extend(value[metric])
        else:
            analysis_timer = track_time("Analysis")
            stats = df.describe()
            correlation = df.select_dtypes(include=[np.number]).corr()
            ts_results = core_model.perform_time_series_analysis(df)
            analysis_timer()

        # Display timing information
        st.subheader("Processing Times")
        for step, duration in processing_times.items():
            st.text(f"{step}: {duration:.2f} seconds")

        # Generate Dataset Profile
        st.subheader("Dataset Profile")
        profile = manager.profile_dataset(df, "temp")

        # --- Flag all-null and constant columns in Streamlit, do NOT drop them ---
        all_null_cols = profile.get("all_null_columns", [])
        constant_cols_dict = profile.get("constant_columns", {})
        if all_null_cols:
            st.warning(f"The following columns are completely null (all values missing): {all_null_cols}. These are retained for transparency and possible schema/joining needs.")
        if constant_cols_dict:
            st.info(f"The following columns have constant values: {list(constant_cols_dict.keys())}. " +
                    ", ".join([f"{col} = {val}" for col, val in constant_cols_dict.items()]))

        # Utility to recursively convert pandas.Timestamp to ISO strings
        def convert_timestamps(obj):
            import pandas as pd
            if isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_timestamps(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_timestamps(i) for i in obj]
            else:
                return obj
        st.json(convert_timestamps(profile))

        # --- FAST VISUALIZATION OPTIMIZATION ---
        # Use only a sample for visualizations if dataset is large
        VIS_SAMPLE_SIZE = 1000
        MAX_VIS_COLS = 5
        vis_df = df.copy()
        if len(vis_df) > VIS_SAMPLE_SIZE:
            vis_df = vis_df.head(VIS_SAMPLE_SIZE)
            st.info(f"Visualizations use only the first {VIS_SAMPLE_SIZE} rows for speed.")
        # Always recompute num_cols from the latest df
        num_cols = vis_df.select_dtypes(include=[np.number]).columns.tolist()
        if len(num_cols) > MAX_VIS_COLS:
            vis_cols = num_cols[:MAX_VIS_COLS]
            st.info(f"Visualizations use only the first {MAX_VIS_COLS} numeric columns for speed.")
        else:
            vis_cols = num_cols

        @st.cache_data(show_spinner=False)
        def fast_pairplot(data, cols):
            import seaborn as sns
            import matplotlib.pyplot as plt
            pairplot_fig = sns.pairplot(data[cols])
            return pairplot_fig.fig

        @st.cache_data(show_spinner=False)
        def fast_corr_heatmap(data, cols):
            import matplotlib.pyplot as plt
            import seaborn as sns
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(data[cols].corr(), annot=True, cmap='coolwarm', ax=ax)
            return fig

        # Generate Plots (FAST)
        st.subheader("Visualizations (Fast Mode)")
        if len(vis_cols) >= 2:
            st.write("Pairplot:")
            fig = fast_pairplot(vis_df, vis_cols)
            st.pyplot(fig)
            st.write("Correlation Heatmap:")
            fig = fast_corr_heatmap(vis_df, vis_cols)
            st.pyplot(fig)
        elif len(vis_cols) == 1:
            st.info("Only one numeric column found. Skipping pairplot and heatmap (need at least 2 numeric columns).")
        else:
            st.info("No numeric columns found for visualization. Please upload a dataset with numeric columns.")

        # Advanced Stats
        st.subheader("Advanced Statistics")
        if len(num_cols) == 0:
            st.info("No numeric columns found. Advanced statistics cannot be computed.")
        else:
            stats = manager.advanced_stats(df, "temp/plots")
            st.write(pd.DataFrame(stats).T)

        # Generate Insights
        st.subheader("LLM-Generated Insights")
        core_model.api_key = api_key  # Update API key
        # Avoid sending the full DataFrame to the LLM to prevent token limit errors
        # Replace NaT with None for JSON serialization
        df_for_json = df.copy()
        for col in df_for_json.columns:
            if pd.api.types.is_datetime64_any_dtype(df_for_json[col]):
                df_for_json[col] = df_for_json[col].where(df_for_json[col].notna(), None)
        sample_json = df_for_json.head(20).to_json(date_format='iso')
        llm_prompt = f"""
You're a senior data analyst. Analyze this dataset completely:
- Describe all numerical and categorical fields
- Detect any issues: outliers, skewness, anomalies
- Summarize key statistics and trends
- Recommend feature engineering ideas
- Propose machine learning or modeling strategies

Here is a sample (first 20 rows) in JSON:
{sample_json}
"""
        insights = core_model.generate_insights(llm_prompt)
        st.write(insights)

        # Generate Recommendations
        recommendations_prompt = "Based on this dataset, provide actionable recommendations for further analysis, feature engineering, or modeling."
        recommendations = core_model.generate_insights(recommendations_prompt)
        st.subheader("LLM-Generated Recommendations")
        st.write(recommendations)

        # Generate Distribution Graphs with Skewness Information
        st.subheader("Distribution Graphs")
        distribution_plots = manager.generate_distribution_plots(df, "temp/plots")
        for column, plot_path in distribution_plots.items():
            st.image(plot_path, caption=f"Distribution of {column}")
            skewness = manager.calculate_skewness(df[column])
            if skewness > 0:
                st.write(f"The data for {column} is positively skewed.")
            elif skewness < 0:
                st.write(f"The data for {column} is negatively skewed.")
            else:
                st.write(f"The data for {column} is symmetric.")

        # Feature Store
        st.subheader("Feature Store")
        feature_store = manager.extract_features(df)
        st.write("Extracted Features:")
        st.write(feature_store.head())

        st.download_button(
            label="Download Feature Store",
            data=feature_store.to_csv(index=False),
            file_name="feature_store.csv",
            mime="text/csv"
        )

        # Interactive Relationship Explanation
        st.subheader("Interactive Relationship Explanation")
        # Always recompute num_cols from the latest df
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        st.write("Detected numeric columns:", num_cols)  # Debug info for user
        # Only allow numeric columns for relationship analysis
        if len(num_cols) < 2:
            st.info("At least two numeric columns are required for relationship analysis and scatter plots.")
        else:
            selected_features = st.multiselect("Select features to analyze relationships:", num_cols)

            if len(selected_features) >= 2:
                st.write("Scatter Plot:")
                scatter_plot_path = manager.generate_scatter_plot(df, selected_features, "temp/plots")
                st.image(scatter_plot_path, caption="Scatter Plot")

                st.write("Correlation Heatmap:")
                correlation_heatmap_path = manager.generate_correlation_heatmap(df[selected_features], "temp/plots")
                st.image(correlation_heatmap_path, caption="Correlation Heatmap")

                st.write("LLM-Generated Insights:")
                # Avoid sending the full DataFrame to the LLM to prevent token limit errors
                rel_sample_json = df[selected_features].head(20).to_json(date_format='iso')
                relationship_insights = core_model.generate_relationship_insights(rel_sample_json)
                st.write(relationship_insights)

                # Correlation Matrix
                st.subheader("Correlation Matrix")
                correlation_matrix = core_model.generate_correlation_matrix(df[selected_features])
                st.write(correlation_matrix)

        # Correlation Matrix (filtering non-numeric columns)
        st.subheader("Correlation Matrix")
        # Only include numeric columns to avoid conversion errors
        num_cols_corr = df.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols_corr:
            corr_mat = core_model.generate_correlation_matrix(df[num_cols_corr])
            st.write(corr_mat)
        else:
            st.info("No numeric columns available for correlation matrix.")

        # Feature Importance Explanation
        st.subheader("Feature Importance Explanation")
        # Avoid sending the full DataFrame to the LLM to prevent token limit errors
        feat_sample_json = df.head(20).to_json(date_format='iso')
        feature_importance_insights = core_model.explain_feature_importance(feat_sample_json)
        st.write(feature_importance_insights)

        # Save Results
        st.download_button(
            label="Download Dataset Profile",
            data=open("temp/dataset_profile.json").read(),
            file_name="dataset_profile.json",
            mime="application/json"
        )

        st.download_button(
            label="Download Advanced Statistics",
            data=open("temp/plots/advanced_stats.csv").read(),
            file_name="advanced_stats.csv",
            mime="text/csv"
        )

        # --- LLM-Enhanced Statistical & Mathematical Analysis Workflow ---

        # 1. Statistical Foundations
        st.header("Statistical Foundations")
        st.subheader("Descriptive Statistics")
        st.write(df.describe(include='all').T)
        st.write("Skewness:", df.select_dtypes(include=[np.number]).skew())
        st.write("Kurtosis:", df.select_dtypes(include=[np.number]).kurt())
        st.write("LLM Explanation:")
        st.write(core_model.generate_insights(
            "Explain the meaning of mean, median, mode, variance, standard deviation, skewness, and kurtosis in the context of this dataset: " 
            + df.describe(include='all').T.to_json(date_format='iso')
        ))

        # --- Additional Mathematical & Statistical Analyses ---
        st.header("Mathematical & Statistical Analyses")
        # Focus on numeric features for advanced metrics
        num_cols_ms = df.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols_ms:
            # PCA for dimensionality reduction
            from sklearn.decomposition import PCA
            pca = PCA(n_components=min(len(num_cols_ms), 5))
            pca_fit = pca.fit(df[num_cols_ms].dropna())
            st.subheader("PCA Explained Variance Ratio")
            st.write({f"PC{i+1}": var for i, var in enumerate(pca_fit.explained_variance_ratio_)})

            # Spearman correlation
            st.subheader("Spearman Correlation Matrix")
            st.write(df[num_cols_ms].corr(method='spearman'))

            # Outlier detection via z-score (use scipy.stats alias to avoid name collision)
            z_scores = np.abs(sstats.zscore(df[num_cols_ms].fillna(0)))
            outlier_counts = (z_scores > 3).sum(axis=0)
            st.subheader("Outlier Counts (|z| > 3)")
            st.write({col: int(cnt) for col, cnt in zip(num_cols_ms, outlier_counts)})

            # Feature entropy
            import scipy.stats as sstats
            entropies = {
                col: sstats.entropy(np.histogram(df[col].dropna(), bins=10)[0])
                for col in num_cols_ms
            }
            st.subheader("Feature Entropy")
            st.write(entropies)

            # K-Means clustering silhouette scores
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score
            silhouette_scores = {}
            for k in [2, 3, 4]:
                km = KMeans(n_clusters=k, random_state=42).fit(df[num_cols_ms].dropna())
                labels = km.labels_
                score = silhouette_score(df[num_cols_ms].dropna(), labels)
                silhouette_scores[k] = score
            st.subheader("K-Means Silhouette Scores")
            st.write(silhouette_scores)
        else:
            st.info("No numeric columns available for advanced mathematical analyses.")
        
        # --- LLM-Driven Analysis Flow Selection ---
        st.subheader("Automated Data Analysis Flow")
        # Use LLM to suggest the best analysis flow for the dataset
        flow_prompt = f"""
        Given the following dataset schema and statistics, suggest an optimal analysis flow. 
        The flow should include: 
        - Data type checks
        - Outlier detection (if numeric columns exist)
        - Correlation analysis (if multiple numeric columns)
        - Time series analysis (if datetime columns)
        - Feature engineering (if categorical columns)
        - Any other relevant steps for this data
        
        Dataset schema: {str(df.dtypes)}
        Statistics: {df.describe(include='all').T.to_json(date_format='iso')}
        """
        flow_suggestion = core_model.generate_insights(flow_prompt)
        st.write("LLM-Suggested Analysis Flow:")
        st.write(flow_suggestion)

        # --- Execute LLM-Driven Flow ---
        # Outlier Detection (if numeric columns)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_results = None
        if len(numeric_cols) > 0:
            Q1 = df[numeric_cols].quantile(0.25)
            Q3 = df[numeric_cols].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[numeric_cols] < (Q1 - 1.5 * IQR)) | (df[numeric_cols] > (Q3 + 1.5 * IQR))).sum()
            outlier_results = outliers
            st.subheader("Outlier Detection (IQR Method)")
            st.write("Outliers detected per numeric column:")
            st.write(outliers)

        # Correlation Analysis (if multiple numeric columns)
        if len(numeric_cols) > 1:
            st.subheader("Correlation Analysis")
            corr = df[numeric_cols].corr()
            st.write(corr)

        # Time Series Analysis (if datetime columns)
        datetime_cols = df.select_dtypes(include=["datetime", "datetime64[ns]"]).columns
        if len(datetime_cols) > 0:
            st.subheader("Time Series Analysis")
            ts_results = core_model.perform_time_series_analysis(df)
            if ts_results:
                for key, analysis in ts_results.items():
                    st.write(f"Analysis for {key}:")
                    st.write("Trend:", analysis['trend'][:10])
                    st.write("Seasonal:", analysis['seasonal'][:10])
                    st.write("Residuals:", analysis['resid'][:10])

        # Feature Engineering (if categorical columns)
        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        if len(cat_cols) > 0:
            st.subheader("Feature Engineering Suggestions")
            feat_prompt = f"Suggest feature engineering steps for these categorical columns: {list(cat_cols)}"
            feat_suggestions = core_model.generate_insights(feat_prompt)
            st.write(feat_suggestions)

        # 3. Data Preprocessing
        st.header("Data Preprocessing")
        # Use LLM to suggest preprocessing steps, but do not show code
        preprocessing_suggestion = core_model.generate_insights("Suggest preprocessing steps for this dataset, including missing value imputation and encoding, but do not provide code snippets.")
        st.write(preprocessing_suggestion)

        # 4. Statistical Techniques
        st.header("Statistical Techniques")
        st.write(core_model.generate_insights("Summarize key statistical techniques relevant to this dataset in 2-3 sentences, focusing on actionable insights only."))

        # 5. Machine Learning Basics
        st.header("Machine Learning Basics")
        st.write(core_model.generate_insights("Briefly summarize the most relevant machine learning approaches for this dataset and their practical use, in 2-3 sentences."))

        # 6. Data Visualization
        st.header("Data Visualization")
        st.write(core_model.generate_insights("Recommend the most effective visualizations for this dataset and what insights they can reveal, in 2-3 sentences."))

        # 7. Advanced Topics
        st.header("Advanced Topics")
        st.write(core_model.generate_insights("Briefly mention any advanced analysis or modeling techniques that could be valuable for this dataset, in 2-3 sentences."))

        # 8. Tools & LLM Integration
        st.header("Tools & LLM Integration")
        st.write(core_model.generate_insights("Summarize how LLMs and automated tools are used in this analysis, focusing on practical benefits for analysts, in 2-3 sentences."))

        # 9. Ethics & Best Practices
        st.header("Ethics & Best Practices")
        st.write(core_model.generate_insights("How to detect bias, ensure fairness, and maintain privacy in data analysis?"))

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
        st.stop()

    # --- DATASET SUMMARY & SIGNIFICANT COLUMN SELECTION ---
    st.subheader("Dataset Summary")
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.write("Column Names and Types:")
    st.write(pd.DataFrame({"Column": df.columns, "Type": [str(df[col].dtype) for col in df.columns]}))
    st.write("Missing values per column:")
    st.write(df.isnull().sum())

    # Ask LLM which columns are significant for analysis
    columns_info = [{"name": col, "dtype": str(df[col].dtype), "n_missing": int(df[col].isnull().sum())} for col in df.columns]
    llm_col_prompt = (
        "Given the following columns with their types and missing value counts, "
        "which columns should be included in meaningful data analysis? "
        "Return a Python list of column names to keep.\n"
        f"Columns: {columns_info}"
    )
    try:
        significant_cols_str = core_model.generate_insights(llm_col_prompt)
        import ast
        significant_cols = ast.literal_eval(significant_cols_str)
        if not isinstance(significant_cols, list):
            raise ValueError("LLM did not return a list.")
        st.info(f"Columns selected for analysis: {significant_cols}")
    except Exception as e:
        st.warning(f"LLM column selection failed, using all columns. Error: {e}")
        significant_cols = list(df.columns)

    # Filter DataFrame to only significant columns for all further analysis
    df = df[significant_cols]

    # --- MLflow Tracking Integration (ALWAYS RUNS AFTER SUCCESSFUL ANALYSIS) ---
    artifact_dir = os.path.abspath("temp/mlflow_artifacts")
    os.makedirs(artifact_dir, exist_ok=True)
    mlflow.set_experiment("LLM_Data_Analysis")
    run = mlflow.start_run(run_name=f"analysis_{uploaded_file.name}")
    try:
        # Log run info
        mlflow.set_tags({
            "filename": uploaded_file.name,
            "file_type": uploaded_file.name.split('.')[-1],
            "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        st.write("[DEBUG] MLflow tags set.")

        # Log parameters
        mlflow.log_params({
            "file_name": uploaded_file.name,
            "file_size_MB": round(file_size, 2),
            "num_rows": df.shape[0],
            "num_columns": df.shape[1],
            "numeric_columns": len(num_cols),
            "categorical_columns": len(cat_cols) if 'cat_cols' in locals() else 0
        })
        st.write("[DEBUG] MLflow parameters logged.")

        # Log feature store
        feature_store_path = os.path.join(artifact_dir, "feature_store.csv")
        os.makedirs(os.path.dirname(feature_store_path), exist_ok=True)
        feature_store.to_csv(feature_store_path, index=False)
        st.write(f"[DEBUG] Feature store saved to: {feature_store_path}")
        mlflow.log_artifact(feature_store_path, "feature_store")
        st.write("[DEBUG] Feature store logged to MLflow.")

        # Log advanced statistics
        if 'stats' in locals():
            stats_path = os.path.join(artifact_dir, "advanced_stats.csv")
            pd.DataFrame(stats).to_csv(stats_path)
            st.write(f"[DEBUG] Advanced stats saved to: {stats_path}")
            mlflow.log_artifact(stats_path, "statistics")
            st.write("[DEBUG] Advanced stats logged to MLflow.")

        # Log plots
        plots_dir = os.path.join(artifact_dir, "plots")
        os.makedirs(plots_dir, exist_ok=True)
        # Log distribution plots
        for column, plot_path in distribution_plots.items():
            if os.path.exists(plot_path):
                st.write(f"[DEBUG] Logging distribution plot: {plot_path}")
                mlflow.log_artifact(plot_path, "plots/distributions")
        # Log correlation plots
        if 'correlation_heatmap_path' in locals() and os.path.exists(correlation_heatmap_path):
            st.write(f"[DEBUG] Logging correlation heatmap: {correlation_heatmap_path}")
            mlflow.log_artifact(correlation_heatmap_path, "plots/correlation")
        if 'scatter_plot_path' in locals() and os.path.exists(scatter_plot_path):
            st.write(f"[DEBUG] Logging scatter plot: {scatter_plot_path}")
            mlflow.log_artifact(scatter_plot_path, "plots/scatter")

        # Log insights and recommendations
        insights_path = os.path.join(artifact_dir, "insights.txt")
        with open(insights_path, "w", encoding="utf-8") as f:
            f.write(f"Analysis Insights:\n{insights}\n\nRecommendations:\n{recommendations}")
        st.write(f"[DEBUG] Insights saved to: {insights_path}")
        mlflow.log_artifact(insights_path, "insights")
        st.write("[DEBUG] Insights logged to MLflow.")

        # Log metrics
        if outlier_results is not None:
            mlflow.log_metrics({f"outliers_{col}": int(val) for col, val in outlier_results.items()})
            st.write("[DEBUG] Outlier metrics logged to MLflow.")
        if 'correlation' in locals() and correlation is not None:
            mean_corr = correlation.abs().mean().mean()
            mlflow.log_metric("mean_correlation", mean_corr)
            st.write("[DEBUG] Mean correlation metric logged to MLflow.")
    finally:
        mlflow.end_run()
        st.write("[DEBUG] MLflow run ended.")

# Display MLflow Tracking Info
st.write("All key artifacts (feature store, advanced stats, insights, plots) are logged to MLflow for experiment tracking and visualization.")
