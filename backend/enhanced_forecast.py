"""
Enhanced Price Forecasting Engine with Advanced Market Analysis
Creates realistic 30-day price predictions using statistical methods and market patterns
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

class EnhancedPriceForecast:
    """Enhanced price forecasting using statistical methods and market dynamics"""
    
    def __init__(self):
        self.backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.backend_dir, "data")
        self.historical_data_path = os.path.join(self.data_dir, "ecommerce_price_dataset_corrected.csv")
        self.forecast_data_path = os.path.join(self.data_dir, "price_forecast_30_days.csv")
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load both historical and forecast data"""
        try:
            historical_df = pd.read_csv(self.historical_data_path)
            historical_df['date'] = pd.to_datetime(historical_df['date'])
            
            forecast_df = pd.read_csv(self.forecast_data_path)
            forecast_df['date'] = pd.to_datetime(forecast_df['date'])
            
            return historical_df, forecast_df
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Dataset files not found. Please run generate_smooth_dataset.py first.")
    
    def analyze_price_patterns(self, product_name: str, retailer: str = None) -> Dict:
        """Analyze historical price patterns for better forecasting"""
        historical_df, forecast_df = self.load_data()
        
        # Filter data
        product_data = historical_df[historical_df['product_name'] == product_name].copy()
        if retailer:
            product_data = product_data[product_data['retailer'] == retailer]
            
        if product_data.empty:
            return {'error': f'No data found for product: {product_name}'}
        
        # Sort by date
        product_data = product_data.sort_values('date')
        
        # Calculate various metrics
        prices = product_data['price_inr'].values
        dates = product_data['date'].values
        
        # Basic statistics
        mean_price = np.mean(prices)
        std_price = np.std(prices)
        min_price = np.min(prices)
        max_price = np.max(prices)
        
        # Trend analysis (using last 30 days vs previous 30 days)
        if len(prices) >= 60:
            recent_prices = prices[-30:]
            older_prices = prices[-60:-30]
            trend_change = (np.mean(recent_prices) - np.mean(older_prices)) / np.mean(older_prices) * 100
        else:
            trend_change = 0
            
        # Volatility analysis
        daily_changes = np.diff(prices) / prices[:-1] * 100
        volatility = np.std(daily_changes)
        
        # Seasonal patterns (day of week effect)
        product_data['day_of_week'] = product_data['date'].dt.dayofweek
        weekend_avg = product_data[product_data['day_of_week'].isin([5, 6])]['price_inr'].mean()
        weekday_avg = product_data[~product_data['day_of_week'].isin([5, 6])]['price_inr'].mean()
        weekend_discount = (weekday_avg - weekend_avg) / weekday_avg * 100 if weekday_avg != 0 else 0
        
        return {
            'product_name': product_name,
            'retailer': retailer,
            'price_stats': {
                'mean': round(mean_price, 2),
                'std': round(std_price, 2),
                'min': round(min_price, 2),
                'max': round(max_price, 2),
                'coefficient_of_variation': round(std_price / mean_price * 100, 2)
            },
            'trend_analysis': {
                'trend_change_pct': round(trend_change, 2),
                'volatility_pct': round(volatility, 2),
                'weekend_discount_pct': round(weekend_discount, 2)
            },
            'data_points': len(prices)
        }
    
    def generate_enhanced_forecast(self, product_name: str, retailer: str = None, days: int = 30) -> Dict:
        """Generate enhanced forecast with confidence intervals and market events"""
        try:
            historical_df, existing_forecast_df = self.load_data()
            
            # Get existing forecast if available
            forecast_data = existing_forecast_df[existing_forecast_df['product_name'] == product_name].copy()
            if retailer:
                forecast_data = forecast_data[forecast_data['retailer'] == retailer]
                
            if forecast_data.empty:
                return {'error': f'No forecast data available for {product_name}'}
            
            # Analyze historical patterns
            pattern_analysis = self.analyze_price_patterns(product_name, retailer)
            if 'error' in pattern_analysis:
                return pattern_analysis
                
            # Sort forecast data by date
            forecast_data = forecast_data.sort_values('date')
            
            # Get current price (last historical data point)
            historical_product = historical_df[historical_df['product_name'] == product_name]
            if retailer:
                historical_product = historical_product[historical_product['retailer'] == retailer]
                
            current_price = historical_product.sort_values('date').iloc[-1]['price_inr']
            
            # Enhance forecast with confidence intervals and market events
            enhanced_forecasts = []
            
            for idx, row in forecast_data.iterrows():
                forecast_date = row['date']
                base_price = row['price_inr']
                
                # Calculate days ahead
                days_ahead = (forecast_date.date() - datetime.now().date()).days
                
                # Confidence decreases over time
                confidence = max(0.5, 1.0 - (days_ahead * 0.015))  # 1.5% decrease per day
                
                # Error margins based on historical volatility
                volatility = pattern_analysis['trend_analysis']['volatility_pct'] / 100
                base_margin = base_price * volatility * 1.5  # 1.5x historical volatility
                
                # Increase margin for future dates
                time_margin = base_price * 0.02 * (days_ahead / 30)  # Up to 2% additional margin
                total_margin = base_margin + time_margin
                
                # Market event adjustments
                market_events = self._identify_market_events(forecast_date, days_ahead)
                event_adjustment = 0
                event_description = None
                
                if market_events:
                    event_adjustment = market_events['price_impact']
                    event_description = market_events['description']
                    base_price *= (1 + event_adjustment)
                
                # Weekend effect
                if forecast_date.weekday() in [5, 6]:
                    weekend_effect = pattern_analysis['trend_analysis']['weekend_discount_pct'] / 100
                    base_price *= (1 - abs(weekend_effect) * 0.5)  # Apply half the historical weekend effect
                
                enhanced_forecast = {
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'day_of_week': forecast_date.strftime('%A'),
                    'days_ahead': days_ahead,
                    'predicted_price': round(base_price, 2),
                    'confidence_score': round(confidence, 3),
                    'price_range': {
                        'lower': round(base_price - total_margin, 2),
                        'upper': round(base_price + total_margin, 2),
                        'margin_pct': round(total_margin / base_price * 100, 1)
                    },
                    'market_insights': {
                        'vs_current_price': round((base_price - current_price) / current_price * 100, 1),
                        'vs_historical_avg': round((base_price - pattern_analysis['price_stats']['mean']) / pattern_analysis['price_stats']['mean'] * 100, 1),
                        'market_event': event_description,
                        'weekend_effect': forecast_date.weekday() in [5, 6]
                    }
                }
                
                enhanced_forecasts.append(enhanced_forecast)
            
            # Calculate summary statistics
            forecast_prices = [f['predicted_price'] for f in enhanced_forecasts]
            best_price = min(forecast_prices)
            worst_price = max(forecast_prices)
            avg_price = np.mean(forecast_prices)
            
            # Find best deal timing
            best_deal = min(enhanced_forecasts, key=lambda x: x['predicted_price'])
            
            # Price trend classification
            if avg_price > current_price * 1.03:
                trend_classification = "INCREASING"
                trend_advice = "Consider buying soon, prices expected to rise"
            elif avg_price < current_price * 0.97:
                trend_classification = "DECREASING"
                trend_advice = "Wait for better deals, prices expected to fall"
            else:
                trend_classification = "STABLE"
                trend_advice = "Prices expected to remain stable"
            
            return {
                'product_name': product_name,
                'retailer_filter': retailer,
                'forecast_period': f"{days} days",
                'current_market_price': round(current_price, 2),
                'historical_analysis': pattern_analysis,
                'forecast_summary': {
                    'best_predicted_price': round(best_price, 2),
                    'worst_predicted_price': round(worst_price, 2),
                    'average_predicted_price': round(avg_price, 2),
                    'best_deal_date': best_deal['date'],
                    'potential_savings': round(max(0, current_price - best_price), 2),
                    'potential_savings_pct': round(max(0, (current_price - best_price) / current_price * 100), 1),
                    'price_trend': trend_classification,
                    'buying_advice': trend_advice
                },
                'daily_forecasts': enhanced_forecasts,
                'model_metadata': {
                    'forecast_method': 'Statistical Analysis + Market Patterns',
                    'confidence_method': 'Time-decay + Historical Volatility',
                    'data_points_used': pattern_analysis['data_points'],
                    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
        except Exception as e:
            return {'error': f'Forecast generation failed: {str(e)}'}
    
    def _identify_market_events(self, forecast_date: pd.Timestamp, days_ahead: int) -> Optional[Dict]:
        """Identify potential market events that could affect pricing"""
        
        # Define market events (simplified simulation)
        events = []
        
        # Month-end sales (last 3 days of month)
        if forecast_date.day >= 28:
            events.append({
                'type': 'month_end_sale',
                'description': 'Month-end promotional pricing',
                'price_impact': -0.02,  # 2% discount
                'probability': 0.7
            })
        
        # Weekend promotions
        if forecast_date.weekday() in [5, 6]:
            events.append({
                'type': 'weekend_promotion',
                'description': 'Weekend special offers',
                'price_impact': -0.015,  # 1.5% discount
                'probability': 0.5
            })
        
        # Festival season (simulated)
        if forecast_date.month in [10, 11]:  # Festive season
            events.append({
                'type': 'festival_sale',
                'description': 'Festival season discounts',
                'price_impact': -0.05,  # 5% discount
                'probability': 0.8
            })
        
        # New product launch effect (first week of month)
        if 1 <= forecast_date.day <= 7:
            events.append({
                'type': 'product_launch',
                'description': 'New product launch may affect pricing',
                'price_impact': 0.01,  # 1% increase
                'probability': 0.3
            })
        
        # Return the most likely event
        if events:
            return max(events, key=lambda x: x['probability'])
        
        return None
    
    def get_competitive_analysis(self, product_name: str) -> Dict:
        """Get competitive analysis across all retailers for a product"""
        try:
            historical_df, forecast_df = self.load_data()
            
            # Get current prices across retailers
            latest_date = historical_df['date'].max()
            current_data = historical_df[
                (historical_df['product_name'] == product_name) & 
                (historical_df['date'] == latest_date)
            ]
            
            if current_data.empty:
                return {'error': f'No current data for {product_name}'}
            
            # Get forecast prices across retailers
            forecast_data = forecast_df[forecast_df['product_name'] == product_name]
            
            retailer_analysis = {}
            
            for retailer in current_data['retailer'].unique():
                current_price = current_data[current_data['retailer'] == retailer]['price_inr'].iloc[0]
                
                # Get retailer forecast
                retailer_forecast = forecast_data[forecast_data['retailer'] == retailer]
                
                if not retailer_forecast.empty:
                    avg_forecast_price = retailer_forecast['price_inr'].mean()
                    min_forecast_price = retailer_forecast['price_inr'].min()
                    max_forecast_price = retailer_forecast['price_inr'].max()
                    
                    retailer_analysis[retailer] = {
                        'current_price': round(current_price, 2),
                        'forecast_avg': round(avg_forecast_price, 2),
                        'forecast_min': round(min_forecast_price, 2),
                        'forecast_max': round(max_forecast_price, 2),
                        'expected_change_pct': round((avg_forecast_price - current_price) / current_price * 100, 1)
                    }
            
            # Find best current and forecast deals
            current_best = min(retailer_analysis.items(), key=lambda x: x[1]['current_price'])
            forecast_best = min(retailer_analysis.items(), key=lambda x: x[1]['forecast_min'])
            
            return {
                'product_name': product_name,
                'analysis_date': latest_date.strftime('%Y-%m-%d'),
                'retailer_analysis': retailer_analysis,
                'market_summary': {
                    'current_best_deal': {
                        'retailer': current_best[0],
                        'price': current_best[1]['current_price']
                    },
                    'forecast_best_deal': {
                        'retailer': forecast_best[0],
                        'price': forecast_best[1]['forecast_min']
                    },
                    'total_retailers': len(retailer_analysis)
                }
            }
            
        except Exception as e:
            return {'error': f'Competitive analysis failed: {str(e)}'}

# Test function
def demo_enhanced_forecast():
    """Demo the enhanced forecasting capabilities"""
    print("🚀 Enhanced Price Forecasting Demo (30 Days)")
    print("=" * 70)
    
    forecaster = EnhancedPriceForecast()
    
    # Test products
    test_products = ["iPhone 16", "Dell XPS 15", "Sony WH-1000XM6 Headphones"]
    
    for product in test_products:
        print(f"\n📱 Enhanced Forecast for: {product}")
        print("-" * 50)
        
        result = forecaster.generate_enhanced_forecast(product, days=30)
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
            continue
        
        summary = result['forecast_summary']
        print(f"   💰 Current Price: ₹{result['current_market_price']:,}")
        print(f"   📊 Avg Forecast: ₹{summary['average_predicted_price']:,}")
        print(f"   🎯 Best Deal: ₹{summary['best_predicted_price']:,} on {summary['best_deal_date']}")
        print(f"   💡 Savings Potential: ₹{summary['potential_savings']:,} ({summary['potential_savings_pct']}%)")
        print(f"   📈 Trend: {summary['price_trend']}")
        print(f"   🧠 Advice: {summary['buying_advice']}")
        
        # Show next 5 days
        print(f"   📅 Next 5 Days:")
        for forecast in result['daily_forecasts'][:5]:
            confidence_stars = "★" * int(forecast['confidence_score'] * 5)
            price_vs_current = forecast['market_insights']['vs_current_price']
            direction = "📈" if price_vs_current > 0 else "📉" if price_vs_current < 0 else "➡️"
            print(f"      {forecast['date']} ({forecast['day_of_week'][:3]}): ₹{forecast['predicted_price']:,} {direction} {confidence_stars}")

if __name__ == "__main__":
    demo_enhanced_forecast()