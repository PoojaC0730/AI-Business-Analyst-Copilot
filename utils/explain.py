import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def explain_sql(question, sql, api_key=None):
    """
    Analyzes the SQL query relative to the user question and returns a structured explanation.
    """
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        return {"interpretation": ["API key missing."], "filters": ["None"], "confidence": 0}
        
    client = Groq(api_key=api_key)
    
    prompt = f"""
    Analyze the following User Question and SQL Query.
    
    User Question: {question}
    SQL Query: {sql}
    
    Provide a JSON response with exactly these keys:
    - "interpretation": A list of short strings mapping the user question to SQL logic.
    - "filters": A list of short strings summarizing the WHERE/HAVING filters applied.
    - "confidence": An integer representing your confidence score (0-100) that this query correctly answers the question.
    - "chart_recommendation": A JSON object containing:
        - "type": One of "bar", "line", "pie", "scatter", or null.
        - "x_col": The exact column name from the SQL output for the X axis (or names for pie).
        - "y_col": The exact column name from the SQL output for the Y axis (or values for pie).
        - "title": A descriptive title for the chart.
    
    Respond ONLY with valid JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        return {
            "interpretation": [f"Error explaining SQL: {str(e)}"], 
            "filters": [], 
            "confidence": 0
        }
