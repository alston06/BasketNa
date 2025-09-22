"""
Test script to verify the updated backend with new dataset
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_search(query):
    """Test the search endpoint"""
    print(f"\n🔍 Testing search for: '{query}'")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/search", params={"query": query})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['items'])} results")
            
            for item in data['items'][:5]:  # Show first 5 results
                print(f"📱 {item['product_name']} ({item['product_id']})")
                print(f"   🏪 {item['site']}: ₹{item['price']:,.2f}")
                print(f"   🔗 {item['url'][:60]}...")
                print()
            
            if data['best_price']:
                best = data['best_price']
                print(f"🏆 BEST DEAL: {best['product_name']}")
                print(f"   💰 ₹{best['price']:,.2f} at {best['site']}")
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_forecast(product_id):
    """Test the forecast endpoint"""
    print(f"\n📈 Testing forecast for: {product_id}")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/forecast/{product_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Forecast generated for: {data.get('product_name', 'Unknown')}")
            print(f"   📊 History points: {len(data.get('history', []))}")
            print(f"   🔮 Forecast points: {len(data.get('forecast', []))}")
            
            if data.get('great_deal'):
                print(f"   🔥 GREAT DEAL: {data.get('great_deal_reason', '')}")
            else:
                print(f"   💰 No special deal detected")
                
            # Show first few forecast points
            forecast = data.get('forecast', [])
            if forecast:
                print(f"\n   📅 Next 3 days forecast:")
                for fp in forecast[:3]:
                    print(f"     {fp['date']}: ₹{fp['price']:,.0f} (₹{fp['lower']:,.0f} - ₹{fp['upper']:,.0f})")
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_compare(product_id):
    """Test the retailer comparison endpoint"""
    print(f"\n🏪 Testing retailer comparison for: {product_id}")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/compare/{product_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Comparison for: {data.get('product_name', 'Unknown')}")
            print(f"   📅 Date: {data.get('date', 'Unknown')}")
            
            retailer_prices = data.get('retailer_prices', [])
            if retailer_prices:
                print(f"\n   💰 Retailer Prices:")
                for rp in retailer_prices:
                    marker = "🏆 BEST DEAL" if rp.get('is_best_deal') else f"(Save {rp.get('potential_savings', '₹0')})"
                    print(f"     {rp['retailer']:20} {rp['formatted_price']:>12} {marker}")
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    print("🚀 TESTING UPDATED BACKEND WITH NEW DATASET")
    print("=" * 60)
    
    # Test various search queries
    search_queries = [
        "phone",
        "iPhone",
        "Samsung",
        "laptop", 
        "MacBook",
        "headphones",
        "watch",
        "TV"
    ]
    
    for query in search_queries:
        test_search(query)
    
    # Test forecasting for a few products
    print(f"\n\n📈 TESTING FORECAST FUNCTIONALITY")
    print("=" * 60)
    
    product_ids = ["P001", "P006", "P013"]  # iPhone, MacBook, Apple Watch
    
    for pid in product_ids:
        test_forecast(pid)
    
    # Test retailer comparison
    print(f"\n\n🏪 TESTING RETAILER COMPARISON")
    print("=" * 60)
    
    for pid in product_ids:
        test_compare(pid)

if __name__ == "__main__":
    main()