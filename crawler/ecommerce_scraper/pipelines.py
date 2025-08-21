# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import csv
import os
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class EcommerceScraperPipeline:
    """Main pipeline for processing scraped items"""
    
    def process_item(self, item, spider):
        # Add timestamp if not present
        if not item.get('scraped_at'):
            item['scraped_at'] = datetime.now().isoformat()
        
        # Validate required fields
        required_fields = ['product_name', 'current_price', 'platform']
        for field in required_fields:
            if not item.get(field):
                item['scraping_errors'] = f"Missing required field: {field}"
                item['is_complete'] = False
                return item
        
        # Clean and normalize data
        item = self._clean_item_data(item)
        
        # Mark as complete if no errors
        if not item.get('scraping_errors'):
            item['is_complete'] = True
        
        return item
    
    def _clean_item_data(self, item):
        """Clean and normalize item data"""
        adapter = ItemAdapter(item)
        
        # Clean product name
        if adapter.get('product_name'):
            adapter['product_name'] = adapter['product_name'].strip()
        
        # Clean price data
        if adapter.get('current_price'):
            adapter['current_price'] = self._extract_price(adapter['current_price'])
        
        if adapter.get('original_price'):
            adapter['original_price'] = self._extract_price(adapter['original_price'])
        
        # Clean discount percentage
        if adapter.get('discount_percentage'):
            adapter['discount_percentage'] = self._extract_percentage(adapter['discount_percentage'])
        
        # Clean ratings
        if adapter.get('product_rating'):
            adapter['product_rating'] = self._extract_rating(adapter['product_rating'])
        
        # Clean review counts
        if adapter.get('product_reviews_count'):
            adapter['product_reviews_count'] = self._extract_number(adapter['product_reviews_count'])
        
        return item
    
    def _extract_price(self, price_str):
        """Extract numeric price from string"""
        if not price_str:
            return None
        
        import re
        # Remove currency symbols and extract numbers
        price_match = re.search(r'[\d,]+\.?\d*', str(price_str))
        if price_match:
            return float(price_match.group().replace(',', ''))
        return None
    
    def _extract_percentage(self, percentage_str):
        """Extract numeric percentage from string"""
        if not percentage_str:
            return None
        
        import re
        # Extract numbers followed by % or just numbers
        percentage_match = re.search(r'(\d+\.?\d*)%?', str(percentage_str))
        if percentage_match:
            return float(percentage_match.group(1))
        return None
    
    def _extract_rating(self, rating_str):
        """Extract numeric rating from string"""
        if not rating_str:
            return None
        
        import re
        # Extract numbers (usually 1-5 scale)
        rating_match = re.search(r'(\d+\.?\d*)', str(rating_str))
        if rating_match:
            rating = float(rating_match.group(1))
            # Normalize to 5-point scale if needed
            if rating > 5 and rating <= 10:
                rating = rating / 2
            return rating
        return None
    
    def _extract_number(self, number_str):
        """Extract numeric value from string"""
        if not number_str:
            return None
        
        import re
        # Extract numbers, handling K, M suffixes
        number_match = re.search(r'([\d,]+\.?\d*)([KM]?)', str(number_str))
        if number_match:
            number = float(number_match.group(1).replace(',', ''))
            suffix = number_match.group(2)
            if suffix == 'K':
                number *= 1000
            elif suffix == 'M':
                number *= 1000000
            return int(number)
        return None


class DuplicatesPipeline:
    """Pipeline to remove duplicate items based on product_id and platform"""
    
    def __init__(self):
        self.ids_seen = set()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        product_id = adapter.get('product_id')
        platform = adapter.get('platform')
        
        if not product_id or not platform:
            return item
        
        # Create unique identifier
        unique_id = f"{platform}_{product_id}"
        
        if unique_id in self.ids_seen:
            raise DropItem(f"Duplicate item found: {unique_id}")
        else:
            self.ids_seen.add(unique_id)
            return item


class JsonWriterPipeline:
    """Pipeline to write items to JSON file"""
    
    def __init__(self):
        self.file = None
        self.items = []
    
    def open_spider(self, spider):
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/products_{timestamp}.json'
        self.file = open(filename, 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True
    
    def close_spider(self, spider):
        if self.file:
            self.file.write('\n]')
            self.file.close()
    
    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(',\n')
        
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False, indent=2)
        self.file.write(line)
        self.first_item = False
        
        return item


class CsvWriterPipeline:
    """Pipeline to write items to CSV file"""
    
    def __init__(self):
        self.file = None
        self.writer = None
    
    def open_spider(self, spider):
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/products_{timestamp}.csv'
        self.file = open(filename, 'w', newline='', encoding='utf-8')
        
        # Define CSV headers based on item fields
        self.headers = [
            'product_id', 'product_name', 'product_url', 'product_image_url',
            'current_price', 'original_price', 'discount_percentage', 'currency',
            'brand', 'category', 'subcategory', 'description',
            'platform', 'seller_name', 'seller_rating', 'seller_reviews_count',
            'product_rating', 'product_reviews_count',
            'availability', 'shipping_info', 'delivery_estimate',
            'sku', 'model_number', 'weight', 'dimensions',
            'scraped_at', 'last_updated', 'tags', 'features', 'specifications',
            'scraping_errors', 'is_complete'
        ]
        
        self.writer = csv.DictWriter(self.file, fieldnames=self.headers)
        self.writer.writeheader()
    
    def close_spider(self, spider):
        if self.file:
            self.file.close()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        row = {}
        
        # Fill in all fields, using empty string for missing values
        for header in self.headers:
            row[header] = adapter.get(header, '')
        
        self.writer.writerow(row)
        return item


class DatabasePipeline:
    """Pipeline to store items in database (placeholder for future implementation)"""
    
    def __init__(self):
        # Initialize database connection here
        pass
    
    def process_item(self, item, spider):
        # Store item in database
        # This is a placeholder for future database integration
        return item
    
    def close_spider(self, spider):
        # Close database connection
        pass


class ImageDownloadPipeline:
    """Pipeline to download product images (optional)"""
    
    def __init__(self):
        self.image_dir = 'images'
        os.makedirs(self.image_dir, exist_ok=True)
    
    def process_item(self, item, spider):
        # Download image if enabled in settings
        # This is a placeholder for future image download functionality
        return item
