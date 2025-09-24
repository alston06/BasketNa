"""
Test Script for Personalized Product Recommendation System
Demonstrates the full functionality with various user scenarios
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

# API Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    "signup": f"{BASE_URL}/user/signup",
    "login": f"{BASE_URL}/user/login",
    "search": f"{BASE_URL}/search",
    "track": f"{BASE_URL}/track",
    "personalized_recs": f"{BASE_URL}/recommendations/personalized",
    "session_recs": f"{BASE_URL}/recommendations/session",
    "record_view": f"{BASE_URL}/activity/view",
    "category_recs": f"{BASE_URL}/recommendations/category",
    "trending_recs": f"{BASE_URL}/recommendations/trending",
    "forecast": f"{BASE_URL}/forecast"
}

class RecommendationTester:
    """Test suite for personalized recommendations"""
    
    def __init__(self):
        self.access_token = None
        self.session_id = f"test_session_{datetime.now().timestamp()}"
        
    def make_request(self, method: str, url: str, data: dict = None, 
                    params: dict = None, headers: dict = None) -> dict:
        """Make HTTP request with error handling"""
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return {"error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.ConnectionError:
            return {"error": "Connection failed. Make sure the server is running on localhost:8000"}
        except Exception as e:
            return {"error": str(e)}
    
    def create_test_user(self) -> bool:
        """Create a test user account"""
        print("👤 Creating test user...")
        
        user_data = {
            "email": f"testuser_{datetime.now().timestamp()}@example.com",
            "password": "testpassword123"
        }
        
        result = self.make_request("POST", API_ENDPOINTS["signup"], data=user_data)
        
        if "error" not in result:
            print(f"✅ User created: {result.get('email')}")
            
            # Login to get access token
            login_data = {
                "username": user_data["email"],
                "password": user_data["password"]
            }
            
            # Note: OAuth2PasswordRequestForm expects form data, not JSON
            response = requests.post(
                API_ENDPOINTS["login"],
                data=login_data,  # Use data instead of json for form data
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                self.access_token = login_result.get("access_token")
                print(f"✅ Login successful, token obtained")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
        else:
            print(f"❌ User creation failed: {result.get('error')}")
            return False
    
    def get_auth_headers(self) -> dict:
        """Get authorization headers"""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
    
    def simulate_user_activity(self) -> None:
        """Simulate user browsing and tracking activity"""
        print("\n🔍 Simulating user activity...")
        
        # Search for products
        search_queries = ["iPhone", "laptop", "headphones", "smartwatch"]
        
        for query in search_queries:
            print(f"   🔎 Searching for: {query}")
            result = self.make_request("GET", API_ENDPOINTS["search"], params={"query": query})
            
            if "error" not in result and result.get("items"):
                # View some products from search results
                for item in result["items"][:2]:  # View first 2 items
                    product_id = item["product_id"]
                    
                    # Record product view
                    view_params = {"session_id": self.session_id} if not self.access_token else {}
                    headers = self.get_auth_headers()
                    
                    view_result = self.make_request(
                        "POST", 
                        f"{API_ENDPOINTS['record_view']}/{product_id}",
                        params=view_params,
                        headers=headers
                    )
                    
                    if "error" not in view_result:
                        print(f"     👁️ Viewed: {item['product_name']}")
                    
                    # Track some products (only if authenticated)
                    if self.access_token and query in ["iPhone", "laptop"]:  # Track interest in phones and laptops
                        track_result = self.make_request(
                            "POST",
                            f"{API_ENDPOINTS['track']}/{product_id}",
                            headers=headers
                        )
                        
                        if "error" not in track_result:
                            print(f"     📌 Tracked: {item['product_name']}")
    
    def test_personalized_recommendations(self) -> None:
        """Test personalized recommendations for authenticated user"""
        if not self.access_token:
            print("\n⚠️ Skipping personalized recommendations (no auth token)")
            return
        
        print("\n🎯 Testing Personalized Recommendations...")
        
        result = self.make_request(
            "GET",
            API_ENDPOINTS["personalized_recs"],
            params={"limit": 5},
            headers=self.get_auth_headers()
        )
        
        if "error" not in result:
            print(f"✅ Generated {result.get('total_recommendations', 0)} personalized recommendations")
            print(f"📊 Personalization Score: {result.get('personalization_score', 0)}")
            
            for i, rec in enumerate(result.get("recommendations", []), 1):
                print(f"\n{i}. 📱 {rec['product_name']}")
                print(f"   🏷️  Category: {rec['category']}")
                print(f"   💰 Price: ₹{rec['current_price']:,} at {rec['best_retailer']}")
                print(f"   ⭐ Rating: {rec['rating']}/5.0")
                print(f"   📈 Score: {rec['score']:.3f}")
                print(f"   🎯 Reasons: {', '.join(rec['reasons'])}")
                print(f"   📝 {rec['description']}")
        else:
            print(f"❌ Failed to get personalized recommendations: {result.get('error')}")
    
    def test_session_recommendations(self) -> None:
        """Test session-based recommendations for anonymous users"""
        print("\n🕵️ Testing Session-Based Recommendations...")
        
        result = self.make_request(
            "GET",
            API_ENDPOINTS["session_recs"],
            params={"session_id": self.session_id, "limit": 5}
        )
        
        if "error" not in result:
            print(f"✅ Generated {result.get('total_recommendations', 0)} session recommendations")
            print(f"📊 Personalization Score: {result.get('personalization_score', 0)}")
            
            for i, rec in enumerate(result.get("recommendations", []), 1):
                print(f"\n{i}. 📱 {rec['product_name']}")
                print(f"   🏷️  Category: {rec['category']}")
                print(f"   💰 Price: ₹{rec['current_price']:,} at {rec['best_retailer']}")
                print(f"   📈 Trending: {rec['trending_score']:.3f}")
                print(f"   🎯 Reasons: {', '.join(rec['reasons'])}")
        else:
            print(f"❌ Failed to get session recommendations: {result.get('error')}")
    
    def test_category_recommendations(self) -> None:
        """Test category-based recommendations"""
        print("\n📂 Testing Category Recommendations...")
        
        categories = ["Smartphones", "Laptops", "Audio", "Wearables"]
        
        for category in categories:
            result = self.make_request(
                "GET",
                f"{API_ENDPOINTS['category_recs']}/{category}",
                params={"limit": 3}
            )
            
            if "error" not in result:
                recs = result.get("recommendations", [])
                print(f"\n📱 {category} Recommendations ({len(recs)} items):")
                
                for rec in recs:
                    print(f"   • {rec['product_name']} - ₹{rec['current_price']:,} "
                          f"(Rating: {rec['rating']}/5.0, Trending: {rec['trending_score']:.2f})")
            else:
                print(f"❌ Failed to get {category} recommendations: {result.get('error')}")
    
    def test_trending_recommendations(self) -> None:
        """Test trending product recommendations"""
        print("\n🔥 Testing Trending Recommendations...")
        
        result = self.make_request(
            "GET",
            API_ENDPOINTS["trending_recs"],
            params={"limit": 8}
        )
        
        if "error" not in result:
            trending = result.get("trending_recommendations", [])
            print(f"✅ Found {len(trending)} trending products")
            
            for i, product in enumerate(trending, 1):
                print(f"\n{i}. 🔥 {product['product_name']}")
                print(f"   📊 Trending Score: {product['trending_score']:.3f}")
                print(f"   💰 Price: ₹{product['current_price']:,} at {product['best_retailer']}")
                print(f"   📈 Price Trend: {product['price_trend']}")
                if product['potential_savings'] > 0:
                    print(f"   💡 Price Range: ₹{product['potential_savings']:,.0f}")
        else:
            print(f"❌ Failed to get trending recommendations: {result.get('error')}")
    
    def test_price_forecasting_integration(self) -> None:
        """Test integration with price forecasting"""
        print("\n🔮 Testing Price Forecasting Integration...")
        
        # Test forecast for a few products
        test_products = ["P001", "P005", "P010"]  # iPhone, Dell XPS, AirPods
        
        for product_id in test_products:
            result = self.make_request(
                "GET",
                f"{API_ENDPOINTS['forecast']}/{product_id}",
                params={"model": "enhanced"}
            )
            
            if "error" not in result:
                print(f"✅ Forecast for {result.get('product_name', product_id)}:")
                print(f"   🎯 Great Deal: {result.get('great_deal', False)}")
                if result.get('great_deal_reason'):
                    print(f"   💡 Reason: {result.get('great_deal_reason')}")
            else:
                print(f"❌ Forecast failed for {product_id}: {result.get('error')}")
    
    def run_full_test_suite(self) -> None:
        """Run the complete test suite"""
        print("🚀 Starting Personalized Recommendation System Test Suite")
        print("=" * 70)
        
        # Create user and authenticate
        if self.create_test_user():
            print("✅ User authentication successful")
        else:
            print("⚠️ Running tests without authentication")
        
        # Simulate user activity
        self.simulate_user_activity()
        
        # Test different recommendation types
        self.test_personalized_recommendations()
        self.test_session_recommendations()
        self.test_category_recommendations()
        self.test_trending_recommendations()
        self.test_price_forecasting_integration()
        
        print("\n" + "=" * 70)
        print("🏁 Test Suite Complete!")
        print("\n💡 Key Features Tested:")
        print("   ✅ User activity tracking (views, searches, tracking)")
        print("   ✅ Personalized recommendations based on user behavior")
        print("   ✅ Session-based recommendations for anonymous users")
        print("   ✅ Category-specific product recommendations")
        print("   ✅ Trending product identification")
        print("   ✅ Integration with price forecasting system")
        print("\n📊 Recommendation Algorithm Features:")
        print("   • User activity pattern analysis")
        print("   • Category preference learning")
        print("   • Similar product suggestions")
        print("   • Trending and highly-rated product boosting")
        print("   • Price trend and savings consideration")
        print("   • Personalization scoring")

def main():
    """Run the recommendation system test"""
    tester = RecommendationTester()
    
    print("🎯 Personalized Product Recommendation System Test")
    print("=" * 60)
    print("This test will:")
    print("1. Create a test user and authenticate")
    print("2. Simulate user browsing and tracking activity")
    print("3. Test personalized recommendations")
    print("4. Test session-based recommendations")
    print("5. Test category and trending recommendations")
    print("6. Test price forecasting integration")
    print("\n💡 Make sure the FastAPI server is running on localhost:8000")
    
    input("\nPress Enter to continue...")
    
    tester.run_full_test_suite()

if __name__ == "__main__":
    main()