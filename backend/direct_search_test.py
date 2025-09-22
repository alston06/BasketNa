"""
Direct test of the search logic without the server
"""

import sys
import os
sys.path.append('.')

def test_search_logic():
    print("🔍 Testing search logic directly...")
    
    try:
        from simple_main import load_data
        
        # Load data
        df = load_data()
        print(f"✅ Data loaded: {df.shape}")
        
        # Test iPhone search
        query = "iPhone"
        mask = df["product_name"].str.contains(query, case=False, na=False)
        results = df[mask]
        
        print(f"📱 iPhone search results: {len(results)} records")
        
        if len(results) > 0:
            # Get latest date for each product-site combination
            latest_date = results.groupby(["product_id", "site"])['date'].transform('max')
            latest_rows = results[results['date'] == latest_date].copy()
            
            print(f"📊 Latest records: {len(latest_rows)}")
            
            print(f"\n🎯 iPhone search results:")
            for _, row in latest_rows.head().iterrows():
                print(f"  📱 {row['product_name']} ({row['product_id']})")
                print(f"     🏪 {row['site']}: ₹{row['price']:,.2f}")
                print(f"     📅 Date: {row['date']}")
                print()
                
            # Check if it's the new dataset
            if any("iPhone 16" in name for name in latest_rows['product_name'].unique()):
                print("🎉 SUCCESS: Using NEW dataset (iPhone 16 found)!")
            elif any("iPhone 14" in name for name in latest_rows['product_name'].unique()):
                print("⚠️  ISSUE: Still using OLD dataset (iPhone 14 found)")
            else:
                print(f"❓ Unknown iPhone models found")
        else:
            print("❌ No iPhone results found")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_logic()