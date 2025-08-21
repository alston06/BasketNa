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
        
        # Extract product links from search results - updated selectors for BigBasket
        product_links = response.css('a[href*="/pd/"]::attr(href)').getall()
        
        # Filter and clean product links
        product_links = [link for link in product_links if '/pd/' in link and 'nc=' in link]
        
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
            
            # Debug: Log available price-related elements
            price_elements = response.css('*[class*="price"]::text').getall()
            amount_elements = response.css('*[class*="amount"]::text').getall()
            rs_elements = response.css('*[class*="rs"]::text').getall()
            
            # Look for any text containing price patterns
            all_text = response.css('::text').getall()
            price_patterns = [text for text in all_text if '₹' in text or 'Rs' in text or 'rs' in text]
            
            # Extract price from JavaScript data embedded in the page
            js_price = self.extract_price_from_js(response.text)
            
            self.logger.info(f"Price elements found: {price_elements[:5]}")
            self.logger.info(f"Amount elements found: {amount_elements[:5]}")
            self.logger.info(f"RS elements found: {rs_elements[:5]}")
            self.logger.info(f"Price patterns found: {price_patterns[:10]}")
            self.logger.info(f"JS extracted price: {js_price}")
            
            # Basic product information
            item['platform'] = 'BigBasket'
            item['product_url'] = response.url
            item['scraped_at'] = datetime.now().isoformat()
            
            # Extract product ID from URL
            product_id_match = re.search(r'/pd/([A-Z0-9-]+)', response.url)
            if product_id_match:
                item['product_id'] = product_id_match.group(1)
            
            # Product name - multiple selector attempts for BigBasket
            product_name = response.css('h1[class*="product-name"]::text').get()
            if not product_name:
                product_name = response.css('h1::text').get()
            if not product_name:
                product_name = response.css('.product-name::text').get()
            if not product_name:
                product_name = response.css('[data-testid="product-name"]::text').get()
            if product_name:
                item['product_name'] = product_name.strip()
            
            # Product image - multiple selector attempts for BigBasket
            image_url = response.css('img[class*="product-image"]::attr(src)').get()
            if not image_url:
                image_url = response.css('img[alt*="product"]::attr(src)').get()
            if not image_url:
                image_url = response.css('.product-image img::attr(src)').get()
            if not image_url:
                image_url = response.css('[data-testid="product-image"] img::attr(src)').get()
            if image_url:
                item['product_image_url'] = image_url
            
            # Price information - try JavaScript extraction first, then CSS selectors
            current_price = js_price  # Use the JavaScript-extracted price
            
            # Fallback to CSS selectors if JavaScript extraction failed
            if not current_price:
                current_price = response.css('.price::text').get()
            if not current_price:
                current_price = response.css('[data-testid="price"]::text').get()
            if not current_price:
                current_price = response.css('.product-price::text').get()
            if not current_price:
                current_price = response.css('.price-value::text').get()
            if not current_price:
                current_price = response.css('.amount::text').get()
            if not current_price:
                current_price = response.css('.rs::text').get()
            if not current_price:
                current_price = response.css('.product-price .amount::text').get()
            if not current_price:
                current_price = response.css('.price-section .amount::text').get()
            if not current_price:
                current_price = response.css('.price-info .amount::text').get()
            if not current_price:
                current_price = response.css('.price-details .amount::text').get()
            if not current_price:
                current_price = response.css('.product-details .price::text').get()
            if not current_price:
                current_price = response.css('.product-info .price::text').get()
            if not current_price:
                current_price = response.css('.product-summary .price::text').get()
            
            if current_price:
                item['current_price'] = current_price.strip()
            
            # Original price (strikethrough price) - try JavaScript extraction first
            original_price = self.extract_original_price_from_js(response.text)
            
            # Fallback to CSS selectors
            if not original_price:
                original_price = response.css('.original-price::text').get()
            if not original_price:
                original_price = response.css('.strike-price::text').get()
            if not original_price:
                original_price = response.css('.mrp::text').get()
            if not original_price:
                original_price = response.css('[data-testid="original-price"]::text').get()
            
            if original_price:
                item['original_price'] = original_price.strip()
            
            # Discount percentage - try JavaScript extraction first
            discount = self.extract_discount_from_js(response.text)
            
            # Fallback to CSS selectors
            if not discount:
                discount = response.css('.discount::text').get()
            if not discount:
                discount = response.css('.discount-percentage::text').get()
            if not discount:
                discount = response.css('[data-testid="discount"]::text').get()
            if not discount:
                discount = response.css('.offer::text').get()
            
            if discount:
                item['discount_percentage'] = discount.strip()
            
            # Currency
            item['currency'] = 'INR'
            
            # Brand - multiple selector attempts for BigBasket
            brand = response.css('.brand::text').get()
            if not brand:
                brand = response.css('[data-testid="brand"]::text').get()
            if not brand:
                brand = response.css('.product-brand::text').get()
            if brand:
                item['brand'] = brand.strip()
            
            # Category and subcategory - multiple selector attempts for BigBasket
            breadcrumb = response.css('.breadcrumb a::text').getall()
            if not breadcrumb:
                breadcrumb = response.css('[data-testid="breadcrumb"] a::text').getall()
            if not breadcrumb:
                breadcrumb = response.css('.category-path a::text').getall()
            if breadcrumb:
                item['category'] = breadcrumb[0].strip() if len(breadcrumb) > 0 else ''
                item['subcategory'] = breadcrumb[1].strip() if len(breadcrumb) > 1 else ''
            
            # Product description - multiple selector attempts for BigBasket
            description = response.css('.description::text').get()
            if not description:
                description = response.css('.product-description::text').get()
            if not description:
                description = response.css('[data-testid="description"]::text').get()
            if description:
                item['description'] = description.strip()
            
            # Product rating - multiple selector attempts for BigBasket
            rating = response.css('.rating::text').get()
            if not rating:
                rating = response.css('.product-rating::text').get()
            if not rating:
                rating = response.css('[data-testid="rating"]::text').get()
            if not rating:
                rating = response.css('.stars::text').get()
            if rating:
                rating_match = re.search(r'(\d+\.?\d*)', rating)
                if rating_match:
                    item['product_rating'] = float(rating_match.group(1))
            
            # Number of reviews - multiple selector attempts for BigBasket
            reviews_count = response.css('.reviews::text').get()
            if not reviews_count:
                reviews_count = response.css('.review-count::text').get()
            if not reviews_count:
                reviews_count = response.css('[data-testid="reviews"]::text').get()
            if reviews_count:
                reviews_match = re.search(r'([\d,]+)', reviews_count)
                if reviews_match:
                    item['product_reviews_count'] = reviews_match.group(1).replace(',', '')
            
            # Availability - multiple selector attempts for BigBasket
            availability = response.css('.availability::text').get()
            if not availability:
                availability = response.css('.stock-status::text').get()
            if not availability:
                availability = response.css('[data-testid="availability"]::text').get()
            if availability:
                item['availability'] = availability.strip()
            
            # Seller information - multiple selector attempts for BigBasket
            seller = response.css('.seller::text').get()
            if not seller:
                seller = response.css('.vendor::text').get()
            if not seller:
                seller = response.css('[data-testid="seller"]::text').get()
            if seller:
                item['seller_name'] = seller.strip()
            
            # Shipping information - multiple selector attempts for BigBasket
            shipping = response.css('.shipping::text').get()
            if not shipping:
                shipping = response.css('.delivery::text').get()
            if not shipping:
                shipping = response.css('[data-testid="shipping"]::text').get()
            if shipping:
                item['shipping_info'] = shipping.strip()
            
            # Product features - multiple selector attempts for BigBasket
            features = response.css('.features li::text').getall()
            if not features:
                features = response.css('.product-features li::text').getall()
            if not features:
                features = response.css('[data-testid="features"] li::text').getall()
            if features:
                item['features'] = [f.strip() for f in features if f.strip()]
            
            # Technical details - multiple selector attempts for BigBasket
            tech_details = response.css('.specifications tr').getall()
            if not tech_details:
                tech_details = response.css('.product-specs tr').getall()
            if not tech_details:
                tech_details = response.css('[data-testid="specifications"] tr').getall()
            if tech_details:
                specs = {}
                for row in tech_details:
                    key = row.css('td:first-child::text').get()
                    value = row.css('td:last-child::text').get()
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
        self.logger.info(f"BigBasket spider closed: {reason}")
        self.logger.info(f"Total pages scraped: {self.current_page}")
    
    def extract_price_from_js(self, html_content):
        """Extract price information from JavaScript data embedded in the page"""
        try:
            # Look for pricing data in JavaScript
            import re
            
            # Pattern 1: Look for "offer_sp" in JavaScript data
            offer_sp_match = re.search(r'"offer_sp":"([^"]+)"', html_content)
            if offer_sp_match:
                return offer_sp_match.group(1)
            
            # Pattern 2: Look for "sp" in pricing section
            sp_match = re.search(r'"sp":"([^"]+)"', html_content)
            if sp_match:
                return sp_match.group(1)
            
            # Pattern 3: Look for price in the format "₹XX" or "₹XX.X"
            price_match = re.search(r'₹(\d+(?:\.\d+)?)', html_content)
            if price_match:
                return price_match.group(1)
            
            # Pattern 4: Look for "Rs XX" or "Rs XX.X"
            rs_match = re.search(r'Rs\s*(\d+(?:\.\d+)?)', html_content)
            if rs_match:
                return rs_match.group(1)
            
            # Pattern 5: Look for pricing in the product details
            pricing_match = re.search(r'"pricing":\s*{[^}]*"offer_sp":\s*"([^"]+)"', html_content)
            if pricing_match:
                return pricing_match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting price from JS: {e}")
            return None
    
    def extract_original_price_from_js(self, html_content):
        """Extract original price (MRP) from JavaScript data"""
        try:
            import re
            
            # Look for MRP in JavaScript data
            mrp_match = re.search(r'"mrp":"([^"]+)"', html_content)
            if mrp_match:
                return mrp_match.group(1)
            
            # Look for base_price in pricing section
            base_price_match = re.search(r'"base_price":"([^"]+)"', html_content)
            if base_price_match:
                return base_price_match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting original price from JS: {e}")
            return None
    
    def extract_discount_from_js(self, html_content):
        """Extract discount percentage from JavaScript data"""
        try:
            import re
            
            # Look for discount percentage in JavaScript data
            discount_match = re.search(r'"d_text":"([^"]+)"', html_content)
            if discount_match:
                discount_text = discount_match.group(1)
                # Extract percentage from text like "47% OFF"
                percent_match = re.search(r'(\d+)%', discount_text)
                if percent_match:
                    return percent_match.group(1)
                return discount_text
            
            # Look for savings percentage
            savings_match = re.search(r'"offer_sp_savings_percent":([^,]+)', html_content)
            if savings_match:
                return savings_match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting discount from JS: {e}")
            return None
