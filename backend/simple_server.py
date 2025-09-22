import os
import sys
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Basketna API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:5174", 
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://localhost:8081",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Simple data loading function
def load_sample_data():
    """Load sample price data from CSV"""
    try:
        data_path = Path(__file__).parent.parent / "data" / "sample_prices.csv"
        if data_path.exists():
            df = pd.read_csv(data_path)
            df["date"] = pd.to_datetime(df["date"]).dt.date
            return df
        else:
            # Return dummy data if file doesn't exist
            return pd.DataFrame([
                {"product_id": "P001", "product_name": "iPhone 14", "site": "Amazon", "price": 65000, "date": "2024-01-01"},
                {"product_id": "P001", "product_name": "iPhone 14", "site": "Flipkart", "price": 67000, "date": "2024-01-01"},
                {"product_id": "P002", "product_name": "MacBook Air", "site": "Amazon", "price": 85000, "date": "2024-01-01"},
                {"product_id": "P003", "product_name": "Samsung Galaxy", "site": "Flipkart", "price": 45000, "date": "2024-01-01"},
            ])
    except Exception as e:
        print(f"Error loading data: {e}")
        # Return dummy data as fallback
        return pd.DataFrame([
            {"product_id": "P001", "product_name": "iPhone 14", "site": "Amazon", "price": 65000, "date": "2024-01-01"},
            {"product_id": "P001", "product_name": "iPhone 14", "site": "Flipkart", "price": 67000, "date": "2024-01-01"},
            {"product_id": "P002", "product_name": "MacBook Air", "site": "Amazon", "price": 85000, "date": "2024-01-01"},
            {"product_id": "P003", "product_name": "Samsung Galaxy", "site": "Flipkart", "price": 45000, "date": "2024-01-01"},
        ])

@app.get("/")
async def read_root():
    return {"message": "Welcome to the BasketNa API!"}

@app.get("/search")
async def search(query: str):
    """Search for products matching the query"""
    try:
        df = load_sample_data()
        
        # Filter products by query
        mask = df["product_name"].str.contains(query, case=False, na=False)
        results = df[mask]
        
        if results.empty:
            return {"query": query, "items": [], "best_price": None}
        
        # Get latest prices for each product-site combination
        latest_date = results.groupby(["product_id", "site"])['date'].transform('max')
        latest_rows = results[results['date'] == latest_date]
        
        items = []
        for _, row in latest_rows.iterrows():
            url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
            if "flipkart" in str(row['site']).lower():
                url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
            
            items.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "site": row["site"],
                "price": float(row["price"]),
                "url": url,
            })
        
        # Find best price
        best = min(items, key=lambda x: x["price"]) if items else None
        
        return {"query": query, "items": items, "best_price": best}
        
    except Exception as e:
        print(f"Search error: {e}")
        return {"query": query, "items": [], "best_price": None}

@app.get("/forecast/{product_id}")
async def forecast(product_id: str):
    """Get price forecast for a product"""
    try:
        df = load_sample_data()
        
        # Get product data
        product_data = df[df["product_id"] == product_id]
        if product_data.empty:
            return {"detail": "Product not found"}
        
        product_name = product_data.iloc[0]["product_name"]
        
        # Mock historical and forecast data
        import random
        base_price = float(product_data["price"].mean())
        
        history = []
        forecast = []
        
        # Generate mock historical data
        for i in range(30):
            price = base_price + random.randint(-5000, 5000)
            history.append({
                "date": f"2024-01-{i+1:02d}",
                "price": price,
                "lower": price * 0.95,
                "upper": price * 1.05
            })
        
        # Generate mock forecast data
        for i in range(7):
            price = base_price + random.randint(-3000, 3000)
            forecast.append({
                "date": f"2024-02-{i+1:02d}",
                "price": price,
                "lower": price * 0.9,
                "upper": price * 1.1
            })
        
        # Determine if it's a great deal
        current_price = history[-1]["price"]
        avg_price = sum(h["price"] for h in history) / len(history)
        great_deal = current_price < avg_price * 0.95
        
        return {
            "product_id": product_id,
            "product_name": product_name,
            "history": history,
            "forecast": forecast,
            "great_deal": great_deal,
            "great_deal_reason": f"Current price ₹{current_price:.0f} is below average" if great_deal else ""
        }
        
    except Exception as e:
        print(f"Forecast error: {e}")
        return {"detail": "Forecast not available"}

# Add CopilotKit integration
try:
    from copilotkit.integrations.fastapi import add_fastapi_endpoint
    from copilotkit import CopilotKitSDK, Action
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    # Initialize Google Gemini model
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key and google_api_key != "your_actual_google_api_key_here":
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=google_api_key,
            temperature=0.7
        )

        # Define CopilotKit actions
        async def scrape_price_action(product_name: str, site: str):
            """Get current price of a product from a specific site"""
            # Use the same data loading logic as search
            df = load_sample_data()
            results = df[
                (df["product_name"].str.contains(product_name, case=False, na=False)) &
                (df["site"].str.contains(site, case=False, na=False))
            ]
            
            if not results.empty:
                row = results.iloc[0]
                return {
                    "site": row["site"],
                    "price": float(row["price"]),
                    "currency": "INR",
                    "product_name": row["product_name"],
                    "url": f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}"
                }
            else:
                # Return mock data
                import random
                return {
                    "site": site,
                    "price": round(random.uniform(400, 1200), 2),
                    "currency": "INR", 
                    "product_name": product_name,
                    "url": f"https://www.{site.lower()}.in/s?k={product_name.replace(' ', '+')}"
                }

        async def compare_prices_action(product_name: str):
            """Compare prices across all sites for a product"""
            sites = ["Amazon", "Flipkart", "BigBasket"]
            results = []
            
            for site in sites:
                price_data = await scrape_price_action(product_name, site)
                results.append(price_data)
            
            # Find best deal
            best_deal = min(results, key=lambda x: x["price"])
            
            return {
                "product_name": product_name,
                "comparison": results,
                "best_deal": best_deal,
                "savings": round(max(r["price"] for r in results) - best_deal["price"], 2)
            }

        # Define actions
        actions = [
            Action(
                name="scrape_price",
                description="Get current price of a product from Amazon, Flipkart, or BigBasket",
                parameters=[
                    {"name": "product_name", "type": "string", "description": "Product name to search for", "required": True},
                    {"name": "site", "type": "string", "description": "Site to check (Amazon, Flipkart, BigBasket)", "required": True}
                ],
                handler=scrape_price_action
            ),
            Action(
                name="compare_prices", 
                description="Compare prices across Amazon, Flipkart, and BigBasket",
                parameters=[
                    {"name": "product_name", "type": "string", "description": "Product name to compare", "required": True}
                ],
                handler=compare_prices_action
            )
        ]

        # Initialize CopilotKit SDK
        copilot_kit = CopilotKitSDK(
            actions=actions
        )
        
        add_fastapi_endpoint(
            app, 
            copilot_kit, 
            "/copilotkit",
            llm=llm
        )
        print("✅ CopilotKit endpoint added at /copilotkit with Google Gemini")
    else:
        print("⚠️ Google API key not set, CopilotKit disabled")
        
except Exception as e:
    print(f"⚠️ Failed to initialize CopilotKit: {e}")
    print("💡 Make sure GOOGLE_API_KEY is set and copilotkit is installed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)