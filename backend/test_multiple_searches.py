"""
Test multiple search terms with the new dataset
"""

from simple_main import load_data

def test_multiple_searches():
    df = load_data()
    print(f"📊 Dataset loaded: {df.shape[0]:,} records")
    print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
    print()
    
    # Test various search terms
    search_terms = ["iPhone", "Samsung", "laptop", "MacBook", "headphones", "watch", "TV"]
    
    for term in search_terms:
        print(f"🔍 Searching for '{term}':")
        mask = df["product_name"].str.contains(term, case=False, na=False)
        results = df[mask]
        
        if len(results) > 0:
            # Get unique products
            unique_products = results['product_name'].unique()
            print(f"  ✅ Found {len(results):,} records, {len(unique_products)} unique products")
            
            # Show products
            for product in unique_products[:3]:  # Show first 3
                print(f"    📱 {product}")
                
            # Show price range
            latest_prices = results[results['date'] == results['date'].max()]
            if len(latest_prices) > 0:
                min_price = latest_prices['price'].min()
                max_price = latest_prices['price'].max()
                print(f"    💰 Price range: ₹{min_price:,.0f} - ₹{max_price:,.0f}")
        else:
            print(f"  ❌ No results found")
        print()

if __name__ == "__main__":
    test_multiple_searches()