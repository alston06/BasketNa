"""
FastAPI server with proper dataset integration
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import logging
from typing import Optional
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BasketNa Price Tracker API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store data
data_df = None

def load_data():
    """Load the price data from CSV file"""
    global data_df
    try:
        # Load the new dataset
        data_path = "../data/ecommerce_price_dataset.csv"
        data_df = pd.read_csv(data_path)
        
        # Rename columns to match expected format
        data_df = data_df.rename(columns={
            'retailer': 'site',
            'price_inr': 'price'
        })
        
        # Convert date column
        data_df['date'] = pd.to_datetime(data_df['date'])
        
        logger.info(f"✅ Loaded {len(data_df):,} records from {data_path}")
        logger.info(f"📊 Unique products: {data_df['product_name'].nunique()}")
        logger.info(f"🏪 Sites: {data_df['site'].unique().tolist()}")
        logger.info(f"📅 Date range: {data_df['date'].min().date()} to {data_df['date'].max().date()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Load data when the app starts"""
    logger.info("🚀 Starting BasketNa API...")
    if not load_data():
        logger.error("❌ Failed to load data!")
        raise Exception("Failed to load dataset")
    logger.info("✅ API ready!")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BasketNa Price Tracker API",
        "version": "1.0.0",
        "dataset": "ecommerce_price_dataset.csv",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if data_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    return {
        "status": "healthy",
        "total_records": len(data_df),
        "products": data_df['product_name'].nunique(),
        "sites": data_df['site'].nunique(),
        "date_range": f"{data_df['date'].min().date()} to {data_df['date'].max().date()}"
    }

@app.get("/search")
async def search_products(query: str = Query(..., description="Search query for products")):
    """Search for products"""
    try:
        if not query.strip():
            return {
                "query": "",
                "items": [],
                "count": 0,
                "message": "Please provide a search query"
            }
        
        if data_df is None:
            raise HTTPException(status_code=500, detail="Data not available")
        
        # Search logic
        query_lower = query.lower()
        
        # Filter products that match the query
        mask = data_df['product_name'].str.lower().str.contains(query_lower, na=False)
        filtered_df = data_df[mask]
        
        if filtered_df.empty:
            return {
                "query": query,
                "items": [],
                "count": 0,
                "message": f"No products found matching '{query}'"
            }
        
        # Get latest prices for each product-site combination
        latest_prices = filtered_df.loc[filtered_df.groupby(['product_name', 'site'])['date'].idxmax()]
        
        # Convert to list of items
        items = []
        for _, row in latest_prices.iterrows():
            items.append({
                "product_name": row['product_name'],
                "site": row['site'],
                "price": float(row['price']),
                "date": row['date'].strftime('%Y-%m-%d'),
                "product_id": row.get('product_id', 'N/A')
            })
        
        # Sort by price (ascending)
        items.sort(key=lambda x: x['price'])
        
        # Find best price
        best_price = None
        if items:
            best_price = {
                "product_name": items[0]['product_name'],
                "site": items[0]['site'],
                "price": items[0]['price'],
                "date": items[0]['date']
            }
        
        logger.info(f"🔍 Search '{query}' returned {len(items)} results")
        if items:
            logger.info(f"📱 Top result: {items[0]['product_name']} at {items[0]['site']} for ₹{items[0]['price']:,.2f}")
        
        return {
            "query": query,
            "items": items,
            "count": len(items),
            "best_price": best_price
        }
        
    except Exception as e:
        logger.error(f"❌ Search error for '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting BasketNa FastAPI Server...")
    print("🌐 Server will be available at: http://127.0.0.1:8003")
    print("📋 Endpoints:")
    print("   GET /          - Root endpoint")
    print("   GET /health    - Health check")
    print("   GET /search    - Search products (?query=...)")
    print()
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8003,
        log_level="info"
    )