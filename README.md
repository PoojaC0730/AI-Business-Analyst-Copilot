# 📊 AI Business Analyst Copilot

The AI Business Analyst Copilot is a Streamlit-based web application that allows users to ask business questions in natural language. It translates these questions into SQL queries, executes them against a local sales database, and provides analytical insights through interactive charts and data tables.

## ✨ Features

- **Natural Language to SQL:** Uses the Groq API to convert user questions (e.g., "Why did West region revenue fall in April?") into valid SQL queries.
- **Explainable AI Layer:** Breaks down the generated SQL by explaining the interpretation logic, filters applied, and providing a confidence score.
- **SQL Safety Validation:** Intercepts and blocks unsafe queries before they are executed.
- **Smart Chart Generation:** Automatically creates interactive Plotly visualizations based on the shape of the queried data.
- **Interactive Dashboard:** A seamless Streamlit UI featuring tabs for Insights & Charts, Raw Data, and Explainable SQL.
- **Synthetic Data Generation:** Includes a built-in script (`data/generate_data.py`) to generate a realistic `sales.db` database containing predefined trends and seasonality for testing.

## 🛠️ Technology Stack

- **Framework:** Streamlit
- **LLM Provider:** Groq
- **Database:** SQLite (`sales.db`)
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly

## ⚙️ Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone <repository-url>
   cd "AI Business Analyst Copilot"
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables:
   - Create a `.env` file in the root directory.
   - Add your Groq API key: `GROQ_API_KEY=your_api_key_here`. (Alternatively, you can enter this directly in the app's sidebar).

## 🚀 Usage

### 1. Generate Synthetic Data
Before running the app for the first time (or to regenerate fresh data), run the data generation script to create the `sales.db` database:

```bash
python data/generate_data.py
```

### 2. Run the Application

Run the Streamlit application using the following command:

```bash
streamlit run app.py
```

Once running, navigate to the localhost URL provided in your terminal, type a business question in the input field, and click "Analyze" to generate insights!

---

*More coming soon!*
