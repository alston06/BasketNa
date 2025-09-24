
from config import settings
from pydantic_ai import Agent, Tool
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from transformers import pipeline

from .tools.calculate_drop_timeline import calculate_drop_timeline_tool
from .tools.check_item_availability_across_sites import (
    check_item_availability_across_sites,
)
from .tools.compare_all_sites import compare_all_sites_tool
from .tools.estimate_total_cost import estimate_total_cost
from .tools.fetch_historical_prices import fetch_historical_prices
from .tools.find_coupons import find_coupons
from .tools.generate_price_trend_graph import generate_price_trend_graph
from .tools.predict_price import predict_price_tool
from .tools.scrape_price import scrape_price_tool
from .tools.suggest_alternatives import suggest_alternatives
from .tools.summarize_reviews import summarize_reviews

sentiment_analyzer = pipeline("sentiment-analysis")

# Initialize provider and model
provider = GoogleProvider(api_key=settings.GOOGLE_API_KEY.get_secret_value())
model = GoogleModel('gemini-2.5-flash', provider=provider)  # Adjusted back to original model name

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
        Tool(check_item_availability_across_sites, takes_ctx=False),
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