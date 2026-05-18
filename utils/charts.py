import plotly.express as px
import pandas as pd

def generate_chart(df: pd.DataFrame, chart_rec: dict = None):
    """
    Smart Chart Generator: Uses LLM recommendation if available, else falls back to heuristics to generate an appropriate Plotly chart.
    """
    if df is None or df.empty or len(df.columns) < 2:
        return None
        
    # Attempt to use LLM Chart Recommendation First
    try:
        if chart_rec and chart_rec.get("type"):
            c_type = chart_rec.get("type").lower()
            x_col = chart_rec.get("x_col")
            y_col = chart_rec.get("y_col")
            title = chart_rec.get("title", "Generated Chart")
            
            # Ensure the LLM didn't hallucinate columns
            if x_col in df.columns and y_col in df.columns:
                if c_type == "line":
                    fig = px.line(df.sort_values(by=x_col), x=x_col, y=y_col, title=title, markers=True)
                elif c_type == "pie":
                    fig = px.pie(df, names=x_col, values=y_col, title=title, hole=0.4)
                elif c_type == "scatter":
                    fig = px.scatter(df, x=x_col, y=y_col, title=title)
                else:
                    fig = px.bar(df, x=x_col, y=y_col, title=title, text_auto='.2s')
                
                fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
                return fig
    except Exception as e:
        pass # Fallback to heuristics if LLM recommendation fails
        
    # Heuristics for smart charting
    # Date column check
    date_col = next((col for col in df.columns if 'date' in col.lower() or df[col].dtype == 'datetime64[ns]'), None)
    
    # Numeric columns
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Categorical columns
    cat_cols = df.select_dtypes(exclude=['number', 'datetime64[ns]']).columns.tolist()
    
    if not num_cols:
        return None
        
    y_col = num_cols[0]
    
    try:
        if date_col:
            # If date trend -> Line chart
            # Sort by date just in case
            df_sorted = df.sort_values(by=date_col)
            fig = px.line(df_sorted, x=date_col, y=y_col, title=f"Trend of {y_col.replace('_', ' ').title()} over Time", markers=True)
            
        elif cat_cols:
            x_col = cat_cols[0]
            # Check unique count for Pie chart (e.g. share breakdown if 5 or fewer categories)
            unique_count = len(df[x_col].unique())
            if 0 < unique_count <= 5 and df[y_col].min() >= 0:
                fig = px.pie(df, names=x_col, values=y_col, title=f"Share of {y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}", hole=0.4)
            else:
                # If categorical + numeric -> Bar chart
                fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}", text_auto='.2s')
                
        else:
            # Fallback bar chart on index
            fig = px.bar(df, y=y_col, title=f"{y_col.replace('_', ' ').title()}")
            
        # UI Polish
        fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        return fig
    except Exception:
        return None
