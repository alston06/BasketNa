import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_endpoints():
    """Test the new recommendation API endpoints"""
    
    print("🚀 Testing New Price Recommendation API Endpoints\n")
    
    # Test 1: Get best deals
    print("1️⃣ Testing Best Deals Endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/recommendations/best-deals?top_n=5")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Found {data['count']} best deals")
            for deal in data['best_deals'][:3]:
                print(f"      • {deal['product_name']} at {deal['retailer']}: ₹{deal['current_price']:,} (Save ₹{deal['savings_amount']:,})")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print()
    
    # Test 2: Get buy/wait recommendations
    print("2️⃣ Testing Buy/Wait Recommendations:")
    try:
        response = requests.get(f"{BASE_URL}/recommendations/buy-wait?days_ahead=10")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Found {data['count']} recommendations")
            for rec in data['recommendations'][:3]:
                print(f"      • {rec['product_name']}: {rec['recommendation']} - {rec['reason']}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print()
    
    # Test 3: Get 10-day forecast
    print("3️⃣ Testing 10-Day Forecast (iPhone 16):")
    try:
        response = requests.get(f"{BASE_URL}/forecast/10-day?product_name=iPhone 16")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Found {data['count']} forecast entries")
            # Show first 3 days
            for forecast in data['forecast'][:3]:
                print(f"      • {forecast['date']}: Best at {forecast['best_retailer']} - ₹{forecast['predicted_price']:,}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print()
    
    # Test 4: Price trend analysis
    print("4️⃣ Testing Price Trend Analysis (iPhone 16):")
    try:
        response = requests.get(f"{BASE_URL}/analysis/price-trend/iPhone 16?days_back=30")
        if response.status_code == 200:
            data = response.json()
            analysis = data['analysis']
            print(f"   ✅ Success! Analysis completed")
            print(f"      • Average Price: ₹{analysis['average_price']:,}")
            print(f"      • Price Volatility: {analysis['volatility_percentage']}%")
            print(f"      • Current Trend: {analysis['current_trend']}")
            print(f"      • Min/Max in Period: ₹{analysis['min_price_in_period']:,} - ₹{analysis['max_price_in_period']:,}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print()
    
    # Test 5: Available products
    print("5️⃣ Testing Available Products:")
    try:
        response = requests.get(f"{BASE_URL}/products/available")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Found {data['count']} products")
            print(f"      • Products: {', '.join(data['products'][:5])}{'...' if len(data['products']) > 5 else ''}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print("\n🎉 API Testing Complete!")

if __name__ == "__main__":
    test_endpoints()