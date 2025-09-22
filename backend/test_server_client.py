"""
Simple test client to verify the server is working
"""

import requests
import json

def test_server():
    base_url = "http://127.0.0.1:8003"
    
    print("🔍 Testing server endpoints...")
    
    try:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Records: {health_data.get('total_records'):,}")
            print(f"   Products: {health_data.get('products')}")
            print(f"   Date range: {health_data.get('date_range')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test root endpoint
        print("\n2. Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            root_data = response.json()
            print(f"✅ Root endpoint working")
            print(f"   Version: {root_data.get('version')}")
            print(f"   Dataset: {root_data.get('dataset')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test search endpoint
        print("\n3. Testing search endpoint...")
        test_queries = ["phone", "iPhone", "Samsung", "laptop"]
        
        for query in test_queries:
            print(f"\n   🔍 Searching for '{query}'...")
            response = requests.get(f"{base_url}/search", params={"query": query}, timeout=10)
            
            if response.status_code == 200:
                search_data = response.json()
                items = search_data.get('items', [])
                print(f"   ✅ Found {len(items)} results")
                
                if items:
                    first_item = items[0]
                    print(f"   📱 First result: {first_item.get('product_name')}")
                    print(f"   🏪 Site: {first_item.get('site')}")
                    print(f"   💰 Price: ₹{first_item.get('price'):,.2f}")
                    
                    best_price = search_data.get('best_price')
                    if best_price:
                        print(f"   🏆 Best deal: ₹{best_price.get('price'):,.2f} at {best_price.get('site')}")
                else:
                    print(f"   📝 No results for '{query}'")
            else:
                print(f"   ❌ Search failed: {response.status_code} - {response.text}")
                return False
        
        print(f"\n🎉 All tests passed! Server is working correctly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - server not running on {base_url}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_server()