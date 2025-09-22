"""
Minimal working server for search functionality with new dataset
"""

import os
import pandas as pd
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import quote_plus

app = FastAPI(title="Basketna Search API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8081",
        "http://localhost:5174",  # Current Vite server
        "http://localhost:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "ecommerce_price_dataset_corrected.csv"))

def build_site_search_url(site: str, product_name: str) -> str:
    s = site.lower()
    q = quote_plus(product_name)
    if "amazon" in s:
        return f"https://www.amazon.in/s?k={q}"
    if "flipkart" in s:
        return f"https://www.flipkart.com/search?q={q}"
    if "reliance" in s:
        return f"https://www.reliancedigital.in/search?q={q}"
    if "croma" in s:
        return f"https://www.croma.com/search/?text={q}"
    return f"https://www.google.com/search?q={quote_plus(site + ' ' + product_name)}"

def load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=500, detail="E-commerce dataset not found")
    
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    
    # Create product_id mapping for the new dataset
    product_mapping = {
        "iPhone 16": "P001",
        "Samsung Galaxy S26 Ultra": "P002", 
        "Google Pixel 10 Pro": "P003",
        "OnePlus 14": "P004",
        "Dell XPS 15": "P005",
        "Apple MacBook Air (M4)": "P006",
        "HP Spectre x360": "P007",
        "Lenovo Legion 5 Pro": "P008",
        "Sony WH-1000XM6 Headphones": "P009",
        "Apple AirPods Pro 3": "P010",
        "Bose QuietComfort Ultra Earbuds": "P011",
        "JBL Flip 7 Speaker": "P012",
        "Apple Watch Series 11": "P013",
        "Samsung Galaxy Watch 7": "P014",
        "Samsung 55-inch QLED TV": "P015",
        "LG C5 65-inch OLED TV": "P016",
        "Sony PlayStation 5 Pro": "P017",
        "Canon EOS R7 Camera": "P018",
        "DJI Mini 5 Pro Drone": "P019",
        "Logitech MX Master 4 Mouse": "P020"
    }
    
    df["product_id"] = df["product_name"].map(product_mapping)
    df["price"] = df["price_inr"]
    df["site"] = df["retailer"]
    df = df.dropna(subset=["product_id"])
    
    return df

@app.get("/")
def root():
    return {
        "message": "Basketna Search API with Enhanced Dataset", 
        "version": "0.2.0",
        "dataset": "ecommerce_price_dataset.csv",
        "products": 20,
        "retailers": 4,
        "records": "29,200+"
    }

@app.get("/search")
def search(query: str) -> Dict[str, Any]:
    try:
        df = load_data()
        
        # Search for products
        mask = df["product_name"].str.contains(query, case=False, na=False)
        results = df[mask]
        
        if results.empty:
            return {"query": query, "items": [], "best_price": None}
        
        # Get latest prices for each product-site combination
        latest_date = results.groupby(["product_id", "site"])['date'].transform('max')
        latest_rows = results[results['date'] == latest_date].copy()
        
        items = []
        for _, row in latest_rows.iterrows():
            url = build_site_search_url(str(row['site']), str(row['product_name']))
            items.append({
                "product_id": str(row["product_id"]),
                "product_name": str(row["product_name"]),
                "site": str(row["site"]),
                "price": float(row["price"]),
                "url": url,
            })
        
        # Find best price
        best = min(items, key=lambda x: x["price"]) if items else None
        
        return {"query": query, "items": items, "best_price": best}
        
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/health")
def health_check():
    try:
        df = load_data()
        return {
            "status": "healthy",
            "dataset_loaded": True,
            "total_records": len(df),
            "date_range": f"{df['date'].min()} to {df['date'].max()}",
            "products": len(df['product_name'].unique()),
            "retailers": len(df['site'].unique())
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "dataset_loaded": False
        }

@app.get("/forecast/{product_id}")
def get_forecast(product_id: str):
    try:
        from simple_forecast import generate_forecast
        result = generate_forecast(product_id, DATA_PATH)
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found or no data available")
        
        return result
    except Exception as e:
        print(f"Forecast error for {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Basketna Search API...")
    print("📊 Loading enhanced dataset with 20 products...")
    
    # Test data loading first
    try:
        df = load_data()
        print(f"✅ Dataset loaded: {len(df)} records")
        print(f"📱 Sample products: {df['product_name'].unique()[:3].tolist()}")
    except Exception as e:
        print(f"❌ Dataset loading failed: {e}")
        exit(1)
    
    print("🌐 Starting server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")