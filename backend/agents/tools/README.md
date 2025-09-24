# AI Agent Tools - Enhanced Integration

This directory contains enhanced AI agent tools that have been modified for full compatibility with Pydantic AI agents and integrated into the BasketNa FastAPI backend.

## Enhanced Tools

### 1. find_coupons.py
**Enhanced Coupon Discovery Tool**

- **Function**: `find_coupons(product_name: str) -> Dict[str, Any]`
- **Features**:
  - Comprehensive coupon search with multiple offer types
  - Percentage discounts, cashback offers, shipping deals, and bundle offers
  - Realistic coupon validation with expiry dates and minimum order values
  - Site compatibility information
  - Potential savings calculation
  - Best coupon recommendation

**Example Response**:
```json
{
  "product_name": "iPhone 16",
  "total_coupons_found": 3,
  "coupons": [
    {
      "code": "BASKET10",
      "discount": "10%",
      "description": "10% off on iPhone 16",
      "type": "percentage_discount",
      "min_order_value": 999,
      "expires_in_days": 15,
      "terms": "Valid on orders above ₹999. Expires in 15 days.",
      "site_compatibility": ["Amazon", "Flipkart"]
    }
  ],
  "max_potential_savings": 150.0,
  "best_coupon_recommendation": {...}
}
```

### 2. summarize_reviews.py
**Enhanced Review Analysis Tool**

- **Function**: `summarize_reviews(product_name: str, site: str = "all") -> Dict[str, Any]`
- **Features**:
  - Real web scraping from Amazon and Flipkart
  - AI-powered sentiment analysis using transformers
  - Structured review data with confidence scores
  - Key positive and negative word extraction
  - Detailed sentiment breakdown (positive/negative/neutral percentages)
  - Sample reviews with sentiment classification
  - Fallback to realistic mock data if scraping fails

**Example Response**:
```json
{
  "product_name": "iPhone 16",
  "sites_analyzed": ["Amazon", "Flipkart"],
  "total_reviews_analyzed": 50,
  "average_rating": 4.2,
  "sentiment_breakdown": {
    "positive": 75.0,
    "negative": 15.0,
    "neutral": 10.0
  },
  "key_positives": ["excellent", "quality", "performance"],
  "key_negatives": ["expensive", "battery"],
  "insights": ["Highly positive customer feedback", "High customer satisfaction"],
  "sample_reviews": [...]
}
```

### 3. tool_integration.py
**FastAPI Integration Module**

- **Class**: `ToolsIntegration`
- **Features**:
  - Direct access to tools from FastAPI endpoints  
  - Concurrent execution for better performance
  - Comprehensive product analysis combining multiple tools
  - Error handling and graceful degradation

## API Endpoints

The enhanced tools are accessible through new FastAPI endpoints:

### GET `/ai-tools/coupons/{product_name}`
Get available coupons and deals for a specific product.

**Response**:
```json
{
  "status": "success",
  "coupon_data": { ... }
}
```

### GET `/ai-tools/reviews/{product_name}?site=all`
Get AI-powered review summary and sentiment analysis.

**Parameters**:
- `site`: "all", "amazon", or "flipkart"

**Response**:
```json
{
  "status": "success", 
  "review_analysis": { ... }
}
```

### GET `/ai-tools/comprehensive/{product_name}`
Get comprehensive product analysis including coupons and reviews.

**Response**:
```json
{
  "status": "success",
  "comprehensive_analysis": {
    "product_name": "iPhone 16",
    "coupons": { ... },
    "reviews": { ... },
    "analysis_complete": true
  }
}
```

### GET `/ai-tools/health`
Check the health and availability of AI agent tools.

**Response**:
```json
{
  "status": "healthy",
  "tools_available": true,
  "available_endpoints": [...],
  "message": "AI agent tools are ready for use"
}
```

## Pydantic AI Agent Integration

The tools are integrated into the Pydantic AI agent (`price_copilot.py`) with proper async support:

```python
from .tools.find_coupons import find_coupons
from .tools.summarize_reviews import summarize_reviews

tools=[
    Tool(find_coupons, takes_ctx=False),      # Enhanced coupon discovery
    Tool(summarize_reviews, takes_ctx=False), # Enhanced review analysis
    # ... other tools
]
```

## Dependencies

The enhanced tools require these additional packages (already in pyproject.toml):
- `requests` - for web scraping
- `beautifulsoup4` - for HTML parsing
- `transformers` - for sentiment analysis
- `torch` - for ML models

## Testing

Run the test suite to verify tool functionality:

```bash
cd backend
python test_ai_tools.py
```

## Features Summary

✅ **Async/Await Support** - Fully compatible with Pydantic AI's async architecture
✅ **Real Web Scraping** - Actual data from Amazon and Flipkart with fallback
✅ **AI Sentiment Analysis** - Using transformer models for accurate sentiment detection
✅ **Structured Data** - Rich, structured responses instead of simple strings
✅ **Error Handling** - Graceful degradation with realistic mock data
✅ **FastAPI Integration** - Direct access via REST endpoints
✅ **Performance Optimized** - Concurrent execution and lazy loading
✅ **Production Ready** - Proper logging, timeouts, and error management

## Usage in Pydantic AI Agent

When using the BasketNa price comparison agent, users can now access:

1. **Enhanced Coupon Discovery**: "Find me the best coupons for iPhone 16"
2. **Intelligent Review Analysis**: "What do customers say about the Dell XPS 15?"
3. **Comprehensive Product Intelligence**: Automatic analysis combining price data, coupons, and reviews

The tools provide rich, actionable insights that help users make informed purchasing decisions with confidence.