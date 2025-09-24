
import asyncio
import random
from typing import Any


async def scrape_price_tool(product_name: str, site: str) -> dict[str, Any]:
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