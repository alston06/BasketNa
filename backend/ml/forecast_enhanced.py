"""
Updated ML Forecast Model for E-commerce Price Dataset
Adapted to work with the synthetic dataset generated for Indian e-commerce price tracking
"""

import os
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Optional, Tuple

import matplotlib

matplotlib.use('Agg')
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

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
        "Samsung Galaxy Watch 7": "P014",
        "Samsung 55-inch QLED TV": "P015",
        "LG C5 65-inch OLED TV": "P016",
        "Sony PlayStation 5 Pro": "P017",
        "Canon EOS R7 Camera": "P018",
        "DJI Mini 5 Pro Drone": "P019",
        "Logitech MX Master 4 Mouse": "P020"
    }
    
    df["product_id"] = df["product_name"].map(product_mapping)
    df["site"] = df["retailer"]  # Rename for compatibility
    
    return df


def get_available_products() -> Dict[str, str]:
    """Get list of available products with their IDs and names"""
    try:
        df = load_dataset()
        product_map = dict(zip(df["product_id"], df["product_name"]))
        return product_map
    except:
        return {}


def _prepare_series(df: pd.DataFrame, product_id: str, retailer: str = None) -> Optional[pd.DataFrame]:
    """Prepare time series data for a specific product, optionally for a specific retailer"""
    if df.empty:
        return None
    
    product_df = df[df["product_id"] == product_id].copy()
    if product_df.empty:
        return None
    
    if retailer:
        # Filter for specific retailer
        product_df = product_df[product_df["retailer"] == retailer]
        if product_df.empty:
            return None
        agg = product_df.groupby("date", as_index=False)["price_inr"].mean()
    else:
        # Aggregate across all retailers (mean price per day)
        agg = product_df.groupby("date", as_index=False)["price_inr"].mean()
    
    agg = agg.sort_values("date")
    agg = agg.rename(columns={"price_inr": "price"})
    
    return agg


def _advanced_forecast(series: pd.DataFrame, horizon_days: int = 14) -> Tuple[list, list]:
    """Enhanced forecasting with trend detection and seasonality awareness"""
    series = series.copy()
    series["date"] = pd.to_datetime(series["date"]).dt.date
    series["t"] = np.arange(len(series))
    
    # Create additional features
    series["day_of_year"] = pd.to_datetime(series["date"]).dt.dayofyear
    series["month"] = pd.to_datetime(series["date"]).dt.month
    series["quarter"] = pd.to_datetime(series["date"]).dt.quarter
    
    # Detect if we're in a sale period (rapid price drops)
    series["price_change"] = series["price"].pct_change().fillna(0)
    series["is_sale_period"] = (series["price_change"] < -0.1).astype(int)
    
    # Use multiple features for prediction
    feature_cols = ["t", "day_of_year", "month", "quarter", "is_sale_period"]
    X = series[feature_cols].values
    y = series["price"].values
    
    # Use Random Forest for better handling of non-linear patterns
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Get predictions with uncertainty
    pred = model.predict(X)
    
    # Calculate residual-based uncertainty
    residuals = y - pred
    residual_std = float(np.std(residuals))
    
    # Future predictions
    last_t = int(series["t"].iloc[-1])
    future_dates = [series["date"].iloc[-1] + timedelta(days=i) for i in range(1, horizon_days + 1)]
    
    future_features = []
    for i, future_date in enumerate(future_dates):
        future_dt = pd.to_datetime(future_date)
        future_features.append([
            last_t + i + 1,  # t
            future_dt.dayofyear,  # day_of_year
            future_dt.month,  # month
            future_dt.quarter,  # quarter
            0  # assume no sale period in future (conservative)
        ])
    
    future_X = np.array(future_features)
    future_pred = model.predict(future_X)
    
    # Calculate confidence intervals
    z = 1.96  # ~95% interval
    
    # Historical intervals
    lower_hist = pred - z * residual_std
    upper_hist = pred + z * residual_std
    
    # Future intervals (wider due to uncertainty)
    uncertainty_growth = np.linspace(1, 1.5, horizon_days)  # Growing uncertainty
    lower_fut = future_pred - z * residual_std * uncertainty_growth
    upper_fut = future_pred + z * residual_std * uncertainty_growth
    
    history = [
        {
            "date": d,
            "price": float(p),
            "lower": float(l),
            "upper": float(u),
        }
        for d, p, l, u in zip(series["date"].tolist(), pred.tolist(), lower_hist.tolist(), upper_hist.tolist())
    ]
    
    forecast = [
        {
            "date": d,
            "price": float(p),
            "lower": float(l),
            "upper": float(u),
        }
        for d, p, l, u in zip(future_dates, future_pred.tolist(), lower_fut.tolist(), upper_fut.tolist())
    ]
    
    return history, forecast


def _enhanced_deal_detection(df: pd.DataFrame, product_id: str, current_price: float, forecast_data: list) -> Tuple[bool, str]:
    """Enhanced deal detection with multiple criteria"""
    product_prices = df[df["product_id"] == product_id]["price_inr"].values
    
    if len(product_prices) == 0:
        return False, "No price history available"
    
    # Multiple deal detection criteria
    p5 = float(np.percentile(product_prices, 5))
    p10 = float(np.percentile(product_prices, 10))
    p25 = float(np.percentile(product_prices, 25))
    recent_avg = float(np.mean(product_prices[-30:]))  # Last 30 days average
    
    deal_reasons = []
    
    # Criterion 1: Historical percentiles
    if current_price < p5:
        deal_reasons.append(f"Price ₹{current_price:,.0f} is in bottom 5% (below ₹{p5:,.0f})")
    elif current_price < p10:
        deal_reasons.append(f"Price ₹{current_price:,.0f} is in bottom 10% (below ₹{p10:,.0f})")
    
    # Criterion 2: Recent price comparison
    if current_price < recent_avg * 0.85:  # 15% below recent average
        deal_reasons.append(f"Price ₹{current_price:,.0f} is 15%+ below recent average (₹{recent_avg:,.0f})")
    
    # Criterion 3: Forecast comparison
    if len(forecast_data) > 0:
        forecast_lower0 = forecast_data[0]["lower"]
        if current_price < forecast_lower0:
            deal_reasons.append(f"Price ₹{current_price:,.0f} is below forecast lower bound (₹{forecast_lower0:,.0f})")
    
    # Criterion 4: Retailer comparison (if multiple retailers have data)
    latest_date = df["date"].max()
    latest_day_prices = df[(df["product_id"] == product_id) & (df["date"] == latest_date)]["price_inr"].values
    if len(latest_day_prices) > 1:
        min_competitor_price = float(np.min(latest_day_prices[latest_day_prices != current_price]))
        if current_price < min_competitor_price * 0.95:  # 5% cheaper than cheapest competitor
            deal_reasons.append(f"Price ₹{current_price:,.0f} is 5%+ cheaper than competitors (₹{min_competitor_price:,.0f})")
    
    is_deal = len(deal_reasons) > 0
    reason = "; ".join(deal_reasons) if is_deal else ""
    
    return is_deal, reason


def forecast_for_product(product_id: str, retailer: str = None, horizon_days: int = 14):
    """Generate forecast for a specific product, optionally for a specific retailer"""
    try:
        df = load_dataset()
    except FileNotFoundError:
        return {"error": "Dataset not found. Please ensure ecommerce_price_dataset_corrected.csv exists in the data folder."}
    
    # Get product info
    product_df = df[df["product_id"] == product_id]
    if product_df.empty:
        available_products = get_available_products()
        return {
            "error": f"Product {product_id} not found", 
            "available_products": available_products
        }
    
    product_name = product_df["product_name"].iloc[0]
    
    # Prepare time series
    series = _prepare_series(df, product_id, retailer)
    if series is None or len(series) < 7:  # Need at least a week of data
        return {"error": f"Insufficient data for product {product_id}"}
    
    # Generate forecast
    history, forecast = _advanced_forecast(series, horizon_days)
    
    # Get latest actual price
    if retailer:
        latest_prices = df[(df["product_id"] == product_id) & (df["retailer"] == retailer)]
    else:
        latest_prices = df[df["product_id"] == product_id]
    
    latest_actual = float(latest_prices.sort_values("date").iloc[-1]["price_inr"])
    
    # Deal detection
    is_great_deal, deal_reason = _enhanced_deal_detection(df, product_id, latest_actual, forecast)
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    retailer_suffix = f" ({retailer})" if retailer else " (All Retailers Avg)"
    plt.title(f"{product_name}{retailer_suffix} — Price History & {horizon_days}-day Forecast", fontsize=14, pad=20)
    
    # Historical data
    h_dates = [p["date"] for p in history]
    h_prices = [p["price"] for p in history]
    h_lower = [p["lower"] for p in history]
    h_upper = [p["upper"] for p in history]
    
    plt.plot(h_dates, h_prices, label="Historical Fit", color="navy", linewidth=2)
    plt.fill_between(h_dates, h_lower, h_upper, color="navy", alpha=0.2, label="Historical Confidence")
    
    # Forecast data
    f_dates = [p["date"] for p in forecast]
    f_prices = [p["price"] for p in forecast]
    f_lower = [p["lower"] for p in forecast]
    f_upper = [p["upper"] for p in forecast]
    
    plt.plot(f_dates, f_prices, label="Forecast", color="darkorange", linewidth=2, linestyle="--")
    plt.fill_between(f_dates, f_lower, f_upper, color="darkorange", alpha=0.3, label="Forecast Confidence")
    
    # Highlight current price
    plt.axhline(y=latest_actual, color="red", linestyle=":", alpha=0.7, label=f"Current Price: ₹{latest_actual:,.0f}")
    
    # Formatting
    plt.xticks(rotation=45)
    plt.ylabel("Price (₹)", fontsize=12)
    plt.xlabel("Date", fontsize=12)
    plt.legend(loc="upper right")
    plt.grid(True, alpha=0.3)
    
    # Add deal indicator
    if is_great_deal:
        plt.text(0.02, 0.98, "🔥 GREAT DEAL!", transform=plt.gca().transAxes, 
                fontsize=12, fontweight='bold', color='red', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                verticalalignment='top')
    
    plt.tight_layout()
    
    # Save plot
    filename_suffix = f"_{retailer}" if retailer else "_all_retailers"
    out_path = os.path.join(OUTPUT_DIR, f"{product_id}{filename_suffix}.png")
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Calculate price trends
    recent_trend = "stable"
    if len(h_prices) >= 7:
        recent_change = (h_prices[-1] - h_prices[-7]) / h_prices[-7] * 100
        if recent_change > 5:
            recent_trend = "increasing"
        elif recent_change < -5:
            recent_trend = "decreasing"
    
    return {
        "product_id": product_id,
        "product_name": product_name,
        "retailer": retailer or "All Retailers (Average)",
        "current_price": latest_actual,
        "history": history,
        "forecast": forecast,
        "great_deal": is_great_deal,
        "great_deal_reason": deal_reason,
        "recent_trend": recent_trend,
        "forecast_plot": out_path,
        "data_points": len(series),
        "forecast_horizon_days": horizon_days
    }


def get_retailer_comparison(product_id: str, date_str: str = None):
    """Compare prices across all retailers for a specific product on a given date"""
    try:
        df = load_dataset()
    except FileNotFoundError:
        return {"error": "Dataset not found"}
    
    if date_str is None:
        # Use latest date
        target_date = df["date"].max()
    else:
        target_date = pd.to_datetime(date_str).date()
    
    product_data = df[(df["product_id"] == product_id) & (df["date"] == target_date)]
    
    if product_data.empty:
        return {"error": f"No data found for product {product_id} on {target_date}"}
    
    product_name = product_data["product_name"].iloc[0]
    
    retailer_prices = []
    for _, row in product_data.iterrows():
        retailer_prices.append({
            "retailer": row["retailer"],
            "price": float(row["price_inr"]),
            "formatted_price": f"₹{row['price_inr']:,.2f}"
        })
    
    # Sort by price
    retailer_prices.sort(key=lambda x: x["price"])
    
    # Find best deal
    best_price = retailer_prices[0]["price"]
    for rp in retailer_prices:
        rp["is_best_deal"] = rp["price"] == best_price
        if rp["price"] > best_price:
            savings = rp["price"] - best_price
            rp["potential_savings"] = f"₹{savings:,.2f}"
    
    return {
        "product_id": product_id,
        "product_name": product_name,
        "date": str(target_date),
        "retailer_prices": retailer_prices,
        "best_price": best_price,
        "best_retailer": retailer_prices[0]["retailer"]
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Price Forecasting for E-commerce Dataset")
    parser.add_argument("product_id", type=str, help="Product ID, e.g., P001")
    parser.add_argument("--retailer", type=str, help="Specific retailer (Amazon.in, Flipkart, RelianceDigital, Croma)")
    parser.add_argument("--horizon", type=int, default=14, help="Forecast horizon in days (default: 14)")
    parser.add_argument("--compare", action="store_true", help="Show retailer price comparison")
    
    args = parser.parse_args()
    
    if args.compare:
        result = get_retailer_comparison(args.product_id)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("\n=== RETAILER PRICE COMPARISON ===")
            print(f"Product: {result['product_name']}")
            print(f"Date: {result['date']}")
            print("\nPrices by Retailer:")
            for rp in result["retailer_prices"]:
                marker = "🏆 BEST DEAL" if rp["is_best_deal"] else f"(Save {rp.get('potential_savings', '₹0')})"
                print(f"  {rp['retailer']:20} {rp['formatted_price']:>12} {marker}")
    else:
        result = forecast_for_product(args.product_id, args.retailer, args.horizon)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            if "available_products" in result:
                print("\nAvailable products:")
                for pid, pname in result["available_products"].items():
                    print(f"  {pid}: {pname}")
        else:
            print("\n=== PRICE FORECAST RESULTS ===")
            print(f"Product: {result['product_name']} ({result['product_id']})")
            print(f"Retailer: {result['retailer']}")
            print(f"Current Price: ₹{result['current_price']:,.2f}")
            print(f"Recent Trend: {result['recent_trend'].title()}")
            print(f"Data Points: {result['data_points']}")
            
            if result['great_deal']:
                print("\n🔥 GREAT DEAL DETECTED!")
                print(f"Reason: {result['great_deal_reason']}")
            
            print(f"\nForecast saved to: {result['forecast_plot']}")
            
            # Show next few days forecast
            print(f"\n=== {result['forecast_horizon_days']}-DAY FORECAST ===")
            for i, fp in enumerate(result['forecast'][:7]):  # Show first week
                print(f"{fp['date']}: ₹{fp['price']:7,.0f} (₹{fp['lower']:,.0f} - ₹{fp['upper']:,.0f})")
            if len(result['forecast']) > 7:
                print(f"... and {len(result['forecast']) - 7} more days")