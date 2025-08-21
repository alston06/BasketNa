#!/usr/bin/env python3
"""
Example script demonstrating programmatic usage of the e-commerce scraper
"""

import subprocess
import json
import time
from pathlib import Path


def run_spider_example():
    """Example of running a spider programmatically"""
    print("🚀 Running Amazon spider example...")
    
    # Run Amazon spider for laptops (limited to 2 pages)
    cmd = [
        'scrapy', 'crawl', 'amazon',
        '-a', 'search_query=laptop',
        '-a', 'max_pages=2',
        '-s', 'FEEDS=data/example_amazon.json:json'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Amazon spider completed successfully!")
        print(f"Output: {result.stdout}")
        return True
    except subprocess.CmdProcessError as e:
        print(f"❌ Amazon spider failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def analyze_example_data():
    """Example of analyzing scraped data"""
    print("\n📊 Analyzing example data...")
    
    # Check if data file exists
    data_file = Path('data/example_amazon.json')
    if not data_file.exists():
        print("❌ No data file found. Run the spider first.")
        return False
    
    try:
        # Load and analyze data
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} products")
        
        # Basic analysis
        platforms = set(item.get('platform', 'Unknown') for item in data)
        categories = set(item.get('category', 'Unknown') for item in data)
        
        print(f"Platforms: {', '.join(platforms)}")
        print(f"Categories: {', '.join(categories)}")
        
        # Price analysis
        prices = []
        for item in data:
            price = item.get('current_price')
            if price:
                try:
                    prices.append(float(str(price).replace(',', '')))
                except ValueError:
                    continue
        
        if prices:
            print(f"Price range: ₹{min(prices):.2f} - ₹{max(prices):.2f}")
            print(f"Average price: ₹{sum(prices)/len(prices):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")
        return False


def run_multiple_spiders():
    """Example of running multiple spiders"""
    print("\n🕷️  Running multiple spiders example...")
    
    spiders = [
        ('amazon', 'laptop', 1),
        ('flipkart', 'smartphone', 1)
    ]
    
    results = {}
    
    for spider_name, search_query, max_pages in spiders:
        print(f"\nRunning {spider_name} spider for '{search_query}'...")
        
        cmd = [
            'scrapy', 'crawl', spider_name,
            '-a', f'search_query={search_query}',
            '-a', f'max_pages={max_pages}',
            '-s', f'FEEDS=data/example_{spider_name}.json:json'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ {spider_name} spider completed!")
            results[spider_name] = True
        except subprocess.CalledProcessError as e:
            print(f"❌ {spider_name} spider failed: {e}")
            results[spider_name] = False
        
        # Add delay between spiders
        time.sleep(2)
    
    # Summary
    successful = sum(1 for success in results.values() if success)
    print(f"\n📈 Summary: {successful}/{len(spiders)} spiders completed successfully")
    
    return results


def create_sample_config():
    """Create a sample configuration file"""
    print("\n⚙️  Creating sample configuration...")
    
    config = {
        "spiders": {
            "amazon": {
                "search_query": "laptop",
                "max_pages": 3,
                "category": None
            },
            "flipkart": {
                "search_query": "smartphone",
                "max_pages": 2,
                "category": None
            },
            "bigbasket": {
                "search_query": None,
                "max_pages": 2,
                "category": "fruits-vegetables"
            }
        },
        "output": {
            "format": "json",
            "directory": "data",
            "filename_template": "products_{platform}_{timestamp}"
        },
        "settings": {
            "download_delay": 2,
            "concurrent_requests": 8,
            "max_pages_per_spider": 5
        }
    }
    
    config_file = Path('sample_config.json')
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Sample configuration saved to: {config_file}")
    return config_file


def main():
    """Main example function"""
    print("=" * 60)
    print("E-COMMERCE SCRAPER - EXAMPLE USAGE")
    print("=" * 60)
    
    # Create data directory
    Path('data').mkdir(exist_ok=True)
    
    # Example 1: Run single spider
    print("\n1️⃣  SINGLE SPIDER EXAMPLE")
    print("-" * 30)
    run_spider_example()
    
    # Example 2: Analyze data
    print("\n2️⃣  DATA ANALYSIS EXAMPLE")
    print("-" * 30)
    analyze_example_data()
    
    # Example 3: Run multiple spiders
    print("\n3️⃣  MULTIPLE SPIDERS EXAMPLE")
    print("-" * 30)
    run_multiple_spiders()
    
    # Example 4: Create sample config
    print("\n4️⃣  CONFIGURATION EXAMPLE")
    print("-" * 30)
    create_sample_config()
    
    print("\n" + "=" * 60)
    print("🎉 EXAMPLES COMPLETED!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check the 'data/' directory for scraped data")
    print("2. Run 'python data_analyzer.py' to analyze the data")
    print("3. Customize the spiders for your specific needs")
    print("4. Use 'python run_spiders.py --help' for command-line usage")


if __name__ == '__main__':
    main()
