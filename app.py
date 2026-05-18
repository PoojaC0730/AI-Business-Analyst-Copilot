import streamlit as st
import os
from utils.llm_sql import generate_sql
from utils.validator import is_safe_sql
from utils.db import execute_sql
from utils.explain import explain_sql
from utils.charts import generate_chart
from data.generate_data import create_database

if not os.path.exists("sales.db"):
    generate_sales_data()

# Set page configuration
st.set_page_config(page_title="AI Business Analyst Copilot", layout="wide")

# PHASE 3 — Build Streamlit UI
st.title("📊 AI Business Analyst Copilot")

# Sidebar for configuration (moved to top so it evaluates before button click)
with st.sidebar:
    st.header("⚙️ Settings")
    st.write("This copilot uses synthetic sales data to provide business insights.")
    user_api_key = st.text_input("Groq API Key", type="password", help="Enter your Groq API Key. If left blank, it will try to use the key from your .env file.")
    
    if not user_api_key and not os.getenv("GROQ_API_KEY"):
        st.warning("⚠️ Groq API Key missing! Please enter it above or in your .env file.")
        
    st.markdown("---")
    st.subheader("📚 Dataset Info")
    st.markdown("""
    The `sales` database contains the following columns:
    - **date**, **region**, **city**
    - **product**, **category**
    - **customer_type** (New/Repeat)
    - **units**, **revenue**, **profit**
    """)

# Input Box
question = st.text_input(
    "Ask a business question", 
    placeholder="Why did West region revenue fall in April?"
)

# Analyze Button
if st.button("Analyze"):
    if question:
        st.subheader("Analysis")
        
        # PHASE 4 — Natural Language to SQL
        with st.spinner("Analyzing with LLM..."):
            sql_query = generate_sql(question, api_key=user_api_key)
            
            if sql_query.startswith("Error"):
                st.error(sql_query)
                if "GROQ_API_KEY" in sql_query:
                    st.info("Please add your `GROQ_API_KEY` to the `.env` file or enter it in the sidebar.")
            else:
                # PHASE 5 — SQL Safety Validation
                if not is_safe_sql(sql_query):
                    st.error("Unsafe query blocked.")
                else:
                    try:
                        # PHASE 6 — Execute SQL
                        df = execute_sql(sql_query)
                        
                        # PHASE 7 — Explain SQL Layer
                        with st.spinner("Generating explanation..."):
                            explanation = explain_sql(question, sql_query, api_key=user_api_key)
                        
                        # UI POLISH: Set up Tabs
                        tab1, tab2, tab3 = st.tabs(["📊 Insights & Chart", "🔍 Raw Data", "💡 Explainable SQL"])
                        
                        with tab1:
                            # PHASE 8 — Smart Chart Generator
                            chart = generate_chart(df, explanation.get("chart_recommendation"))
                            if chart:
                                st.plotly_chart(chart, use_container_width=True)
                            else:
                                st.info("Could not generate a chart for this data shape. Check the Raw Data tab.")
                                
                        with tab2:
                            st.dataframe(df, use_container_width=True)
                            
                        with tab3:
                            # Show Card
                            st.markdown("##### User Prompt")
                            st.info(question)
                            
                            st.markdown("##### Generated SQL")
                            st.code(sql_query, language="sql")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("##### Interpretation Logic")
                                for logic in explanation.get("interpretation", []):
                                    st.markdown(f"- {logic}")
                                    
                            with col2:
                                st.markdown("##### Filters Applied")
                                for filt in explanation.get("filters", []):
                                    st.markdown(f"- {filt}")
                                    
                            st.metric(label="Confidence", value=f"{explanation.get('confidence', 0)}%")
                            
                    except Exception as e:
                        st.error(f"Error executing query: {e}")
    else:
        st.warning("Please enter a question to analyze.")


