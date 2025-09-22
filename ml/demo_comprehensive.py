"""
E-commerce Price Tracking ML Model - Demo Script
Demonstrates all features of the enhanced forecasting system
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from forecast_enhanced import forecast_for_product, get_retailer_comparison, get_available_products

def demo_header():
    print("="*80)
    print("🛒 E-COMMERCE PRICE TRACKING ML MODEL - COMPREHENSIVE DEMO")
    print("="*80)
    print("📊 Dataset: 365 days of synthetic price data for 20 electronic products")
    print("🏪 Retailers: Amazon.in, Flipkart, RelianceDigital, Croma")
    print("🤖 ML Features: Random Forest regression with trend detection")
    print("="*80)

def demo_product_list():
    print("\n" + "="*50)
    print("📦 AVAILABLE PRODUCTS")
    print("="*50)
    
    products = get_available_products()
    if not products:
        print("❌ No products available!")
        return False
    
    categories = {
        "📱 Smartphones": ["P001", "P002", "P003", "P004"],
        "💻 Laptops": ["P005", "P006", "P007", "P008"], 
        "🎵 Audio": ["P009", "P010", "P011", "P012"],
        "⌚ Wearables": ["P013", "P014"],
        "📺 Home Entertainment": ["P015", "P016", "P017"],
        "📷 Cameras & Accessories": ["P018", "P019", "P020"]
    }
    
    for category, product_ids in categories.items():
        print(f"\n{category}:")
        for pid in product_ids:
            if pid in products:
                print(f"  {pid}: {products[pid]}")
    
    return True

def demo_forecast_analysis():
    print("\n" + "="*50)
    print("📈 FORECAST ANALYSIS DEMO")
    print("="*50)
    
    # Test products from different categories
    test_products = [
        ("P001", "iPhone 16 (Smartphone)"),
        ("P006", "Apple MacBook Air M4 (Laptop)"),
        ("P010", "Apple AirPods Pro 3 (Audio)"),
        ("P016", "LG C5 65-inch OLED TV (High-value)")
    ]
    
    for product_id, description in test_products:
        print(f"\n🔍 ANALYZING: {description}")
        print("-" * 60)
        
        result = forecast_for_product(product_id, horizon_days=7)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            continue
        
        print(f"💰 Current Price: ₹{result['current_price']:,.2f}")
        print(f"📈 Recent Trend: {result['recent_trend'].title()}")
        print(f"📊 Data Points: {result['data_points']} days")
        
        if result['great_deal']:
            print(f"🔥 GREAT DEAL DETECTED!")
            print(f"💡 Reason: {result['great_deal_reason'][:100]}...")
        else:
            print("💰 No special deal detected")
        
        # Show 3-day forecast
        print(f"📅 Next 3 Days Forecast:")
        for i, fp in enumerate(result['forecast'][:3]):
            print(f"  {fp['date']}: ₹{fp['price']:7,.0f} (±₹{(fp['upper']-fp['lower'])/2:,.0f})")

def demo_retailer_comparison():
    print("\n" + "="*50)
    print("🏪 RETAILER COMPARISON DEMO")
    print("="*50)
    
    test_products = ["P001", "P006", "P013"]  # Different price ranges
    
    for product_id in test_products:
        result = get_retailer_comparison(product_id)
        
        if "error" in result:
            print(f"❌ Error for {product_id}: {result['error']}")
            continue
        
        print(f"\n📦 {result['product_name']} ({product_id})")
        print(f"📅 Date: {result['date']}")
        print("💰 Retailer Prices:")
        
        for rp in result["retailer_prices"]:
            if rp["is_best_deal"]:
                print(f"  🏆 {rp['retailer']:18} {rp['formatted_price']:>12} ← BEST DEAL")
            else:
                savings = rp.get('potential_savings', '₹0.00')
                print(f"     {rp['retailer']:18} {rp['formatted_price']:>12} (Save {savings})")

def demo_retailer_specific_forecast():
    print("\n" + "="*50)
    print("🎯 RETAILER-SPECIFIC FORECAST DEMO") 
    print("="*50)
    
    # Compare iPhone 16 across different retailers
    product_id = "P001"
    retailers = ["Amazon.in", "Flipkart", "RelianceDigital", "Croma"]
    
    print(f"🔍 COMPARING iPhone 16 FORECASTS ACROSS RETAILERS")
    print("-" * 60)
    
    retailer_results = []
    
    for retailer in retailers:
        result = forecast_for_product(product_id, retailer, horizon_days=3)
        
        if "error" in result:
            print(f"❌ {retailer}: {result['error']}")
            continue
        
        retailer_results.append({
            "retailer": retailer,
            "current_price": result['current_price'],
            "is_deal": result['great_deal'],
            "forecast_3d": result['forecast'][2]['price'] if len(result['forecast']) > 2 else 0
        })
    
    # Sort by current price
    retailer_results.sort(key=lambda x: x['current_price'])
    
    print(f"📊 Current Prices & 3-Day Forecasts:")
    for rr in retailer_results:
        deal_icon = "🔥" if rr['is_deal'] else "  "
        print(f"{deal_icon} {rr['retailer']:18} Current: ₹{rr['current_price']:8,.0f} → 3-day: ₹{rr['forecast_3d']:8,.0f}")

def demo_ml_insights():
    print("\n" + "="*50)
    print("🤖 ML MODEL INSIGHTS")
    print("="*50)
    
    print("🔬 Model Features:")
    print("  • Random Forest Regression for non-linear pattern detection")
    print("  • Seasonal awareness (day of year, month, quarter)")
    print("  • Sale period detection based on rapid price drops")
    print("  • Multi-criteria deal detection system")
    print("  • Uncertainty quantification with confidence intervals")
    
    print("\n📊 Deal Detection Criteria:")
    print("  1. Historical percentile analysis (bottom 5-10%)")
    print("  2. Recent price deviation (15%+ below 30-day average)")  
    print("  3. Forecast-based anomaly detection")
    print("  4. Cross-retailer price comparison")
    
    print("\n⚡ Performance Highlights:")
    print("  • 365 days of training data per product")
    print("  • 29,200 total data points across all products")
    print("  • Real-time retailer price comparison")
    print("  • Automated visualization generation")
    
    # Show a specific example
    print(f"\n🎯 Example Analysis:")
    result = forecast_for_product("P001", "Amazon.in", horizon_days=1)
    if "error" not in result:
        print(f"  Product: {result['product_name']}")
        print(f"  Retailer: {result['retailer']}")
        print(f"  Current Price: ₹{result['current_price']:,.2f}")
        print(f"  Training Data: {result['data_points']} days")
        if result['great_deal']:
            print(f"  🔥 Deal Status: GREAT DEAL DETECTED")
        else:
            print(f"  💰 Deal Status: No special deal")

def main():
    demo_header()
    
    # Check dataset availability
    if not demo_product_list():
        print("❌ Cannot continue demo - dataset not available")
        return
    
    print("\n🚀 Starting comprehensive demo...")
    input("⏵ Press Enter to continue...")
    
    # Run all demo sections
    demo_forecast_analysis()
    input("\n⏵ Press Enter for retailer comparison demo...")
    
    demo_retailer_comparison()
    input("\n⏵ Press Enter for retailer-specific forecast demo...")
    
    demo_retailer_specific_forecast()
    input("\n⏵ Press Enter for ML insights...")
    
    demo_ml_insights()
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("📁 Generated forecast charts are saved in: data/forecasts/")
    print("🚀 Ready for production use!")
    print("💡 Use 'python price_tracker_cli.py' for interactive mode")
    print("="*80)

if __name__ == "__main__":
    main()