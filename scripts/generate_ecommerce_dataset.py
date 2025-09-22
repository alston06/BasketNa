"""
E-commerce Price Tracking Dataset Generator for India
Generates realistic synthetic price data for 20 electronic products across 4 retailers over 365 days
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Product definitions with realistic base prices in INR
PRODUCTS = {
    # Smartphones
    "iPhone 16": 89900,
    "Samsung Galaxy S26 Ultra": 124999,
    "Google Pixel 10 Pro": 84999,
    "OnePlus 14": 69999,
    
    # Laptops
    "Dell XPS 15": 189999,
    "Apple MacBook Air (M4)": 119900,
    "HP Spectre x360": 159999,
    "Lenovo Legion 5 Pro": 139999,
    
    # Audio
    "Sony WH-1000XM6 Headphones": 29990,
    "Apple AirPods Pro 3": 24900,
    "Bose QuietComfort Ultra Earbuds": 26990,
    "JBL Flip 7 Speaker": 9999,
    
    # Wearables
    "Apple Watch Series 11": 41900,
    "Samsung Galaxy Watch 7": 29999,
    
    # Home Entertainment
    "Samsung 55-inch QLED TV": 89999,
    "LG C5 65-inch OLED TV": 249999,
    "Sony PlayStation 5 Pro": 54990,
    
    # Cameras & Accessories
    "Canon EOS R7 Camera": 134999,
    "DJI Mini 5 Pro Drone": 89999,
    "Logitech MX Master 4 Mouse": 7995
}

RETAILERS = ["Amazon.in", "Flipkart", "RelianceDigital", "Croma"]

# Date range: September 23, 2024 to September 22, 2025 (365 days)
START_DATE = datetime(2024, 9, 23)
END_DATE = datetime(2025, 9, 22)

def generate_initial_prices():
    """Generate initial retailer-specific prices with slight variations"""
    initial_prices = {}
    
    for product, base_price in PRODUCTS.items():
        initial_prices[product] = {}
        for retailer in RETAILERS:
            # Add retailer-specific variation (±2-5%)
            variation = np.random.uniform(-0.05, 0.05)
            initial_prices[product][retailer] = base_price * (1 + variation)
    
    return initial_prices

def get_sale_events():
    """Define sale event periods and discounts"""
    return {
        # Great Indian Festival / Big Billion Days (Amazon & Flipkart only)
        "festival_sale": {
            "start": datetime(2024, 10, 3),
            "end": datetime(2024, 10, 10),
            "retailers": ["Amazon.in", "Flipkart"],
            "discount": (0.15, 0.30)  # 15-30% discount
        },
        
        # Diwali Sale (All retailers)
        "diwali_sale": {
            "start": datetime(2024, 10, 28),
            "end": datetime(2024, 11, 3),
            "retailers": RETAILERS,
            "discount": (0.10, 0.20)  # 10-20% discount
        },
        
        # Republic Day Sale (All retailers)
        "republic_day_sale": {
            "start": datetime(2025, 1, 24),
            "end": datetime(2025, 1, 28),
            "retailers": RETAILERS,
            "discount": (0.10, 0.15)  # 10-15% discount
        }
    }

def is_sale_period(date, sale_events):
    """Check if a date falls within any sale period and return applicable discounts"""
    active_sales = []
    
    for sale_name, sale_info in sale_events.items():
        if sale_info["start"] <= date <= sale_info["end"]:
            active_sales.append(sale_info)
    
    return active_sales

def calculate_correlation_factor(base_change, correlation=0.7):
    """Calculate correlated price change for other retailers"""
    # Correlated change with some noise
    correlated_change = base_change * correlation + np.random.normal(0, 0.002)
    return correlated_change

def generate_price_data():
    """Generate the complete price dataset"""
    initial_prices = generate_initial_prices()
    sale_events = get_sale_events()
    
    # Initialize current prices
    current_prices = {}
    for product in PRODUCTS:
        current_prices[product] = initial_prices[product].copy()
    
    # Store all data
    data = []
    
    # Generate data for each day
    current_date = START_DATE
    day_count = 0
    
    while current_date <= END_DATE:
        day_count += 1
        
        # Check for active sales
        active_sales = is_sale_period(current_date, sale_events)
        
        for product in PRODUCTS:
            # Calculate long-term depreciation (gradual decline over year)
            # Electronics depreciate about 15-25% per year
            yearly_depreciation = 0.20
            daily_depreciation = yearly_depreciation / 365
            depreciation_factor = 1 - (daily_depreciation * day_count)
            
            # Generate base daily change for the "lead" retailer (Amazon)
            daily_volatility = np.random.normal(0, 0.005)  # ±0.5% daily noise
            
            for retailer in RETAILERS:
                # Start with current price
                price = current_prices[product][retailer]
                
                # Apply depreciation
                price *= (1 - daily_depreciation)
                
                # Apply retailer-specific or correlated daily change
                if retailer == "Amazon.in":
                    # Amazon as the "lead" retailer
                    price *= (1 + daily_volatility)
                    base_change = daily_volatility
                else:
                    # Other retailers follow with correlation
                    correlated_change = calculate_correlation_factor(base_change)
                    price *= (1 + correlated_change)
                
                # Apply sale discounts if applicable
                for sale in active_sales:
                    if retailer in sale["retailers"]:
                        discount = np.random.uniform(sale["discount"][0], sale["discount"][1])
                        price *= (1 - discount)
                
                # Update current price
                current_prices[product][retailer] = price
                
                # Add to dataset
                data.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "product_name": product,
                    "retailer": retailer,
                    "price_inr": round(price, 2)
                })
        
        current_date += timedelta(days=1)
    
    return data

def main():
    """Generate and save the dataset"""
    print("Generating e-commerce price tracking dataset...")
    print(f"Products: {len(PRODUCTS)}")
    print(f"Retailers: {len(RETAILERS)}")
    print(f"Date range: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
    print(f"Expected records: {len(PRODUCTS) * len(RETAILERS) * 365}")
    
    # Generate data
    data = generate_price_data()
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_file = "d:/Alston/Python Projects/SOP/BasketNa/data/ecommerce_price_dataset.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\nDataset generated successfully!")
    print(f"Total records: {len(df)}")
    print(f"Saved to: {output_file}")
    
    # Display sample data
    print("\nSample data (first 10 rows):")
    print(df.head(10))
    
    # Display price statistics
    print(f"\nPrice statistics:")
    print(f"Min price: ₹{df['price_inr'].min():,.2f}")
    print(f"Max price: ₹{df['price_inr'].max():,.2f}")
    print(f"Average price: ₹{df['price_inr'].mean():,.2f}")
    
    # Show data distribution
    print(f"\nData distribution by retailer:")
    print(df['retailer'].value_counts())

if __name__ == "__main__":
    main()