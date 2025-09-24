import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_smooth_ecommerce_dataset():
    """Generate a smooth e-commerce dataset with minimal price fluctuations and 10-day forecast"""
    
    # Product catalog with base prices
    products = [
        {"name": "iPhone 16", "base_price": 79999, "category": "smartphones"},
        {"name": "Samsung Galaxy S26 Ultra", "base_price": 124999, "category": "smartphones"},
        {"name": "Google Pixel 10 Pro", "base_price": 84999, "category": "smartphones"},
        {"name": "OnePlus 14", "base_price": 69999, "category": "smartphones"},
        {"name": "Dell XPS 15", "base_price": 189999, "category": "laptops"},
        {"name": "Apple MacBook Air (M4)", "base_price": 114999, "category": "laptops"},
        {"name": "HP Spectre x360", "base_price": 144999, "category": "laptops"},
        {"name": "Lenovo Legion 5 Pro", "base_price": 129999, "category": "laptops"},
        {"name": "Sony WH-1000XM6 Headphones", "base_price": 32990, "category": "audio"},
        {"name": "Apple AirPods Pro 3", "base_price": 24900, "category": "audio"},
        {"name": "Bose QuietComfort Ultra Earbuds", "base_price": 26900, "category": "audio"},
        {"name": "JBL Flip 7 Speaker", "base_price": 12990, "category": "audio"},
        {"name": "Apple Watch Series 11", "base_price": 42900, "category": "wearables"},
        {"name": "Samsung Galaxy Watch 8", "base_price": 28999, "category": "wearables"},
        {"name": "Fitbit Charge 7", "base_price": 15999, "category": "wearables"},
        {"name": "Garmin Forerunner 965", "base_price": 59999, "category": "wearables"},
        {"name": "iPad Pro 13-inch (M4)", "base_price": 109999, "category": "tablets"},
        {"name": "Samsung Galaxy Tab S10 Ultra", "base_price": 94999, "category": "tablets"},
        {"name": "Microsoft Surface Pro 11", "base_price": 124999, "category": "tablets"},
        {"name": "Nothing Tab (1)", "base_price": 32999, "category": "tablets"}
    ]
    
    # Retailer configurations
    retailers = {
        "Amazon.in": {"discount_factor": 0.95, "variation": 0.02},  # 5% avg discount, 2% variation
        "Flipkart": {"discount_factor": 0.93, "variation": 0.025},  # 7% avg discount, 2.5% variation
        "RelianceDigital": {"discount_factor": 0.97, "variation": 0.015},  # 3% avg discount, 1.5% variation
        "Croma": {"discount_factor": 0.96, "variation": 0.02}  # 4% avg discount, 2% variation
    }
    
    # Generate historical data (last 90 days) + forecast (next 30 days)
    start_date = datetime.now() - timedelta(days=90)
    end_date = datetime.now() + timedelta(days=30)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    
    # For each product, create smooth price trends
    for product in products:
        base_price = product["base_price"]
        
        # Create a more complex trend with multiple components
        # Long-term seasonal trend
        seasonal_trend = np.sin(np.linspace(0, 2*np.pi, len(date_range))) * 0.04
        # Market volatility trend
        volatility_trend = np.sin(np.linspace(0, 4*np.pi, len(date_range))) * 0.02
        # Random walk component for more realistic price movements
        random_walk = np.cumsum(np.random.normal(0, 0.005, len(date_range)))
        random_walk = random_walk - random_walk[0]  # Start at zero
        
        # Combine trends
        combined_trend = seasonal_trend + volatility_trend + random_walk
        
        for i, date in enumerate(date_range):
            # Apply combined trend
            seasonal_price = base_price * (1 + combined_trend[i])
            
            for retailer, config in retailers.items():
                # Apply retailer-specific pricing with minimal daily variation
                retailer_base = seasonal_price * config["discount_factor"]
                
                # Different variation for forecast vs historical
                is_forecast = date > datetime.now()
                if is_forecast:
                    # Slightly more variation in forecast to show uncertainty
                    daily_variation = random.uniform(-config["variation"] * 1.2, config["variation"] * 1.2)
                else:
                    # Small daily variation for historical data
                    daily_variation = random.uniform(-config["variation"], config["variation"])
                
                final_price = retailer_base * (1 + daily_variation)
                
                # Add market events and promotions
                if not is_forecast:
                    # Weekend discounts (more realistic for historical)
                    if date.weekday() in [5, 6]:  # Weekend
                        final_price *= random.uniform(0.97, 0.99)
                    
                    # Month-end sales
                    if date.day >= 28:
                        final_price *= random.uniform(0.95, 0.98)
                
                # Add small random walk component for smooth transitions
                if i > 0:
                    # Get previous price for this product-retailer combo
                    prev_entries = [d for d in data if d["product_name"] == product["name"] and d["retailer"] == retailer]
                    if prev_entries:
                        prev_price = prev_entries[-1]["price_inr"]
                        # Limit price change based on historical vs forecast
                        max_change_pct = 0.015 if not is_forecast else 0.025  # Less change for historical
                        max_change = prev_price * max_change_pct
                        price_change = random.uniform(-max_change, max_change)
                        final_price = prev_price + price_change
                
                # Ensure price doesn't go below reasonable threshold
                min_price = base_price * 0.8  # Never below 20% discount
                final_price = max(final_price, min_price)
                
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "product_name": product["name"],
                    "retailer": retailer,
                    "price_inr": round(final_price, 2),
                    "category": product["category"],
                    "is_forecast": date > datetime.now()
                })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Sort by date and product for better organization
    df = df.sort_values(['date', 'product_name', 'retailer']).reset_index(drop=True)
    
    # Save historical data (excluding forecast flag for main dataset)
    historical_df = df[df['is_forecast'] == False].drop(['category', 'is_forecast'], axis=1)
    output_file = "../backend/data/ecommerce_price_dataset_corrected.csv"
    historical_df.to_csv(output_file, index=False)
    
    # Save forecast data separately
    forecast_df = df[df['is_forecast'] == True].drop(['category', 'is_forecast'], axis=1)
    forecast_file = "../backend/data/price_forecast_30_days.csv"
    forecast_df.to_csv(forecast_file, index=False)
    
    print(f"\n✅ Smooth dataset generated successfully!")
    print(f"📊 Historical records: {len(historical_df):,}")
    print(f"🔮 Forecast records: {len(forecast_df):,}")
    print(f"📁 Historical data saved to: {output_file}")
    print(f"📁 Forecast data saved to: {forecast_file}")
    
    # Show price stability analysis for sample products
    print(f"\n📈 Price Stability Analysis (last 30 days):")
    recent_data = historical_df[historical_df['date'] >= (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')]
    
    for product_name in ["iPhone 16", "Dell XPS 15", "Sony WH-1000XM6 Headphones"]:
        product_data = recent_data[recent_data['product_name'] == product_name]
        if not product_data.empty:
            price_std = product_data.groupby('retailer')['price_inr'].std().mean()
            price_mean = product_data['price_inr'].mean()
            stability_pct = (price_std / price_mean) * 100
            print(f"  • {product_name}: {stability_pct:.1f}% price variation")
    
    # Show 10-day forecast summary
    print(f"\n🔮 30-Day Price Forecast Preview:")
    forecast_summary = forecast_df.groupby(['product_name', 'retailer'])['price_inr'].agg(['min', 'max', 'mean']).round(2)
    print("Top deals expected (lowest average prices):")
    
    # Show top 10 best deals in forecast
    best_deals = forecast_df.groupby(['product_name', 'retailer'])['price_inr'].mean().sort_values().head(10)
    for (product, retailer), avg_price in best_deals.items():
        print(f"  • {product} at {retailer}: ₹{avg_price:,.2f}")
    
    print(f"\n📈 Price Movement Analysis (30-day forecast):")
    # Show products with biggest expected price changes
    current_prices = historical_df[historical_df['date'] == historical_df['date'].max()].groupby('product_name')['price_inr'].mean()
    forecast_avg_prices = forecast_df.groupby('product_name')['price_inr'].mean()
    
    price_changes = {}
    for product in current_prices.index:
        if product in forecast_avg_prices.index:
            current = current_prices[product]
            forecast = forecast_avg_prices[product]
            change_pct = ((forecast - current) / current) * 100
            price_changes[product] = change_pct
    
    # Show biggest expected changes
    sorted_changes = sorted(price_changes.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
    for product, change_pct in sorted_changes:
        direction = "📈 increase" if change_pct > 0 else "📉 decrease"
        print(f"  • {product}: {direction} of {abs(change_pct):.1f}%")
    
    return df

if __name__ == "__main__":
    generate_smooth_ecommerce_dataset()