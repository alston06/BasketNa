import random
from datetime import datetime, timedelta


def fetch_historical_prices(product_name: str, site: str = "all") -> dict:
    """
    Fetch historical price data for a product across sites.
    """
    base_price = 1000.0
    if 'iphone' in product_name.lower():
        base_price = 60000.0
    elif 'laptop' in product_name.lower():
        base_price = 40000.0
    start_date = datetime.now() - timedelta(days=90)
    prices = {}
    current_price = base_price
    for i in range(91):
        date = start_date + timedelta(days=i)
        fluctuation = random.uniform(-0.05, 0.05)
        current_price *= (1 + fluctuation)
        prices[date.strftime('%Y-%m-%d')] = round(current_price, 2)
    return prices
