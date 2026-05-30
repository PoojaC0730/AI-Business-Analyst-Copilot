import os
import json
import sqlite3
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
from utils.db import execute_sql

load_dotenv()

def analyze_root_cause(question: str, api_key: str = None) -> dict:
    """
    Performs a Period-over-Period (POP) root cause analysis to explain changes.
    Returns a dictionary of analysis metrics and top drivers.
    """
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        return {"is_comparison": False, "error": "Groq API key not provided."}
        
    client = Groq(api_key=api_key)
    
    # 1. Use LLM to extract target metric, periods, and filters
    prompt = f"""
    Analyze the following business question: "{question}"
    
    We want to perform a Period-over-Period (POP) root cause analysis to explain a change over time.
    Identify if the user is asking about a change, fall, rise, difference, or comparison over time.
    
    If the question is NOT asking to explain a change or make a comparison over time, return "is_comparison": false.
    
    If it is asking about a change, return "is_comparison": true, along with:
    - "metric": the column name under discussion (must be one of: "revenue", "profit", "units").
    - "current_period": {{
         "start": "YYYY-MM-DD",
         "end": "YYYY-MM-DD",
         "name": "e.g., April 2023"
      }} (Representing the later/target period in question. In our dataset, sales span 2023-01-01 to mid-2024. If not specified, default to the year 2023 or 2024 based on context).
    - "previous_period": {{
         "start": "YYYY-MM-DD",
         "end": "YYYY-MM-DD",
         "name": "e.g., March 2023"
      }} (Representing the baseline/previous period. If not explicitly specified, infer the immediate previous period of the exact same duration. For example, if current is April 2023 (30 days), previous should be March 2023 (31 days). If current is Q4 2023, previous should be Q3 2023).
    - "filters": A dictionary of simple matching dimensions (e.g. {{"region": "West"}} or {{"category": "Electronics"}}). Valid filter columns are: "region", "city", "product", "category", "customer_type".
    
    Respond ONLY with valid JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst assistant that responds only in structured JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        
        extracted = json.loads(response.choices[0].message.content.strip())
        
        if not extracted.get("is_comparison"):
            return {"is_comparison": False}
            
        metric = extracted.get("metric", "revenue").lower()
        if metric not in ["revenue", "profit", "units"]:
            metric = "revenue"
            
        curr_period = extracted.get("current_period", {})
        prev_period = extracted.get("previous_period", {})
        filters = extracted.get("filters", {})
        
        if not curr_period.get("start") or not prev_period.get("start"):
            return {"is_comparison": False, "reason": "Could not identify target date ranges."}
            
        # 2. Build parameterized query to fetch data for both ranges
        where_clauses = ["((date BETWEEN :prev_start AND :prev_end) OR (date BETWEEN :curr_start AND :curr_end))"]
        params = {
            "prev_start": prev_period["start"],
            "prev_end": prev_period["end"],
            "curr_start": curr_period["start"],
            "curr_end": curr_period["end"]
        }
        
        # Apply extracted filters
        for col, val in filters.items():
            col_lower = col.lower()
            if col_lower in ["region", "city", "product", "category", "customer_type"]:
                where_clauses.append(f"{col_lower} = :{col_lower}")
                params[col_lower] = val
                
        where_str = " AND ".join(where_clauses)
        sql = f"""
        SELECT date, region, city, product, category, customer_type, units, revenue, profit 
        FROM sales 
        WHERE {where_str}
        """
        
        # Execute query
        df = execute_sql(sql, params=params)
        
        if df.empty:
            return {
                "is_comparison": True,
                "error": "No matching database records found for the comparison periods.",
                "current_period": curr_period,
                "previous_period": prev_period
            }
            
        # 3. Separate into two dataframes for calculations
        curr_start, curr_end = curr_period["start"], curr_period["end"]
        prev_start, prev_end = prev_period["start"], prev_period["end"]
        
        curr_df = df[(df["date"] >= curr_start) & (df["date"] <= curr_end)]
        prev_df = df[(df["date"] >= prev_start) & (df["date"] <= prev_end)]
        
        total_curr = curr_df[metric].sum()
        total_prev = prev_df[metric].sum()
        
        change = total_curr - total_prev
        pct_change = (change / total_prev) * 100 if total_prev > 0 else 0
        
        # 4. Perform groupby calculations for dimensions
        dimensions = ["category", "product", "city", "customer_type"]
        drivers = []
        
        for dim in dimensions:
            curr_grp = curr_df.groupby(dim)[metric].sum()
            prev_grp = prev_df.groupby(dim)[metric].sum()
            
            # Align groups
            comparison = pd.DataFrame({"prev": prev_grp, "curr": curr_grp}).fillna(0)
            comparison["change"] = comparison["curr"] - comparison["prev"]
            comparison["pct_contribution"] = (comparison["change"] / total_prev) * 100 if total_prev > 0 else 0
            
            for val, row in comparison.iterrows():
                # Only include elements that actually contributed to the change
                if abs(row["change"]) > 0:
                    drivers.append({
                        "dimension": dim,
                        "value": val,
                        "prev_val": float(row["prev"]),
                        "curr_val": float(row["curr"]),
                        "change": float(row["change"]),
                        "pct_contribution": float(row["pct_contribution"])
                    })
                    
        # 5. Sort drivers based on sign of change
        if change < 0:
            # Sort ascending (most negative contribution first)
            drivers_sorted = sorted(drivers, key=lambda x: x["pct_contribution"])
        else:
            # Sort descending (most positive contribution first)
            drivers_sorted = sorted(drivers, key=lambda x: x["pct_contribution"], reverse=True)
            
        top_drivers = drivers_sorted[:3]
        
        # 6. Format Markdown Explanation Narrative
        direction = "dropped" if change < 0 else "increased"
        metric_title = metric.title()
        
        markdown_summary = f"📊 **{metric_title}** {direction} by **{abs(pct_change):.1f}%** "
        markdown_summary += f"(from **{total_prev:,.0f}** in *{prev_period['name']}* to **{total_curr:,.0f}** in *{curr_period['name']}*).\n\n"
        
        if top_drivers:
            markdown_summary += "##### Key Drivers of this Change:\n"
            for driver in top_drivers:
                dim_name = driver["dimension"].replace("_", " ").title()
                val_name = str(driver["value"])
                contrib = driver["pct_contribution"]
                sign = "" if contrib < 0 else "+"
                
                # Format friendly display
                markdown_summary += f"- 🎯 **{val_name}** ({dim_name}): **{sign}{contrib:.1f}%** contribution to the overall change.\n"
        else:
            markdown_summary += "*No strong individual dimension drivers detected for this change.*"
            
        return {
            "is_comparison": True,
            "metric": metric,
            "total_prev": float(total_prev),
            "total_curr": float(total_curr),
            "change": float(change),
            "pct_change": float(pct_change),
            "current_period": curr_period,
            "previous_period": prev_period,
            "top_drivers": top_drivers,
            "summary": markdown_summary
        }
        
    except Exception as e:
        return {
            "is_comparison": False,
            "error": f"Error performing root cause analysis: {str(e)}"
        }
