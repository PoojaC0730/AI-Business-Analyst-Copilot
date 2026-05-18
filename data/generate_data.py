import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta

def generate_sales_data(num_rows=5000):
    """
    Generates synthetic sales data with specific trends:
    - Seasonality (higher sales in Q4)
    - Weak April performance in the West region
    - Declining sales in the Electronics category over time
    - Drop in Repeat customer segments in the second half of the period
    """
    np.random.seed(42)
    
    regions = ['North', 'South', 'East', 'West']
    cities = ['Mumbai', 'Delhi', 'Ahmedabad', 'Pune', 'Bangalore']
    products = ['Laptop', 'Phone', 'Mouse', 'Keyboard', 'Monitor']
    categories = {
        'Laptop': 'Electronics', 
        'Phone': 'Electronics', 
        'Monitor': 'Electronics', 
        'Mouse': 'Accessories', 
        'Keyboard': 'Accessories'
    }
    customer_types = ['New', 'Repeat']
    
    # Generate dates across 2023 and early 2024
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=np.random.randint(0, 500)) for _ in range(num_rows)]
    
    data = []
    for date in dates:
        region = np.random.choice(regions)
        city = np.random.choice(cities)
        product = np.random.choice(products)
        category = categories[product]
        customer_type = np.random.choice(customer_types)
        
        # Base units
        units = np.random.randint(1, 20)
        
        # Base prices and profit margins
        prices = {'Laptop': 50000, 'Phone': 20000, 'Monitor': 10000, 'Mouse': 1000, 'Keyboard': 1500}
        margins = {'Laptop': 0.15, 'Phone': 0.12, 'Monitor': 0.18, 'Mouse': 0.30, 'Keyboard': 0.25}
        
        base_price = prices[product]
        revenue = units * base_price
        profit = revenue * margins[product]
        
        # 1. Apply Seasonality (Higher in Q4: Oct, Nov, Dec)
        if date.month in [10, 11, 12]:
            units = int(units * 1.8)
            
        # 2. Weak April West region
        if date.month == 4 and region == 'West':
            units = max(1, int(units * 0.2))
            
        # 3. Declining electronics sales (Decline starting mid-2023)
        days_since_start = (date - start_date).days
        if category == 'Electronics' and days_since_start > 200:
            # Linear decline factor from 1.0 to 0.4
            decline_factor = max(0.4, 1 - ((days_since_start - 200) / 300) * 0.6)
            units = max(1, int(units * decline_factor))
            
        # 4. Repeat customer drop (Decline starting in 2024)
        if customer_type == 'Repeat' and date.year == 2024:
            # Drop factor from 1.0 down to 0.3
            drop_factor = max(0.3, 1 - (date.month / 12) * 0.7)
            units = max(1, int(units * drop_factor))

        # Recalculate revenue and profit based on adjusted units
        revenue = units * base_price
        profit = revenue * margins[product]

        data.append([
            date.strftime('%Y-%m-%d'),
            region,
            city,
            product,
            category,
            customer_type,
            units,
            float(revenue),
            float(profit)
        ])
    
    df = pd.DataFrame(data, columns=[
        'date', 'region', 'city', 'product', 'category', 
        'customer_type', 'units', 'revenue', 'profit'
    ])
    
    return df

if __name__ == "__main__":
    print("Generating synthetic sales data...")
    df = generate_sales_data(5000)
    
    # Save to SQLite
    db_path = "sales.db"
    conn = sqlite3.connect(db_path)
    df.to_sql("sales", conn, if_exists="replace", index=False)
    conn.close()
    
    print(f"Successfully generated {len(df)} rows.")
    print(f"Database saved to: {db_path}")
    
    # Verify the table exists and show a few rows
    conn = sqlite3.connect(db_path)
    check_df = pd.read_sql("SELECT * FROM sales LIMIT 5", conn)
    print("\nSample Data:")
    print(check_df)
    conn.close()
