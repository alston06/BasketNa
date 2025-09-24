"""
Simple API Test Script for Personalized Recommendations with Website Links
Demonstrates the new website link functionality
"""

import requests
import json
from urllib.parse import urlencode

BASE_URL = "http://localhost:8001"  # Updated port

def test_recommendations_with_links():
    """Test the recommendation endpoints to show website links"""
    
    print("🌐 Testing Personalized Recommendations with Website Links")
    print("=" * 65)
    
    # Test session-based recommendations (no auth required)
    session_id = "demo_session_12345"
    
    try:
        print("\n🔍 Testing Session-Based Recommendations...")
        
        response = requests.get(
            f"{BASE_URL}/recommendations/session",
            params={"session_id": session_id, "limit": 3}
        )
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get("recommendations", [])
            
            print(f"✅ Retrieved {len(recommendations)} recommendations")
            
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. 🛍️ {rec['product_name']}")
                print(f"   💰 Price: ₹{rec['current_price']:,} at {rec['best_retailer']}")
                print(f"   🔗 Direct Link: {rec['website_url']}")
                print(f"   🛒 All Retailers:")
                
                for retailer, url in rec['all_retailer_links'].items():
                    print(f"     • {retailer}: {url}")
                
                print(f"   ⭐ Rating: {rec['rating']}/5.0")
                print(f"   📝 {rec['description']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Please start the server with:")
        print("   uvicorn main:app --reload --port 8001")
        return
    
    # Test trending recommendations
    try:
        print("\n\n🔥 Testing Trending Recommendations...")
        
        response = requests.get(
            f"{BASE_URL}/recommendations/trending",
            params={"limit": 3}
        )
        
        if response.status_code == 200:
            data = response.json()
            trending = data.get("trending_recommendations", [])
            
            print(f"✅ Retrieved {len(trending)} trending products")
            
            for i, product in enumerate(trending, 1):
                print(f"\n{i}. 🔥 {product['product_name']} (Trending: {product['trending_score']:.2f})")
                print(f"   💰 Best Price: ₹{product['current_price']:,} at {product['best_retailer']}")
                print(f"   🔗 Shop Now: {product['website_url']}")
                print(f"   🛒 Compare at {len(product['all_retailer_links'])} retailers")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Error testing trending: {e}")
    
    # Test category recommendations
    try:
        print("\n\n📱 Testing Category Recommendations (Smartphones)...")
        
        response = requests.get(
            f"{BASE_URL}/recommendations/category/Smartphones",
            params={"limit": 2}
        )
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get("recommendations", [])
            
            print(f"✅ Retrieved {len(recommendations)} smartphone recommendations")
            
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. 📱 {rec['product_name']}")
                print(f"   💰 Price: ₹{rec['current_price']:,} at {rec['best_retailer']}")
                print(f"   🔗 Buy Now: {rec['website_url']}")
                print(f"   📊 Rating: {rec['rating']}/5.0 | Trending: {rec['trending_score']:.2f}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Error testing categories: {e}")
    
    print("\n" + "=" * 65)
    print("✅ API Test Complete!")
    print("\n💡 Key Features Demonstrated:")
    print("   🔗 Direct retailer website links for immediate purchase")
    print("   🛒 Multiple retailer options for price comparison")
    print("   📊 Smart recommendations based on ratings and trends")
    print("   🎯 Category-specific product suggestions")
    print("   🔥 Trending products with active price movements")

def demonstrate_website_links():
    """Demonstrate different types of website links generated"""
    
    print("\n🌐 Website Link Examples:")
    print("-" * 40)
    
    examples = [
        ("Amazon.in", "iPhone 16", "https://www.amazon.in/s?k=iPhone+16"),
        ("Flipkart", "Dell XPS 15", "https://www.flipkart.com/search?q=Dell+XPS+15"),
        ("RelianceDigital", "Apple AirPods Pro 3", "https://www.reliancedigital.in/search?q=Apple+AirPods+Pro+3"),
        ("Croma", "Samsung Galaxy Watch 7", "https://www.croma.com/search/?text=Samsung+Galaxy+Watch+7")
    ]
    
    for retailer, product, url in examples:
        print(f"🛒 {retailer:<18} | {product:<25} | {url}")

if __name__ == "__main__":
    print("🚀 BasketNA Smart Recommendations with Website Links")
    print("This script demonstrates the new website link functionality")
    print("in personalized product recommendations.")
    
    demonstrate_website_links()
    
    input("\n⏸️  Press Enter to test the API endpoints (make sure server is running)...")
    
    test_recommendations_with_links()