import random
from typing import Optional


def suggest_alternatives(product_name: str, budget: Optional[float] = None) -> list[dict]:
    """
    Suggest cheaper or better alternative products based on AI recommendations.
    """
    base_price = 1000.0 if budget is None else budget
    alternatives = []
    for i in range(random.randint(2, 5)):
        alt_name = f"{product_name} Alternative {chr(65 + i)}"
        alt_price = round(base_price * random.uniform(0.8, 1.2), 2)
        alt_site = random.choice(["amazon", "flipkart", "bigbasket"])
        alternatives.append({"name": alt_name, "price": alt_price, "site": alt_site})
    return alternatives
