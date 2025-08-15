def calculate_iqr_for_columns(df: pd.DataFrame, query: str) -> str:
    """Calculate IQR for numeric columns with clean, simple formatting"""
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
