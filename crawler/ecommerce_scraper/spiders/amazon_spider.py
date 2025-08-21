# -*- coding: utf-8 -*-

import re
from datetime import datetime
from urllib.parse import urljoin

import scrapy

from ecommerce_scraper.items import EcommerceProductItem


class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['amazon.in', 'amazon.com']
    
    def __init__(self, category=None, search_query=None, max_pages=10, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.category = category
        self.search_query = search_query
        self.max_pages = int(max_pages)
        self.current_page = 1
        
        # Base URLs for different search types
        if self.search_query:
            self.start_urls = [
                f'https://www.amazon.in/s?k={self.search_query.replace(" ", "+")}'
            ]
        elif self.category:
            self.start_urls = [
                f'https://www.amazon.in/s?i={self.category}'
            ]
        else:
            # Default to electronics category
            self.start_urls = [
                'https://www.amazon.in/s?i=electronics'
            ]
    
    def parse(self, response):
        """Parse the search results page"""
        self.logger.info(f"Parsing page {self.current_page}: {response.url}")
        
        # Extract product links from search results - updated selectors
        product_links = response.css('a[href*="/dp/"]::attr(href)').getall()
        
        # Filter and clean product links
        product_links = [link for link in product_links if '/dp/' in link and 'ref=' in link]
        
        # Remove duplicates and limit
        unique_links = list(dict.fromkeys(product_links))[:20]
        
        self.logger.info(f"Found {len(unique_links)} product links on page {self.current_page}")
        
        # Follow product links
        for link in unique_links:
            full_url = urljoin(response.url, link)
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_product,
                meta={'dont_cache': True}
            )
        
        # Follow next page if available and within limit
        if self.current_page < self.max_pages:
            next_page = response.css('a.s-pagination-next::attr(href)').get()
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
            item['platform'] = 'Amazon'
            item['product_url'] = response.url
            item['scraped_at'] = datetime.now().isoformat()
            
            # Extract product ID from URL
            product_id_match = re.search(r'/dp/([A-Z0-9]{10})', response.url)
            if product_id_match:
                item['product_id'] = product_id_match.group(1)
            
            # Product name - multiple selector attempts
            product_name = response.css('#productTitle::text').get()
            if not product_name:
                product_name = response.css('h1.a-size-large::text').get()
            if not product_name:
                product_name = response.css('span.a-size-large::text').get()
            if product_name:
                item['product_name'] = product_name.strip()
            
            # Product image - multiple selector attempts
            image_url = response.css('#landingImage::attr(src)').get()
            if not image_url:
                image_url = response.css('img[data-old-hires]::attr(src)').get()
            if not image_url:
                image_url = response.css('img.a-dynamic-image::attr(src)').get()
            if image_url:
                item['product_image_url'] = image_url
            
            # Price information - multiple selector attempts
            current_price = response.css('.a-price-whole::text').get()
            if not current_price:
                current_price = response.css('.a-price .a-offscreen::text').get()
            if not current_price:
                current_price = response.css('[data-a-color="price"] .a-offscreen::text').get()
            if current_price:
                item['current_price'] = current_price.strip()
            
            # Original price (strikethrough price) - multiple selector attempts
            original_price = response.css('.a-price.a-text-price .a-offscreen::text').get()
            if not original_price:
                original_price = response.css('.a-text-strike::text').get()
            if not original_price:
                original_price = response.css('.a-price.a-text-price span::text').get()
            if original_price:
                item['original_price'] = original_price.strip()
            
            # Discount percentage - multiple selector attempts
            discount = response.css('.a-size-large.a-color-price::text').get()
            if not discount:
                discount = response.css('.a-color-price::text').get()
            if not discount:
                discount = response.css('[data-a-color="secondary"]::text').get()
            if discount:
                item['discount_percentage'] = discount.strip()
            
            # Currency
            item['currency'] = 'INR'
            
            # Brand
            brand = response.css('#bylineInfo::text').get()
            if brand:
                item['brand'] = brand.strip()
            
            # Category and subcategory
            breadcrumb = response.css('#wayfinding-breadcrumbs_feature_div .a-list-item::text').getall()
            if breadcrumb:
                item['category'] = breadcrumb[0].strip() if len(breadcrumb) > 0 else ''
                item['subcategory'] = breadcrumb[1].strip() if len(breadcrumb) > 1 else ''
            
            # Product description
            description = response.css('#productDescription p::text').get()
            if description:
                item['description'] = description.strip()
            
            # Product rating
            rating = response.css('.a-icon-alt::text').get()
            if rating:
                rating_match = re.search(r'(\d+\.?\d*)', rating)
                if rating_match:
                    item['product_rating'] = float(rating_match.group(1))
            
            # Number of reviews
            reviews_count = response.css('#acrCustomerReviewText::text').get()
            if reviews_count:
                reviews_match = re.search(r'([\d,]+)', reviews_count)
                if reviews_match:
                    item['product_reviews_count'] = reviews_match.group(1).replace(',', '')
            
            # Availability
            availability = response.css('#availability .a-color-success::text').get()
            if availability:
                item['availability'] = availability.strip()
            
            # Seller information
            seller = response.css('#merchant-info::text').get()
            if seller:
                item['seller_name'] = seller.strip()
            
            # Shipping information
            shipping = response.css('#deliveryBlockMessage::text').get()
            if shipping:
                item['shipping_info'] = shipping.strip()
            
            # Product features
            features = response.css('#feature-bullets .a-list-item::text').getall()
            if features:
                item['features'] = [f.strip() for f in features if f.strip()]
            
            # Technical details
            tech_details = response.css('#productDetails_techSpec_section_1 tr')
            if tech_details:
                specs = {}
                for row in tech_details:
                    key = row.css('th::text').get()
                    value = row.css('td::text').get()
                    if key and value:
                        specs[key.strip()] = value.strip()
                item['specifications'] = specs
            
            # Debug logging
            self.logger.info(f"Extracted data for {response.url}:")
            self.logger.info(f"  Name: {item.get('product_name', 'N/A')}")
            self.logger.info(f"  Price: {item.get('current_price', 'N/A')}")
            self.logger.info(f"  Brand: {item.get('brand', 'N/A')}")
            
            # Check if item has required fields
            if item.get('product_name') and item.get('current_price'):
                self.logger.info("✅ Valid product data extracted")
                yield item
            else:
                self.logger.warning(f"❌ Incomplete product data: {response.url}")
                # Still yield the item for debugging
                yield item
                
        except Exception as e:
            self.logger.error(f"Error parsing product {response.url}: {str(e)}")
            item['scraping_errors'] = str(e)
            yield item
    
    def closed(self, reason):
        self.logger.info(f"Amazon spider closed: {reason}")
        self.logger.info(f"Total pages scraped: {self.current_page}")
