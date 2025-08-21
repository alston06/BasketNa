# -*- coding: utf-8 -*-

import re
from datetime import datetime
from urllib.parse import urljoin

import scrapy

from ecommerce_scraper.items import EcommerceProductItem


class BigBasketSpider(scrapy.Spider):
    name = 'bigbasket'
    allowed_domains = ['bigbasket.com']
    
    def __init__(self, category=None, search_query=None, max_pages=10, *args, **kwargs):
        super(BigBasketSpider, self).__init__(*args, **kwargs)
        self.category = category
        self.search_query = search_query
        self.max_pages = int(max_pages)
        self.current_page = 1
        
        # Base URLs for different search types
        if self.search_query:
            self.start_urls = [
                f'https://www.bigbasket.com/ps/?q={self.search_query.replace(" ", "%20")}'
            ]
        elif self.category:
            self.start_urls = [
                f'https://www.bigbasket.com/{self.category}'
            ]
        else:
            # Default to fruits & vegetables category
            self.start_urls = [
                'https://www.bigbasket.com/pc/fruits-vegetables/'
            ]
    
    def parse(self, response):
        """Parse the search results page"""
        self.logger.info(f"Parsing page {self.current_page}: {response.url}")
        
        # Extract product links from search results
        product_links = response.css('a[href*="/pd/"]::attr(href)').getall()
        
        # Filter and clean product links
        product_links = [link for link in product_links if '/pd/' in link]
        
        # Follow product links
        for link in product_links[:20]:  # Limit to 20 products per page
            full_url = urljoin(response.url, link)
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_product,
                meta={'dont_cache': True}
            )
        
        # Follow next page if available and within limit
        if self.current_page < self.max_pages:
            next_page = response.css('a[class*="next"]::attr(href)').get()
            if next_page:
                self.current_page += 1
                next_url = urljoin(response.url, next_page)
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    meta={'dont_cache': True}
                )
    
    def parse_product(self, response):
        """Parse individual product page"""
        try:
            item = EcommerceProductItem()
            
            # Basic product information
            item['platform'] = 'BigBasket'
            item['product_url'] = response.url
            item['scraped_at'] = datetime.now().isoformat()
            
            # Extract product ID from URL
            product_id_match = re.search(r'/pd/([A-Z0-9-]+)', response.url)
            if product_id_match:
                item['product_id'] = product_id_match.group(1)
            
            # Product name
            product_name = response.css('h1[class*="product-name"]::text').get()
            if not product_name:
                product_name = response.css('h1::text').get()
            if product_name:
                item['product_name'] = product_name.strip()
            
            # Product image
            image_url = response.css('img[class*="product-image"]::attr(src)').get()
            if not image_url:
                image_url = response.css('img[alt*="product"]::attr(src)').get()
            if image_url:
                item['product_image_url'] = image_url
            
            # Price information
            current_price = response.css('span[class*="price"]::text').get()
            if not current_price:
                current_price = response.css('div[class*="price"]::text').get()
            if current_price:
                item['current_price'] = current_price.strip()
            
            # Original price (strikethrough price)
            original_price = response.css('span[class*="strike"]::text').get()
            if not original_price:
                original_price = response.css('div[class*="strike"]::text').get()
            if original_price:
                item['original_price'] = original_price.strip()
            
            # Discount percentage
            discount = response.css('span[class*="discount"]::text').get()
            if not discount:
                discount = response.css('div[class*="discount"]::text').get()
            if discount:
                item['discount_percentage'] = discount.strip()
            
            # Currency
            item['currency'] = 'INR'
            
            # Brand
            brand = response.css('span[class*="brand"]::text').get()
            if brand:
                item['brand'] = brand.strip()
            
            # Category and subcategory
            breadcrumb = response.css('a[class*="breadcrumb"]::text').getall()
            if breadcrumb:
                item['category'] = breadcrumb[0].strip() if len(breadcrumb) > 0 else ''
                item['subcategory'] = breadcrumb[1].strip() if len(breadcrumb) > 1 else ''
            
            # Product description
            description = response.css('div[class*="description"]::text').get()
            if description:
                item['description'] = description.strip()
            
            # Product rating
            rating = response.css('span[class*="rating"]::text').get()
            if not rating:
                rating = response.css('div[class*="rating"]::text').get()
            if rating:
                rating_match = re.search(r'(\d+\.?\d*)', rating)
                if rating_match:
                    item['product_rating'] = float(rating_match.group(1))
            
            # Number of reviews
            reviews_count = response.css('span[class*="reviews"]::text').get()
            if reviews_count:
                reviews_match = re.search(r'([\d,]+)', reviews_count)
                if reviews_match:
                    item['product_reviews_count'] = reviews_match.group(1).replace(',', '')
            
            # Availability
            availability = response.css('div[class*="availability"]::text').get()
            if availability:
                item['availability'] = availability.strip()
            
            # Seller information
            seller = response.css('div[class*="seller"]::text').get()
            if seller:
                item['seller_name'] = seller.strip()
            
            # Shipping information
            shipping = response.css('div[class*="shipping"]::text').get()
            if shipping:
                item['shipping_info'] = shipping.strip()
            
            # Product features
            features = response.css('div[class*="feature"]::text').getall()
            if features:
                item['features'] = [f.strip() for f in features if f.strip()]
            
            # Technical details
            tech_details = response.css('div[class*="specification"] tr')
            if tech_details:
                specs = {}
                for row in tech_details:
                    key = row.css('td:first-child::text').get()
                    value = row.css('td:last-child::text').get()
                    if key and value:
                        specs[key.strip()] = value.strip()
                item['specifications'] = specs
            
            # Check if item has required fields
            if item.get('product_name') and item.get('current_price'):
                yield item
            else:
                self.logger.warning(f"Incomplete product data: {response.url}")
                
        except Exception as e:
            self.logger.error(f"Error parsing product {response.url}: {str(e)}")
            item['scraping_errors'] = str(e)
            yield item
    
    def closed(self, reason):
        self.logger.info(f"BigBasket spider closed: {reason}")
        self.logger.info(f"Total pages scraped: {self.current_page}")
