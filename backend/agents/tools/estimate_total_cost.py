import random
from typing import Optional


def estimate_total_cost(product_name: str, site: str, address: Optional[str] = None) -> dict:
    """
    Estimate total cost including shipping, taxes, and any fees.
    """
    base_price = round(random.uniform(500, 50000), 2)
    shipping = 0 if random.random() > 0.7 else round(random.uniform(50, 200), 2)
    taxes = round(base_price * 0.18, 2)
    total = base_price + shipping + taxes
    return {
        "base_price": base_price,
        "shipping": shipping,
        "taxes": taxes,
        "total": total
    }
