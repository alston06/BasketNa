#!/usr/bin/env python3
"""
Test script to verify spider functionality
"""

import subprocess
import sys
from pathlib import Path


def test_spider_listing():
    """Test if spiders can be listed"""
    print("Testing spider listing...")
    try:
        result = subprocess.run(['scrapy', 'list'], 
                              capture_output=True, text=True, check=True)
        spiders = result.stdout.strip().split('\n')
        print(f"✅ Found {len(spiders)} spiders: {', '.join(spiders)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error listing spiders: {e}")
        return False


def test_spider_check():
    """Test individual spider checks"""
    print("\nTesting individual spider checks...")
    spiders = ['amazon', 'flipkart', 'bigbasket', 'dmart']
    
    for spider in spiders:
        try:
            result = subprocess.run(['scrapy', 'check', spider], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ {spider} spider check passed")
        except subprocess.CalledProcessError as e:
            print(f"❌ {spider} spider check failed: {e.stderr.strip()}")


def test_directory_structure():
    """Test if required directories exist"""
    print("\nTesting directory structure...")
    required_dirs = ['ecommerce_scraper', 'ecommerce_scraper/spiders']
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path} exists")
        else:
            print(f"❌ {dir_path} missing")


def test_spider_files():
    """Test if spider files exist"""
    print("\nTesting spider files...")
    spider_files = [
        'ecommerce_scraper/spiders/amazon_spider.py',
        'ecommerce_scraper/spiders/flipkart_spider.py',
        'ecommerce_scraper/spiders/bigbasket_spider.py',
        'ecommerce_scraper/spiders/dmart_spider.py'
    ]
    
    for file_path in spider_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")


def test_configuration():
    """Test Scrapy configuration"""
    print("\nTesting Scrapy configuration...")
    config_files = ['scrapy.cfg', 'ecommerce_scraper/settings.py']
    
    for file_path in config_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")


def test_dependencies():
    """Test if required dependencies are available"""
    print("\nTesting dependencies...")
    try:
        import scrapy
        print(f"✅ Scrapy {scrapy.__version__} available")
    except ImportError:
        print("❌ Scrapy not available")
    
    try:
        import pandas
        print(f"✅ Pandas {pandas.__version__} available")
    except ImportError:
        print("❌ Pandas not available")
    
    try:
        import matplotlib
        print(f"✅ Matplotlib {matplotlib.__version__} available")
    except ImportError:
        print("❌ Matplotlib not available")


def main():
    """Run all tests"""
    print("=" * 50)
    print("E-COMMERCE SCRAPER TEST SUITE")
    print("=" * 50)
    
    tests = [
        test_directory_structure,
        test_spider_files,
        test_configuration,
        test_dependencies,
        test_spider_listing,
        test_spider_check
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All tests passed! The scraper is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
