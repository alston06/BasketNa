#!/usr/bin/env python3
"""
Data analysis script for scraped e-commerce data
Provides insights, statistics, and data visualization
"""

import json
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import argparse
import os


class EcommerceDataAnalyzer:
    """Analyze scraped e-commerce data"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.data = None
        self.df = None
        
    def load_latest_data(self):
        """Load the most recent data file"""
        data_files = list(self.data_dir.glob('*.json'))
        if not data_files:
            print("No data files found")
            return False
        
        # Get the most recent file
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        print(f"Loading data from: {latest_file}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # Convert to DataFrame
            self.df = pd.DataFrame(self.data)
            print(f"Loaded {len(self.df)} products")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def load_csv_data(self, filename=None):
        """Load data from CSV file"""
        if filename:
            csv_file = self.data_dir / filename
        else:
            # Get the most recent CSV file
            csv_files = list(self.data_dir.glob('*.csv'))
            if not csv_files:
                print("No CSV files found")
                return False
            csv_file = max(csv_files, key=lambda x: x.stat().st_mtime)
        
        try:
            self.df = pd.read_csv(csv_file)
            print(f"Loaded {len(self.df)} products from CSV")
            return True
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    
    def basic_statistics(self):
        """Generate basic statistics"""
        if self.df is None:
            print("No data loaded")
            return
        
        print("\n" + "="*60)
        print("BASIC STATISTICS")
        print("="*60)
        
        # Platform distribution
        print(f"\nPlatform Distribution:")
        platform_counts = self.df['platform'].value_counts()
        for platform, count in platform_counts.items():
            print(f"  {platform}: {count} products")
        
        # Price statistics
        if 'current_price' in self.df.columns:
            price_col = 'current_price'
        elif 'price' in self.df.columns:
            price_col = 'price'
        else:
            price_col = None
        
        if price_col and self.df[price_col].notna().any():
            prices = pd.to_numeric(self.df[price_col], errors='coerce').dropna()
            if len(prices) > 0:
                print(f"\nPrice Statistics (INR):")
                print(f"  Mean: ₹{prices.mean():.2f}")
                print(f"  Median: ₹{prices.median():.2f}")
                print(f"  Min: ₹{prices.min():.2f}")
                print(f"  Max: ₹{prices.max():.2f}")
                print(f"  Standard Deviation: ₹{prices.std():.2f}")
        
        # Rating statistics
        if 'product_rating' in self.df.columns:
            ratings = self.df['product_rating'].dropna()
            if len(ratings) > 0:
                print(f"\nRating Statistics:")
                print(f"  Mean: {ratings.mean():.2f}/5")
                print(f"  Median: {ratings.median():.2f}/5")
                print(f"  Min: {ratings.min():.2f}/5")
                print(f"  Max: {ratings.max():.2f}/5")
        
        # Category distribution
        if 'category' in self.df.columns:
            print(f"\nTop Categories:")
            category_counts = self.df['category'].value_counts().head(10)
            for category, count in category_counts.items():
                print(f"  {category}: {count} products")
    
    def price_analysis(self):
        """Analyze price patterns"""
        if self.df is None:
            print("No data loaded")
            return
        
        print("\n" + "="*60)
        print("PRICE ANALYSIS")
        print("="*60)
        
        # Find price column
        price_col = None
        for col in ['current_price', 'price']:
            if col in self.df.columns:
                price_col = col
                break
        
        if not price_col:
            print("No price data found")
            return
        
        # Convert prices to numeric
        self.df['price_numeric'] = pd.to_numeric(self.df[price_col], errors='coerce')
        prices_df = self.df.dropna(subset=['price_numeric'])
        
        if len(prices_df) == 0:
            print("No valid price data found")
            return
        
        # Price by platform
        print(f"\nPrice by Platform:")
        platform_prices = prices_df.groupby('platform')['price_numeric'].agg(['mean', 'median', 'count'])
        print(platform_prices.round(2))
        
        # Price by category
        if 'category' in prices_df.columns:
            print(f"\nTop 10 Categories by Average Price:")
            category_prices = prices_df.groupby('category')['price_numeric'].agg(['mean', 'count']).round(2)
            category_prices = category_prices.sort_values('mean', ascending=False).head(10)
            print(category_prices)
        
        # Discount analysis
        if 'discount_percentage' in prices_df.columns:
            discounts = pd.to_numeric(prices_df['discount_percentage'], errors='coerce').dropna()
            if len(discounts) > 0:
                print(f"\nDiscount Statistics:")
                print(f"  Mean discount: {discounts.mean():.2f}%")
                print(f"  Max discount: {discounts.max():.2f}%")
                print(f"  Products with discount: {len(discounts)}")
    
    def platform_comparison(self):
        """Compare data across platforms"""
        if self.df is None:
            print("No data loaded")
            return
        
        print("\n" + "="*60)
        print("PLATFORM COMPARISON")
        print("="*60)
        
        platforms = self.df['platform'].unique()
        
        for platform in platforms:
            platform_data = self.df[self.df['platform'] == platform]
            print(f"\n{platform.upper()}:")
            print(f"  Total products: {len(platform_data)}")
            
            # Price statistics
            if 'current_price' in platform_data.columns:
                prices = pd.to_numeric(platform_data['current_price'], errors='coerce').dropna()
                if len(prices) > 0:
                    print(f"  Average price: ₹{prices.mean():.2f}")
                    print(f"  Price range: ₹{prices.min():.2f} - ₹{prices.max():.2f}")
            
            # Rating statistics
            if 'product_rating' in platform_data.columns:
                ratings = platform_data['product_rating'].dropna()
                if len(ratings) > 0:
                    print(f"  Average rating: {ratings.mean():.2f}/5")
            
            # Category distribution
            if 'category' in platform_data.columns:
                top_categories = platform_data['category'].value_counts().head(3)
                print(f"  Top categories: {', '.join(top_categories.index)}")
    
    def create_visualizations(self, output_dir='charts'):
        """Create data visualizations"""
        if self.df is None:
            print("No data loaded")
            return
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\nCreating visualizations in: {output_path}")
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Platform distribution
        plt.figure(figsize=(10, 6))
        platform_counts = self.df['platform'].value_counts()
        plt.pie(platform_counts.values, labels=platform_counts.index, autopct='%1.1f%%')
        plt.title('Product Distribution by Platform')
        plt.savefig(output_path / 'platform_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Price distribution by platform
        price_col = None
        for col in ['current_price', 'price']:
            if col in self.df.columns:
                price_col = col
                break
        
        if price_col:
            self.df['price_numeric'] = pd.to_numeric(self.df[price_col], errors='coerce')
            prices_df = self.df.dropna(subset=['price_numeric'])
            
            if len(prices_df) > 0:
                plt.figure(figsize=(12, 6))
                for platform in prices_df['platform'].unique():
                    platform_prices = prices_df[prices_df['platform'] == platform]['price_numeric']
                    plt.hist(platform_prices, alpha=0.7, label=platform, bins=30)
                
                plt.xlabel('Price (INR)')
                plt.ylabel('Frequency')
                plt.title('Price Distribution by Platform')
                plt.legend()
                plt.yscale('log')
                plt.savefig(output_path / 'price_distribution.png', dpi=300, bbox_inches='tight')
                plt.close()
        
        # 3. Category distribution
        if 'category' in self.df.columns:
            plt.figure(figsize=(12, 8))
            top_categories = self.df['category'].value_counts().head(15)
            plt.barh(range(len(top_categories)), top_categories.values)
            plt.yticks(range(len(top_categories)), top_categories.index)
            plt.xlabel('Number of Products')
            plt.title('Top 15 Product Categories')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig(output_path / 'category_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. Rating distribution
        if 'product_rating' in self.df.columns:
            ratings = self.df['product_rating'].dropna()
            if len(ratings) > 0:
                plt.figure(figsize=(10, 6))
                plt.hist(ratings, bins=20, alpha=0.7, edgecolor='black')
                plt.xlabel('Rating')
                plt.ylabel('Frequency')
                plt.title('Product Rating Distribution')
                plt.savefig(output_path / 'rating_distribution.png', dpi=300, bbox_inches='tight')
                plt.close()
        
        print("Visualizations created successfully!")
    
    def export_summary(self, output_file='analysis_summary.txt'):
        """Export analysis summary to text file"""
        if self.df is None:
            print("No data loaded")
            return
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("E-COMMERCE DATA ANALYSIS SUMMARY\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total products analyzed: {len(self.df)}\n\n")
            
            # Platform summary
            f.write("PLATFORM SUMMARY:\n")
            f.write("-" * 20 + "\n")
            platform_counts = self.df['platform'].value_counts()
            for platform, count in platform_counts.items():
                f.write(f"{platform}: {count} products\n")
            
            # Price summary
            price_col = None
            for col in ['current_price', 'price']:
                if col in self.df.columns:
                    price_col = col
                    break
            
            if price_col:
                prices = pd.to_numeric(self.df[price_col], errors='coerce').dropna()
                if len(prices) > 0:
                    f.write(f"\nPRICE SUMMARY:\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Mean price: ₹{prices.mean():.2f}\n")
                    f.write(f"Median price: ₹{prices.median():.2f}\n")
                    f.write(f"Price range: ₹{prices.min():.2f} - ₹{prices.max():.2f}\n")
            
            # Category summary
            if 'category' in self.df.columns:
                f.write(f"\nCATEGORY SUMMARY:\n")
                f.write("-" * 20 + "\n")
                top_categories = self.df['category'].value_counts().head(10)
                for category, count in top_categories.items():
                    f.write(f"{category}: {count} products\n")
        
        print(f"Analysis summary exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='E-commerce Data Analyzer')
    parser.add_argument('--data-dir', default='data', help='Directory containing data files')
    parser.add_argument('--csv', help='Specific CSV file to analyze')
    parser.add_argument('--output-dir', default='charts', help='Directory for output charts')
    parser.add_argument('--export', help='Export summary to specified file')
    
    args = parser.parse_args()
    
    analyzer = EcommerceDataAnalyzer(args.data_dir)
    
    # Load data
    if args.csv:
        success = analyzer.load_csv_data(args.csv)
    else:
        success = analyzer.load_latest_data()
    
    if not success:
        print("Failed to load data")
        return
    
    # Run analysis
    analyzer.basic_statistics()
    analyzer.price_analysis()
    analyzer.platform_comparison()
    
    # Create visualizations
    analyzer.create_visualizations(args.output_dir)
    
    # Export summary if requested
    if args.export:
        analyzer.export_summary(args.export)
    else:
        analyzer.export_summary()


if __name__ == '__main__':
    main()
