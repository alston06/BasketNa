"""
Advanced ML Forecast Model with Multiple Algorithms and 30-day Predictions
Uses ensemble methods, seasonal patterns, and market dynamics for realistic forecasting
"""

import os
import warnings
from dataclasses import dataclass
from datetime import date, timedelta, datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

warnings.filterwarnings('ignore')

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "ecommerce_price_dataset_corrected.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "forecasts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@dataclass
class ForecastPoint:
    date: date
    price: float
    lower: float
    upper: float
    confidence: float

class AdvancedPriceForecast:
    """Advanced price forecasting using ensemble methods and market dynamics"""
    
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
            'gradient_boost': GradientBoostingRegressor(n_estimators=150, learning_rate=0.1, random_state=42),
            'linear_trend': LinearRegression()
        }
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names = []
        
    def create_features(self, df: pd.DataFrame, product_id: str, retailer: str = None) -> pd.DataFrame:
        """Create advanced features for price prediction"""
        # Filter data
        product_data = df[df['product_id'] == product_id].copy()
        if retailer:
            product_data = product_data[product_data['retailer'] == retailer]
            
        if len(product_data) < 10:
            raise ValueError(f"Insufficient data for product {product_id}")
            
        # Sort by date
        product_data = product_data.sort_values('date')
        product_data.reset_index(drop=True, inplace=True)
        
        # Create time-based features
        product_data['day_of_week'] = pd.to_datetime(product_data['date']).dt.dayofweek
        product_data['day_of_month'] = pd.to_datetime(product_data['date']).dt.day
        product_data['month'] = pd.to_datetime(product_data['date']).dt.month
        product_data['days_since_start'] = (pd.to_datetime(product_data['date']) - pd.to_datetime(product_data['date']).min()).dt.days
        
        # Create price-based features
        product_data['price_lag_1'] = product_data['price'].shift(1)
        product_data['price_lag_3'] = product_data['price'].shift(3)
        product_data['price_lag_7'] = product_data['price'].shift(7)
        
        # Rolling statistics
        product_data['price_ma_3'] = product_data['price'].rolling(window=3, min_periods=1).mean()
        product_data['price_ma_7'] = product_data['price'].rolling(window=7, min_periods=1).mean()
        product_data['price_std_7'] = product_data['price'].rolling(window=7, min_periods=1).std().fillna(0)
        
        # Price change features
        product_data['price_change_1d'] = product_data['price'].pct_change(1).fillna(0)
        product_data['price_change_3d'] = product_data['price'].pct_change(3).fillna(0)
        product_data['price_change_7d'] = product_data['price'].pct_change(7).fillna(0)
        
        # Volatility features
        product_data['volatility_7d'] = product_data['price_change_1d'].rolling(window=7, min_periods=1).std().fillna(0)
        
        # Seasonal features
        product_data['is_weekend'] = (product_data['day_of_week'] >= 5).astype(int)
        product_data['is_month_end'] = (product_data['day_of_month'] >= 28).astype(int)
        
        # Market trend features
        product_data['price_position'] = product_data['price'].rank(pct=True)  # Position in price distribution
        product_data['trend_strength'] = product_data['price'].rolling(window=14, min_periods=1).apply(
            lambda x: np.corrcoef(np.arange(len(x)), x)[0, 1] if len(x) > 1 else 0
        ).fillna(0)
        
        # Drop rows with NaN values in key features
        product_data = product_data.dropna(subset=['price_lag_1'])
        
        return product_data
    
    def prepare_training_data(self, features_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for training"""
        feature_cols = [
            'day_of_week', 'day_of_month', 'month', 'days_since_start',
            'price_lag_1', 'price_lag_3', 'price_lag_7',
            'price_ma_3', 'price_ma_7', 'price_std_7',
            'price_change_1d', 'price_change_3d', 'price_change_7d',
            'volatility_7d', 'is_weekend', 'is_month_end',
            'price_position', 'trend_strength'
        ]
        
        # Filter to only include columns that exist
        available_cols = [col for col in feature_cols if col in features_df.columns]
        self.feature_names = available_cols
        
        X = features_df[available_cols].values
        y = features_df['price'].values
        
        return X, y
    
    def fit(self, df: pd.DataFrame, product_id: str, retailer: str = None):
        """Train the ensemble model"""
        # Create features
        features_df = self.create_features(df, product_id, retailer)
        X, y = self.prepare_training_data(features_df)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train all models
        for name, model in self.models.items():
            model.fit(X_scaled, y)
            
        self.is_fitted = True
        self.last_known_data = features_df.iloc[-1:].copy()  # Store last row for prediction
        
        return self
    
    def predict_ensemble(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make ensemble predictions with confidence intervals"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
            
        X_scaled = self.scaler.transform(X)
        predictions = {}
        
        # Get predictions from all models
        for name, model in self.models.items():
            pred = model.predict(X_scaled)
            predictions[name] = pred
            
        # Ensemble prediction (weighted average)
        weights = {
            'random_forest': 0.5,
            'gradient_boost': 0.35,
            'linear_trend': 0.15
        }
        
        ensemble_pred = np.zeros(len(X))
        for name, pred in predictions.items():
            ensemble_pred += weights[name] * pred
            
        # Calculate confidence intervals based on model disagreement
        pred_array = np.array(list(predictions.values()))
        prediction_std = np.std(pred_array, axis=0)
        
        # Add base uncertainty
        base_uncertainty = ensemble_pred * 0.02  # 2% base uncertainty
        total_uncertainty = np.sqrt(prediction_std**2 + base_uncertainty**2)
        
        return ensemble_pred, total_uncertainty
    
    def forecast_30_days(self, df: pd.DataFrame, product_id: str, retailer: str = None) -> List[ForecastPoint]:
        """Generate 30-day forecast with realistic market dynamics"""
        self.fit(df, product_id, retailer)
        
        forecasts = []
        current_data = self.last_known_data.copy()
        
        # Get the last known date
        last_date = pd.to_datetime(current_data['date'].iloc[0])
        
        for day in range(1, 31):  # 30 days
            forecast_date = last_date + timedelta(days=day)
            
            # Update time features
            current_data['day_of_week'] = forecast_date.dayofweek
            current_data['day_of_month'] = forecast_date.day
            current_data['month'] = forecast_date.month
            current_data['days_since_start'] = current_data['days_since_start'].iloc[0] + day
            current_data['is_weekend'] = int(forecast_date.dayofweek >= 5)
            current_data['is_month_end'] = int(forecast_date.day >= 28)
            
            # Prepare features for prediction
            X_pred = current_data[self.feature_names].values
            
            # Make prediction
            pred_price, uncertainty = self.predict_ensemble(X_pred)
            pred_price = pred_price[0]
            uncertainty = uncertainty[0]
            
            # Add market dynamics and noise
            # Weekend effect
            if forecast_date.dayofweek in [5, 6]:  # Weekend
                pred_price *= 0.995  # Slight discount on weekends
                
            # Month-end effect
            if forecast_date.day >= 28:
                pred_price *= 0.992  # Month-end sales
                
            # Add realistic noise based on day
            noise_factor = 0.005 * np.sin(day * 0.2) + 0.003 * np.random.normal()
            pred_price *= (1 + noise_factor)
            
            # Calculate confidence intervals
            confidence = max(0.6, 1.0 - (day * 0.01))  # Decreasing confidence over time
            margin = uncertainty * 1.96  # 95% confidence interval
            
            forecast_point = ForecastPoint(
                date=forecast_date.date(),
                price=float(pred_price),
                lower=float(pred_price - margin),
                upper=float(pred_price + margin),
                confidence=float(confidence)
            )
            
            forecasts.append(forecast_point)
            
            # Update data for next iteration
            current_data['price_lag_7'] = current_data['price_lag_3'].iloc[0]
            current_data['price_lag_3'] = current_data['price_lag_1'].iloc[0]
            current_data['price_lag_1'] = pred_price
            
            # Update moving averages (simplified)
            current_data['price_ma_3'] = (current_data['price_ma_3'].iloc[0] * 2 + pred_price) / 3
            current_data['price_ma_7'] = (current_data['price_ma_7'].iloc[0] * 6 + pred_price) / 7
            
            # Update price changes
            if day > 1:
                prev_price = forecasts[-2].price if len(forecasts) > 1 else current_data['price_lag_1'].iloc[0]
                current_data['price_change_1d'] = (pred_price - prev_price) / prev_price
            
        return forecasts

def load_dataset() -> pd.DataFrame:
    """Load and preprocess the e-commerce dataset"""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    
    # Create product_id mapping for compatibility
    product_mapping = {
        "iPhone 16": "P001",
        "Samsung Galaxy S26 Ultra": "P002", 
        "Google Pixel 10 Pro": "P003",
        "OnePlus 14": "P004",
        "Dell XPS 15": "P005",
        "Apple MacBook Air (M4)": "P006",
        "HP Spectre x360": "P007",
        "Lenovo Legion 5 Pro": "P008",
        "Sony WH-1000XM6 Headphones": "P009",
        "Apple AirPods Pro 3": "P010",
        "Bose QuietComfort Ultra Earbuds": "P011",
        "JBL Flip 7 Speaker": "P012",
        "Apple Watch Series 11": "P013",
        "Samsung Galaxy Watch 8": "P014",
        "Fitbit Charge 7": "P015",
        "Garmin Forerunner 965": "P016",
        "iPad Pro 13-inch (M4)": "P017",
        "Samsung Galaxy Tab S10 Ultra": "P018",
        "Microsoft Surface Pro 11": "P019",
        "Nothing Tab (1)": "P020"
    }
    
    # Map product names to IDs
    df["product_id"] = df["product_name"].map(product_mapping)
    
    # Rename price column for consistency
    if "price_inr" in df.columns:
        df["price"] = df["price_inr"]
    
    return df

def forecast_for_product(product_id: str, retailer: str = None, days: int = 30) -> Dict:
    """Generate advanced forecast for a specific product"""
    try:
        df = load_dataset()
    except FileNotFoundError:
        return {"error": "Dataset not found. Please ensure ecommerce_price_dataset_corrected.csv exists in the data folder."}
    
    # Get product info
    product_df = df[df["product_id"] == product_id]
    if product_df.empty:
        available_products = get_available_products()
        return {
            "error": f"Product {product_id} not found. Available products: {available_products}"
        }
    
    product_name = product_df["product_name"].iloc[0]
    
    try:
        # Create and use advanced forecasting model
        forecaster = AdvancedPriceForecast()
        forecasts = forecaster.forecast_30_days(df, product_id, retailer)
        
        # Calculate current price stats
        recent_data = product_df[product_df["date"] >= (datetime.now().date() - timedelta(days=7))]
        if retailer:
            recent_data = recent_data[recent_data["retailer"] == retailer]
            
        current_avg_price = recent_data["price"].mean()
        current_min_price = recent_data["price"].min()
        current_max_price = recent_data["price"].max()
        
        # Find best deals in forecast
        best_forecast_price = min(f.price for f in forecasts)
        best_forecast_date = next(f.date for f in forecasts if f.price == best_forecast_price)
        
        # Calculate metrics
        forecast_prices = [f.price for f in forecasts]
        avg_forecast_price = np.mean(forecast_prices)
        price_trend = "stable"
        
        if avg_forecast_price > current_avg_price * 1.02:
            price_trend = "increasing"
        elif avg_forecast_price < current_avg_price * 0.98:
            price_trend = "decreasing"
            
        # Prepare response
        forecast_data = [
            {
                "date": f.date.strftime("%Y-%m-%d"),
                "price": round(f.price, 2),
                "lower": round(f.lower, 2),
                "upper": round(f.upper, 2),
                "confidence": round(f.confidence, 3)
            }
            for f in forecasts
        ]
        
        return {
            "product_id": product_id,
            "product_name": product_name,
            "retailer_filter": retailer,
            "forecast_days": len(forecasts),
            "current_price_stats": {
                "average": round(current_avg_price, 2),
                "min": round(current_min_price, 2),
                "max": round(current_max_price, 2)
            },
            "forecast_summary": {
                "average_predicted_price": round(avg_forecast_price, 2),
                "best_predicted_price": round(best_forecast_price, 2),
                "best_price_date": best_forecast_date.strftime("%Y-%m-%d"),
                "price_trend": price_trend,
                "potential_savings": round(max(0, current_min_price - best_forecast_price), 2)
            },
            "forecast": forecast_data,
            "model_info": {
                "algorithm": "Ensemble (Random Forest + Gradient Boosting + Linear Trend)",
                "features_used": forecaster.feature_names if forecaster.is_fitted else [],
                "confidence_method": "Model disagreement + temporal decay"
            }
        }
        
    except Exception as e:
        return {"error": f"Forecasting failed: {str(e)}"}

def get_available_products() -> List[str]:
    """Get list of available products in the dataset"""
    try:
        df = load_dataset()
        return sorted(df["product_id"].unique().tolist())
    except:
        return []

# Demo function
def demo_advanced_forecast():
    """Demonstrate the advanced forecasting capabilities"""
    print("🚀 Advanced Price Forecasting Demo (30 Days)")
    print("=" * 60)
    
    # Test products
    test_products = ["P001", "P005", "P009"]  # iPhone, Dell XPS, Sony Headphones
    
    for product_id in test_products:
        print(f"\n📱 Forecasting for Product {product_id}:")
        result = forecast_for_product(product_id, days=30)
        
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
            continue
            
        print(f"   📊 Product: {result['product_name']}")
        print(f"   💰 Current Avg Price: ₹{result['current_price_stats']['average']:,}")
        print(f"   🔮 Predicted Avg Price: ₹{result['forecast_summary']['average_predicted_price']:,}")
        print(f"   🎯 Best Deal Expected: ₹{result['forecast_summary']['best_predicted_price']:,} on {result['forecast_summary']['best_price_date']}")
        print(f"   📈 Price Trend: {result['forecast_summary']['price_trend']}")
        print(f"   💡 Potential Savings: ₹{result['forecast_summary']['potential_savings']:,}")
        
        # Show first 5 days of forecast
        print(f"   📅 Next 5 Days Preview:")
        for forecast in result['forecast'][:5]:
            conf_stars = "★" * int(forecast['confidence'] * 5)
            print(f"      {forecast['date']}: ₹{forecast['price']:,} (±₹{(forecast['upper'] - forecast['lower'])/2:.0f}) {conf_stars}")

if __name__ == "__main__":
    demo_advanced_forecast()