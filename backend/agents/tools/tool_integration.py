"""
Integration module for enhanced AI agent tools.
Provides direct access to tools for FastAPI endpoints.
"""

import asyncio
from typing import Any, Dict

from .find_coupons import find_coupons
from .summarize_reviews import summarize_reviews


class ToolsIntegration:
    """Integration class for accessing AI agent tools directly from FastAPI endpoints"""
    
    @staticmethod
    async def get_product_coupons(product_name: str) -> Dict[str, Any]:
        """Get available coupons for a product"""
        return await find_coupons(product_name)
    
    @staticmethod
    async def get_product_reviews_summary(product_name: str, site: str = "all") -> Dict[str, Any]:
        """Get summarized reviews for a product"""
        return await summarize_reviews(product_name, site)
    
    @staticmethod
    async def get_comprehensive_product_info(product_name: str) -> Dict[str, Any]:
        """Get comprehensive product information including coupons and reviews"""
        # Run both tools concurrently for better performance
        coupons_task = find_coupons(product_name)
        reviews_task = summarize_reviews(product_name, "all")
        
        coupons_data, reviews_data = await asyncio.gather(coupons_task, reviews_task)
        
        return {
            "product_name": product_name,
            "coupons": coupons_data,
            "reviews": reviews_data,
            "analysis_complete": True
        }


# Create singleton instance
tools_integration = ToolsIntegration()