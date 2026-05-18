import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def generate_sql(user_question, api_key=None):
    """
    Converts a natural language business question into a SQLite SQL query.
    """
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        return "Error: GROQ_API_KEY not found in environment variables or UI."

    client = Groq(api_key=api_key)
    
    prompt = f"""
    You are an expert data analyst.
    Convert user request into SQLite SQL.
    
    Table:
    sales(date, region, city, product, category, customer_type, units, revenue, profit)
    
    Return SQL only. Do not include any explanation or markdown formatting unless it is a code block.
    
    Example User Prompt: Top 5 low profit products in West
    Example Return:
    SELECT product, SUM(profit) total_profit
    FROM sales
    WHERE region='West'
    GROUP BY product
    ORDER BY total_profit ASC
    LIMIT 5;
    
    User Request: {user_question}
    """
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are an expert data analyst who returns only SQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        
        sql = response.choices[0].message.content.strip()
        
        # Clean up common LLM formatting
        if "```sql" in sql:
            sql = sql.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql:
            sql = sql.split("```")[1].split("```")[0].strip()
            
        return sql
    except Exception as e:
        return f"Error: {str(e)}"
