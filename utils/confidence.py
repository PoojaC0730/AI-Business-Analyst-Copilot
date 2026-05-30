import pandas as pd
import re
from datetime import datetime

def calculate_confidence(df: pd.DataFrame, sql: str, question: str) -> dict:
    """
    Programmatically calculates a reliability score for the analyzed data.
    Returns a dictionary with 'score', 'reason', and 'color'.
    """
    # 1. Handle empty datasets
    if df is None or df.empty:
        return {
            "score": "Low",
            "reason": "No data returned from the database for this query.",
            "color": "red"
        }
        
    row_count = len(df)
    score = "High"
    reasons = []
    
    # 2. Row Count Analysis
    if row_count < 15:
        score = "Low"
        reasons.append(f"Very small sample size ({row_count} rows returned)")
    elif row_count < 150:
        score = "Medium"
        reasons.append(f"Limited dataset size ({row_count} rows returned)")
    else:
        reasons.append("Large dataset size")

    # 3. Date / Time Completeness Analysis
    date_col = next((col for col in df.columns if "date" in col.lower()), None)
    if date_col and row_count >= 5:
        try:
            # Parse dates
            df_dates = pd.to_datetime(df[date_col])
            min_dt = df_dates.min()
            max_dt = df_dates.max()
            
            # If min and max cover some span
            days_span = (max_dt - min_dt).days + 1
            unique_days = df_dates.nunique()
            
            if days_span > 5:
                coverage = unique_days / days_span
                if coverage < 0.85:
                    # Incomplete days detected!
                    month_name = min_dt.strftime("%B")
                    # Downgrade score
                    if score == "High":
                        score = "Medium"
                    
                    reasons.append(f"{month_name} data incomplete ({unique_days}/{days_span} active days available)")
                else:
                    reasons.append(f"Complete date coverage across active days")
        except Exception:
            pass # Keep going if date parsing fails

    # 4. Standard Deviation / Signal Variance Analysis
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    if num_cols and row_count >= 5:
        primary_num = num_cols[0]
        std_val = df[primary_num].std()
        mean_val = df[primary_num].mean()
        
        if pd.isna(std_val) or std_val == 0:
            if score == "High":
                score = "Medium"
            reasons.append("Weak statistical signal (zero variance in numeric results)")
        elif mean_val > 0:
            cv = std_val / mean_val
            if cv < 0.05:
                # Standard deviation is extremely low compared to the mean
                if score == "High":
                    score = "Medium"
                reasons.append("Low statistical variance detected")
            else:
                reasons.append("Strong variance signal")
                
    # 5. Clean up reasons and formulate final response
    # Choose color
    if score == "High":
        color = "green"
        # Filter reasons to keep summary clean
        display_reason = "Reliable dataset with complete date coverage."
        # If there are specific warnings, prioritize them
        warnings = [r for r in reasons if "incomplete" in r or "variance" in r]
        if warnings:
            display_reason = warnings[0]
    elif score == "Medium":
        color = "orange"
        warnings = [r for r in reasons if "incomplete" in r or "variance" in r or "limited" in r]
        display_reason = warnings[0] if warnings else "Limited dataset size."
    else:
        color = "red"
        warnings = [r for r in reasons if "small" in r or "No data" in r]
        display_reason = warnings[0] if warnings else "Insufficient data returned."

    return {
        "score": score,
        "reason": display_reason,
        "color": color
    }
