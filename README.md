# 📊 AI Business Analyst Copilot

The **AI Business Analyst Copilot** is a state-of-the-art, Streamlit-based web application that acts as a cognitive analytical workspace. It translates complex natural language business questions into valid, secure SQLite queries, executes them against a local sales database, programmatically gauges statistical reliability, performs Period-over-Period (PoP) root cause driver analyses, and produces dynamic McKinsey-style visualizations alongside executive strategic summaries.

Designed as an **interactive analyst workspace**, it preserves investigation continuity using a stateful chronological timeline expander and dynamically carries over query filters so you can drill deeper into business questions seamlessly.

---

## 🌟 Core Features

### 1. Conversational Analytics Timeline (Phases 12 & 14)
*   **Stateful Workspace**: Instead of a simple search box that wipes previous screens, the copilot caches your last 5 analyses in Streamlit session state (`st.session_state.analysis_history`), presenting them chronologically in collapsible accordion expanders below a divider.
*   **Context Carryover**: Automatically rewrites suggested next questions using Groq to inherit parent metrics, filters, and timeframes (e.g. converting a suggested *"Show monthly trend"* into *"Show monthly revenue trend for West region in April"*).

### 2. Smart Ambiguity Clarification Engine (Phase 13)
*   **Cognitive Gatekeeper**: Gracefully catches ambiguous adjectives (e.g. *"bad products"*, *"worst region"*, *"top customers"*) before compiling SQL.
*   **Resolution Options**: Pauses execution and prompts you with 4 database-friendly metric options (Low Revenue, Low Profit, Declining Sales, Low Units). Clicking a choice completely replaces the query with a fully-resolved, unambiguous question, preventing infinite loops.

### 3. McKinsey-Style Intelligent Visualizations (Phases 8 & 14 Upgrades)
*   **Visualization Blueprints**: Dynamically configures sorting, orientation (preferring horizontal bars for categories to prevent label overlapping), and multi-dimensional color groupings automatically based on the returned data shape.
*   **McKinsey Annotation Arrow**: Draws a **striking red arrow pointer** directly at specific data coordinates with a custom callout box highlighting strategic findings (e.g. pointing directly to Laptop's drop).
*   **Premium Theme**: Transparent backgrounds that blend with Streamlit light/dark templates, muted grids, and modern fonts.

### 4. Period-over-Period (PoP) Root Cause Analysis (Phase 9)
*   **Business Driver Layer**: When comparing periods, it runs a Pandas contribution calculation across 4 dimensions: `category`, `product`, `city`, and `customer_type`. It ranks the top 3 drivers (most negative for dips, most positive for gains) and creates a strategic markdown summary card.

### 5. Executive Analyst Narrative Mode (Phase 11)
*   **Executive Translation**: Translates raw rows and charts into professional stakeholder narrative (strictly 2 to 3 sentences) focusing on strategic concepts (e.g. *pricing compression, volume gains, product mix shifting*) instead of dry raw list recitations.

### 6. Data-Driven Trust Score Engine (Phase 10)
*   **Statistical Integrity**: Rejects LLM self-reporting and programmatically computes data reliability (High, Medium, Low trust badges) by auditing query row size, active calendar date coverage (flagging under-85% spans as "incomplete"), and standard deviation coefficients.

### 7. Explainable SQL & Safety Layer (Phases 2, 5, 7)
*   **Full Explainability**: Deconstructs compiled SQL by showing prompt-to-schema field mappings, active SQL filters, and query formulation confidence.
*   **Audit Interceptor**: Runs regular expression validation to strictly block modifying keywords (`DROP`, `DELETE`, `ALTER`, `UPDATE`, `INSERT`, `TRUNCATE`) before database execution.

---

## 🛠️ Technology Stack

*   **UI Framework:** Streamlit (Stateful Session State Management)
*   **Cognitive Engines:** Groq API (`llama-3.3-70b-versatile` & Llama-based SQL models)
*   **Data Reshaping & Statistics:** Pandas, NumPy
*   **Visualizations:** Plotly Express
*   **Database:** SQLite (`sales.db`)

---

## ⚙️ Installation & Setup

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd "AI-Business-Analyst-Copilot"
    ```
2.  **Set Up a Virtual Environment & Dependencies**:
    ```bash
    python -m venv .venv
    # Activate virtual environment
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    
    pip install -r requirements.txt
    ```
3.  **Configure Environment Variables**:
    *   Create a `.env` file in the root directory.
    *   Add your Groq API Key: `GROQ_API_KEY=your_groq_api_key_here`. (Alternatively, you can input this directly in the Streamlit Sidebar).

---

## 🚀 Execution & Usage

### 1. Populate Synthetic Sales Data
Before running the application for the first time, populate the SQLite database with 5,000 synthetic rows containing seasonality and test trends (such as an April drop in the West region):
```bash
python data/generate_data.py
```

### 2. Run the Streamlit Workspace
Execute the main Streamlit application:
```bash
streamlit run app.py
```

---

## ⚡ Try These Sample Diagnostic Queries!

Open the dashboard and test the following scenarios to observe the copilot's deep analytical workspace capabilities:

1.  **Smart Clarifier (Phase 13)**:
    *   *Type*: `"show bad products"`
    *   *Result*: UI pauses, shows ambiguity alert, and prompts with 4 options. Click `"💸 Low Profit"`. It completely rewrites the query to *"Show top 5 products by total profit in 2023"* and auto-runs, outputting a descending horizontal bar chart with a red McKinsey-style annotation arrow!
2.  **McKinsey Annotation Arrow (Phase 14 Upgrades)**:
    *   *Type*: `"Why did West region revenue fall in April 2023?"`
    *   *Result*: Look at the chart. You will see a **styled red callout arrow** pointing directly at the `"Laptop"` or `"Electronics"` coordinate stating *"Laptop contributed -50% to West region drop"*! A dedicated **🔍 Root Cause** comparison tab also spawns showing the $13.9M vs $1.9M delta statistics.
3.  **Multidimensional Chart Grouping**:
    *   *Type*: `"Compare monthly revenue for West region vs East region in 2023"`
    *   *Result*: Plotly renders a grouped multi-series line chart displaying months on the X-axis, color-coded by region with an automatic legend, showcasing East vs West performance side-by-side.
4.  **Chronological Timeline Expanders**:
    *   Execute 3 or 4 questions in sequence. Scroll down to see **"📜 Investigation History Timeline"**. Click on previous expanders to review old charts, SQL queries, raw data samples, and narratives archived below without cluttering the screen.
