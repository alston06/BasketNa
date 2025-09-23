import json
import re

import requests
from bs4 import BeautifulSoup
from config import settings
from pydantic_ai import Agent, Tool
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from .price_tools import (
    calculate_drop_timeline_tool,
    compare_all_sites_tool,
    predict_price_tool,
    scrape_price_tool,
)


# Helper function to make HTTP requests with user-agent to avoid blocking
def make_request(url: str, headers=None) -> requests.Response:
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    if headers:
        default_headers.update(headers)
    return requests.get(url, headers=default_headers)

# New innovative tool implementations
# Using real scraping from relevant websites. Note: Scraping may violate terms of service; use APIs where available in production.
# For demonstration, handling common Indian e-commerce sites and price trackers like pricehistory.in, grabon.in, etc.
# Error handling added to return meaningful messages if scraping fails.

def fetch_historical_prices(product_name: str, site: str = "all") -> dict:
    """
    Fetch historical price data for a product across sites.
    
    Args:
        product_name: Name or URL of the product.
        site: Specific site (amazon, flipkart, bigbasket) or 'all'.
    
    Returns:
        A dictionary with timestamps as keys and prices (in INR) as values.
    """
    # Use pricehistory.in as a tracker for Indian sites
    search_url = f"https://pricehistory.in/search?q={requests.utils.quote(product_name)}"
    try:
        response = make_request(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first relevant product link
        product_link = soup.find('a', href=re.compile(r'/product/'))
        if not product_link:
            return {"error": "No product found on pricehistory.in"}
        
        product_url = "https://pricehistory.in" + product_link['href']
        product_response = make_request(product_url)
        product_response.raise_for_status()
        product_soup = BeautifulSoup(product_response.text, 'html.parser')
        
        # Extract historical prices (assuming script tag with data or table)
        script_tags = product_soup.find_all('script')
        prices = {}
        for script in script_tags:
            if 'chartData' in str(script):  # Look for chart data
                data_str = re.search(r'chartData = (\[.*?\]);', str(script), re.DOTALL)
                if data_str:
                    chart_data = json.loads(data_str.group(1))
                    for entry in chart_data:
                        date = entry.get('date')  # Assuming format YYYY-MM-DD
                        price = entry.get('price')
                        if date and price:
                            prices[date] = float(price)
                    break
        if not prices:
            return {"error": "No historical prices found"}
        return prices
    except Exception as e:
        return {"error": str(e)}

def find_coupons(product_name: str) -> list[str]:
    """
    Search for available coupons or promo codes for the product.
    
    Args:
        product_name: Name of the product to find coupons for.
    
    Returns:
        List of coupon codes or descriptions.
    """
    # Use grabon.in for coupons
    search_url = f"https://www.grabon.in/search/?q={requests.utils.quote(product_name)}"
    try:
        response = make_request(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        coupons = []
        coupon_elements = soup.find_all('div', class_='coupon-item')  # Adjust class based on site structure
        for elem in coupon_elements[:5]:  # Limit to top 5
            code = elem.find('span', class_='coupon-code')
            desc = elem.find('p', class_='coupon-desc')
            if code and desc:
                coupons.append(f"{code.text.strip()} - {desc.text.strip()}")
            elif desc:
                coupons.append(desc.text.strip())
        return coupons if coupons else ["No coupons found"]
    except Exception as e:
        return [f"Error: {str(e)}"]

def summarize_reviews(product_name: str, site: str = "all") -> str:
    """
    Summarize user reviews for the product across sites using AI analysis.
    
    Args:
        product_name: Name or URL of the product.
        site: Specific site or 'all'.
    
    Returns:
        A concise summary of reviews, including sentiment and key pros/cons.
    """
    # For simplicity, scrape from Amazon.in as example; extend for others
    if site == "all":
        site = "amazon"  # Default to amazon
    base_url = {
        "amazon": "https://www.amazon.in/s?k=",
        "flipkart": "https://www.flipkart.com/search?q=",
        "bigbasket": "https://www.bigbasket.com/search/?q="
    }.get(site, "https://www.amazon.in/s?k=")
    
    search_url = base_url + requests.utils.quote(product_name)
    try:
        response = make_request(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find first product link
        if site == "amazon":
            product_link = soup.find('a', class_='a-link-normal s-no-outline')
            if product_link:
                product_url = "https://www.amazon.in" + product_link['href']
        elif site == "flipkart":
            product_link = soup.find('a', class_='_1fQZEK')
            if product_link:
                product_url = "https://www.flipkart.com" + product_link['href']
        else:
            return "Site not supported for review scraping"
        
        if not product_link:
            return "No product found"
        
        # Scrape reviews from product page
        product_response = make_request(product_url)
        product_response.raise_for_status()
        product_soup = BeautifulSoup(product_response.text, 'html.parser')
        
        reviews = []
        if site == "amazon":
            review_elements = product_soup.find_all('div', class_='a-section review')
            for rev in review_elements[:10]:
                rating = rev.find('span', class_='a-icon-alt')
                text = rev.find('span', class_='review-text')
                if rating and text:
                    reviews.append(f"{rating.text.strip()}: {text.text.strip()}")
        elif site == "flipkart":
            review_elements = product_soup.find_all('div', class_='t-ZTKy')
            for rev in review_elements[:10]:
                rating = rev.find_previous('div', class_='_3LWZlK')
                text = rev.find('div', class_='qwjRop')
                if rating and text:
                    reviews.append(f"{rating.text.strip()} stars: {text.text.strip()}")
        
        if not reviews:
            return "No reviews found"
        
        # Simple summary (count positives/negatives)
        positive = sum(1 for r in reviews if '4' in r or '5' in r)
        negative = sum(1 for r in reviews if '1' in r or '2' in r)
        total = len(reviews)
        summary = f"Overall: {positive/total*100:.1f}% positive based on {total} reviews. Sample reviews: {'; '.join(reviews[:3])}"
        return summary
    except Exception as e:
        return f"Error: {str(e)}"

def check_stock_availability(product_name: str, site: str = "all") -> dict:
    """
    Check current stock availability across sites.
    
    Args:
        product_name: Name or URL of the product.
        site: Specific site or 'all'.
    
    Returns:
        Dictionary with site as key and availability status as value.
    """
    sites = ["amazon", "flipkart", "bigbasket"] if site == "all" else [site]
    availability = {}
    for s in sites:
        base_url = {
            "amazon": "https://www.amazon.in/s?k=",
            "flipkart": "https://www.flipkart.com/search?q=",
            "bigbasket": "https://www.bigbasket.com/search/?q="
        }.get(s)
        search_url = base_url + requests.utils.quote(product_name)
        try:
            response = make_request(search_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            status = "Unknown"
            if s == "amazon":
                if soup.find('span', text=re.compile(r'Currently unavailable', re.I)):
                    status = "Out of stock"
                elif soup.find('span', id='submit.add-to-cart'):
                    status = "In stock"
            elif s == "flipkart":
                if soup.find('button', text='Notify Me'):
                    status = "Out of stock"
                elif soup.find('button', class_='_2KpZ6l _2U9uOA _3v1-ww'):
                    status = "In stock"
            elif s == "bigbasket":
                if soup.find('span', text='Out of Stock'):
                    status = "Out of stock"
                elif soup.find('button', text='Add to basket'):
                    status = "In stock"
            availability[s] = status
        except Exception as e:
            availability[s] = f"Error: {str(e)}"
    return availability

def suggest_alternatives(product_name: str, budget: float = None) -> list[dict]:
    """
    Suggest cheaper or better alternative products based on AI recommendations.
    
    Args:
        product_name: Original product name.
        budget: Optional maximum budget in INR.
    
    Returns:
        List of dictionaries with alternative product details (name, price, site).
    """
    # Use web search or scrape from comparison sites like mysmartprice.com
    search_url = f"https://www.mysmartprice.com/search?q={requests.utils.quote(product_name)}"
    try:
        response = make_request(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        alternatives = []
        product_elements = soup.find_all('div', class_='prdct-item')  # Adjust based on site
        for elem in product_elements[:5]:
            name = elem.find('a', class_='prdct-item__name')
            price = elem.find('span', class_='prdct-item__prc')
            site = elem.find('img', alt=re.compile(r'logo'))['alt'] if elem.find('img') else "unknown"
            if name and price:
                alt_price = float(re.sub(r'[^\d.]', '', price.text))
                if budget is None or alt_price <= budget:
                    alternatives.append({
                        "name": name.text.strip(),
                        "price": alt_price,
                        "site": site
                    })
        return alternatives if alternatives else [{"error": "No alternatives found"}]
    except Exception as e:
        return [{"error": str(e)}]

def estimate_total_cost(product_name: str, site: str, address: str = None) -> dict:
    """
    Estimate total cost including shipping, taxes, and any fees.
    
    Args:
        product_name: Name or URL of the product.
        site: Specific site.
        address: Optional shipping address for accurate shipping calculation.
    
    Returns:
        Dictionary with breakdown: base_price, shipping, taxes, total.
    """
    base_url = {
        "amazon": "https://www.amazon.in/s?k=",
        "flipkart": "https://www.flipkart.com/search?q=",
        "bigbasket": "https://www.bigbasket.com/search/?q="
    }.get(site)
    if not base_url:
        return {"error": "Invalid site"}
    
    search_url = base_url + requests.utils.quote(product_name)
    try:
        response = make_request(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find product link
        if site == "amazon":
            product_link = soup.find('a', class_='a-link-normal s-no-outline')
            product_url = "https://www.amazon.in" + product_link['href'] if product_link else None
        elif site == "flipkart":
            product_link = soup.find('a', class_='_1fQZEK')
            product_url = "https://www.flipkart.com" + product_link['href'] if product_link else None
        else:
            return {"error": "Site not supported"}
        
        if not product_url:
            return {"error": "No product found"}
        
        product_response = make_request(product_url)
        product_response.raise_for_status()
        product_soup = BeautifulSoup(product_response.text, 'html.parser')
        
        base_price = 0.0
        shipping = 0.0
        if site == "amazon":
            price_elem = product_soup.find('span', id='price')
            base_price = float(re.sub(r'[^\d.]', '', price_elem.text)) if price_elem else 0.0
            shipping_elem = product_soup.find('span', id='freeShippingPrice')
            shipping = float(re.sub(r'[^\d.]', '', shipping_elem.text)) if shipping_elem else 40.0  # Default estimate
        elif site == "flipkart":
            price_elem = product_soup.find('div', class_='_30jeq3 _1_WHN1')
            base_price = float(re.sub(r'[^\d.]', '', price_elem.text)) if price_elem else 0.0
            shipping_elem = product_soup.find('div', text=re.compile(r'Delivery Charges'))
            shipping = float(re.sub(r'[^\d.]', '', shipping_elem.next_sibling.text)) if shipping_elem else 40.0
        
        taxes = base_price * 0.18  # Assume 18% GST
        total = base_price + shipping + taxes
        return {
            "base_price": base_price,
            "shipping": shipping,
            "taxes": taxes,
            "total": total
        }
    except Exception as e:
        return {"error": str(e)}

def generate_price_trend_graph(product_name: str) -> str:
    """
    Generate a textual or ASCII representation of price trend graph.
    
    For advanced use: Could return multimodal content (image URL) if supported.
    
    Args:
        product_name: Name of the product.
    
    Returns:
        ASCII art or description of the graph.
    """
    historical_prices = fetch_historical_prices(product_name)
    if "error" in historical_prices:
        return historical_prices["error"]
    
    # Sort dates
    sorted_dates = sorted(historical_prices.keys())
    prices = [historical_prices[d] for d in sorted_dates]
    if not prices:
        return "No data for graph"
    
    max_price = max(prices)
    min_price = min(prices)
    num_points = min(len(prices), 20)  # Limit for ASCII
    step = len(prices) // num_points if num_points < len(prices) else 1
    selected_prices = prices[::step]
    
    graph = f"Price Trend for {product_name} (INR):\n"
    for height in range(10, 0, -1):
        line = f"{int(min_price + (max_price - min_price) * height / 10):5d} | "
        for p in selected_prices:
            if p >= min_price + (max_price - min_price) * (height - 1) / 10:
                line += "*"
            else:
                line += " "
            line += " "
        graph += line + "\n"
    graph += "------+" + "--" * len(selected_prices) + "\n"
    graph += "      " + " ".join([d[-5:] for d in sorted_dates[::step]])  # Short dates
    return graph

# Initialize provider and model
provider = GoogleProvider(api_key=settings.GOOGLE_API_KEY.get_secret_value())
model = GoogleModel('gemini-1.5-flash', provider=provider)

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

# Optional: Demonstrate decorator usage for a tool that needs context (e.g., user location from deps)
# @price_agent.tool  # Registers via decorator, needs RunContext for deps like user location
# def personalized_recommendation(ctx: RunContext[dict], product_name: str) -> str:
#     """Provide personalized recommendations based on user preferences."""
#     user_location = ctx.deps.get('location', 'India')  # Example dep
#     user_budget = ctx.deps.get('budget', 50000.0)
#     # Use real data by calling other tools or scraping, but for demo, simple string
#     alternatives = suggest_alternatives(product_name, user_budget)
#     return f"Based on your location in {user_location} and budget ₹{user_budget}, recommended: {product_name} or {alternatives[0]['name'] if alternatives else 'no alternatives'}."

copilot_app = price_agent.to_ag_ui()