import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def detect_ambiguity(question: str, api_key: str = None) -> dict:
    """
    Analyzes the user question using Groq to detect ambiguous business concepts
    (e.g., 'bad products', 'worst region', 'top customer') and generates clarification paths.
    """
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        # Fallback to bypass clarifier if no API key is set
        return {"is_ambiguous": False}
        
    client = Groq(api_key=api_key)
    
    schema_columns = "date, region, city, product, category, customer_type, units, revenue, profit"
    prompt = f"""
You are an ambiguity detection agent for a general AI data analyst system.

The system helps users analyze arbitrary datasets using natural language.

Your task:
Determine whether the user's request is sufficiently specific to generate a meaningful analytical query.

A request is ambiguous if it:
- uses vague descriptors without measurable criteria
- lacks analytical intent
- does not specify what should be measured or compared
- could reasonably mean multiple things

Examples of vague descriptors:
bad, good, best, worst, top, poor, weak, strong, unhealthy, declining, successful, high-performing

Examples of clear analytical metrics:
revenue, profit, sales, count, growth, trend, average, percentage, units sold, retention, churn

User question:
"{question}"

Dataset columns:
{schema_columns}

RULES:

1. If the request is sufficiently specific and measurable, return:
{{
  "is_ambiguous": false
}}

2. If clarification is needed, return:
{{
  "is_ambiguous": true,
  "ambiguity_reason": "...",
  "clarification_prompt": "...",
  "options": [
    {{
      "label": "...",
      "resolved_query": "..."
    }}
  ]
}}

Requirements for options:
- Generate exactly 4 options
- Each option must represent a different analytical interpretation
- Each resolved_query must be fully rewritten and unambiguous
- Do NOT append clarification text to the original query
- Use dataset column names when possible
- Keep labels short and UI-friendly
- Prefer measurable analytical language

Respond ONLY with valid JSON.
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful business intelligence clarifier that only returns structured JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        
        # Ensure schema structure exists
        if result.get("is_ambiguous") and (not result.get("options") or len(result.get("options")) < 2):
            result["is_ambiguous"] = False
            
        return result
    except Exception:
        # Graceful fallback: treat as non-ambiguous to prevent pipeline failure
        return {"is_ambiguous": False}
