import os
import json
from groq import Groq
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

DEFAULT_SUGGESTIONS = [
    {"label": "📈 Show monthly trend?", "query": "Show monthly sales and revenue trend"},
    {"label": "🏢 Want city-wise breakdown?", "query": "Breakdown total revenue and profit by city"},
    {"label": "👥 Show customer segment impact?", "query": "Show units and revenue split by customer segment"}
]

def generate_suggestions(question: str, sql: str, df: pd.DataFrame, api_key: str = None) -> list:
    """
    Dynamically generates 3 contextually relevant follow-up questions based on what the user asked
    and what query was executed. Exposes a list of dictionaries with 'label' and 'query'.
    """
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        return DEFAULT_SUGGESTIONS
        
    client = Groq(api_key=api_key)
    
    prompt = f"""
    You are an expert business intelligence architect designing a conversational analytics timeline.
    Based on the user's current business question and the SQL query executed, suggest exactly 3 contextually relevant, highly specific follow-up questions that the user might want to click next to drill deeper into the exact same investigation.
    
    User Question: "{question}"
    SQL Executed: "{sql}"
    
    CRITICAL RULE FOR Conversational Continuity:
    The suggested follow-up questions must carry over the timeframe, the active filters (like specific region, category, or customer segment), and the target metric from the original question. They should behave like 'continuing an investigation' rather than starting over completely.
    
    Example:
    If original question: "Why did West region revenue fall in April?"
    - Correct Label: "🏢 Show city breakdown" -> Correct Query: "Show city-wise revenue breakdown for West region in April" (Timeframe 'April', filter 'West region', metric 'revenue' inherited!)
    - Correct Label: "👉 Compare with East region" -> Correct Query: "Compare West region vs East region revenue in April"
    - Correct Label: "👥 Analyze customer segments" -> Correct Query: "Show customer segment impact on West region revenue in April"
    
    Database Columns available: date, region, city, product, category, customer_type, units, revenue, profit.
    
    Format the response as a JSON object containing a "suggestions" list of objects.
    Each object MUST have:
    - "label": A short, action-oriented button label prefixed with a relevant emoji (e.g. "🏢 Show city breakdown", "👉 Compare with East region", "📈 Show monthly trend"). Keep it under 35 characters.
    - "query": The exact, fully expanded natural language question containing the carried over context, to be executed when clicked.
    
    Respond ONLY with valid JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a business intelligence assistant that responds only in structured JSON formats."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        
        extracted = json.loads(response.choices[0].message.content.strip())
        suggestions = extracted.get("suggestions", [])
        
        if len(suggestions) >= 2:
            return suggestions[:3]
        return DEFAULT_SUGGESTIONS
    except Exception:
        return DEFAULT_SUGGESTIONS
