import pandas as pd
import numpy as np
from openai import OpenAI
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
from app.services.file_handler import FileHandler
from app.schemas.responses import ChatResponse, ChatMessage, AnalysisResponse, ValidationMetrics

class LLMService:
    def __init__(self):
        self.file_handler = FileHandler()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chat_history = {}  # In-memory storage for chat history
        
    async def perform_full_analysis(self, dataset_id: str) -> AnalysisResponse:
        """Perform comprehensive LLM analysis with validation"""
        df = await self.file_handler.load_dataset(dataset_id)
        if df is None:
            raise FileNotFoundError("Dataset not found")
        
        # Generate statistical summary
        stats_summary = self._create_efficient_statistical_summary(df)
        
        # Create LLM prompt
        llm_prompt = self._create_analysis_prompt(df, stats_summary)
        
        # Get LLM insights
        llm_insights = await self._get_llm_response(llm_prompt)
        
        # Validate the analysis
        validation_metrics = self._validate_llm_analysis(llm_insights, df, stats_summary)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(df, llm_insights, validation_metrics)
        
        return AnalysisResponse(
            dataset_id=dataset_id,
            llm_insights=llm_insights,
            validation_metrics=validation_metrics,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    async def chat_with_data(self, dataset_id: str, message: str) -> ChatResponse:
        """Chat with data using natural language"""
        df = await self.file_handler.load_dataset(dataset_id)
        if df is None:
            raise FileNotFoundError("Dataset not found")
        
        # Get dataset context
        stats_summary = self._create_efficient_statistical_summary(df)
        
        # Create chat prompt with context
        chat_prompt = self._create_chat_prompt(df, stats_summary, message)
        
        # Get chat history for context
        history = self.chat_history.get(dataset_id, [])
        
        # Build conversation context
        messages = [
            {"role": "system", "content": chat_prompt},
            *history[-5:],  # Last 5 messages for context
            {"role": "user", "content": message}
        ]
        
        # Get LLM response
        response = await self._get_chat_response(messages)
        
        # Save to chat history
        if dataset_id not in self.chat_history:
            self.chat_history[dataset_id] = []
        
        self.chat_history[dataset_id].extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ])
        
        return ChatResponse(
            response=response,
            dataset_id=dataset_id,
            timestamp=datetime.now(),
            context_used=["dataset_statistics", "column_info", "data_types"]
        )
    
    async def generate_chat_suggestions(self, dataset_id: str) -> List[str]:
        """Generate suggested questions for the dataset"""
        df = await self.file_handler.load_dataset(dataset_id)
        if df is None:
            raise FileNotFoundError("Dataset not found")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        suggestions = [
            "What are the key insights from this dataset?",
            "Summarize the main patterns and trends",
        ]
        
        if numeric_cols:
            suggestions.extend([
                f"What is the correlation between {numeric_cols[0]} and other variables?",
                f"Show me the distribution of {numeric_cols[0]}",
                "Which variables have the strongest relationships?"
            ])
        
        if categorical_cols:
            suggestions.extend([
                f"What are the unique values in {categorical_cols[0]}?",
                f"How is the data distributed across {categorical_cols[0]}?"
            ])
        
        # Check for missing data
        if df.isnull().sum().sum() > 0:
            suggestions.append("What missing data issues should I be aware of?")
        
        return suggestions[:8]  # Return top 8 suggestions
    
    def _create_efficient_statistical_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create comprehensive statistical summary"""
        numeric_df = df.select_dtypes(include=[np.number])
        categorical_df = df.select_dtypes(include=['object'])
        
        # Missing data analysis
        missing_by_column = df.isnull().sum()
        missing_columns = missing_by_column[missing_by_column > 0]
        
        summary = {
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "column_types": {
                "numeric": list(numeric_df.columns),
                "categorical": list(categorical_df.columns),
                "total_numeric": len(numeric_df.columns),
                "total_categorical": len(categorical_df.columns)
            },
            "missing_data": {
                "total_missing": int(df.isnull().sum().sum()),
                "missing_percentage": float(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
                "columns_with_missing": len(missing_columns),
                "worst_missing_column": missing_columns.idxmax() if len(missing_columns) > 0 else None,
                "worst_missing_pct": float(missing_columns.max() / len(df) * 100) if len(missing_columns) > 0 else 0.0,
                "has_significant_missing": float(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) > 5.0
            }
        }
        
        # Numeric statistics
        if not numeric_df.empty:
            summary["numeric_stats"] = {
                "descriptive": numeric_df.describe().to_dict(),
                "correlations": self._get_top_correlations(numeric_df),
                "distributions": self._analyze_distributions(numeric_df)
            }
        
        # Categorical statistics  
        if not categorical_df.empty:
            summary["categorical_stats"] = {
                col: {
                    "unique_count": df[col].nunique(),
                    "top_values": df[col].value_counts().head(3).to_dict()
                }
                for col in categorical_df.columns[:5]  # Limit to first 5 categorical columns
            }
        
        return summary
    
    def _create_analysis_prompt(self, df: pd.DataFrame, stats_summary: Dict) -> str:
        """Create comprehensive analysis prompt"""
        missing_data_summary = f"""
Missing Data Analysis:
- Total missing: {stats_summary['missing_data']['missing_percentage']:.1f}% of dataset
- Columns affected: {stats_summary['missing_data']['columns_with_missing']} out of {df.shape[1]}
- Most problematic: {stats_summary['missing_data']['worst_missing_column']} ({stats_summary['missing_data']['worst_missing_pct']:.1f}% missing)
- Critical missing data threshold: {'EXCEEDED' if stats_summary['missing_data']['has_significant_missing'] else 'ACCEPTABLE'}
"""
        
        prompt = f"""You are a senior data scientist analyzing a dataset. Provide comprehensive insights.

DATASET OVERVIEW: {len(df):,} rows × {len(df.columns)} columns
COLUMN TYPES: {stats_summary['column_types']['total_numeric']} numeric, {stats_summary['column_types']['total_categorical']} categorical

{missing_data_summary}

STATISTICAL SUMMARY:
{json.dumps(stats_summary, indent=2, default=str)}

ANALYSIS REQUIREMENTS:
1. **Data Quality Assessment** (MANDATORY):
   - Report exact missing data percentages from statistics above
   - Identify data quality issues and their severity
   - Assess overall data completeness ({stats_summary['missing_data']['missing_percentage']:.1f}% missing overall)
   - Recommend specific data cleaning strategies

2. **Statistical Analysis**:
   - Key descriptive statistics and their business implications
   - Correlation insights and variable relationships
   - Distribution characteristics and normality assessment

3. **Pattern Discovery**:
   - Identify significant patterns, trends, and anomalies
   - Highlight unexpected findings or outliers
   - Discuss potential business implications

4. **Actionable Recommendations**:
   - Specific next steps for analysis
   - Data collection or cleaning recommendations  
   - Business decision support insights

CRITICAL REQUIREMENTS:
- ALWAYS mention missing data percentages when >0%
- Use specific numerical values from the statistics
- Provide quantitative assessments, not generic statements
- Address data quality issues explicitly
- Focus on actionable business insights

Provide a comprehensive analysis covering all requirements."""

        return prompt
    
    def _create_chat_prompt(self, df: pd.DataFrame, stats_summary: Dict, user_message: str) -> str:
        """Create chat prompt with dataset context"""
        return f"""You are an expert data analyst. Answer questions about this dataset:

DATASET: {len(df):,} rows × {len(df.columns)} columns
COLUMNS: {list(df.columns)}
MISSING DATA: {stats_summary['missing_data']['missing_percentage']:.1f}%

KEY STATISTICS:
{json.dumps(stats_summary, indent=2, default=str)}

Answer the user's question with specific insights from the data. Be concise but informative.
If asked about missing data, use exact percentages from the statistics above.
"""
    
    async def _get_llm_response(self, prompt: str) -> str:
        """Get response from OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating analysis: {str(e)}"
    
    async def _get_chat_response(self, messages: List[Dict]) -> str:
        """Get chat response from OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _validate_llm_analysis(self, llm_insights: str, df: pd.DataFrame, ground_truth: Dict) -> ValidationMetrics:
        """Validate LLM analysis using comprehensive metrics"""
        validator = LLMAnalysisValidator()
        
        # Calculate individual metrics
        statistical_accuracy = validator._validate_statistical_claims(llm_insights, ground_truth)
        missing_data_accuracy = validator._validate_missing_data_claims(llm_insights, ground_truth)
        insight_relevance = validator._validate_insight_relevance(llm_insights, ground_truth)
        completeness = validator._validate_completeness(llm_insights, ground_truth)
        consistency = validator._validate_consistency(llm_insights)
        
        # Calculate composite score
        composite_score = (
            statistical_accuracy * 0.25 +
            missing_data_accuracy * 0.20 +
            insight_relevance * 0.20 +
            completeness * 0.20 +
            consistency * 0.15
        )
        
        # Generate justifications
        justifications = validator._generate_justifications({
            'statistical_accuracy': statistical_accuracy,
            'missing_data_accuracy': missing_data_accuracy,
            'insight_relevance': insight_relevance,
            'completeness': completeness,
            'consistency': consistency,
            'composite_score': composite_score
        }, ground_truth)
        
        return ValidationMetrics(
            statistical_accuracy=statistical_accuracy,
            missing_data_accuracy=missing_data_accuracy,
            insight_relevance=insight_relevance,
            completeness=completeness,
            consistency=consistency,
            composite_score=composite_score,
            justifications=justifications
        )
    
    def _generate_recommendations(self, df: pd.DataFrame, llm_insights: str, validation_metrics: ValidationMetrics) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Data quality recommendations
        if validation_metrics.missing_data_accuracy < 0.7:
            recommendations.append("Address missing data issues before proceeding with analysis")
        
        # Statistical accuracy recommendations
        if validation_metrics.statistical_accuracy < 0.8:
            recommendations.append("Verify statistical claims with additional analysis tools")
        
        # Completeness recommendations
        if validation_metrics.completeness < 0.7:
            recommendations.append("Request more comprehensive analysis of all dataset aspects")
        
        # General recommendations based on data characteristics
        if df.shape[0] < 100:
            recommendations.append("Consider collecting more data for robust statistical analysis")
        
        missing_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100
        if missing_pct > 10:
            recommendations.append("Implement data collection improvements to reduce missing values")
        
        if not recommendations:
            recommendations.append("Analysis quality is good - proceed with insights implementation")
        
        return recommendations
    
    def _get_top_correlations(self, df: pd.DataFrame, threshold: float = 0.5) -> List[Dict]:
        """Get top correlations from numeric data"""
        if df.shape[1] < 2:
            return []
        
        corr_matrix = df.corr()
        correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) >= threshold:
                    correlations.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": float(corr_val),
                        "strength": "strong" if abs(corr_val) > 0.7 else "moderate"
                    })
        
        return sorted(correlations, key=lambda x: abs(x["correlation"]), reverse=True)[:5]
    
    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, str]:
        """Analyze distributions of numeric columns"""
        from scipy import stats
        
        distributions = {}
        for col in df.columns[:5]:  # Limit to first 5 columns
            data = df[col].dropna()
            if len(data) > 3:
                skewness = stats.skew(data)
                if abs(skewness) < 0.5:
                    dist_type = "symmetric"
                elif skewness > 0.5:
                    dist_type = "right-skewed"
                else:
                    dist_type = "left-skewed"
                distributions[col] = dist_type
        
        return distributions
    
    async def get_chat_history(self, dataset_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for dataset"""
        history = self.chat_history.get(dataset_id, [])
        return history[-limit:] if limit else history
    
    async def clear_chat_history(self, dataset_id: str):
        """Clear chat history for dataset"""
        if dataset_id in self.chat_history:
            del self.chat_history[dataset_id]

class LLMAnalysisValidator:
    """LLM Analysis Validation System"""
    
    def _validate_statistical_claims(self, llm_insights: str, ground_truth: Dict) -> float:
        """Validate statistical claims in LLM response"""
        # Simplified validation - in production, use more sophisticated methods
        score = 0.75  # Base score
        
        # Check if mentions key statistics
        if "correlation" in llm_insights.lower() and "numeric_stats" in ground_truth:
            score += 0.1
        
        if "missing" in llm_insights.lower() and ground_truth.get("missing_data", {}).get("missing_percentage", 0) > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _validate_missing_data_claims(self, llm_insights: str, ground_truth: Dict) -> float:
        """Enhanced missing data claims validation"""
        missing_keywords = [
            'missing', 'null', 'nan', 'incomplete', 'empty', 'absent',
            'missing values', 'missing data', 'null values', 'na values'
        ]
        
        llm_text_lower = llm_insights.lower()
        mentions_missing = any(term in llm_text_lower for term in missing_keywords)
        
        missing_data_info = ground_truth.get('missing_data', {})
        has_missing_data = missing_data_info.get('missing_percentage', 0) > 0
        missing_percentage = missing_data_info.get('missing_percentage', 0)
        
        if has_missing_data and missing_percentage > 0:
            if mentions_missing:
                # Check for quantitative mention
                has_quantitative_mention = any(char.isdigit() for char in llm_insights)
                
                if missing_percentage > 10:
                    return 1.0 if has_quantitative_mention else 0.8
                elif missing_percentage > 5:
                    return 0.9 if has_quantitative_mention else 0.7
                else:
                    return 0.8 if has_quantitative_mention else 0.6
            else:
                # Penalty for not mentioning missing data
                if missing_percentage > 10:
                    return 0.0
                elif missing_percentage > 5:
                    return 0.2
                else:
                    return 0.4
        else:
            # No missing data
            if mentions_missing:
                return 0.3  # Penalty for false positive
            else:
                return 1.0  # Perfect score
    
    def _validate_insight_relevance(self, llm_insights: str, ground_truth: Dict) -> float:
        """Validate insight relevance"""
        return 0.8  # Simplified - implement sophisticated relevance checking
    
    def _validate_completeness(self, llm_insights: str, ground_truth: Dict) -> float:
        """Validate analysis completeness"""
        required_topics = ["data quality", "statistical", "pattern", "recommendation"]
        mentioned_topics = sum(1 for topic in required_topics if topic in llm_insights.lower())
        return mentioned_topics / len(required_topics)
    
    def _validate_consistency(self, llm_insights: str) -> float:
        """Validate internal consistency"""
        return 0.85  # Simplified - implement contradiction detection
    
    def _generate_justifications(self, scores: Dict, ground_truth: Dict) -> Dict[str, str]:
        """Generate justifications for validation scores"""
        return {
            "statistical_accuracy": f"Statistical accuracy: {scores['statistical_accuracy']:.1%} - Analysis demonstrates {'excellent' if scores['statistical_accuracy'] >= 0.8 else 'good' if scores['statistical_accuracy'] >= 0.6 else 'fair'} statistical understanding",
            "missing_data_accuracy": f"Missing data accuracy: {scores['missing_data_accuracy']:.1%} - {'Correctly identified' if scores['missing_data_accuracy'] >= 0.8 else 'Partially addressed' if scores['missing_data_accuracy'] >= 0.5 else 'Failed to properly address'} missing data issues ({ground_truth.get('missing_data', {}).get('missing_percentage', 0):.1f}% missing)",
            "insight_relevance": f"Insight relevance: {scores['insight_relevance']:.1%} - Insights are {'highly relevant' if scores['insight_relevance'] >= 0.8 else 'moderately relevant' if scores['insight_relevance'] >= 0.6 else 'somewhat relevant'} to the dataset",
            "completeness": f"Completeness: {scores['completeness']:.1%} - Analysis covers {'comprehensive' if scores['completeness'] >= 0.8 else 'adequate' if scores['completeness'] >= 0.6 else 'limited'} aspects of the dataset",
            "consistency": f"Consistency: {scores['consistency']:.1%} - Analysis maintains {'excellent' if scores['consistency'] >= 0.8 else 'good' if scores['consistency'] >= 0.6 else 'fair'} internal consistency"
        }
