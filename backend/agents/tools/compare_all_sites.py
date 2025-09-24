import asyncio
from typing import Any, Dict

from .scrape_price import scrape_price_tool


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