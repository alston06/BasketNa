#!/usr/bin/env python3
"""
Main script to run e-commerce spiders
Supports running individual spiders or all spiders with various configurations
"""

import argparse
import subprocess
from pathlib import Path


def run_spider(spider_name, **kwargs):
    """Run a specific spider with given parameters"""
    cmd = ['scrapy', 'crawl', spider_name]
    
    # Add spider parameters
    for key, value in kwargs.items():
        if value is not None:
            cmd.extend(['-a', f'{key}={value}'])
    
    print(f"Running spider: {spider_name}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd='.', check=True, capture_output=True, text=True)
        print(f"Spider {spider_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running spider {spider_name}: {e}")
        print(f"Error output: {e.stderr}")
        return False


def run_all_spiders(**kwargs):
    """Run all available spiders"""
    spiders = ['amazon', 'flipkart', 'bigbasket', 'dmart']
    results = {}
    
    print("Starting all spiders...")
    
    for spider in spiders:
        print(f"\n{'='*50}")
        print(f"Running {spider.upper()} spider")
        print(f"{'='*50}")
        
        success = run_spider(spider, **kwargs)
        results[spider] = success
        
        if success:
            print(f"✅ {spider} completed successfully")
        else:
            print(f"❌ {spider} failed")
    
    # Summary
    print(f"\n{'='*50}")
    print("SPIDER EXECUTION SUMMARY")
    print(f"{'='*50}")
    
    successful = sum(1 for success in results.values() if success)
    total = len(spiders)
    
    for spider, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{spider:12} : {status}")
    
    print(f"\nOverall: {successful}/{total} spiders completed successfully")
    
    return results


def list_spiders():
    """List all available spiders"""
    cmd = ['scrapy', 'list']
    try:
        result = subprocess.run(cmd, cwd='.', check=True, capture_output=True, text=True)
        spiders = result.stdout.strip().split('\n')
        print("Available spiders:")
        for spider in spiders:
            if spider:
                print(f"  - {spider}")
    except subprocess.CalledProcessError as e:
        print(f"Error listing spiders: {e}")


def check_spider_status(spider_name):
    """Check if a spider exists and is properly configured"""
    cmd = ['scrapy', 'list']
    try:
        result = subprocess.run(cmd, cwd='.', check=True, capture_output=True, text=True)
        spiders = result.stdout.strip().split('\n')
        if spider_name in spiders:
            print(f"✅ Spider '{spider_name}' is available")
            return True
        else:
            print(f"❌ Spider '{spider_name}' not found")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking spider status: {e}")
        return False


def create_data_directories():
    """Create necessary data directories"""
    directories = ['data', 'logs', 'images']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")


def main():
    parser = argparse.ArgumentParser(description='E-commerce Web Scraper')
    parser.add_argument('--spider', '-s', help='Specific spider to run')
    parser.add_argument('--all', '-a', action='store_true', help='Run all spiders')
    parser.add_argument('--list', '-l', action='store_true', help='List available spiders')
    parser.add_argument('--search', help='Search query for products')
    parser.add_argument('--category', help='Product category to scrape')
    parser.add_argument('--max-pages', type=int, default=5, help='Maximum pages to scrape per spider')
    parser.add_argument('--check', help='Check if a specific spider exists')
    
    args = parser.parse_args()
    
    # Create data directories
    create_data_directories()
    
    if args.list:
        list_spiders()
        return
    
    if args.check:
        check_spider_status(args.check)
        return
    
    if args.all:
        run_all_spiders(
            search_query=args.search,
            category=args.category,
            max_pages=args.max_pages
        )
    elif args.spider:
        if check_spider_status(args.spider):
            run_spider(
                args.spider,
                search_query=args.search,
                category=args.category,
                max_pages=args.max_pages
            )
    else:
        print("No action specified. Use --help for usage information.")
        print("\nExample usage:")
        print("  python run_spiders.py --spider amazon --search 'laptop' --max-pages 3")
        print("  python run_spiders.py --all --category 'electronics' --max-pages 5")
        print("  python run_spiders.py --list")


if __name__ == '__main__':
    main()
