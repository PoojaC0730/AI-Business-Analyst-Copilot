import plotly.express as px
import pandas as pd

def generate_chart(df: pd.DataFrame, chart_rec: dict = None):
    """
    Smart Chart Generator: Uses detailed LLM visual blueprints (sorting, orientation, color grouping,
    stacked/grouped modes, and strategic red arrow annotations) if available, falling back to heuristics.
    """
    if df is None or df.empty or len(df.columns) < 2:
        return None
        
    # Attempt to use LLM Chart Recommendation Blueprint First
    try:
        if chart_rec and chart_rec.get("type"):
            c_type = chart_rec.get("type").lower()
            x_col = chart_rec.get("x_col")
            y_col = chart_rec.get("y_col")
            title = chart_rec.get("title", "Generated Chart")
            
            # Ensure the LLM didn't hallucinate column keys
            if x_col in df.columns and y_col in df.columns:
                
                # 1. Apply Sorting Config
                sorting = chart_rec.get("sorting")
                if sorting in ["descending", "ascending"]:
                    df = df.sort_values(by=y_col, ascending=(sorting == "ascending"))
                    
                # 2. Extract Color Groupings
                color_col = chart_rec.get("color_col")
                if color_col not in df.columns:
                    color_col = None
                    
                barmode = chart_rec.get("barmode", "group").lower()
                if barmode not in ["group", "stack", "overlay"]:
                    barmode = "group"
                    
                # 3. Handle Chart Orientation Swap (for horizontal bars)
                orientation = chart_rec.get("orientation", "v").lower()
                if orientation == "h" and c_type == "bar":
                    plotly_x = y_col
                    plotly_y = x_col
                else:
                    plotly_x = x_col
                    plotly_y = y_col
                    orientation = "v"
                
                # 4. Generate Plotly Figure
                if c_type == "line":
                    # Sort lines by x values for correct line continuity
                    df_sorted = df.sort_values(by=x_col) if not sorting else df
                    fig = px.line(df_sorted, x=plotly_x, y=plotly_y, color=color_col, title=title, markers=True)
                elif c_type == "pie":
                    fig = px.pie(df, names=plotly_x, values=plotly_y, title=title, hole=0.4)
                elif c_type == "scatter":
                    fig = px.scatter(df, x=plotly_x, y=plotly_y, color=color_col, title=title)
                else:
                    fig = px.bar(df, x=plotly_x, y=plotly_y, color=color_col, barmode=barmode,
                                 orientation=orientation, title=title, text_auto='.2s')
                
                # 5. Apply Premium Themes (White Transparency, clean fonts, grid suppression)
                fig.update_layout(
                    template="plotly_white",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter, -apple-system, sans-serif", size=12),
                    margin=dict(l=20, r=20, t=55, b=20)
                )
                
                # Mute grid lines for clean BI workspace
                if orientation == "h" and c_type == "bar":
                    fig.update_xaxes(gridcolor="#F0F2F6")
                    fig.update_yaxes(showgrid=False, linecolor="#E6E9EF")
                else:
                    fig.update_xaxes(showgrid=False, linecolor="#E6E9EF")
                    fig.update_yaxes(gridcolor="#F0F2F6")
                    
                # 6. Apply McKinsey Strategic Annotation Arrow Layer
                ann_text = chart_rec.get("annotation_text")
                ann_x = chart_rec.get("annotation_x")
                ann_y = chart_rec.get("annotation_y")
                
                if ann_text and ann_x is not None and ann_y is not None:
                    # Switch target coordinate mappings for horizontal charts
                    if orientation == "h" and c_type == "bar":
                        target_x = ann_y
                        target_y = ann_x
                    else:
                        target_x = ann_x
                        target_y = ann_y
                        
                    # Verify target values exist in dataframe to prevent drawing off-canvas
                    x_exists = df[x_col].astype(str).eq(str(ann_x)).any() if x_col in df.columns else False
                    
                    if x_exists or c_type == "line":
                        fig.add_annotation(
                            x=target_x,
                            y=target_y,
                            text=ann_text,
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1,
                            arrowwidth=2,
                            arrowcolor="#EF4444", # Strategic red pointer arrow
                            ax=30,
                            ay=-40,
                            bgcolor="#FEE2E2", # Soft light-red background
                            bordercolor="#EF4444",
                            borderwidth=1,
                            borderpad=4,
                            font=dict(size=10, color="#B91C1C")
                        )
                
                return fig
    except Exception:
        pass # Fallback to heuristics if LLM recommendation fails
        
    # --- HEURISTICS FALLBACK LAYER ---
    date_col = next((col for col in df.columns if 'date' in col.lower() or df[col].dtype == 'datetime64[ns]'), None)
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(exclude=['number', 'datetime64[ns]']).columns.tolist()
    
    if not num_cols:
        return None
        
    y_col = num_cols[0]
    
    try:
        if date_col:
            df_sorted = df.sort_values(by=date_col)
            fig = px.line(df_sorted, x=date_col, y=y_col, title=f"Trend of {y_col.replace('_', ' ').title()} over Time", markers=True)
            
        elif cat_cols:
            x_col = cat_cols[0]
            unique_count = len(df[x_col].unique())
            if 0 < unique_count <= 5 and df[y_col].min() >= 0:
                fig = px.pie(df, names=x_col, values=y_col, title=f"Share of {y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}", hole=0.4)
            else:
                fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}", text_auto='.2s')
                
        else:
            fig = px.bar(df, y=y_col, title=f"{y_col.replace('_', ' ').title()}")
            
        # Standard Visual Theme Polish
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, -apple-system, sans-serif", size=12),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        fig.update_xaxes(showgrid=False, linecolor="#E6E9EF")
        fig.update_yaxes(gridcolor="#F0F2F6")
        return fig
    except Exception:
        return None
