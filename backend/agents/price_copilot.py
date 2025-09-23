from typing import List

from config import settings
from copilotkit import Action, CopilotKitRemoteEndpoint
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from .price_tools import (
    calculate_drop_timeline_tool,
    compare_all_sites_tool,
    predict_price_tool,
    scrape_price_tool,
)

provider = GoogleProvider(api_key=settings.GOOGLE_API_KEY.get_secret_value())
model = GoogleModel('gemini-2.5-flash', provider=provider)

agent = Agent(
        model=model,
    instructions="""
    You are a helpful AI assistant for BasketNa, India's smart price comparison platform. 
    
    Your role is to help users:
    - Find the best deals across Amazon.in, Flipkart.com, and BigBasket.com  
    - Predict future price trends using AI analysis
    - Calculate optimal timing for purchases
    - Track price drops and notify about savings opportunities
    
    Always:
    - Use Indian Rupees (₹) for all prices
    - Provide specific, actionable advice
    - Show price comparisons in easy-to-read tables when possible
    - Explain your predictions with confidence levels
    - Suggest the best time to buy based on forecasts
    - Be conversational and helpful, like talking to a friend
    
    When users ask about a product:
    1. First compare prices across all supported sites
    2. Then provide price predictions and trends  
    3. Calculate when prices might drop if relevant
    4. Give a clear recommendation on when to buy
    
    Format your responses with emojis and clear structure for better readability.
    """
)

# Define actions for CopilotKit
actions: List[Action] = [
    Action(
        name="scrape_price",
        description="Get the current price of a product from a specific Indian e-commerce site like Amazon.in, Flipkart.com, or BigBasket.com",
        parameters=[
            {
                "name": "product_name",
                "type": "string", 
                "description": "The name of the product to search for",
                "required": True
            },
            {
                "name": "site",
                "type": "string",
                "description": "The website to scrape from. Supported: Amazon, Flipkart, BigBasket",
                "required": True
            }
        ],
        handler=scrape_price_tool
    ),
    
    Action(
        name="predict_price",
        description="Forecast the future price of a product using AI and historical data analysis",
        parameters=[
            {
                "name": "product_id", 
                "type": "string",
                "description": "The unique identifier for the product (e.g., 'P001')",
                "required": True
            }
        ],
        handler=predict_price_tool
    ),
    
    Action(
        name="calculate_drop_timeline",
        description="Calculate when a product price is likely to drop by a certain percentage based on trends",
        parameters=[
            {
                "name": "product_id",
                "type": "string", 
                "description": "The unique identifier for the product",
                "required": True
            },
            {
                "name": "target_discount",
                "type": "number",
                "description": "The percentage discount to wait for (default: 10%)",
                "required": False
            }
        ],
        handler=calculate_drop_timeline_tool
    ),
    
    Action(
        name="compare_all_sites", 
        description="Compare prices across Amazon, Flipkart, and BigBasket to find the best deal",
        parameters=[
            {
                "name": "product_name",
                "type": "string",
                "description": "The name of the product to compare prices for",
                "required": True
            }
        ],
        handler=compare_all_sites_tool
    )
]

# Initialize CopilotKit SDK
copilot_kit = CopilotKitRemoteEndpoint(
    actions=actions,
    # agents=[agent.to_ag_ui()],
)