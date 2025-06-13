import os
import json
import pandas as pd
import openai
from dataset_manager import DatasetManager

# Core Model Class
class CoreModel:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key
        self.llm_name = "gpt-4"  # Default LLM

    def set_llm(self, llm_name):
        """Set the LLM to be used for analysis."""
        self.llm_name = llm_name
        print(f"LLM set to: {llm_name}")

    def ingest_data(self, file_path):
        """Ingest and validate diverse datasets."""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            raise ValueError("Unsupported file format")

    def preprocess_data(self, data):
        """Handle structured, unstructured, textual, numerical, or mixed data formats."""
        if isinstance(data, pd.DataFrame):
            # Fill missing values
            data = data.ffill().bfill()

            # Normalize numerical columns
            numerical_cols = data.select_dtypes(include=['number']).columns
            data[numerical_cols] = (data[numerical_cols] - data[numerical_cols].mean()) / data[numerical_cols].std()

            # Encode categorical columns
            categorical_cols = data.select_dtypes(include=['object']).columns
            data = pd.get_dummies(data, columns=categorical_cols, drop_first=True)

        return data

    def perform_eda(self, data):
        """Perform exploratory data analysis."""
        if isinstance(data, pd.DataFrame):
            eda_results = {
                "summary": data.describe().to_dict(),
                "correlation_matrix": data.corr().to_dict(),
                "value_counts": {
                    col: data[col].value_counts().to_dict()
                    for col in data.select_dtypes(include=['object']).columns
                }
            }
        else:
            eda_results = "EDA not implemented for this format"

        return eda_results

    def generate_insights(self, data, context="general"):
        """Use LLM to generate insights."""
        if context == "finance":
            system_role = "You are a financial data analyst. Your answers should reflect real-world financial markets, trading behavior, and securities data."
        else:
            system_role = "You are a data analyst."
        response = openai.ChatCompletion.create(
            model=self.llm_name,  # Use the dynamically set LLM
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": f"Analyze the following data: {data}"}
            ],
            max_tokens=1000  # Adjust token limit as needed
        )
        return response.choices[0].message['content']

    def benchmark_llm(self, data, model_versions):
        """Compare LLM performance across versions."""
        results = {}
        for version in model_versions:
            response = openai.completions.create(
                model=version,
                prompt=f"Analyze the following data: {data}",
                max_tokens=500
            )
            results[version] = response.choices[0].text
        return results

    def process(self, file_path):
        """Main processing pipeline."""
        data = self.ingest_data(file_path)
        preprocessed_data = self.preprocess_data(data)
        eda_results = self.perform_eda(preprocessed_data)
        insights = self.generate_insights(preprocessed_data)
        return {
            "eda": eda_results,
            "insights": insights
        }

    def process_large_dataset(self, file_path, chunk_size=100):
        """Process large datasets in chunks and generate insights."""
        data = self.ingest_data(file_path)

        if isinstance(data, pd.DataFrame):
            num_chunks = (len(data) + chunk_size - 1) // chunk_size  # Calculate number of chunks
            all_insights = []

            for i in range(num_chunks):
                chunk = data.iloc[i * chunk_size:(i + 1) * chunk_size]
                chunk_insights = self.generate_insights(chunk.to_json())  # Convert chunk to JSON for LLM
                all_insights.append({"chunk": i + 1, "insights": chunk_insights})

            # Save combined insights to a file
            insights_file = file_path.replace('.csv', '_insights.json')
            with open(insights_file, 'w') as f:
                json.dump(all_insights, f, indent=2)

            print(f"Insights saved to {insights_file}")
            return all_insights
        else:
            raise ValueError("Unsupported data format for large dataset processing")

    def process_large_dataset_parallel(self, file_path, chunk_size=100):
        """Process large datasets in parallel and generate insights."""
        from concurrent.futures import ThreadPoolExecutor

        data = self.ingest_data(file_path)

        if isinstance(data, pd.DataFrame):
            num_chunks = (len(data) + chunk_size - 1) // chunk_size  # Calculate number of chunks
            all_insights = []

            def process_chunk(chunk):
                return self.generate_insights(chunk.to_json())

            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(process_chunk, data.iloc[i * chunk_size:(i + 1) * chunk_size])
                    for i in range(num_chunks)
                ]

                for i, future in enumerate(futures):
                    all_insights.append({"chunk": i + 1, "insights": future.result()})

            # Save combined insights to a file
            insights_file = file_path.replace('.csv', '_parallel_insights.json')
            with open(insights_file, 'w') as f:
                json.dump(all_insights, f, indent=2)

            print(f"Parallel insights saved to {insights_file}")
            return all_insights
        else:
            raise ValueError("Unsupported data format for large dataset processing")

    def process_sample_based(self, file_path, sample_size=100):
        """Process a sample of the dataset and dynamically generate code for further analysis."""
        data = self.ingest_data(file_path)

        if isinstance(data, pd.DataFrame):
            sample = data.sample(n=min(sample_size, len(data)))
            sample_insights = self.generate_insights(sample.to_json())

            print("Sample insights:", sample_insights)

            # Placeholder: Use LLM response to dynamically generate further analysis code
            # For now, just return the sample insights
            return sample_insights
        else:
            raise ValueError("Unsupported data format for sample-based processing")

    def generate_relationship_insights(self, json_data):
        """Generate insights about relationships between selected features using LLM."""
        prompt = (
            "Analyze the relationships between the selected features in the dataset. "
            "Provide insights about correlations, trends, and any notable patterns. "
            "Here is the dataset in JSON format: " + json_data
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst."},
                {"role": "user", "content": prompt}
            ]
        )

        return response['choices'][0]['message']['content']

    def generate_correlation_matrix(self, df):
        """Generate a correlation matrix for the dataset."""
        return df.corr()

    def explain_feature_importance(self, json_data):
        """Explain feature importance using LLM."""
        prompt = (
            "Analyze the dataset and explain the importance of each feature. "
            "Provide insights into which features are most influential and why. "
            "Here is the dataset in JSON format: " + json_data
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst."},
                {"role": "user", "content": prompt}
            ]
        )

        return response['choices'][0]['message']['content']

    def perform_time_series_analysis(self, df):
        """Perform time series analysis on temporal data."""
        import pandas as pd
        from statsmodels.tsa.seasonal import seasonal_decompose
        import numpy as np
        
        def find_date_columns(df):
            date_cols = []
            for col in df.columns:
                if df[col].dtype == 'datetime64[ns]':
                    date_cols.append(col)
                elif isinstance(df[col].dtype, object):
                    # Try to parse as datetime
                    try:
                        pd.to_datetime(df[col])
                        date_cols.append(col)
                    except:
                        continue
            return date_cols

        date_columns = find_date_columns(df)
        if not date_columns:
            return None

        results = {}
        for date_col in date_columns:
            # Convert to datetime if not already
            df[date_col] = pd.to_datetime(df[date_col])
            # Drop rows with NaT in the datetime column
            df = df.dropna(subset=[date_col])
            # Find numeric columns for analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for num_col in numeric_cols:
                if len(df) >= 2:  # Need at least 2 points for analysis
                    # Sort by date
                    ts_data = df.sort_values(date_col)[[date_col, num_col]].set_index(date_col)
                    # Remove missing values
                    ts_data = ts_data.dropna()
                    # Resample to regular intervals if needed
                    if ts_data.index.inferred_freq is None:
                        # Determine appropriate frequency
                        date_min = ts_data.index.min()
                        date_max = ts_data.index.max()
                        # Check for NaT before proceeding
                        if pd.isna(date_min) or pd.isna(date_max):
                            continue  # Skip this time series
                        date_range = date_max - date_min
                        if date_range.days > 365*2:
                            freq = 'M'  # Monthly
                        elif date_range.days > 30:
                            freq = 'D'  # Daily
                        else:
                            freq = 'H'  # Hourly
                        ts_data = ts_data.resample(freq).mean()
                    # Remove missing values again after resampling
                    ts_data = ts_data.dropna()
                    if len(ts_data) >= 2:  # Check again after cleaning
                        try:
                            # Perform seasonal decomposition
                            decomposition = seasonal_decompose(ts_data, period=min(len(ts_data)//2, 12))
                            results[f"{num_col}_vs_{date_col}"] = {
                                "trend": decomposition.trend.dropna().tolist(),
                                "seasonal": decomposition.seasonal.dropna().tolist(),
                                "resid": decomposition.resid.dropna().tolist(),
                                "frequency": ts_data.index.inferred_freq,
                                "data_points": len(ts_data)
                            }
                        except Exception as e:
                            continue
        
        return results

    def suggest_target_and_models(self, df):
        """Suggest target columns and suitable ML models based on the dataset."""
        import json
        stats_json = df.describe(include='all').to_json(date_format='iso')
        schema = df.dtypes.apply(str).to_dict()

        prompt = f"""
You are a machine learning expert.

Given the following dataset schema and summary statistics, please:

1. Suggest the most likely target variable(s) (i.e., what could be predicted).
2. Recommend appropriate types of machine learning models (classification, regression, clustering, etc.) based on the data characteristics.
3. Provide reasoning behind your suggestions.

Schema:
{json.dumps(schema)}

Statistics:
{stats_json}
"""
        response = openai.ChatCompletion.create(
            model=self.llm_name,
            messages=[
                {"role": "system", "content": "You are a senior machine learning expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        return response['choices'][0]['message']['content']

# Example usage
if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    core_model = CoreModel(api_key)

    # Initialize DatasetManager
    manager = DatasetManager()

    # Example datasets
    datasets = [
        {"url": "https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv", "name": "heights_weights", "file": "hw_200.csv"},
        {"url": "https://jsonplaceholder.typicode.com/posts", "name": "json_placeholder", "file": "posts.json"}
    ]

    # Add securities dataset
    datasets.append({
        "url": "https://query1.finance.yahoo.com/v7/finance/download/AAPL?period1=1609459200&period2=1640995200&interval=1d&events=history&includeAdjustedClose=true",
        "name": "securities_data",
        "file": "AAPL.csv"
    })

    # Add real estate dataset
    datasets.append({
        "url": "https://people.sc.fsu.edu/~jburkardt/data/csv/real_estate.csv",
        "name": "real_estate",
        "file": "Real_Estate_Sales_2001-2022_GL.csv"
    })

    for dataset in datasets:
        file_path = manager.download_dataset(dataset['url'], dataset['name'], dataset['file'])
        df = manager.load_dataset(file_path)
        manager.generate_plots(df, os.path.join(manager.base_folder, dataset['name'], 'plots'))

        # Generate dataset profile
        profile = manager.profile_dataset(df, os.path.join(manager.base_folder, dataset['name'], 'plots'))
        print(f"Dataset profile for {dataset['name']}:", json.dumps(profile, indent=2))

        # Perform advanced stats and time-series analysis for securities data
        if dataset['name'] == "securities_data":
            stats = manager.advanced_stats(df, os.path.join(manager.base_folder, dataset['name'], 'plots'))
            print(f"Advanced stats for {dataset['name']}:\n", json.dumps(stats, indent=2))
            manager.generate_time_series_plots(df, os.path.join(manager.base_folder, dataset['name'], 'plots'))

    # Process a specific dataset using CoreModel
    file_path = "sample_data.csv"  # Replace with your dataset path
    results = core_model.process(file_path)
    print(json.dumps(results, indent=2))
