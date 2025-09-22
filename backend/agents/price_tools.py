import asyncio
import random
import os
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

async def scrape_price_tool(product_name: str, site: str) -> Dict[str, Any]:
    """
    Scrape the current price of a product from a specific e-commerce site.
    For development, this returns mocked data with realistic variations.
    """
    print(f"🔍 Scraping price for '{product_name}' on {site}...")
    
    # Simulate network delay
    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    # Mock price data with realistic site-specific variations
    base_price = random.uniform(400, 1200)
    
    site_multipliers = {
        "Amazon": 1.0,
        "Flipkart": random.uniform(0.95, 1.05),
        "BigBasket": random.uniform(0.90, 1.10)
    }
    
    multiplier = site_multipliers.get(site, 1.0)
    price = round(base_price * multiplier, 2)
    
    # Generate realistic URLs
    site_urls = {
        "Amazon": f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}",
        "Flipkart": f"https://www.flipkart.com/search?q={product_name.replace(' ', '%20')}",
        "BigBasket": f"https://www.bigbasket.com/ps/?q={product_name.replace(' ', '%20')}"
    }
    
    url = site_urls.get(site, f"https://www.google.com/search?q={product_name}")
    
    return {
        "site": site,
        "price": price,
        "currency": "INR",
        "url": url,
        "availability": "In Stock",
        "timestamp": "now"
    }

async def predict_price_tool(product_id: str) -> Dict[str, Any]:
    """
    Predict future prices using ML models.
    For development, this returns mocked forecasts based on historical patterns.
    """
    print(f"🔮 Generating price predictions for product '{product_id}'...")
    
    # Simulate ML processing time
    await asyncio.sleep(random.uniform(1.0, 2.0))
    
    # Try to load actual data if available
    sample_data_path = Path(__file__).parent.parent / "data" / "sample_prices.csv"
    current_price = 500  # Default fallback
    
    try:
        df = pd.read_csv(sample_data_path)
        product_data = df[df['product_id'] == product_id]
        if not product_data.empty:
            current_price = float(product_data['price'].mean())
    except Exception:
        pass
    
    # Generate realistic predictions with decreasing confidence over time
    predictions = []
    base_price = current_price
    
    # Simulate different trend scenarios
    trend_scenarios = [
        {"name": "declining", "multipliers": [0.95, 0.92, 0.88, 0.85]},
        {"name": "stable", "multipliers": [0.98, 0.97, 0.96, 0.95]},
        {"name": "increasing", "multipliers": [1.02, 1.05, 1.08, 1.12]}
    ]
    
    chosen_trend = random.choice(trend_scenarios)
    timeframes = ["7 days", "14 days", "30 days", "60 days"]
    confidences = [0.85, 0.80, 0.75, 0.70]
    
    for i, (timeframe, multiplier, confidence) in enumerate(zip(timeframes, chosen_trend["multipliers"], confidences)):
        predicted_price = round(base_price * multiplier, 2)
        change_percent = round((multiplier - 1) * 100, 1)
        
        predictions.append({
            "timeframe": timeframe,
            "predicted_price": predicted_price,
            "currency": "INR",
            "confidence": confidence,
            "change_percent": change_percent,
            "change_direction": "decrease" if change_percent < 0 else "increase" if change_percent > 0 else "stable"
        })
    
    # Generate recommendation based on trend
    if chosen_trend["name"] == "declining":
        recommendation = "💡 Price is expected to drop. Consider waiting 1-2 weeks for a better deal."
    elif chosen_trend["name"] == "increasing":
        recommendation = "⚡ Price may rise soon. Consider buying now if you need this product."
    else:
        recommendation = "📊 Price is expected to remain stable. Buy when convenient."
    
    return {
        "product_id": product_id,
        "current_price": current_price,
        "currency": "INR",
        "predictions": predictions,
        "trend": chosen_trend["name"],
        "recommendation": recommendation,
        "generated_at": "now"
    }

async def calculate_drop_timeline_tool(product_id: str, target_discount: float = 10.0) -> Dict[str, Any]:
    """
    Calculate when a product price is likely to drop by a certain percentage.
    """
    print(f"📈 Calculating price drop timeline for product '{product_id}'...")
    
    # Get prediction data
    prediction_data = await predict_price_tool(product_id)
    current_price = prediction_data["current_price"]
    target_price = current_price * (1 - target_discount / 100)
    
    # Analyze predictions to find when target price might be reached
    predictions = prediction_data["predictions"]
    drop_timeline = None
    
    for pred in predictions:
        if pred["predicted_price"] <= target_price:
            drop_timeline = pred["timeframe"]
            break
    
    if drop_timeline:
        message = f"💰 Price likely to drop {target_discount}% (to ₹{target_price:.0f}) within {drop_timeline}"
        likelihood = "High" if predictions[0]["confidence"] > 0.8 else "Medium"
    else:
        message = f"📊 {target_discount}% drop not expected in the next 60 days based on current trends"
        likelihood = "Low"
    
    return {
        "product_id": product_id,
        "current_price": current_price,
        "target_discount_percent": target_discount,
        "target_price": target_price,
        "timeline": drop_timeline,
        "likelihood": likelihood,
        "message": message,
        "currency": "INR"
    }

async def compare_all_sites_tool(product_name: str) -> Dict[str, Any]:
    """
    Compare prices across all supported e-commerce sites.
    """
    print(f"🛒 Comparing prices for '{product_name}' across all sites...")
    
    sites = ["Amazon", "Flipkart", "BigBasket"]
    
    # Scrape all sites concurrently
    tasks = [scrape_price_tool(product_name, site) for site in sites]
    results = await asyncio.gather(*tasks)
    
    # Find best deal
    best_deal = min(results, key=lambda x: x["price"])
    
    # Calculate savings
    prices = [r["price"] for r in results]
    max_price = max(prices)
    min_price = min(prices)
    max_savings = round(max_price - min_price, 2)
    
    return {
        "product_name": product_name,
        "comparison": results,
        "best_deal": best_deal,
        "price_range": {
            "min": min_price,
            "max": max_price,
            "currency": "INR"
        },
        "max_savings": max_savings,
        "comparison_count": len(results)
    }