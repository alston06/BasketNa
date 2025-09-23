import random
from datetime import datetime, timedelta

from config import settings
from pydantic_ai import Agent, Tool
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from transformers import pipeline

from .price_tools import (
    calculate_drop_timeline_tool,
    compare_all_sites_tool,
    predict_price_tool,
    scrape_price_tool,
)

sentiment_analyzer = pipeline("sentiment-analysis")

# New innovative tool implementations
# For demonstration, using generated fake data that mimics real scenarios.
# In a production environment, replace with actual scraping/API calls (e.g., using requests and BeautifulSoup for sites like pricehistory.app or camelcamelcamel.com).
# Ensure compliance with terms of service and legal requirements for scraping.

def fetch_historical_prices(product_name: str, site: str = "all") -> dict:
    """
    Fetch historical price data for a product across sites.
    
    Args:
        product_name: Name or URL of the product.
        site: Specific site (amazon, flipkart, bigbasket) or 'all'.
    
    Returns:
        A dictionary with timestamps as keys and prices (in INR) as values.
    """
    # Determine base price based on product name for realism
    base_price = 1000.0
    if 'iphone' in product_name.lower():
        base_price = 60000.0
    elif 'laptop' in product_name.lower():
        base_price = 40000.0
    # Generate 90 days of historical prices
    start_date = datetime.now() - timedelta(days=90)
    prices = {}
    current_price = base_price
    for i in range(91):
        date = start_date + timedelta(days=i)
        fluctuation = random.uniform(-0.05, 0.05)  # +/- 5% fluctuation
        current_price *= (1 + fluctuation)
        prices[date.strftime('%Y-%m-%d')] = round(current_price, 2)
    # In real implementation: Use requests to scrape from pricehistory.app or similar
    # Example:
    # import requests
    # from bs4 import BeautifulSoup
    # url = f"https://pricehistory.app/search?q={product_name}"
    # response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    # soup = BeautifulSoup(response.text, 'html.parser')
    # # Parse for historical data...
    return prices

def find_coupons(product_name: str) -> list[str]:
    """
    Search for available coupons or promo codes for the product.
    
    Args:
        product_name: Name of the product to find coupons for.
    
    Returns:
        List of coupon codes or descriptions.
    """
    # Fake coupons; in real: Scrape from coupon sites like CouponDunia or GrabOn
    coupons = [
        f"10% off on {product_name} with code BASKET10",
        f"₹500 cashback on {product_name} using HDFC card",
        f"Free shipping for {product_name} with FLIP20"
    ]
    random.shuffle(coupons)
    return coupons[:random.randint(1, 3)]

def summarize_reviews(product_name: str, site: str = "all") -> str:
    """
    Summarize user reviews for the product across sites using web scraping and basic sentiment analysis.
    
    Args:
        product_name: Name or URL of the product.
        site: Specific site or 'all'.
    
    Returns:
        A concise summary of reviews, including sentiment and key pros/cons.
    """
    import re

    import requests
    from bs4 import BeautifulSoup
    
    def clean_text(text):
        return re.sub(r'\s+', ' ', text).strip()
    
    from urllib.parse import quote
    def get_amazon_url(product_name):
        # This is a basic search URL for Amazon India
        return f"https://www.amazon.in/s?k={quote(product_name)}"
    def get_flipkart_url(product_name):
        return f"https://www.flipkart.com/search?q={quote(product_name)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    reviews = []
    ratings = []
    pros = set()
    cons = set()
    try:
        # Try Amazon first
        if site in ("all", "amazon"):
            search_url = get_amazon_url(product_name)
            resp = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Find first product link
            link = soup.select_one('a.a-link-normal.s-no-outline')
            href = link.get('href') if link else None
            if href and isinstance(href, str):
                product_url = "https://www.amazon.in" + href
                prod_resp = requests.get(product_url, headers=headers, timeout=10)
                prod_soup = BeautifulSoup(prod_resp.text, 'html.parser')
                # Get average rating
                rating_tag = prod_soup.select_one('span[data-asin][class*="averageStarRating"]') or prod_soup.select_one('span.a-icon-alt')
                if rating_tag:
                    rating_text = rating_tag.get_text()
                    match = re.search(r"([0-9.]+) out of 5", rating_text)
                    if match:
                        ratings.append(float(match.group(1)))
                # Get review snippets
                review_tags = prod_soup.select('span[data-hook="review-body"]')
                for tag in review_tags[:10]:
                    text = clean_text(tag.get_text())
                    reviews.append(text)
        # Try Flipkart if needed
        if (not reviews or site == "flipkart") and site in ("all", "flipkart"):
            search_url = get_flipkart_url(product_name)
            resp = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            link = soup.select_one('a._1fQZEK') or soup.select_one('a.s1Q9rs')
            href = link.get('href') if link else None
            if href and isinstance(href, str):
                product_url = "https://www.flipkart.com" + href
                prod_resp = requests.get(product_url, headers=headers, timeout=10)
                prod_soup = BeautifulSoup(prod_resp.text, 'html.parser')
                # Get average rating
                rating_tag = prod_soup.select_one('div._3LWZlK')
                if rating_tag:
                    try:
                        ratings.append(float(rating_tag.get_text()))
                    except Exception:
                        pass
                # Get review snippets
                review_tags = prod_soup.select('div.t-ZTKy')
                for tag in review_tags[:10]:
                    text = clean_text(tag.get_text())
                    reviews.append(text)

        # Use HuggingFace transformers for sentiment analysis

        sentiment_results = []
        for review in reviews:
            try:
                sentiment_results.append(sentiment_analyzer(review[:512])[0])
            except Exception:
                continue
        pos_count = sum(1 for r in sentiment_results if r['label'].lower().startswith('pos'))
        neg_count = sum(1 for r in sentiment_results if r['label'].lower().startswith('neg'))
        total_reviews = len(sentiment_results)
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
        sentiment = 0
        if total_reviews > 0:
            sentiment = int(100 * pos_count / (pos_count + neg_count + 1))
        # Extract key pros/cons using most common positive/negative words in positive/negative reviews
        from collections import Counter
        pros_words = []
        cons_words = []
        for i, review in enumerate(reviews):
            if i < len(sentiment_results):
                label = sentiment_results[i]['label'].lower()
                words = [w for w in re.findall(r'\w+', review.lower()) if len(w) > 3]
                if label.startswith('pos'):
                    pros_words.extend(words)
                elif label.startswith('neg'):
                    cons_words.extend(words)
        pros_common = [w for w, _ in Counter(pros_words).most_common(3)]
        cons_common = [w for w, _ in Counter(cons_words).most_common(3)]
        if total_reviews > 0:
            summary = f"Overall rating: {avg_rating if avg_rating else 'N/A'}/5 stars based on {total_reviews} reviews. Positive sentiment ({sentiment}%). "
            if pros_common:
                summary += f"Key pros: {', '.join(pros_common)}. "
            if cons_common:
                summary += f"Key cons: {', '.join(cons_common)}. "
            return summary.strip()
    except Exception as exc:
        print("⚠️ Error fetching or parsing reviews, returning fake data., ", exc)
    # Fallback to fake data if scraping fails
    stars = round(random.uniform(3.5, 5.0), 1)
    pros = ["Durable", "Good battery life", "Value for money"]
    cons = ["Expensive", "Slow charging", "Average camera"]
    return f"Overall rating: {stars}/5 stars based on {random.randint(100, 10000)} reviews. Positive sentiment (75%). Key pros: {', '.join(random.sample(pros, 2))}. Key cons: {', '.join(random.sample(cons, 1))}."

def check_stock_availability(product_name: str, site: str = "all") -> dict:
    """
    Check current stock availability across sites.
    
    Args:
        product_name: Name or URL of the product.
        site: Specific site or 'all'.
    
    Returns:
        Dictionary with site as key and availability status as value.
    """
    # Fake availability; in real: Scrape product pages for stock info
    sites = ["amazon", "flipkart", "bigbasket"] if site == "all" else [site]
    availability = {}
    for s in sites:
        status = random.choice(["In stock", "Out of stock", "Limited stock", "Pre-order"])
        availability[s] = status
    return availability

from typing import Optional


def suggest_alternatives(product_name: str, budget: Optional[float] = None) -> list[dict]:
    """
    Suggest cheaper or better alternative products based on AI recommendations.
    
    Args:
        product_name: Original product name.
        budget: Optional maximum budget in INR.
    
    Returns:
        List of dictionaries with alternative product details (name, price, site).
    """
    # Fake alternatives; in real: Use similarity search via embeddings (e.g., SentenceTransformers) or API recommendations
    base_price = 1000.0 if budget is None else budget
    alternatives = []
    for i in range(random.randint(2, 5)):
        alt_name = f"{product_name} Alternative {chr(65 + i)}"
        alt_price = round(base_price * random.uniform(0.8, 1.2), 2)
        alt_site = random.choice(["amazon", "flipkart", "bigbasket"])
        alternatives.append({"name": alt_name, "price": alt_price, "site": alt_site})
    return alternatives

def estimate_total_cost(product_name: str, site: str, address: 'Optional[str]' = None) -> dict:
    """
    Estimate total cost including shipping, taxes, and any fees.
    
    Args:
        product_name: Name or URL of the product.
        site: Specific site.
        address: Optional shipping address for accurate shipping calculation.
    
    Returns:
        Dictionary with breakdown: base_price, shipping, taxes, total.
    """
    # Fake costs; in real: Scrape product page for base price, use shipping APIs (e.g., Shiprocket) for estimates
    base_price = round(random.uniform(500, 50000), 2)
    shipping = 0 if random.random() > 0.7 else round(random.uniform(50, 200), 2)  # Free shipping sometimes
    taxes = round(base_price * 0.18, 2)  # 18% GST
    total = base_price + shipping + taxes
    return {
        "base_price": base_price,
        "shipping": shipping,
        "taxes": taxes,
        "total": total
    }

def generate_price_trend_graph(product_name: str) -> str:
    """
    Generate a textual or ASCII representation of price trend graph.
    
    For advanced use: Could return multimodal content (image URL) if supported.
    
    Args:
        product_name: Name of the product.
    
    Returns:
        ASCII art or description of the graph.
    """
    # Generate fake prices for graph
    prices = [random.randint(900, 1100) for _ in range(10)]  # 10 points
    max_price = max(prices)
    min_price = min(prices)
    graph = "Price Trend for {} (last 10 periods):\n".format(product_name)
    for height in range(10, 0, -1):
        line = "{:4d} | ".format(min_price + (max_price - min_price) * height // 10)
        for p in prices:
            if p >= min_price + (max_price - min_price) * (height - 1) / 10:
                line += "*"
            else:
                line += " "
            line += "  "
        graph += line + "\n"
    graph += "-----+" + "---" * len(prices) + "\n"
    graph += "     " + " ".join([f"P{i+1}" for i in range(len(prices))])
    # In real: Use matplotlib to generate image and return URL
    return graph

# Initialize provider and model
provider = GoogleProvider(api_key=settings.GOOGLE_API_KEY.get_secret_value())
model = GoogleModel('gemini-1.5-flash', provider=provider)  # Adjusted back to original model name

# Enhanced Price Agent with new tools
price_agent = Agent(
    model=model,
    instructions="""
    You are a helpful AI assistant for BasketNa, India's smart price comparison platform. 
    
    Your role is to help users:
    - Find the best deals across Amazon.in, Flipkart.com, and BigBasket.com  
    - Predict future price trends using AI analysis
    - Calculate optimal timing for purchases
    - Track price drops and notify about savings opportunities
    - Analyze historical prices and trends
    - Find coupons and promo codes
    - Summarize product reviews
    - Check stock availability
    - Suggest alternative products
    - Estimate total costs including shipping and taxes
    - Visualize price trends
    
    Always:
    - Use Indian Rupees (₹) for all prices
    - Provide specific, actionable advice
    - Show price comparisons in easy-to-read tables when possible
    - Explain your predictions with confidence levels
    - Suggest the best time to buy based on forecasts
    - Be conversational and helpful, like talking to a friend
    
    When users ask about a product:
    1. First compare prices across all supported sites
    2. Check stock availability
    3. Provide price predictions, trends, and historical analysis  
    4. Find any coupons or promos
    5. Summarize reviews
    6. Estimate total costs
    7. Suggest alternatives if better deals exist
    8. Calculate when prices might drop if relevant
    9. Give a clear recommendation on when to buy
    
    Format your responses with emojis and clear structure for better readability.
    Use advanced tools to provide mind-boggling insights, like trend graphs and AI-driven alternatives.
    """,
    tools=[
        Tool(scrape_price_tool),
        Tool(predict_price_tool),
        Tool(calculate_drop_timeline_tool),
        Tool(compare_all_sites_tool),
        # New innovative tools added here
        Tool(fetch_historical_prices, takes_ctx=False),
        Tool(find_coupons, takes_ctx=False),
        Tool(summarize_reviews, takes_ctx=False),
        Tool(check_stock_availability, takes_ctx=False),
        Tool(suggest_alternatives, takes_ctx=False),
        Tool(estimate_total_cost, takes_ctx=False),
        Tool(generate_price_trend_graph, takes_ctx=False),
    ]
)

# # Optional: Demonstrate decorator usage for a tool that needs context (e.g., user location from deps)
# @price_agent.tool  # Registers via decorator, needs RunContext for deps like user location
# def personalized_recommendation(ctx: RunContext[dict], product_name: str) -> str:
#     """Provide personalized recommendations based on user preferences."""
#     user_location = ctx.deps.get('location', 'India')  # Example dep
#     user_budget = ctx.deps.get('budget', 50000.0)
#     # Fake recommendation; in real: Use user data to filter
#     return f"Based on your location in {user_location} and budget ₹{user_budget}, I recommend {product_name} or alternatives if prices drop soon."

copilot_app = price_agent.to_ag_ui()