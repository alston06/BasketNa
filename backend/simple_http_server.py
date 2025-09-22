"""
Super simple HTTP server for testing search functionality
"""

import http.server
import socketserver
import json
import urllib.parse
import csv
from datetime import datetime
import os

# Global data storage
products_data = []

def load_csv_data():
    """Load data from the CSV file"""
    global products_data
    products_data = []
    
    csv_path = "../data/ecommerce_price_dataset.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                products_data.append({
                    'date': row['date'],
                    'product_name': row['product_name'],
                    'site': row['retailer'],  # Map retailer to site
                    'price': float(row['price_inr'])
                })
        
        print(f"✅ Loaded {len(products_data):,} records")
        
        # Show unique products
        unique_products = list(set(item['product_name'] for item in products_data))
        print(f"📱 Products: {unique_products[:5]}{'...' if len(unique_products) > 5 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return False

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        # Parse the URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        if path == "/":
            self.handle_root()
        elif path == "/health":
            self.handle_health()
        elif path == "/search":
            query = query_params.get('query', [''])[0]
            self.handle_search(query)
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def handle_root(self):
        response = {
            "message": "BasketNa Simple Server",
            "version": "1.0.0",
            "dataset": "ecommerce_price_dataset.csv",
            "status": "active"
        }
        
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_health(self):
        if not products_data:
            response = {
                "status": "error",
                "message": "No data loaded"
            }
            self.send_response(500)
        else:
            unique_products = len(set(item['product_name'] for item in products_data))
            unique_sites = len(set(item['site'] for item in products_data))
            
            response = {
                "status": "healthy",
                "total_records": len(products_data),
                "products": unique_products,
                "sites": unique_sites
            }
            self.send_response(200)
        
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_search(self, query):
        if not query.strip():
            response = {
                "query": "",
                "items": [],
                "count": 0,
                "message": "Please provide a search query"
            }
        else:
            # Search for products matching the query
            query_lower = query.lower()
            
            # Filter products
            matching_products = []
            for item in products_data:
                if query_lower in item['product_name'].lower():
                    matching_products.append(item)
            
            if not matching_products:
                response = {
                    "query": query,
                    "items": [],
                    "count": 0,
                    "message": f"No products found matching '{query}'"
                }
            else:
                # Get unique product-site combinations with latest prices
                latest_prices = {}
                for item in matching_products:
                    key = f"{item['product_name']}_{item['site']}"
                    if key not in latest_prices or item['date'] > latest_prices[key]['date']:
                        latest_prices[key] = item
                
                # Convert to list and sort by price
                items = list(latest_prices.values())
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
                
                response = {
                    "query": query,
                    "items": items,
                    "count": len(items),
                    "best_price": best_price
                }
                
                print(f"🔍 Search '{query}' found {len(items)} results")
                if items:
                    print(f"📱 Top result: {items[0]['product_name']} at {items[0]['site']} for ₹{items[0]['price']:,.2f}")
        
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

if __name__ == "__main__":
    PORT = 8003
    
    print("🚀 Starting Simple HTTP Server...")
    
    # Load data
    if not load_csv_data():
        print("❌ Failed to load data. Exiting.")
        exit(1)
    
    # Start server
    print(f"🌐 Server starting on http://127.0.0.1:{PORT}")
    print("📋 Endpoints:")
    print("   GET /          - Root endpoint")
    print("   GET /health    - Health check")
    print("   GET /search    - Search products (?query=...)")
    print()
    
    try:
        with socketserver.TCPServer(("127.0.0.1", PORT), SimpleHandler) as httpd:
            print(f"✅ Server ready! Listening on port {PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")