"""
Simple forecast functionality for the minimal server
"""
import os
import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Any, Optional

def generate_forecast(product_id: str, data_path: str) -> Optional[Dict[str, Any]]:
    """
    Generate a simple price forecast for a product
    """
    if not os.path.exists(data_path):
        return None
    
    try:
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        # Product mapping
        product_mapping = {
            "P001": "iPhone 16",
            "P002": "Samsung Galaxy S26 Ultra", 
            "P003": "Google Pixel 10 Pro",
            "P004": "OnePlus 14",
            "P005": "Dell XPS 15",
            "P006": "Apple MacBook Air (M4)",
            "P007": "HP Spectre x360",
            "P008": "Lenovo Legion 5 Pro",
            "P009": "Sony WH-1000XM6 Headphones",
            "P010": "Apple AirPods Pro 3",
            "P011": "Bose QuietComfort Ultra Earbuds",
            "P012": "JBL Flip 7 Speaker",
            "P013": "Apple Watch Series 11",
            "P014": "Samsung Galaxy Watch 7",
            "P015": "Samsung 55-inch QLED TV",
            "P016": "LG C5 65-inch OLED TV",
            "P017": "Sony PlayStation 5 Pro",
            "P018": "Canon EOS R7 Camera",
            "P019": "DJI Mini 5 Pro Drone",
            "P020": "Logitech MX Master 4 Mouse"
        }
        
        product_name = product_mapping.get(product_id)
        if not product_name:
            return None
            
        # Filter data for this product
        product_df = df[df['product_name'] == product_name].copy()
        if product_df.empty:
            return None
        
        # Group by date and calculate average price across retailers
        daily_prices = product_df.groupby('date')['price_inr'].agg(['mean', 'min', 'max']).reset_index()
        daily_prices = daily_prices.sort_values('date')
        
        # Get last 30 days for trend analysis
        latest_date = daily_prices['date'].max()
        recent_data = daily_prices[daily_prices['date'] >= (latest_date - timedelta(days=30))]
        
        # Simple trend calculation
        if len(recent_data) >= 2:
            recent_prices = recent_data['mean'].values
            trend_slope = float((recent_prices[-1] - recent_prices[0]) / len(recent_prices))
        else:
            trend_slope = 0.0
        
        # Generate forecast for next 14 days
        current_price = float(daily_prices['mean'].iloc[-1])
        forecast_days = 14
        forecast_data = []
        
        for i in range(1, forecast_days + 1):
            forecast_date = latest_date + timedelta(days=i)
            
            # Simple linear trend with some randomness
            base_forecast = current_price + (trend_slope * i)
            
            # Add some market volatility (±5%)
            volatility = np.random.uniform(-0.05, 0.05)
            forecasted_price = base_forecast * (1 + volatility)
            
            # Confidence intervals (wider for future dates)
            confidence_width = 0.1 + (i * 0.01)  # Increasing uncertainty
            lower_bound = forecasted_price * (1 - confidence_width)
            upper_bound = forecasted_price * (1 + confidence_width)
            
            forecast_data.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "price": round(float(forecasted_price), 2),
                "lower": round(float(lower_bound), 2),
                "upper": round(float(upper_bound), 2)
            })
        
        # Historical data for chart
        history_data = []
        for _, row in daily_prices.tail(30).iterrows():
            history_data.append({
                "date": row['date'].strftime("%Y-%m-%d"),
                "price": round(float(row['mean']), 2),
                "lower": round(float(row['min']), 2),
                "upper": round(float(row['max']), 2)
            })
        
        # Determine if current price is a good deal
        recent_avg = float(recent_data['mean'].mean())
        current_latest = float(daily_prices['mean'].iloc[-1])
        is_good_deal = bool(current_latest < (recent_avg * 0.95))  # 5% below recent average
        
        return {
            "product_id": product_id,
            "product_name": product_name,
            "current_price": round(current_latest, 2),
            "trend": "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable",
            "forecast": forecast_data,
            "history": history_data,
            "is_good_deal": is_good_deal,
            "deal_reason": f"Current price ₹{current_latest:.0f} is below recent average ₹{recent_avg:.0f}" if is_good_deal else "",
            "forecast_summary": f"Expected to {'increase' if trend_slope > 0 else 'decrease' if trend_slope < 0 else 'remain stable'} over next 14 days"
        }
        
    except Exception as e:
        print(f"Forecast error: {e}")
        return None