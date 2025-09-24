import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class PriceRecommendationEngine:
    """Enhanced price recommendation engine with 10-day forecasts"""
    
    def __init__(self):
        self.backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.backend_dir, "data")
        self.historical_data_path = os.path.join(self.data_dir, "ecommerce_price_dataset_corrected.csv")
        self.forecast_data_path = os.path.join(self.data_dir, "price_forecast_10_days.csv")
        
    def load_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Load both historical and forecast data"""
        try:
            historical_df = pd.read_csv(self.historical_data_path)
            historical_df['date'] = pd.to_datetime(historical_df['date'])
            historical_df['is_forecast'] = False
            
            forecast_df = pd.read_csv(self.forecast_data_path)
            forecast_df['date'] = pd.to_datetime(forecast_df['date'])
            forecast_df['is_forecast'] = True
            
            return historical_df, forecast_df
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Dataset files not found. Please run generate_smooth_dataset.py first.")
    
    def get_current_best_deals(self, top_n: int = 10) -> List[Dict]:
        """Get current best deals across all retailers"""
        historical_df, _ = self.load_data()
        
        # Get latest date in historical data
        latest_date = historical_df['date'].max()
        current_data = historical_df[historical_df['date'] == latest_date]
        
        # Find best price for each product
        best_deals = []
        for product in current_data['product_name'].unique():
            product_data = current_data[current_data['product_name'] == product]
            best_deal = product_data.loc[product_data['price_inr'].idxmin()]
            
            # Calculate savings compared to most expensive retailer
            max_price = product_data['price_inr'].max()
            savings = max_price - best_deal['price_inr']
            savings_pct = (savings / max_price) * 100
            
            best_deals.append({
                'product_name': best_deal['product_name'],
                'retailer': best_deal['retailer'],
                'current_price': round(best_deal['price_inr'], 2),
                'savings_amount': round(savings, 2),
                'savings_percentage': round(savings_pct, 1),
                'date': best_deal['date'].strftime('%Y-%m-%d')
            })
        
        # Sort by savings amount and return top N
        best_deals.sort(key=lambda x: x['savings_amount'], reverse=True)
        return best_deals[:top_n]
    
    def get_10_day_forecast(self, product_name: Optional[str] = None) -> List[Dict]:
        """Get 10-day price forecast for specific product or all products"""
        _, forecast_df = self.load_data()
        
        if product_name:
            forecast_df = forecast_df[forecast_df['product_name'] == product_name]
        
        # Group by date and product to find daily best deals
        daily_forecasts = []
        for date in forecast_df['date'].unique():
            date_data = forecast_df[forecast_df['date'] == date]
            
            for product in date_data['product_name'].unique():
                product_data = date_data[date_data['product_name'] == product]
                best_deal = product_data.loc[product_data['price_inr'].idxmin()]
                
                daily_forecasts.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'product_name': product,
                    'best_retailer': best_deal['retailer'],
                    'predicted_price': round(best_deal['price_inr'], 2),
                    'all_prices': [
                        {
                            'retailer': row['retailer'],
                            'price': round(row['price_inr'], 2)
                        }
                        for _, row in product_data.iterrows()
                    ]
                })
        
        return sorted(daily_forecasts, key=lambda x: (x['date'], x['product_name']))
    
    def get_buy_recommendations(self, days_ahead: int = 10) -> List[Dict]:
        """Get buy/wait recommendations based on price trends"""
        historical_df, forecast_df = self.load_data()
        
        recommendations = []
        
        # Get current prices (latest historical data)
        latest_historical = historical_df['date'].max()
        current_data = historical_df[historical_df['date'] == latest_historical]
        
        for product in current_data['product_name'].unique():
            # Current best price
            current_product_data = current_data[current_data['product_name'] == product]
            current_best = current_product_data.loc[current_product_data['price_inr'].idxmin()]
            
            # Forecast best prices for next N days
            forecast_product_data = forecast_df[forecast_df['product_name'] == product]
            
            if not forecast_product_data.empty:
                # Find minimum predicted price in forecast period
                future_best = forecast_product_data.loc[forecast_product_data['price_inr'].idxmin()]
                
                # Calculate potential savings
                potential_savings = current_best['price_inr'] - future_best['price_inr']
                savings_pct = (potential_savings / current_best['price_inr']) * 100
                
                # Determine recommendation
                if potential_savings > 1000 and savings_pct > 2:  # Wait if significant savings expected
                    recommendation = "WAIT"
                    reason = f"Price expected to drop by ₹{potential_savings:,.0f} ({savings_pct:.1f}%) on {future_best['date'].strftime('%Y-%m-%d')}"
                elif savings_pct < -1:  # Buy now if prices expected to rise
                    recommendation = "BUY_NOW"
                    reason = f"Price may increase by {abs(savings_pct):.1f}% soon"
                else:  # Stable pricing
                    recommendation = "NEUTRAL"
                    reason = "Price expected to remain stable"
                
                recommendations.append({
                    'product_name': product,
                    'current_best_price': round(current_best['price_inr'], 2),
                    'current_best_retailer': current_best['retailer'],
                    'predicted_best_price': round(future_best['price_inr'], 2),
                    'predicted_best_retailer': future_best['retailer'],
                    'predicted_best_date': future_best['date'].strftime('%Y-%m-%d'),
                    'potential_savings': round(potential_savings, 2),
                    'savings_percentage': round(savings_pct, 1),
                    'recommendation': recommendation,
                    'reason': reason
                })
        
        # Sort by potential savings (highest first)
        recommendations.sort(key=lambda x: x['potential_savings'], reverse=True)
        return recommendations
    
    def get_price_trend_analysis(self, product_name: str, days_back: int = 30) -> Dict:
        """Analyze price trends for a specific product"""
        historical_df, forecast_df = self.load_data()
        
        # Get recent historical data
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_data = historical_df[
            (historical_df['product_name'] == product_name) & 
            (historical_df['date'] >= cutoff_date)
        ]
        
        if recent_data.empty:
            return {'error': 'No data found for the specified product'}
        
        # Calculate trend metrics
        daily_best_prices = recent_data.groupby('date')['price_inr'].min()
        price_volatility = daily_best_prices.std()
        avg_price = daily_best_prices.mean()
        price_trend = 'stable'
        
        # Determine trend direction
        if len(daily_best_prices) >= 7:
            recent_avg = daily_best_prices.tail(7).mean()
            older_avg = daily_best_prices.head(7).mean()
            price_change_pct = ((recent_avg - older_avg) / older_avg) * 100
            
            if price_change_pct > 2:
                price_trend = 'increasing'
            elif price_change_pct < -2:
                price_trend = 'decreasing'
        
        # Get forecast trend
        forecast_data = forecast_df[forecast_df['product_name'] == product_name]
        forecast_best_prices = forecast_data.groupby('date')['price_inr'].min() if not forecast_data.empty else pd.Series()
        
        return {
            'product_name': product_name,
            'analysis_period_days': days_back,
            'average_price': round(avg_price, 2),
            'price_volatility': round(price_volatility, 2),
            'volatility_percentage': round((price_volatility / avg_price) * 100, 1),
            'current_trend': price_trend,
            'min_price_in_period': round(daily_best_prices.min(), 2),
            'max_price_in_period': round(daily_best_prices.max(), 2),
            'forecast_available': not forecast_data.empty,
            'forecast_min_price': round(forecast_best_prices.min(), 2) if not forecast_best_prices.empty else None,
            'forecast_max_price': round(forecast_best_prices.max(), 2) if not forecast_best_prices.empty else None
        }

# Example usage and testing
if __name__ == "__main__":
    engine = PriceRecommendationEngine()
    
    try:
        print("🏆 Current Best Deals (Top 5):")
        best_deals = engine.get_current_best_deals(5)
        for deal in best_deals:
            print(f"  • {deal['product_name']} at {deal['retailer']}: ₹{deal['current_price']:,} (Save ₹{deal['savings_amount']:,})")
        
        print(f"\n🔮 Buy/Wait Recommendations (Top 5):")
        recommendations = engine.get_buy_recommendations()[:5]
        for rec in recommendations:
            print(f"  • {rec['product_name']}: {rec['recommendation']} - {rec['reason']}")
        
        print(f"\n📊 Price Trend Analysis - iPhone 16:")
        trend = engine.get_price_trend_analysis("iPhone 16")
        print(f"  • Average Price: ₹{trend['average_price']:,}")
        print(f"  • Price Volatility: {trend['volatility_percentage']}%")
        print(f"  • Current Trend: {trend['current_trend']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")