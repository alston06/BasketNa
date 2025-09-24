import random


def generate_price_trend_graph(product_name: str) -> str:
    """
    Generate a textual or ASCII representation of price trend graph.
    """
    prices = [random.randint(900, 1100) for _ in range(10)]
    max_price = max(prices)
    min_price = min(prices)
    graph = f"Price Trend for {product_name} (last 10 periods):\n"
    for height in range(10, 0, -1):
        line = "{:4d} | ".format(int(min_price + (max_price - min_price) * height // 10))
        for p in prices:
            if p >= min_price + (max_price - min_price) * (height - 1) / 10:
                line += "*"
            else:
                line += " "
            line += "  "
        graph += line + "\n"
    graph += "-----+" + "---" * len(prices) + "\n"
    graph += "     " + " ".join([f"P{i+1}" for i in range(len(prices))])
    return graph
