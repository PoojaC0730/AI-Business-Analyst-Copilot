import streamlit as st
import os
from utils.llm_sql import generate_sql
from utils.validator import is_safe_sql
from utils.db import execute_sql
from utils.explain import explain_sql
from utils.charts import generate_chart
from utils.confidence import calculate_confidence
from utils.root_cause import analyze_root_cause
from utils.narrative import generate_narrative
from utils.suggestions import generate_suggestions
from utils.clarifier import detect_ambiguity
from data.generate_data import generate_sales_data
import sqlite3

if not os.path.exists("sales.db"):
    df_gen = generate_sales_data(5000)
    conn = sqlite3.connect("sales.db")
    df_gen.to_sql("sales", conn, if_exists="replace", index=False)
    conn.close()

# Set page configuration
st.set_page_config(page_title="AI Business Analyst Copilot", layout="wide")

# PHASE 3 — Build Streamlit UI
st.title("📊 AI Business Analyst Copilot")
st.markdown("##### *Ask business questions in plain English, translate to safe SQL, and get strategic analytical insights.*")

# Initialize session state variables
if "query" not in st.session_state:
    st.session_state.query = ""
if "auto_submit" not in st.session_state:
    st.session_state.auto_submit = False
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []
if "clarification_data" not in st.session_state:
    st.session_state.clarification_data = None

def set_query(new_query):
    st.session_state.query = new_query
    st.session_state.auto_submit = True
    st.session_state.clarification_data = None

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
    
    st.markdown("---")
    st.subheader("💡 Example Questions")
    if st.button("📉 Why did West revenue fall?"):
        set_query("Why did West region revenue fall in April 2023?")
    if st.button("🏆 Top 5 low-profit products"):
        set_query("Top 5 low-profit products")
    if st.button("📅 Monthly revenue trend"):
        set_query("Show monthly sales and revenue trend")
    if st.button("⚖️ Compare East vs West revenue"):
        set_query("Compare East region vs West region revenue in 2023")

# Input Box
question = st.text_input(
    "Ask a business question", 
    value=st.session_state.query,
    placeholder="Why did West region revenue fall in April?"
)
st.session_state.query = question

# Analyze Button & State check
analyze_clicked = st.button("Analyze")

if analyze_clicked or st.session_state.auto_submit:
    # Reset auto submit trigger
    st.session_state.auto_submit = False
    
    if question:
        # Step 1: Detect ambiguity before generating SQL (PHASE 13)
        with st.spinner("Analyzing query clarity..."):
            clarity_result = detect_ambiguity(question, api_key=user_api_key)
            
        if clarity_result.get("is_ambiguous"):
            # Store ambiguity structure in state to render choice buttons
            st.session_state.clarification_data = clarity_result
        else:
            # Not ambiguous: run standard analytics pipeline
            st.session_state.clarification_data = None
            
            with st.spinner("Analyzing business data..."):
                try:
                    # PHASE 4 — Natural Language to SQL
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
                            # PHASE 6 — Execute SQL
                            df = execute_sql(sql_query)
                            
                            # PHASE 10 — Calculate Trust / Confidence Score
                            trust_score = calculate_confidence(df, sql_query, question)
                            
                            # PHASE 7 — Explain SQL Layer
                            explanation = explain_sql(question, sql_query, api_key=user_api_key)
                                
                            # PHASE 9 — Root Cause Analysis Layer
                            rc_analysis = analyze_root_cause(question, api_key=user_api_key)
                                
                            # PHASE 11 — Analyst Narrative Mode
                            executive_narrative = generate_narrative(question, sql_query, df, api_key=user_api_key)
                                
                            # PHASE 12 — Suggested Next Questions
                            suggestions = generate_suggestions(question, sql_query, df, api_key=user_api_key)
                            
                            # Package into analysis record
                            record = {
                                "question": question,
                                "sql_query": sql_query,
                                "df": df,
                                "trust_score": trust_score,
                                "explanation": explanation,
                                "rc_analysis": rc_analysis,
                                "executive_narrative": executive_narrative,
                                "suggestions": suggestions
                            }
                            
                            # Push into history (cap at last 5)
                            st.session_state.analysis_history.insert(0, record)
                            st.session_state.analysis_history = st.session_state.analysis_history[:5]
                            
                except Exception:
                    st.error("⚠️ **Could not understand the request.** Try asking about revenue, profit, units, products, or regions.")

# --- RENDER CLARIFIER UI (PHASE 13) ---
if st.session_state.clarification_data:
    clarity = st.session_state.clarification_data
    
    st.markdown("---")
    st.info(f"💡 **Clarification Required:** {clarity['clarification_prompt']}")
    
    def apply_clarity(resolved_q):
        st.session_state.clarification_data = None
        # Completely replace the query with the resolved query to prevent infinite loops
        set_query(resolved_q)
        
    cols = st.columns(4)
    for idx, opt in enumerate(clarity["options"]):
        with cols[idx]:
            st.button(
                opt["label"],
                on_click=apply_clarity,
                args=(opt["resolved_query"],),
                key=f"clarity_btn_{idx}"
            )

# --- RENDER ANALYSIS TIMELINE WORKSPACE (PHASE 14) ---
if st.session_state.analysis_history:
    latest = st.session_state.analysis_history[0]
    
    st.markdown("---")
    st.subheader(f"📊 Current Analysis: *{latest['question']}*")
    
    df = latest["df"]
    
    # Empty Results Guard
    if df is None or df.empty:
        st.info("🔍 **No matching data found for this query.** Try adjusting date ranges or clearing active dimension filters.")
    else:
        # STRICT REORDERED LAYOUT SEQUENCE
        
        # 1. Explainable SQL Section
        with st.expander("💡 1. Explainable SQL & Interpretation", expanded=True):
            st.markdown("**Generated SQL Query:**")
            st.code(latest["sql_query"], language="sql")
            
            exp = latest["explanation"]
            col_logic, col_filt = st.columns(2)
            with col_logic:
                st.markdown("**Interpretation Logic:**")
                for logic in exp.get("interpretation", []):
                    st.markdown(f"- {logic}")
            with col_filt:
                st.markdown("**Filters Applied:**")
                for filt in exp.get("filters", []):
                    st.markdown(f"- {filt}")
                    
        # 2. Confidence Score Banner
        trust = latest["trust_score"]
        score_level = trust.get("score")
        score_reason = trust.get("reason")
        if score_level == "High":
            st.success(f"🔒 **Trust Score: High** — {score_reason}")
        elif score_level == "Medium":
            st.warning(f"🔒 **Trust Score: Medium** — {score_reason}")
        else:
            st.error(f"🔒 **Trust Score: Low** — {score_reason}")
            
        # 3. Results Table
        with st.expander("📋 3. Raw Results Data Table", expanded=True):
            st.dataframe(df, use_container_width=True)
            
        # 4. Visualization Layer
        with st.expander("📊 4. Visual Insights", expanded=True):
            chart = generate_chart(df, latest["explanation"].get("chart_recommendation"))
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("Could not generate a chart for this data shape.")
                
        # 5. Root Cause Analysis (dynamic if POP comparison query)
        rc = latest["rc_analysis"]
        if rc and rc.get("is_comparison"):
            with st.expander("🔍 5. Root Cause Comparison Analysis", expanded=True):
                if rc.get("error"):
                    st.error(rc.get("error"))
                else:
                    m_col1, m_col2, m_col3 = st.columns(3)
                    with m_col1:
                        st.metric(
                            label=f"Previous {rc['metric'].title()} ({rc['previous_period']['name']})", 
                            value=f"{rc['total_prev']:,.0f}"
                        )
                    with m_col2:
                        st.metric(
                            label=f"Current {rc['metric'].title()} ({rc['current_period']['name']})", 
                            value=f"{rc['total_curr']:,.0f}",
                            delta=f"{rc['change']:+,.0f} ({rc['pct_change']:.1f}%)"
                        )
                    with m_col3:
                        st.metric(
                            label="Primary Dimension Factor",
                            value=rc['top_drivers'][0]['value'] if rc['top_drivers'] else "N/A",
                            delta=f"{rc['top_drivers'][0]['pct_contribution']:.1f}% contribution" if rc['top_drivers'] else None,
                            delta_color="normal"
                        )
                    st.markdown("---")
                    st.markdown(rc.get("summary"))
                    
        # 6. Analyst Narrative Card
        st.markdown("##### 👩‍💼 6. Executive Strategic Takeaway")
        st.info(latest["executive_narrative"])
        
        # 7. Suggested Questions (context carried over)
        sug = latest["suggestions"]
        if sug:
            st.markdown("##### 🚀 7. Suggested Follow-up Actions")
            cols = st.columns(len(sug))
            for idx, item in enumerate(sug):
                with cols[idx]:
                    st.button(
                        item["label"], 
                        on_click=set_query, 
                        args=(item["query"],), 
                        key=f"sug_latest_btn_{idx}"
                    )

    # RENDER PREVIOUS HISTORY TIMELINE (PHASE 14 COLLAPSIBLIES)
    if len(st.session_state.analysis_history) > 1:
        st.markdown("---")
        st.subheader("📜 Investigation History Timeline")
        st.write("Review previous findings in your continuous analysis session:")
        
        for idx, hist in enumerate(st.session_state.analysis_history[1:]):
            hist_id = idx + 1
            with st.expander(f"🔍 Analysis {hist_id}: {hist['question']}", expanded=False):
                st.info(hist["executive_narrative"])
                st.code(hist["sql_query"], language="sql")
                
                col_tbl, col_cht = st.columns(2)
                with col_tbl:
                    st.markdown("**Data Sample (First 5 Rows):**")
                    st.dataframe(hist["df"].head(5), use_container_width=True)
                with col_cht:
                    st.markdown("**Chart Preview:**")
                    h_chart = generate_chart(hist["df"], hist["explanation"].get("chart_recommendation"))
                    if h_chart:
                        st.plotly_chart(h_chart, use_container_width=True, key=f"hist_chart_{hist_id}")
                    else:
                        st.info("No chart preview available.")



