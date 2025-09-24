from typing import Any, Dict

from .predict_price import predict_price_tool


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