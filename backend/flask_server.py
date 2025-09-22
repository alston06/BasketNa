"""
Alternative server implementation using Flask for better stability
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variable to store data
data_df = None

def load_data():
    """Load the price data from CSV file"""
    global data_df
    try:
        # Try new dataset first
        data_path = "../data/ecommerce_price_dataset.csv"
        data_df = pd.read_csv(data_path)
        
        # Convert date column
        data_df['date'] = pd.to_datetime(data_df['date'])
        
        logger.info(f"✅ Loaded {len(data_df):,} records from {data_path}")
        logger.info(f"📊 Unique products: {data_df['product_name'].nunique()}")
        # Rename columns to match expected format
        data_df = data_df.rename(columns={'retailer': 'site', 'price_inr': 'price'})
        
        logger.info(f"🏪 Sites: {data_df['site'].unique().tolist()}")
        logger.info(f"📅 Date range: {data_df['date'].min().date()} to {data_df['date'].max().date()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        return False

@app.route("/")
def root():
    """Root endpoint"""
    return jsonify({
        "message": "BasketNa Price Tracker API",
        "version": "1.0.0",
        "dataset": "ecommerce_price_dataset.csv",
        "status": "active"
    })

@app.route("/health")
def health_check():
    """Health check endpoint"""
    if data_df is None:
        return jsonify({
            "status": "error",
            "message": "Data not loaded"
        }), 500
    
    return jsonify({
        "status": "healthy",
        "total_records": len(data_df),
        "products": data_df['product_name'].nunique(),
        "sites": data_df['site'].nunique(),
        "date_range": f"{data_df['date'].min().date()} to {data_df['date'].max().date()}"
    })

@app.route("/search")
def search():
    """Search for products"""
    try:
        query = request.args.get('query', '').strip()
        
        if not query:
            return jsonify({
                "query": "",
                "items": [],
                "count": 0,
                "message": "Please provide a search query"
            })
        
        if data_df is None:
            return jsonify({
                "error": "Data not available",
                "query": query,
                "items": [],
                "count": 0
            }), 500
        
        # Search logic
        query_lower = query.lower()
        
        # Filter products that match the query
        mask = data_df['product_name'].str.lower().str.contains(query_lower, na=False)
        filtered_df = data_df[mask]
        
        if filtered_df.empty:
            return jsonify({
                "query": query,
                "items": [],
                "count": 0,
                "message": f"No products found matching '{query}'"
            })
        
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
        
        return jsonify({
            "query": query,
            "items": items,
            "count": len(items),
            "best_price": best_price
        })
        
    except Exception as e:
        logger.error(f"❌ Search error for '{query}': {e}")
        return jsonify({
            "error": str(e),
            "query": query,
            "items": [],
            "count": 0
        }), 500

if __name__ == "__main__":
    print("🚀 Starting BasketNa Flask Server...")
    
    # Load data on startup
    if not load_data():
        print("❌ Failed to load data. Exiting.")
        sys.exit(1)
    
    print("✅ Data loaded successfully!")
    print("🌐 Server will be available at: http://127.0.0.1:8002")
    print("📋 Endpoints:")
    print("   GET /          - Root endpoint")
    print("   GET /health    - Health check")
    print("   GET /search    - Search products (?query=...)")
    print()
    
    # Run the Flask app
    app.run(
        host='127.0.0.1',
        port=8002,
        debug=False,  # Set to False for production
        threaded=True
    )