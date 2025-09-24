import asyncio
import random
from pathlib import Path
from typing import Any, Dict

import pandas as pd


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