"""
Personalized Product Recommendation Engine
Generates user-specific product recommendations based on activity patterns, preferences, and market trends
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import Counter, defaultdict
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
import models
import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProductRecommendation:
    """Individual product recommendation with details"""
    product_id: str
    product_name: str
    category: str
    current_price: float
    best_retailer: str
    description: str
    score: float
    reasons: List[str]
    rating: float
    trending_score: float
    price_trend: str  # "stable", "decreasing", "increasing"
    potential_savings: float
    website_url: str  # Direct link to product search on retailer website
    all_retailer_links: Dict[str, str]  # Links to all available retailers

@dataclass
class RecommendationSet:
    """Complete set of personalized recommendations"""
    user_id: Optional[int]
    session_id: Optional[str]
    recommendations: List[ProductRecommendation]
    generated_at: datetime
    total_count: int
    personalization_score: float

class PersonalizedRecommendationEngine:
    """Advanced personalized recommendation system"""
    
    def __init__(self):
        self.backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.backend_dir, "data")
        self.historical_data_path = os.path.join(self.data_dir, "ecommerce_price_dataset_corrected.csv")
        
        # Product categories mapping
        self.product_categories = {
            "Apple AirPods Pro 3": "Audio",
            "Apple MacBook Air (M4)": "Laptops", 
            "Apple Watch Series 11": "Wearables",
            "Bose QuietComfort Ultra Earbuds": "Audio",
            "Dell XPS 15": "Laptops",
            "Fitbit Charge 7": "Wearables",
            "Garmin Forerunner 965": "Wearables",
            "Google Pixel 10 Pro": "Smartphones",
            "HP Spectre x360": "Laptops",
            "JBL Flip 7 Speaker": "Audio",
            "Samsung Galaxy Watch 7": "Wearables",
            "Samsung 55-inch QLED TV": "TVs",
            "LG C5 65-inch OLED TV": "TVs",
            "Sony PlayStation 5 Pro": "Gaming",
            "Canon EOS R7 Camera": "Photography",
            "DJI Mini 5 Pro Drone": "Drones",
            "Logitech MX Master 4 Mouse": "Accessories",
            "iPhone 16": "Smartphones",
            "Samsung Galaxy S26 Ultra": "Smartphones",
            "OnePlus 14": "Smartphones",
            "Lenovo Legion 5 Pro": "Gaming Laptops",
            "Sony WH-1000XM6 Headphones": "Audio"
        }
        
        # Product similarity groups for cross-selling
        self.similarity_groups = {
            "Smartphones": ["Google Pixel 10 Pro", "iPhone 16", "Samsung Galaxy S26 Ultra", "OnePlus 14"],
            "Laptops": ["Apple MacBook Air (M4)", "Dell XPS 15", "HP Spectre x360"],
            "Audio": ["Apple AirPods Pro 3", "Bose QuietComfort Ultra Earbuds", "JBL Flip 7 Speaker", "Sony WH-1000XM6 Headphones"],
            "Wearables": ["Apple Watch Series 11", "Fitbit Charge 7", "Garmin Forerunner 965", "Samsung Galaxy Watch 7"],
            "Gaming": ["Sony PlayStation 5 Pro", "Lenovo Legion 5 Pro"],
            "TVs": ["Samsung 55-inch QLED TV", "LG C5 65-inch OLED TV"]
        }
        
        # Mock ratings for products (in real system, this would come from user reviews)
        self.product_ratings = {
            "Apple AirPods Pro 3": 4.6,
            "Apple MacBook Air (M4)": 4.8,
            "Apple Watch Series 11": 4.5,
            "Bose QuietComfort Ultra Earbuds": 4.7,
            "Dell XPS 15": 4.4,
            "Fitbit Charge 7": 4.2,
            "Garmin Forerunner 965": 4.6,
            "Google Pixel 10 Pro": 4.3,
            "HP Spectre x360": 4.1,
            "JBL Flip 7 Speaker": 4.4,
            "Samsung Galaxy Watch 7": 4.3,
            "Samsung 55-inch QLED TV": 4.5,
            "LG C5 65-inch OLED TV": 4.7,
            "Sony PlayStation 5 Pro": 4.8,
            "Canon EOS R7 Camera": 4.6,
            "DJI Mini 5 Pro Drone": 4.5,
            "Logitech MX Master 4 Mouse": 4.3,
            "iPhone 16": 4.5,
            "Samsung Galaxy S26 Ultra": 4.4,
            "OnePlus 14": 4.2,
            "Lenovo Legion 5 Pro": 4.6,
            "Sony WH-1000XM6 Headphones": 4.8
        }
    
    def build_retailer_url(self, retailer: str, product_name: str) -> str:
        """Build search URL for a specific retailer and product"""
        from urllib.parse import quote_plus
        
        retailer_lower = retailer.lower()
        q = quote_plus(product_name)
        
        if "amazon" in retailer_lower:
            return f"https://www.amazon.in/s?k={q}"
        elif "flipkart" in retailer_lower:
            return f"https://www.flipkart.com/search?q={q}"
        elif "reliance" in retailer_lower:
            return f"https://www.reliancedigital.in/search?q={q}"
        elif "croma" in retailer_lower:
            return f"https://www.croma.com/search/?text={q}"
        else:
            return f"https://www.google.com/search?q={quote_plus(retailer + ' ' + product_name)}"
    
    def get_all_retailer_links(self, df: pd.DataFrame, product_name: str) -> Dict[str, str]:
        """Get website links for all retailers selling this product"""
        retailer_links = {}
        
        # Get all retailers for this product
        product_data = df[df['product_name'] == product_name]
        if not product_data.empty:
            retailers = product_data['retailer'].unique()
            
            for retailer in retailers:
                retailer_links[retailer] = self.build_retailer_url(retailer, product_name)
        
        return retailer_links
    
    def load_price_data(self) -> pd.DataFrame:
        """Load and preprocess price data"""
        try:
            df = pd.read_csv(self.historical_data_path)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except FileNotFoundError:
            raise FileNotFoundError("Price dataset not found. Please ensure ecommerce_price_dataset_corrected.csv exists.")
    
    def get_user_activity_patterns(self, db: Session, user_id: Optional[int] = None, 
                                 session_id: Optional[str] = None) -> Dict:
        """Analyze user activity patterns from database"""
        patterns = {
            'viewed_products': [],
            'tracked_products': [],
            'category_preferences': {},
            'viewing_frequency': {},
            'recent_activity': [],
            'activity_score': 0.0
        }
        
        if not user_id and not session_id:
            return patterns
        
        try:
            # Get viewed products
            viewed = crud.top_viewed_products_for_identity(db, user_id, session_id, limit=50)
            patterns['viewed_products'] = [{'product_id': v[0], 'views': v[1]} for v in viewed]
            
            # Get tracked products (only for authenticated users)
            if user_id:
                tracked = crud.list_tracked_items(db, user_id)
                patterns['tracked_products'] = [t.product_id for t in tracked]
            
            # Calculate category preferences from views
            df = self.load_price_data()
            for view in patterns['viewed_products']:
                try:
                    product_name = self._get_product_name(view['product_id'])
                    if product_name and product_name in self.product_categories:
                        category = self.product_categories[product_name]
                        patterns['category_preferences'][category] = patterns['category_preferences'].get(category, 0) + view['views']
                except Exception as e:
                    logger.warning(f"Could not process view for product {view['product_id']}: {e}")
                    continue
            
            # Enhanced activity score calculation
            total_views = sum(v['views'] for v in patterns['viewed_products'])
            unique_products_viewed = len(patterns['viewed_products'])
            tracking_engagement = len(patterns['tracked_products']) * 2  # Tracking shows higher engagement
            
            # Multi-factor activity score
            raw_activity = total_views + tracking_engagement + (unique_products_viewed * 0.5)
            patterns['activity_score'] = min(1.0, raw_activity / 30.0)  # Normalize to 0-1 with higher threshold
            
            logger.info(f"User activity patterns loaded: {len(patterns['viewed_products'])} viewed, {len(patterns['tracked_products'])} tracked")
            
        except Exception as e:
            logger.error(f"Error loading user activity: {e}")
        
        return patterns
    
    def _get_product_name(self, product_id: str) -> str:
        """Map product ID to product name (reverse of main.py mapping)"""
        id_to_name = {
            "P001": "iPhone 16",
            "P002": "Samsung Galaxy S26 Ultra",
            "P003": "Google Pixel 10 Pro", 
            "P004": "OnePlus 14",
            "P005": "Dell XPS 15",
            "P006": "Apple MacBook Air (M4)",
            "P007": "HP Spectre x360",
            "P008": "Lenovo Legion 5 Pro",
            "P009": "Sony WH-1000XM6 Headphones",
            "P010": "Apple AirPods Pro 3",
            "P011": "Bose QuietComfort Ultra Earbuds",
            "P012": "JBL Flip 7 Speaker",
            "P013": "Apple Watch Series 11",
            "P014": "Samsung Galaxy Watch 7",
            "P015": "Samsung 55-inch QLED TV",
            "P016": "LG C5 65-inch OLED TV",
            "P017": "Sony PlayStation 5 Pro",
            "P018": "Canon EOS R7 Camera",
            "P019": "DJI Mini 5 Pro Drone",
            "P020": "Logitech MX Master 4 Mouse"
        }
        return id_to_name.get(product_id, "Unknown Product")
    
    def calculate_trending_score(self, df: pd.DataFrame, product_name: str) -> float:
        """Calculate trending score based on price volatility and market activity"""
        product_data = df[df['product_name'] == product_name]
        if product_data.empty:
            return 0.0
        
        # Calculate price volatility as trending indicator
        recent_data = product_data[product_data['date'] >= (datetime.now() - timedelta(days=14))]
        if len(recent_data) < 5:
            return 0.0
        
        price_std = recent_data['price_inr'].std()
        price_mean = recent_data['price_inr'].mean()
        volatility = price_std / price_mean if price_mean > 0 else 0
        
        # Higher volatility = more trending (people are actively comparing prices)
        trending_score = min(1.0, volatility * 10)  # Normalize to 0-1
        
        return trending_score
    
    def _calculate_personalization_score(self, user_patterns: Dict, recommendations_count: int) -> float:
        """Calculate comprehensive personalization score based on multiple factors"""
        score = 0.0
        
        # Factor 1: User activity level (0.0 - 0.4)
        activity_component = user_patterns['activity_score'] * 0.4
        score += activity_component
        
        # Factor 2: Category diversity and preferences (0.0 - 0.3)
        num_categories = len(user_patterns['category_preferences'])
        if num_categories > 0:
            # More categories = better personalization, but cap at reasonable level
            category_diversity = min(1.0, num_categories / 4.0)
            # Higher preference scores = more personalized
            total_category_engagement = sum(user_patterns['category_preferences'].values())
            engagement_intensity = min(1.0, total_category_engagement / 50.0)
            category_component = (category_diversity * 0.2) + (engagement_intensity * 0.1)
            score += category_component
        
        # Factor 3: Tracking behavior (0.0 - 0.2)
        num_tracked = len(user_patterns['tracked_products'])
        if num_tracked > 0:
            tracking_component = min(0.2, num_tracked / 10.0 * 0.2)
            score += tracking_component
        
        # Factor 4: Recommendation quality indicator (0.0 - 0.1)
        if recommendations_count > 0:
            # Having recommendations indicates we found personalized matches
            recommendation_component = min(0.1, recommendations_count / 10.0 * 0.1)
            score += recommendation_component
        
        # Ensure score is between 0.0 and 1.0
        final_score = max(0.0, min(1.0, score))
        
        logger.info(f"Personalization score breakdown: activity={activity_component:.3f}, "
                   f"categories={num_categories}, tracking={num_tracked}, "
                   f"recommendations={recommendations_count}, final={final_score:.3f}")
        
        return final_score
    
    def calculate_price_trend(self, df: pd.DataFrame, product_name: str) -> Tuple[str, float]:
        """Calculate price trend and potential savings"""
        product_data = df[df['product_name'] == product_name].sort_values('date')
        if len(product_data) < 10:
            return "stable", 0.0
        
        # Compare recent vs older prices
        recent_avg = product_data.tail(7)['price_inr'].mean()
        older_avg = product_data.head(7)['price_inr'].mean()
        
        price_change_pct = ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
        
        # Determine trend
        if price_change_pct > 3:
            trend = "increasing"
        elif price_change_pct < -3:
            trend = "decreasing"
        else:
            trend = "stable"
        
        # Calculate potential savings (difference between max and min price in recent period)
        recent_data = product_data.tail(14)
        max_price = recent_data['price_inr'].max()
        min_price = recent_data['price_inr'].min()
        potential_savings = max_price - min_price
        
        return trend, potential_savings
    
    def get_similar_products(self, product_name: str, exclude_products: List[str] = None) -> List[str]:
        """Get products similar to the given product"""
        if exclude_products is None:
            exclude_products = []
        
        # Find the category of the given product
        category = self.product_categories.get(product_name)
        if not category:
            return []
        
        # Get other products in the same category
        similar = []
        if category in self.similarity_groups:
            for product in self.similarity_groups[category]:
                if product != product_name and product not in exclude_products:
                    similar.append(product)
        
        return similar[:3]  # Limit to top 3 similar products
    
    def calculate_recommendation_score(self, product_name: str, user_patterns: Dict, 
                                     df: pd.DataFrame, excluded_products: List[str]) -> float:
        """Calculate recommendation score for a product"""
        if product_name in excluded_products:
            return 0.0
        
        score = 0.0
        
        # Base score
        score += 0.1
        
        # Category preference boost
        category = self.product_categories.get(product_name, "Unknown")
        if category in user_patterns['category_preferences']:
            category_score = user_patterns['category_preferences'][category] / 10.0
            score += min(0.4, category_score)  # Max 0.4 boost from category preference
        
        # Rating boost
        rating = self.product_ratings.get(product_name, 3.0)
        score += (rating - 3.0) / 5.0  # Convert 3-5 rating to 0-0.4 boost
        
        # Trending boost
        trending_score = self.calculate_trending_score(df, product_name)
        score += trending_score * 0.2  # Max 0.2 boost from trending
        
        # Price trend boost (prefer decreasing prices)
        price_trend, _ = self.calculate_price_trend(df, product_name)
        if price_trend == "decreasing":
            score += 0.15
        elif price_trend == "stable":
            score += 0.05
        
        # Activity score multiplier
        score *= (0.5 + user_patterns['activity_score'] * 0.5)  # Scale by user activity
        
        return min(1.0, score)  # Cap at 1.0
    
    def generate_product_recommendations(self, db: Session, user_id: Optional[int] = None,
                                       session_id: Optional[str] = None, 
                                       limit: int = 10) -> RecommendationSet:
        """Generate personalized product recommendations"""
        logger.info(f"Generating recommendations for user_id={user_id}, session_id={session_id}")
        
        # Load data
        df = self.load_price_data()
        
        # Get user activity patterns
        user_patterns = self.get_user_activity_patterns(db, user_id, session_id)
        
        # Get products user has already interacted with
        excluded_products = set()
        
        # Exclude viewed products if user has many views
        viewed_product_names = []
        for view in user_patterns['viewed_products']:
            product_name = self._get_product_name(view['product_id'])
            viewed_product_names.append(product_name)
            if view['views'] > 3:  # Heavily viewed products
                excluded_products.add(product_name)
        
        # Exclude tracked products
        for product_id in user_patterns['tracked_products']:
            product_name = self._get_product_name(product_id)
            excluded_products.add(product_name)
        
        # Generate candidate products
        all_products = list(self.product_categories.keys())
        candidates = []
        
        # Add similar products to viewed/tracked items
        for product_name in viewed_product_names + [self._get_product_name(pid) for pid in user_patterns['tracked_products']]:
            similar_products = self.get_similar_products(product_name, list(excluded_products))
            candidates.extend(similar_products)
        
        # Add popular products from preferred categories
        for category, preference_score in user_patterns['category_preferences'].items():
            if category in self.similarity_groups:
                category_products = [p for p in self.similarity_groups[category] if p not in excluded_products]
                candidates.extend(category_products[:2])  # Top 2 from each preferred category
        
        # Add trending products
        trending_products = []
        for product_name in all_products:
            if product_name not in excluded_products:
                trending_score = self.calculate_trending_score(df, product_name)
                trending_products.append((product_name, trending_score))
        
        trending_products.sort(key=lambda x: x[1], reverse=True)
        candidates.extend([p[0] for p in trending_products[:5]])  # Top 5 trending
        
        # Add highly rated products
        high_rated = [(name, rating) for name, rating in self.product_ratings.items() 
                     if rating >= 4.5 and name not in excluded_products]
        high_rated.sort(key=lambda x: x[1], reverse=True)
        candidates.extend([p[0] for p in high_rated[:3]])  # Top 3 highly rated
        
        # Remove duplicates while preserving order
        unique_candidates = []
        seen = set()
        for product in candidates:
            if product not in seen:
                unique_candidates.append(product)
                seen.add(product)
        
        # Score and rank candidates
        scored_products = []
        for product_name in unique_candidates:
            score = self.calculate_recommendation_score(
                product_name, user_patterns, df, list(excluded_products)
            )
            if score > 0:
                scored_products.append((product_name, score))
        
        # Sort by score and take top recommendations
        scored_products.sort(key=lambda x: x[1], reverse=True)
        top_products = scored_products[:limit]
        
        # Create detailed recommendations
        recommendations = []
        for product_name, score in top_products:
            # Get current best price
            product_data = df[df['product_name'] == product_name]
            if product_data.empty:
                continue
            
            latest_date = product_data['date'].max()
            latest_data = product_data[product_data['date'] == latest_date]
            best_price_row = latest_data.loc[latest_data['price_inr'].idxmin()]
            
            # Generate product ID
            name_to_id = {v: k for k, v in {
                "P001": "iPhone 16", "P002": "Samsung Galaxy S26 Ultra", "P003": "Google Pixel 10 Pro",
                "P004": "OnePlus 14", "P005": "Dell XPS 15", "P006": "Apple MacBook Air (M4)",
                "P007": "HP Spectre x360", "P008": "Lenovo Legion 5 Pro", "P009": "Sony WH-1000XM6 Headphones",
                "P010": "Apple AirPods Pro 3", "P011": "Bose QuietComfort Ultra Earbuds", "P012": "JBL Flip 7 Speaker",
                "P013": "Apple Watch Series 11", "P014": "Samsung Galaxy Watch 7", "P015": "Samsung 55-inch QLED TV",
                "P016": "LG C5 65-inch OLED TV", "P017": "Sony PlayStation 5 Pro", "P018": "Canon EOS R7 Camera",
                "P019": "DJI Mini 5 Pro Drone", "P020": "Logitech MX Master 4 Mouse"
            }.items()}
            
            product_id = name_to_id.get(product_name, "P000")
            
            # Get category and other details
            category = self.product_categories.get(product_name, "Electronics")
            rating = self.product_ratings.get(product_name, 4.0)
            trending_score = self.calculate_trending_score(df, product_name)
            price_trend, potential_savings = self.calculate_price_trend(df, product_name)
            
            # Generate reasons for recommendation
            reasons = []
            if category in user_patterns['category_preferences']:
                reasons.append(f"You've shown interest in {category} products")
            
            if any(self.get_similar_products(self._get_product_name(pid)) and product_name in self.get_similar_products(self._get_product_name(pid)) 
                  for pid in user_patterns['tracked_products']):
                reasons.append("Similar to products you're tracking")
            
            if trending_score > 0.3:
                reasons.append("Currently trending with active price movements")
            
            if rating >= 4.5:
                reasons.append(f"Highly rated product ({rating}/5.0)")
            
            if price_trend == "decreasing":
                reasons.append("Price is currently decreasing")
            elif potential_savings > 1000:
                reasons.append(f"Price varies by ₹{potential_savings:,.0f} across retailers")
            
            if not reasons:
                reasons.append("Popular choice in this category")
            
            # Generate description
            descriptions = {
                "iPhone 16": "Latest Apple smartphone with advanced camera system and A18 chip",
                "Samsung Galaxy S26 Ultra": "Premium Android flagship with S Pen and pro camera features",
                "Google Pixel 10 Pro": "Google's flagship with advanced AI photography and pure Android",
                "OnePlus 14": "Flagship killer with fast charging and smooth performance", 
                "Dell XPS 15": "Premium ultrabook perfect for professionals and creators",
                "Apple MacBook Air (M4)": "Ultra-thin laptop with exceptional battery life and performance",
                "HP Spectre x360": "Convertible laptop with premium design and versatility",
                "Lenovo Legion 5 Pro": "High-performance gaming laptop with excellent display",
                "Sony WH-1000XM6 Headphones": "Industry-leading noise cancellation headphones",
                "Apple AirPods Pro 3": "Premium wireless earbuds with spatial audio",
                "Bose QuietComfort Ultra Earbuds": "Superior noise cancellation in compact form",
                "JBL Flip 7 Speaker": "Portable Bluetooth speaker with powerful sound",
                "Apple Watch Series 11": "Advanced smartwatch with health monitoring features",
                "Samsung Galaxy Watch 7": "Feature-rich smartwatch with long battery life",
                "Samsung 55-inch QLED TV": "Premium 4K TV with vibrant quantum dot display",
                "LG C5 65-inch OLED TV": "Perfect blacks and infinite contrast with OLED technology",
                "Sony PlayStation 5 Pro": "Next-gen gaming console with 4K gaming capabilities",
                "Canon EOS R7 Camera": "Professional mirrorless camera for photography enthusiasts",
                "DJI Mini 5 Pro Drone": "Compact drone with professional camera capabilities",
                "Logitech MX Master 4 Mouse": "Premium wireless mouse for productivity professionals"
            }
            
            # Get retailer links
            best_retailer_url = self.build_retailer_url(str(best_price_row['retailer']), product_name)
            all_retailer_links = self.get_all_retailer_links(df, product_name)
            
            recommendation = ProductRecommendation(
                product_id=product_id,
                product_name=product_name,
                category=category,
                current_price=float(best_price_row['price_inr']),
                best_retailer=str(best_price_row['retailer']),
                description=descriptions.get(product_name, f"High-quality {category.lower()} product"),
                score=score,
                reasons=reasons,
                rating=rating,
                trending_score=trending_score,
                price_trend=price_trend,
                potential_savings=float(potential_savings),
                website_url=best_retailer_url,
                all_retailer_links=all_retailer_links
            )
            
            recommendations.append(recommendation)
        
        # Calculate comprehensive personalization score
        personalization_score = self._calculate_personalization_score(user_patterns, len(recommendations))
        
        return RecommendationSet(
            user_id=user_id,
            session_id=session_id,
            recommendations=recommendations,
            generated_at=datetime.now(),
            total_count=len(recommendations),
            personalization_score=personalization_score
        )

# Testing and example usage
def demo_personalized_recommendations():
    """Demonstrate the personalized recommendation system"""
    print("🎯 Personalized Product Recommendation Demo")
    print("=" * 60)
    
    engine = PersonalizedRecommendationEngine()
    
    # For demo purposes, create a mock database session and patterns
    class MockDB:
        pass
    
    class MockSession:
        pass
    
    # Generate recommendations for a new user (cold start)
    print("\n👤 Recommendations for New User (Cold Start):")
    mock_db = MockSession()  # This would be a real DB session in production
    
    try:
        # In a real scenario, you'd pass the actual database session
        # For demo, we'll simulate with empty patterns
        df = engine.load_price_data()
        
        # Create sample recommendations based on trending and highly rated products
        all_products = list(engine.product_categories.keys())
        recommendations = []
        
        for product_name in all_products[:10]:  # Top 10 for demo
            product_data = df[df['product_name'] == product_name]
            if not product_data.empty:
                latest_data = product_data[product_data['date'] == product_data['date'].max()]
                best_price_row = latest_data.loc[latest_data['price_inr'].idxmin()]
                
                category = engine.product_categories.get(product_name, "Electronics")
                rating = engine.product_ratings.get(product_name, 4.0)
                trending_score = engine.calculate_trending_score(df, product_name)
                price_trend, potential_savings = engine.calculate_price_trend(df, product_name)
                
                score = rating/5.0 + trending_score * 0.3  # Simple scoring for demo
                
                # Generate website links
                website_url = engine.build_retailer_url(str(best_price_row['retailer']), product_name)
                all_retailer_links = engine.get_all_retailer_links(df, product_name)
                
                recommendation = ProductRecommendation(
                    product_id=f"P{len(recommendations)+1:03d}",
                    product_name=product_name,
                    category=category,
                    current_price=float(best_price_row['price_inr']),
                    best_retailer=str(best_price_row['retailer']),
                    description=f"High-quality {category.lower()} product with great features",
                    score=score,
                    reasons=["Highly rated product", "Popular in category"],
                    rating=rating,
                    trending_score=trending_score,
                    price_trend=price_trend,
                    potential_savings=float(potential_savings),
                    website_url=website_url,
                    all_retailer_links=all_retailer_links
                )
                recommendations.append(recommendation)
        
        # Sort by score and show top 5
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        for i, rec in enumerate(recommendations[:5], 1):
                print(f"\n{i}. 📱 {rec.product_name}")
                print(f"   🏷️  Category: {rec.category}")
                print(f"   💰 Price: ₹{rec.current_price:,} at {rec.best_retailer}")
                print(f"   ⭐ Rating: {rec.rating}/5.0")
                print(f"   📈 Trending Score: {rec.trending_score:.2f}")
                print(f"   📊 Price Trend: {rec.price_trend}")
                if rec.potential_savings > 0:
                    print(f"   💡 Potential Savings: ₹{rec.potential_savings:,.0f}")
                print(f"   📝 {rec.description}")
                print(f"   🎯 Reasons: {', '.join(rec.reasons)}")
                print(f"   🔗 Best Price Link: {rec.website_url}")
                print(f"   🛒 Available at {len(rec.all_retailer_links)} retailers")
        
        print(f"\n✅ Generated {len(recommendations)} recommendations successfully!")
        
    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")

if __name__ == "__main__":
    demo_personalized_recommendations()