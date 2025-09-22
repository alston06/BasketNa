"""
Minimal test of the search functionality
"""

import requests
import json

def test_simple_search():
    try:
        # Test iPhone search
        response = requests.get("http://127.0.0.1:8003/search", params={"query": "iPhone"}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful!")
            print(f"📱 Query: {data['query']}")
            print(f"📊 Results: {len(data['items'])}")
            
            if data['items']:
                first_item = data['items'][0]
                print(f"🎯 First result: {first_item['product_name']} ({first_item['product_id']})")
                print(f"🏪 Site: {first_item['site']}")
                print(f"💰 Price: ₹{first_item['price']:,.2f}")
                
                # Check if it's from the new dataset
                if "iPhone 16" in first_item['product_name']:
                    print("🎉 SUCCESS: Using NEW dataset (iPhone 16)!")
                elif "iPhone 14" in first_item['product_name']:
                    print("⚠️  ISSUE: Still using OLD dataset (iPhone 14)")
                else:
                    print(f"❓ Unknown iPhone model: {first_item['product_name']}")
            else:
                print("❌ No results found")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running on port 8003?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 Testing iPhone search...")
    test_simple_search()