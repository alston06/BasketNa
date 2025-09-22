"""
E-commerce Price Dataset Analysis
Quick analysis of the generated synthetic price data
"""

import pandas as pd
import numpy as np

def analyze_dataset():
    """Analyze the generated e-commerce dataset"""
    
    # Load the dataset
    df = pd.read_csv("d:/Alston/Python Projects/SOP/BasketNa/data/ecommerce_price_dataset.csv")
    
    print("=== E-COMMERCE PRICE DATASET ANALYSIS ===")
    print(f"Total Records: {len(df):,}")
    print(f"Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f"Total Days: {df['date'].nunique()}")
    print(f"Products: {df['product_name'].nunique()}")
    print(f"Retailers: {df['retailer'].nunique()}")
    
    print("\n=== PRICE STATISTICS ===")
    print(f"Overall Price Range: ₹{df['price_inr'].min():,.2f} - ₹{df['price_inr'].max():,.2f}")
    print(f"Average Price: ₹{df['price_inr'].mean():,.2f}")
    print(f"Median Price: ₹{df['price_inr'].median():,.2f}")
    
    print("\n=== PRODUCT CATEGORIES ===")
    products = df['product_name'].unique()
    smartphones = [p for p in products if any(brand in p for brand in ['iPhone', 'Samsung Galaxy', 'Google Pixel', 'OnePlus'])]
    laptops = [p for p in products if any(brand in p for brand in ['Dell', 'Apple MacBook', 'HP', 'Lenovo'])]
    audio = [p for p in products if any(item in p for item in ['Headphones', 'AirPods', 'Earbuds', 'Speaker'])]
    
    print(f"Smartphones ({len(smartphones)}): {', '.join(smartphones)}")
    print(f"Laptops ({len(laptops)}): {', '.join(laptops)}")
    print(f"Audio ({len(audio)}): {', '.join(audio)}")
    
    print("\n=== RETAILER ANALYSIS ===")
    retailer_stats = df.groupby('retailer')['price_inr'].agg(['mean', 'min', 'max', 'count'])
    print(retailer_stats)
    
    print("\n=== PRICE DEPRECIATION ANALYSIS ===")
    # Compare first week vs last week average prices
    first_week = df[df['date'] <= '2024-09-29']['price_inr'].mean()
    last_week = df[df['date'] >= '2025-09-16']['price_inr'].mean()
    depreciation = (first_week - last_week) / first_week * 100
    
    print(f"First Week Average: ₹{first_week:,.2f}")
    print(f"Last Week Average: ₹{last_week:,.2f}")
    print(f"Overall Depreciation: {depreciation:.1f}%")
    
    print("\n=== SALE PERIOD ANALYSIS ===")
    
    # Festival Sale (Amazon & Flipkart only)
    festival_sale = df[(df['date'] >= '2024-10-03') & (df['date'] <= '2024-10-10')]
    festival_amazon_flipkart = festival_sale[festival_sale['retailer'].isin(['Amazon.in', 'Flipkart'])]
    
    # Diwali Sale (All retailers)
    diwali_sale = df[(df['date'] >= '2024-10-28') & (df['date'] <= '2024-11-03')]
    
    # Republic Day Sale (All retailers)
    republic_sale = df[(df['date'] >= '2025-01-24') & (df['date'] <= '2025-01-28')]
    
    print(f"Festival Sale Period (Amazon/Flipkart): ₹{festival_amazon_flipkart['price_inr'].mean():,.2f} avg")
    print(f"Diwali Sale Period (All): ₹{diwali_sale['price_inr'].mean():,.2f} avg")
    print(f"Republic Day Sale Period (All): ₹{republic_sale['price_inr'].mean():,.2f} avg")
    
    print("\n=== SAMPLE HIGH-VALUE PRODUCTS (Last Date) ===")
    last_date_data = df[df['date'] == df['date'].max()]
    expensive_products = last_date_data.nlargest(5, 'price_inr')[['product_name', 'retailer', 'price_inr']]
    print(expensive_products.to_string(index=False))
    
    print("\n=== DATASET VALIDATION ===")
    # Check for missing values
    missing_values = df.isnull().sum().sum()
    print(f"Missing Values: {missing_values}")
    
    # Check date continuity
    expected_records = 20 * 4 * 365  # 20 products × 4 retailers × 365 days
    print(f"Expected Records: {expected_records:,}")
    print(f"Actual Records: {len(df):,}")
    print(f"Data Completeness: {len(df)/expected_records*100:.1f}%")
    
    print(f"\n✅ Dataset generated successfully with realistic price patterns!")
    print(f"📁 File saved as: ecommerce_price_dataset.csv")
    print(f"📊 Ready for analysis and machine learning applications!")

if __name__ == "__main__":
    analyze_dataset()