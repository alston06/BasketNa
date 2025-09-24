# 🎯 Personalized Product Recommendations with Website Links

## Overview

I've successfully implemented a comprehensive **personalized product recommendation system** for BasketNA that generates 5-10 tailored product suggestions based on user activity and includes direct website links for immediate shopping.

## ✨ Key Features Implemented

### 🔍 Smart Recommendation Algorithm
- **User Activity Analysis**: Tracks product views, searches, and wishlist/tracked items
- **Category Preference Learning**: Identifies user preferences based on interaction patterns
- **Similar Product Suggestions**: Recommends products similar to viewed/tracked items
- **Trending Product Detection**: Highlights products with active price movements
- **Rating-Based Filtering**: Prioritizes highly-rated products (4.0+ stars)
- **Price Trend Consideration**: Factors in price trends (decreasing prices preferred)

### 🌐 Website Integration
- **Direct Retailer Links**: Each recommendation includes a direct link to the best-price retailer
- **Multi-Retailer Support**: Links to all available retailers for price comparison
- **Supported Retailers**:
  - Amazon.in
  - Flipkart
  - Reliance Digital
  - Croma
- **Smart URL Generation**: Automatically creates search URLs with proper product names

### 📊 Recommendation Types

#### 1. **Personalized Recommendations** (`/recommendations/personalized`)
- For authenticated users based on their activity history
- Considers viewed products, tracked items, and category preferences
- Personalization score indicates recommendation quality

#### 2. **Session-Based Recommendations** (`/recommendations/session`)
- For anonymous users based on session activity
- Uses session ID to track temporary browsing patterns

#### 3. **Category Recommendations** (`/recommendations/category/{category}`)
- Category-specific suggestions (Smartphones, Laptops, Audio, Wearables, etc.)
- Filtered by ratings and trending scores

#### 4. **Trending Recommendations** (`/recommendations/trending`)
- Products with active price movements and market interest
- Based on price volatility and market dynamics

## 📋 Recommendation Output Format

Each recommendation includes:

```json
{
  "product_id": "P001",
  "product_name": "iPhone 16",
  "category": "Smartphones",
  "current_price": 89999.99,
  "best_retailer": "Amazon.in",
  "description": "Latest Apple smartphone with advanced camera system and A18 chip",
  "score": 0.847,
  "reasons": [
    "You've shown interest in Smartphones products",
    "Similar to products you're tracking",
    "Highly rated product (4.5/5.0)"
  ],
  "rating": 4.5,
  "trending_score": 0.732,
  "price_trend": "decreasing",
  "potential_savings": 5000.0,
  "website_url": "https://www.amazon.in/s?k=iPhone+16",
  "all_retailer_links": {
    "Amazon.in": "https://www.amazon.in/s?k=iPhone+16",
    "Flipkart": "https://www.flipkart.com/search?q=iPhone+16",
    "RelianceDigital": "https://www.reliancedigital.in/search?q=iPhone+16",
    "Croma": "https://www.croma.com/search/?text=iPhone+16"
  }
}
```

## 🔧 API Endpoints

### Authentication Required
- `GET /recommendations/personalized?limit=10` - Personalized recommendations for logged-in users

### No Authentication Required
- `GET /recommendations/session?session_id={id}&limit=10` - Session-based recommendations
- `GET /recommendations/category/{category}?limit=5` - Category-specific recommendations
- `GET /recommendations/trending?limit=10` - Trending product recommendations
- `POST /activity/view/{product_id}?session_id={id}` - Record product views for personalization

## 🏗️ Architecture

### Core Components

1. **PersonalizedRecommendationEngine** (`personalized_recommendations.py`)
   - Main recommendation logic
   - User activity pattern analysis
   - Scoring algorithms
   - Website link generation

2. **Database Models** (`models.py`)
   - User activity tracking (ProductView)
   - Product tracking (TrackedItem)
   - User management (User)

3. **API Integration** (`main.py`)
   - FastAPI endpoints
   - Response formatting
   - Authentication handling

4. **Data Schemas** (`schemas.py`)
   - Response models
   - Data validation

### Algorithm Components

#### Scoring System
- **Base Score**: 0.1 (baseline)
- **Category Preference**: +0.4 max (based on user activity)
- **Rating Boost**: +0.4 max (rating-3.0)/5.0
- **Trending Boost**: +0.2 max (volatility-based)
- **Price Trend Boost**: +0.15 (decreasing), +0.05 (stable)
- **Activity Multiplier**: 0.5-1.0 (based on user engagement)

#### Personalization Features
- **Category Learning**: Tracks which product categories users view most
- **Similar Product Detection**: Groups products by category for cross-selling
- **Exclusion Logic**: Avoids recommending heavily-viewed or purchased items
- **Cold Start Handling**: Falls back to trending and highly-rated products

## 📱 Product Categories

Supported categories with intelligent grouping:
- **Smartphones**: iPhone, Samsung Galaxy, Google Pixel, OnePlus
- **Laptops**: MacBook, Dell XPS, HP Spectre, Lenovo Legion
- **Audio**: AirPods, Bose, JBL, Sony Headphones
- **Wearables**: Apple Watch, Samsung Galaxy Watch, Fitbit, Garmin
- **Gaming**: PlayStation, Gaming Laptops
- **TVs**: Samsung QLED, LG OLED

## 🧪 Testing

### Demo Scripts
- `personalized_recommendations.py` - Run standalone demo
- `test_website_links.py` - Test API endpoints and website links
- `test_personalized_recommendations.py` - Complete test suite

### Sample Output
```
1. 📱 Apple MacBook Air (M4)
   🏷️  Category: Laptops
   💰 Price: ₹98,961 at RelianceDigital
   ⭐ Rating: 4.8/5.0
   📈 Trending Score: 0.90
   📊 Price Trend: stable
   💡 Potential Savings: ₹24,846
   📝 Ultra-thin laptop with exceptional battery life and performance
   🎯 Reasons: Highly rated product, Popular in category
   🔗 Best Price Link: https://www.reliancedigital.in/search?q=Apple+MacBook+Air+%28M4%29
   🛒 Available at 4 retailers
```

## 🚀 Usage Examples

### For Frontend Integration
```javascript
// Get personalized recommendations
const recommendations = await fetch('/recommendations/personalized?limit=5')
  .then(res => res.json());

// Display with website links
recommendations.recommendations.forEach(rec => {
  console.log(`${rec.product_name} - ${rec.website_url}`);
});
```

### For Mobile App
```javascript
// Session-based for anonymous users
const sessionRecs = await fetch(`/recommendations/session?session_id=${sessionId}&limit=8`)
  .then(res => res.json());

// Direct retailer navigation
window.open(recommendation.website_url, '_blank');
```

## 🎯 Business Value

### User Experience
- **Instant Shopping**: Direct links eliminate search friction
- **Price Comparison**: Multiple retailer options in one place
- **Personalization**: Relevant suggestions based on actual behavior
- **Discovery**: Trending and similar product recommendations

### Business Benefits
- **Increased Conversion**: Direct purchase links reduce abandonment
- **User Engagement**: Personalized experience encourages return visits
- **Revenue**: Potential affiliate commissions from retailer partnerships
- **Data Insights**: Rich user behavior analytics for business intelligence

## 📈 Future Enhancements

### Planned Features
- **Purchase History Integration**: Exclude bought items, suggest complementary products
- **Advanced ML Models**: Deep learning for better similarity detection
- **Real-time Price Updates**: Live price tracking and alerts
- **Social Recommendations**: Friend activity and shared wishlists
- **Geographic Personalization**: Location-based store preferences
- **Seasonal Adjustments**: Holiday and event-based recommendations

### Technical Improvements
- **Caching Layer**: Redis for faster recommendation retrieval
- **A/B Testing**: Recommendation algorithm optimization
- **Real-time Analytics**: User interaction tracking and analytics
- **Mobile Optimization**: App-specific recommendation formats

---

## 🏁 Summary

The implemented system successfully delivers personalized product recommendations with integrated website links, providing users with immediate shopping access while leveraging advanced algorithms for relevance and personalization. The system handles both authenticated and anonymous users, supports multiple recommendation types, and includes comprehensive testing and documentation.

**Key Achievement**: Every recommendation now includes direct website links to retailers, enabling seamless transition from discovery to purchase! 🛍️✨