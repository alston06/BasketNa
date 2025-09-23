"""
E-commerce Price Tracker - Interactive Interface
Simple command-line interface for the enhanced ML forecasting model
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from forecast_enhanced import forecast_for_product, get_retailer_comparison, get_available_products

def display_menu():
    print("\n" + "="*60)
    print("🛒 E-COMMERCE PRICE TRACKER & FORECASTER")
    print("="*60)
    print("1. Product Price Forecast")
    print("2. Retailer Price Comparison") 
    print("3. List Available Products")
    print("4. Product Forecast (Specific Retailer)")
    print("5. Exit")
    print("-"*60)

def list_products():
    products = get_available_products()
    if not products:
        print("❌ No products available. Make sure the dataset exists.")
        return
    
    print(f"\n📦 AVAILABLE PRODUCTS ({len(products)} total):")
    print("-"*50)
    
    categories = {
        "Smartphones": ["P001", "P002", "P003", "P004"],
        "Laptops": ["P005", "P006", "P007", "P008"], 
        "Audio": ["P009", "P010", "P011", "P012"],
        "Wearables": ["P013", "P014"],
        "Home Entertainment": ["P015", "P016", "P017"],
        "Cameras & Accessories": ["P018", "P019", "P020"]
    }
    
    for category, product_ids in categories.items():
        print(f"\n📱 {category}:")
        for pid in product_ids:
            if pid in products:
                print(f"  {pid}: {products[pid]}")

def get_product_forecast():
    product_id = input("\n🔍 Enter Product ID (e.g., P001): ").strip().upper()
    if not product_id:
        print("❌ Invalid product ID")
        return
    
    print(f"\n⏳ Generating forecast for {product_id}...")
    result = forecast_for_product(product_id)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        if "available_products" in result:
            print("\n📦 Available products:")
            for pid, pname in list(result["available_products"].items())[:10]:
                print(f"  {pid}: {pname}")
        return
    
    print(f"\n✅ FORECAST RESULTS")
    print(f"📦 Product: {result['product_name']}")
    print(f"💰 Current Price: ₹{result['current_price']:,.2f}")
    print(f"📈 Recent Trend: {result['recent_trend'].title()}")
    
    if result['great_deal']:
        print(f"\n🔥 GREAT DEAL DETECTED!")
        print(f"💡 {result['great_deal_reason']}")
    
    print(f"\n📊 Forecast (Next 7 Days):")
    for i, fp in enumerate(result['forecast'][:7]):
        print(f"  {fp['date']}: ₹{fp['price']:7,.0f} (₹{fp['lower']:,.0f} - ₹{fp['upper']:,.0f})")
    
    print(f"\n📈 Chart saved to: {result['forecast_plot']}")

def get_retailer_comparison_interactive():
    product_id = input("\n🔍 Enter Product ID (e.g., P001): ").strip().upper()
    if not product_id:
        print("❌ Invalid product ID")
        return
    
    print(f"\n⏳ Comparing prices for {product_id}...")
    result = get_retailer_comparison(product_id)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"\n💰 RETAILER PRICE COMPARISON")
    print(f"📦 Product: {result['product_name']}")
    print(f"📅 Date: {result['date']}")
    print(f"\n🏪 Prices by Retailer:")
    
    for rp in result["retailer_prices"]:
        if rp["is_best_deal"]:
            print(f"  🏆 {rp['retailer']:20} {rp['formatted_price']:>12} ← BEST DEAL")
        else:
            savings = rp.get('potential_savings', '₹0')
            print(f"     {rp['retailer']:20} {rp['formatted_price']:>12} (Save {savings})")

def get_specific_retailer_forecast():
    product_id = input("\n🔍 Enter Product ID (e.g., P001): ").strip().upper()
    if not product_id:
        print("❌ Invalid product ID")
        return
    
    print("\n🏪 Available Retailers:")
    retailers = ["Amazon.in", "Flipkart", "RelianceDigital", "Croma"]
    for i, retailer in enumerate(retailers, 1):
        print(f"  {i}. {retailer}")
    
    try:
        choice = int(input("\nSelect retailer (1-4): ").strip())
        if choice < 1 or choice > 4:
            print("❌ Invalid choice")
            return
        retailer = retailers[choice - 1]
    except ValueError:
        print("❌ Invalid input")
        return
    
    print(f"\n⏳ Generating forecast for {product_id} on {retailer}...")
    result = forecast_for_product(product_id, retailer)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"\n✅ FORECAST RESULTS")
    print(f"📦 Product: {result['product_name']}")
    print(f"🏪 Retailer: {result['retailer']}")
    print(f"💰 Current Price: ₹{result['current_price']:,.2f}")
    print(f"📈 Recent Trend: {result['recent_trend'].title()}")
    
    if result['great_deal']:
        print(f"\n🔥 GREAT DEAL DETECTED!")
        print(f"💡 {result['great_deal_reason']}")
    
    print(f"\n📊 Forecast (Next 7 Days):")
    for i, fp in enumerate(result['forecast'][:7]):
        print(f"  {fp['date']}: ₹{fp['price']:7,.0f} (₹{fp['lower']:,.0f} - ₹{fp['upper']:,.0f})")
    
    print(f"\n📈 Chart saved to: {result['forecast_plot']}")

def main():
    print("🚀 Initializing E-commerce Price Tracker...")
    
    # Check if dataset exists
    try:
        products = get_available_products()
        if not products:
            print("❌ Dataset not found! Please ensure ecommerce_price_dataset.csv exists in the data folder.")
            return
        print(f"✅ Dataset loaded successfully! {len(products)} products available.")
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return
    
    while True:
        display_menu()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                get_product_forecast()
            elif choice == "2":
                get_retailer_comparison_interactive()
            elif choice == "3":
                list_products()
            elif choice == "4":
                get_specific_retailer_forecast()
            elif choice == "5":
                print("\n👋 Thank you for using E-commerce Price Tracker!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
        
        input("\n⏵ Press Enter to continue...")

if __name__ == "__main__":
    main()