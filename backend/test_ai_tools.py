"""
Test script for the enhanced AI agent tools.
This script tests the functionality of the find_coupons and summarize_reviews tools.
"""

import asyncio
import json
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.tools.find_coupons import find_coupons
from agents.tools.summarize_reviews import summarize_reviews


async def test_find_coupons():
    """Test the find_coupons tool"""
    print("🎫 Testing find_coupons tool...")
    
    test_products = ["iPhone 16", "Samsung Galaxy S26 Ultra", "Sony WH-1000XM6 Headphones"]
    
    for product in test_products:
        print(f"\n--- Testing coupons for: {product} ---")
        try:
            result = await find_coupons(product)
            print(f"✅ Success! Found {result['total_coupons_found']} coupons")
            print(f"💰 Max potential savings: ₹{result['max_potential_savings']}")
            
            # Show first coupon details
            if result['coupons']:
                first_coupon = result['coupons'][0]
                print(f"🏷️  Best coupon: {first_coupon['code']} - {first_coupon['discount']}")
                print(f"📝 Description: {first_coupon['description']}")
            
        except Exception as e:
            print(f"❌ Error testing {product}: {e}")


async def test_summarize_reviews():
    """Test the summarize_reviews tool"""
    print("\n\n📝 Testing summarize_reviews tool...")
    
    test_products = ["iPhone 16", "Dell XPS 15"]
    test_sites = ["all", "amazon"]
    
    for product in test_products:
        for site in test_sites:
            print(f"\n--- Testing reviews for: {product} on {site} ---")
            try:
                result = await summarize_reviews(product, site)
                print(f"✅ Success! Analyzed {result['total_reviews_analyzed']} reviews")
                print(f"⭐ Average rating: {result['average_rating']}/5")
                print(f"😊 Positive sentiment: {result['sentiment_breakdown']['positive']}%")
                
                # Show key insights
                if result['key_positives']:
                    print(f"👍 Key positives: {', '.join(result['key_positives'])}")
                if result['key_negatives']:
                    print(f"👎 Key concerns: {', '.join(result['key_negatives'])}")
                
                print(f"📊 Summary: {result['summary_text']}")
                
            except Exception as e:
                print(f"❌ Error testing {product} on {site}: {e}")


async def test_tool_integration():
    """Test the tool integration module"""
    print("\n\n🔧 Testing tool integration...")
    
    try:
        from agents.tools.tool_integration import tools_integration
        
        product = "Apple MacBook Air (M4)"
        print(f"\n--- Testing comprehensive analysis for: {product} ---")
        
        result = await tools_integration.get_comprehensive_product_info(product)
        print(f"✅ Comprehensive analysis successful!")
        print(f"🛍️  Product: {result['product_name']}")
        print(f"🎫 Coupons found: {result['coupons']['total_coupons_found']}")
        print(f"📝 Reviews analyzed: {result['reviews']['total_reviews_analyzed']}")
        
    except Exception as e:
        print(f"❌ Error testing tool integration: {e}")


async def main():
    """Run all tests"""
    print("🚀 Starting AI Agent Tools Test Suite")
    print("=" * 50)
    
    await test_find_coupons()
    await test_summarize_reviews()
    await test_tool_integration()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())