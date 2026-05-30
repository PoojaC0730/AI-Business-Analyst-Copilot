import os
from groq import Groq
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def generate_narrative(question: str, sql: str, df: pd.DataFrame, api_key: str = None) -> str:
    """
    Translates raw numbers and query results into a high-impact, strategic business executive narrative.
    """
    if df is None or df.empty:
        return "No data returned, so no narrative could be generated."
        
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        return "Analyst Narrative unavailable: Groq API key is missing."
        
    client = Groq(api_key=api_key)
    
    # Format data summary for context
    df_str = df.head(10).to_string(index=False)
    row_count = len(df)
    
    prompt = f"""
    You are an elite Senior Strategic Business Analyst and executive advisor.
    Synthesize the query output and natural language question into a high-impact, professional executive narrative.
    
    User Question: "{question}"
    SQL Executed: "{sql}"
    Total Rows Returned: {row_count}
    
    Data Returned (Top 10 rows):
    {df_str}
    
    Provide a concise, high-impact executive strategic narrative (strictly 2 to 3 sentences) explaining the deeper business implications, trends, anomalies, or trade-offs behind these numbers.
    
    Guidelines:
    - Do NOT simply repeat/list the raw numbers (e.g. avoid "Laptops sold 450 units, Keyboard sold 200").
    - Instead, convert the findings into strategic executive language. Focus on terms like "softened", "pricing compression", "volume gains", "product mix shifting", "operational headwind", "flat lining demand", "unbalanced contributor", etc.
    - Return ONLY the plain text narrative. Do not add titles, preambles, introductory comments (like "Here is the narrative:"), or markdown code blocks.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a senior strategic business analyst who communicates only in concise executive bullet points or brief strategic sentences."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3, # Slightly warmer temperature for better flow and diverse vocabulary
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Analyst Narrative unavailable: {str(e)}"
