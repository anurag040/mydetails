import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import json
import numpy as np

class DatasetManager:
    def __init__(self, base_folder="datasets"):
        self.base_folder = base_folder
        os.makedirs(self.base_folder, exist_ok=True)

    def download_dataset(self, url, dataset_name, file_name):
        """Download a dataset if it doesn't already exist."""
        dataset_folder = os.path.join(self.base_folder, dataset_name)
        os.makedirs(dataset_folder, exist_ok=True)
        file_path = os.path.join(dataset_folder, file_name)

        if not os.path.exists(file_path):
            print(f"Downloading {dataset_name}...")
            response = requests.get(url)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {dataset_name} to {file_path}")
        else:
            print(f"Dataset {dataset_name} already exists at {file_path}")

        return file_path

    def load_dataset(self, file_path):
        """Load a dataset into a pandas DataFrame."""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format")

    def generate_plots(self, df, output_folder):
        """Generate basic plots for a dataset."""
        os.makedirs(output_folder, exist_ok=True)

        # Pairplot
        numeric_df = df.select_dtypes(include=['number'])  # Select only numeric columns
        if not numeric_df.empty:  # Check if there are numeric columns
            sns.pairplot(numeric_df)
            plt.savefig(os.path.join(output_folder, 'pairplot.png'))
            plt.close()

        # Correlation heatmap
        numeric_df = df.select_dtypes(include=['number'])  # Select only numeric columns
        if not numeric_df.empty:  # Check if there are numeric columns
            plt.figure(figsize=(10, 8))
            sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm')
            plt.savefig(os.path.join(output_folder, 'correlation_heatmap.png'))
            plt.close()

        # Histograms
        for column in df.select_dtypes(include=['number']).columns:
            sanitized_column = re.sub(r'[^a-zA-Z0-9_]', '_', column)  # Replace invalid characters with underscores
            plt.figure()
            sns.histplot(df[column], kde=True)
            plt.title(f"Histogram of {column}")
            plt.savefig(os.path.join(output_folder, f"{sanitized_column}_histogram.png"))
            plt.close()

        print(f"Plots saved to {output_folder}")

    def advanced_stats(self, df, output_folder):
        """Perform advanced statistical analysis on the dataset and save to CSV."""
        stats = {}
        for column in df.select_dtypes(include=['number']).columns:
            stats[column] = {
                "mean": df[column].mean(),
                "median": df[column].median(),
                "std_dev": df[column].std(),
                "skewness": df[column].skew(),
                "kurtosis": df[column].kurt()
            }

        # Save stats to a CSV file
        stats_df = pd.DataFrame(stats).T  # Transpose for better readability
        os.makedirs(output_folder, exist_ok=True)
        stats_file = os.path.join(output_folder, "advanced_stats.csv")
        stats_df.to_csv(stats_file)
        print(f"Advanced stats saved to {stats_file}")

    def generate_time_series_plots(self, df, output_folder):
        """Generate time-series plots for securities data."""
        os.makedirs(output_folder, exist_ok=True)

        for column in df.select_dtypes(include=['number']).columns:
            plt.figure()
            df[column].plot(title=f"Time Series of {column}")
            plt.xlabel("Index")
            plt.ylabel(column)
            plt.savefig(os.path.join(output_folder, f"{column}_time_series.png"))
            plt.close()

        print(f"Time-series plots saved to {output_folder}")

    def clean_and_validate_data(self, df):
        """Clean, validate, and robustly parse dates, handle outliers/skew, and prepare for LLM/MLflow."""
        # --- Robust Date Handling ---
        date_cols = [col for col in df.columns if re.search(r'date', col, re.IGNORECASE)]
        for col in date_cols:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = pd.to_datetime(df[col], errors='coerce')
        # Sort by Date if present
        if 'Date' in df.columns:
            df = df.sort_values('Date')
        # Derive 'Year' column from 'Date' if not present
        if 'Date' in df.columns and 'Year' not in df.columns:
            df['Year'] = df['Date'].dt.year

        # --- Outlier/Skew Handling ---
        for col in df.select_dtypes(include=[np.number]):
            if abs(df[col].skew()) > 1:
                # Keep both original and log-transformed columns
                df[f'{col}_log1p'] = np.where(df[col] > 0, np.log1p(df[col]), np.nan)
                # Optionally, flag outliers (e.g., 3 std from mean)
                df[f'{col}_outlier'] = (np.abs(df[col] - df[col].mean()) > 3 * df[col].std())

        # --- Remove constant columns, but log them for transparency ---
        nunique = df.nunique(dropna=False)
        constant_cols = nunique[nunique == 1].index.tolist()
        profile_constant_cols = {col: df[col].iloc[0] if len(df) > 0 else None for col in constant_cols}
        df = df.drop(columns=constant_cols)

        # --- NaN/NaT Robustness for LLM and JSON ---
        df.replace({pd.NaT: None}, inplace=True)
        df = df.where(pd.notnull(df), None)

        return df, profile_constant_cols

    def profile_dataset(self, df, output_folder):
        """Generate a detailed profile of the dataset and save to a file."""
        # --- Clean and Validate Data ---
        df, profile_constant_cols = self.clean_and_validate_data(df)

        # ---- Extra Verification and Logging ----
        null_counts = df.isnull().sum()
        nunique_counts = df.nunique(dropna=False)
        all_null_cols = null_counts[null_counts == df.shape[0]].index.tolist()
        constant_cols = nunique_counts[nunique_counts == 1].index.tolist()

        # --- Profile Construction ---
        profile = {
            "data_types": df.dtypes.apply(lambda x: str(x)).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "statistical_summary": df.describe(include='all').to_dict(),
            "constant_columns": profile_constant_cols,
            "all_null_columns": all_null_cols
        }

        # --- LLM Data Quality, Target, and Model Suggestions ---
        from .main import CoreModel
        import openai
        api_key = os.environ.get("OPENAI_API_KEY", "")
        core_model = CoreModel(api_key)
        stats_json = df.describe(include='all').to_json(date_format='iso')
        validation_prompt = f"""
You are a data quality expert. Analyze the following statistical summary and suggest any real-world data quality concerns.

- Identify numeric columns that have unusually high precision or unnecessary decimal places.
- Point out columns with many zero or null values and whether they may indicate missing data or meaningful sparse data.
- Detect potential outliers or skewed distributions that may impact downstream analysis.
- Identify columns that are either:
  - All null (empty)
  - Constant with a single repeated value
  For each, suggest whether it might be necessary to retain for schema conformity or joining across datasets, or if it can be safely excluded.
- Do NOT assume specific column names (like 'Open', 'Volume'). Use only data patterns and summary statistics.
- Avoid domain-specific assumptions. Keep analysis general and adaptable across domains.
- Additionally, summarize whether any columns were flagged as constant or all-null in the preliminary diagnostics.

Statistics: {stats_json}
"""
        profile['llm_data_quality'] = core_model.generate_insights(validation_prompt)
        profile['llm_target_and_model_suggestions'] = core_model.suggest_target_and_models(df)

        def convert(obj):
            import pandas as pd
            import numpy as np
            if isinstance(obj, pd.Timestamp):
                if pd.isna(obj):
                    return None
                return obj.isoformat()
            elif isinstance(obj, float) and (np.isnan(obj) or obj is pd.NaT):
                return None
            elif isinstance(obj, (pd.NaT.__class__, type(pd.NaT))):
                return None
            elif hasattr(obj, 'isnull') and obj.isnull():
                return None
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(i) for i in obj]
            else:
                return obj

        profile = convert(profile)  # Safely convert timestamps

        # Save profile to a JSON file
        os.makedirs(output_folder, exist_ok=True)
        profile_file = os.path.join(output_folder, "dataset_profile.json")
        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2)

        print(f"Dataset profile saved to {profile_file}")
        return profile

    # --- Feature/Data Drift Detection ---
    @staticmethod
    def detect_drift(df1, df2):
        from scipy.stats import ks_2samp
        drift_report = {}
        for col in df1.select_dtypes(include=[np.number]):
            if col in df2.columns:
                stat, p_value = ks_2samp(df1[col].dropna(), df2[col].dropna())
                drift_report[col] = {"ks_stat": stat, "p_value": p_value}
        return drift_report

    def sanitize_filename(self, name):
        """Sanitize a string to be used as a valid filename."""
        return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

    def generate_distribution_plots(self, df, output_folder):
        """Generate distribution plots for each numeric column in the dataset."""
        os.makedirs(output_folder, exist_ok=True)
        distribution_plots = {}

        for column in df.select_dtypes(include=[np.number]).columns:
            plt.figure(figsize=(8, 6))
            sns.histplot(df[column].dropna(), kde=True, bins=30, color='blue')
            plt.title(f"Distribution of {column}")
            plt.xlabel(column)
            plt.ylabel("Frequency")

            sanitized_column = self.sanitize_filename(column)
            plot_path = os.path.join(output_folder, f"{sanitized_column}_distribution.png")
            plt.savefig(plot_path)
            plt.close()

            distribution_plots[column] = plot_path

        return distribution_plots

    def calculate_skewness(self, series):
        """Calculate skewness of a numeric series."""
        return series.skew()

    def extract_features(self, df):
        """Extract features from the dataset."""
        # Example: Add basic feature engineering logic here
        features = df.copy()
        for column in df.select_dtypes(include=[np.number]).columns:
            features[f"{column}_squared"] = df[column] ** 2
            features[f"{column}_sqrt"] = np.sqrt(df[column].clip(lower=0))
        return features

    def generate_scatter_plot(self, df, selected_features, output_folder):
        """Generate scatter plot for selected features."""
        os.makedirs(output_folder, exist_ok=True)
        plt.figure(figsize=(8, 6))
        sns.pairplot(df[selected_features])
        plot_path = os.path.join(output_folder, "scatter_plot.png")
        plt.savefig(plot_path)
        plt.close()
        return plot_path

    def generate_correlation_heatmap(self, df, output_folder):
        """Generate correlation heatmap for selected features."""
        os.makedirs(output_folder, exist_ok=True)
        plt.figure(figsize=(10, 8))
        sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
        plot_path = os.path.join(output_folder, "correlation_heatmap_selected.png")
        plt.savefig(plot_path)
        plt.close()
        return plot_path
