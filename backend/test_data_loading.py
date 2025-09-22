"""
Simple test to verify the backend data loading
"""

import sys
import os
sys.path.append('.')

# Test loading the data directly
try:
    from main import load_data
    
    df = load_data()
    print(f"✅ Dataset loaded successfully!")
    print(f"📊 Shape: {df.shape}")
    print(f"📝 Columns: {df.columns.tolist()}")
    
    print(f"\n📱 Unique products:")
    for i, product in enumerate(df['product_name'].unique()[:10], 1):
        print(f"  {i:2d}. {product}")
    
    print(f"\n🏪 Unique retailers:")
    for retailer in df['site'].unique():
        print(f"  - {retailer}")
    
    print(f"\n🔍 Testing iPhone search:")
    mask = df["product_name"].str.contains("iPhone", case=False, na=False)
    iphone_results = df[mask]
    print(f"  Found {len(iphone_results)} iPhone records")
    
    if len(iphone_results) > 0:
        print(f"  Sample iPhone products:")
        for product in iphone_results['product_name'].unique():
            print(f"    - {product}")
    
    print(f"\n📅 Date range:")
    print(f"  From: {df['date'].min()}")
    print(f"  To: {df['date'].max()}")
    
except Exception as e:
    print(f"❌ Error loading data: {e}")
    import traceback
    traceback.print_exc()