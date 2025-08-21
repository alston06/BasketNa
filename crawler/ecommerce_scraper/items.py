# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class EcommerceProductItem(scrapy.Item):
    # Basic product information
    product_id = Field()
    product_name = Field()
    product_url = Field()
    product_image_url = Field()
    
    # Price information
    current_price = Field()
    original_price = Field()
    discount_percentage = Field()
    currency = Field()
    
    # Product details
    brand = Field()
    category = Field()
    subcategory = Field()
    description = Field()
    
    # E-commerce platform specific
    platform = Field()
    seller_name = Field()
    seller_rating = Field()
    seller_reviews_count = Field()
    
    # Product ratings and reviews
    product_rating = Field()
    product_reviews_count = Field()
    
    # Availability and shipping
    availability = Field()
    shipping_info = Field()
    delivery_estimate = Field()
    
    # Technical details
    sku = Field()
    model_number = Field()
    weight = Field()
    dimensions = Field()
    
    # Timestamps
    scraped_at = Field()
    last_updated = Field()
    
    # Additional metadata
    tags = Field()
    features = Field()
    specifications = Field()
    
    # Error handling
    scraping_errors = Field()
    is_complete = Field()


class ProductPriceHistoryItem(scrapy.Item):
    """Item for tracking price history over time"""
    product_id = Field()
    platform = Field()
    price = Field()
    currency = Field()
    timestamp = Field()
    price_type = Field()  # current, original, discounted


class ProductReviewItem(scrapy.Item):
    """Item for individual product reviews"""
    product_id = Field()
    platform = Field()
    reviewer_name = Field()
    rating = Field()
    review_title = Field()
    review_text = Field()
    review_date = Field()
    helpful_votes = Field()
    verified_purchase = Field()
