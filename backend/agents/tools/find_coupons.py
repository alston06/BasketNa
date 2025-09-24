import random


def find_coupons(product_name: str) -> list[str]:
    """
    Search for available coupons or promo codes for the product.
    """
    coupons = [
        f"10% off on {product_name} with code BASKET10",
        f"₹500 cashback on {product_name} using HDFC card",
        f"Free shipping for {product_name} with FLIP20"
    ]
    random.shuffle(coupons)
    return coupons[:random.randint(1, 3)]
