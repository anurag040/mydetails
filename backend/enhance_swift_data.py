import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def enhance_swift_transactions():
    """
    Enhance SWIFT transactions data with realistic dates and additional numeric features.
    Following project guidelines for robust data processing with proper error handling.
    """
    try:
        # Read the original CSV with proper error handling
        input_file = 'swift_transactions_last_3_months.csv'
        logger.info(f"Reading CSV file: {input_file}")
        
        df = pd.read_csv(input_file)
        logger.info(f"Successfully loaded {len(df)} records")
        
        # Validate input data
        if df.empty:
            raise ValueError("Input CSV file is empty")
        
        required_columns = ['date', 'message_type', 'direction', 'count']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Create realistic date range (last 3 months)
        end_date = datetime(2025, 8, 5)
        start_date = end_date - timedelta(days=90)
        
        # Generate weighted random dates for realistic distribution
        np.random.seed(42)  # For reproducibility
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Weight recent dates more heavily (business realistic pattern)
        weights = np.linspace(0.5, 1.5, len(date_range))
        weights = weights / weights.sum()
        
        random_dates = np.random.choice(date_range, size=len(df), p=weights)
        df['date'] = random_dates
        
        # Convert to datetime for feature extraction
        df['date'] = pd.to_datetime(df['date'])
        
        # Add time-based numeric features
        logger.info("Adding time-based features...")
        df['day_of_week'] = df['date'].dt.dayofweek + 1  # 1=Monday, 7=Sunday
        df['day_of_week_name'] = df['date'].dt.day_name()
        df['is_weekend'] = df['day_of_week'].isin([6, 7]).astype(int)
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        
        # Add business hour simulation (realistic SWIFT processing times)
        business_hours = np.random.choice(
            range(8, 18), 
            size=len(df), 
            p=[0.05, 0.08, 0.12, 0.15, 0.15, 0.15, 0.12, 0.08, 0.05, 0.05]  # Peak at midday
        )
        df['hour'] = business_hours
        df['is_business_hour'] = ((df['hour'] >= 9) & (df['hour'] <= 17)).astype(int)
        df['is_peak_hour'] = df['hour'].isin([10, 11, 14, 15]).astype(int)
        
        # Calculate derived transaction volume features
        logger.info("Calculating volume analytics...")
        
        # Daily aggregations for volume analysis
        daily_stats = df.groupby('date').agg({
            'count': ['sum', 'mean', 'std', 'min', 'max']
        }).reset_index()
        daily_stats.columns = ['date', 'daily_total_volume', 'daily_avg_volume', 
                              'daily_volume_volatility', 'daily_min_volume', 'daily_max_volume']
        daily_stats['daily_volume_volatility'] = daily_stats['daily_volume_volatility'].fillna(0)
        
        # Merge daily stats back
        df = df.merge(daily_stats, on='date', how='left')
        
        # Add transaction flow features per message type and direction
        df['volume_per_type_direction'] = df.groupby(['date', 'message_type', 'direction'])['count'].transform('sum')
        df['daily_type_total'] = df.groupby(['date', 'message_type'])['count'].transform('sum')
        df['volume_ratio_in_type'] = df['count'] / df['daily_type_total']
        
        # Calculate inbound/outbound ratios
        pivot_df = df.pivot_table(
            index=['date', 'message_type'], 
            columns='direction', 
            values='count', 
            aggfunc='sum', 
            fill_value=0
        ).reset_index()
        
        # Handle cases where inbound or outbound might not exist
        if 'inbound' not in pivot_df.columns:
            pivot_df['inbound'] = 0
        if 'outbound' not in pivot_df.columns:
            pivot_df['outbound'] = 0
            
        pivot_df['net_flow'] = pivot_df['outbound'] - pivot_df['inbound']
        pivot_df['flow_ratio'] = pivot_df['outbound'] / (pivot_df['inbound'] + 1)  # +1 to avoid division by zero
        pivot_df['total_flow'] = pivot_df['inbound'] + pivot_df['outbound']
        
        # Merge flow stats back
        flow_stats = pivot_df[['date', 'message_type', 'net_flow', 'flow_ratio', 'total_flow']]
        df = df.merge(flow_stats, on=['date', 'message_type'], how='left')
        
        # Add rolling window features (3-day and 7-day)
        logger.info("Calculating rolling window features...")
        df_sorted = df.sort_values(['date', 'message_type', 'direction']).copy()
        
        # Calculate rolling averages per message type and direction
        for window in [3, 7]:
            df_sorted[f'rolling_avg_{window}d'] = df_sorted.groupby(['message_type', 'direction'])['count'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            df_sorted[f'rolling_std_{window}d'] = df_sorted.groupby(['message_type', 'direction'])['count'].transform(
                lambda x: x.rolling(window=window, min_periods=1).std().fillna(0)
            )
        
        # Add transaction classification features
        logger.info("Adding classification features...")
        
        # Volume quartiles for categorization
        volume_quartiles = df_sorted['count'].quantile([0.25, 0.5, 0.75]).values
        df_sorted['volume_category'] = pd.cut(
            df_sorted['count'], 
            bins=[-np.inf] + list(volume_quartiles) + [np.inf], 
            labels=['Low', 'Medium', 'High', 'Very High']
        )
        
        # Anomaly detection (simple statistical approach)
        df_sorted['volume_zscore'] = df_sorted.groupby(['message_type', 'direction'])['count'].transform(
            lambda x: np.abs((x - x.mean()) / x.std()) if x.std() > 0 else 0
        )
        df_sorted['is_volume_anomaly'] = (df_sorted['volume_zscore'] > 2).astype(int)
        
        # Business logic features for SWIFT compliance
        logger.info("Adding business logic features...")
        
        # Peak processing load indicator
        df_sorted['processing_load_score'] = (
            df_sorted['count'] / df_sorted['daily_avg_volume'] * 
            (2 - df_sorted['is_weekend']) * 
            (1 + df_sorted['is_peak_hour'] * 0.5)
        ).round(2)
        
        # Flow balance indicator (closer to 0 = more balanced)
        df_sorted['flow_imbalance'] = np.abs(df_sorted['net_flow'] / df_sorted['total_flow']).fillna(0)
        
        # Operational efficiency score
        df_sorted['efficiency_score'] = (
            (1 - df_sorted['daily_volume_volatility'] / (df_sorted['daily_avg_volume'] + 1)) * 
            (1 - df_sorted['flow_imbalance']) * 
            df_sorted['is_business_hour']
        ).clip(0, 1).round(3)
        
        # Reorder columns for better readability
        columns = [
            'date', 'day_of_week', 'day_of_week_name', 'is_weekend',
            'hour', 'is_business_hour', 'is_peak_hour', 'week_of_year', 'month', 'quarter',
            'message_type', 'direction', 'count',
            'daily_total_volume', 'daily_avg_volume', 'daily_volume_volatility',
            'daily_min_volume', 'daily_max_volume',
            'volume_per_type_direction', 'daily_type_total', 'volume_ratio_in_type',
            'net_flow', 'flow_ratio', 'total_flow',
            'rolling_avg_3d', 'rolling_std_3d', 'rolling_avg_7d', 'rolling_std_7d',
            'volume_category', 'volume_zscore', 'is_volume_anomaly',
            'processing_load_score', 'flow_imbalance', 'efficiency_score'
        ]
        
        # Select only existing columns
        existing_columns = [col for col in columns if col in df_sorted.columns]
        df_final = df_sorted[existing_columns].copy()
        
        # Sort by date and message details
        df_final = df_final.sort_values(['date', 'message_type', 'direction']).reset_index(drop=True)
        
        # Save enhanced dataset
        output_file = 'swift_transactions_enhanced.csv'
        df_final.to_csv(output_file, index=False)
        
        # Also update the original file
        df_final.to_csv(input_file, index=False)
        
        logger.info(f"✅ Successfully enhanced SWIFT transactions dataset!")
        logger.info(f"📊 Processed {len(df_final)} records")
        logger.info(f"📅 Date range: {df_final['date'].min().strftime('%Y-%m-%d')} to {df_final['date'].max().strftime('%Y-%m-%d')}")
        logger.info(f"📁 Saved to: {output_file} and updated {input_file}")
        
        print("\n📋 Sample of enhanced data:")
        print(df_final.head(10).to_string(index=False))
        
        print(f"\n📈 Feature Summary:")
        print(f"• Total features: {len(df_final.columns)}")
        print(f"• Numeric features: {len(df_final.select_dtypes(include=[np.number]).columns)}")
        print(f"• Day of Week Distribution: {dict(df_final['day_of_week_name'].value_counts())}")
        print(f"• Weekend vs Weekday: {dict(df_final['is_weekend'].value_counts())}")
        print(f"• Volume Categories: {dict(df_final['volume_category'].value_counts())}")
        print(f"• Business Hours: {dict(df_final['is_business_hour'].value_counts())}")
        print(f"• Volume Anomalies: {dict(df_final['is_volume_anomaly'].value_counts())}")
        
        return df_final
        
    except Exception as e:
        logger.error(f"❌ Error enhancing dataset: {str(e)}")
        return None

if __name__ == "__main__":
    result = enhance_swift_transactions()
    if result is not None:
        print(f"\n🎉 Enhancement completed successfully!")
        print(f"📊 Dataset now has {len(result)} rows and {len(result.columns)} columns")
    else:
        print("❌ Enhancement failed!")
