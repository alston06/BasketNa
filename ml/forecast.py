import os
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Try new dataset first, fallback to old one
NEW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "ecommerce_price_dataset.csv")
OLD_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "sample_prices.csv")
DATA_PATH = NEW_DATA_PATH if os.path.exists(NEW_DATA_PATH) else OLD_DATA_PATH
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "forecasts")
os.makedirs(OUTPUT_DIR, exist_ok=True)


@dataclass
class ForecastPoint:
	date: date
	price: float
	lower: float
	upper: float


def _prepare_series(df: pd.DataFrame, product_id: str) -> Optional[pd.DataFrame]:
	if df.empty:
		return None
	
	# Handle both old and new dataset formats
	if "price_inr" in df.columns:
		# New dataset format
		df = df[df["product_name"].str.contains("iPhone 16|Samsung Galaxy|Google Pixel|OnePlus|Dell XPS|Apple MacBook|HP Spectre|Lenovo Legion|Sony WH|Apple AirPods|Bose QuietComfort|JBL Flip|Apple Watch|Samsung Galaxy Watch|Samsung 55|LG C5|Sony PlayStation|Canon EOS|DJI Mini|Logitech MX", na=False)]
		if product_id == "P001":
			df = df[df["product_name"] == "iPhone 16"]
		elif product_id == "P002":
			df = df[df["product_name"] == "Samsung Galaxy S26 Ultra"]
		# Add more mappings as needed
		else:
			return None
		
		if df.empty:
			return None
		# Aggregate by date across retailers (mean price)
		agg = df.groupby("date", as_index=False)["price_inr"].mean()
		agg = agg.rename(columns={"price_inr": "price"})
	else:
		# Old dataset format
		df = df[df["product_id"] == product_id].copy()
		if df.empty:
			return None
		# Aggregate by date across sites (mean price)
		agg = df.groupby("date", as_index=False)["price"].mean()
	
	agg = agg.sort_values("date")
	return agg


def _fit_and_forecast(series: pd.DataFrame, horizon_days: int = 14) -> Tuple[list, list]:
	# Use day index as feature, simple linear regression baseline
	series = series.copy()
	series["date"] = pd.to_datetime(series["date"]).dt.date
	series["t"] = np.arange(len(series))
	X = series[["t"]].values
	y = series["price"].values
	model = LinearRegression().fit(X, y)
	pred = model.predict(X)
	residual_std = float(np.std(y - pred))

	last_t = int(series["t"].iloc[-1])
	future_t = np.arange(last_t + 1, last_t + horizon_days + 1)
	future_dates = [series["date"].iloc[-1] + timedelta(days=i) for i in range(1, horizon_days + 1)]
	future_pred = model.predict(future_t.reshape(-1, 1))

	z = 1.96  # ~95% interval
	lower_hist = pred - z * residual_std
	upper_hist = pred + z * residual_std
	lower_fut = future_pred - z * residual_std
	upper_fut = future_pred + z * residual_std

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


def _great_deal_flags(df: pd.DataFrame, product_id: str, current_price: float, forecast_lower0: Optional[float]) -> Tuple[bool, str]:
	prices = df[df["product_id"] == product_id]["price"].values
	if len(prices) == 0:
		return False, "No history"
	p10 = float(np.percentile(prices, 10))
	if current_price < p10:
		return True, f"Current price {current_price:.0f} < 10th percentile {p10:.0f}"
	if forecast_lower0 is not None and current_price < float(forecast_lower0):
		return True, f"Current price {current_price:.0f} < forecast lower bound {forecast_lower0:.0f}"
	return False, ""


def forecast_for_product(product_id: str):
	if not os.path.exists(DATA_PATH):
		return None
	df = pd.read_csv(DATA_PATH)
	df["date"] = pd.to_datetime(df["date"]).dt.date
	series = _prepare_series(df, product_id)
	if series is None or series.empty:
		return None
	history, forecast = _fit_and_forecast(series)
	product_name = df[df["product_id"] == product_id]["product_name"].iloc[0]
	latest_actual = df[df["product_id"] == product_id].sort_values("date").iloc[-1]["price"]
	forecast_lower0 = forecast[0]["lower"] if len(forecast) > 0 else None
	great_deal, reason = _great_deal_flags(df, product_id, float(latest_actual), forecast_lower0)

	# Save plot
	plt.figure(figsize=(10, 5))
	plt.title(f"{product_name} — Price History & 14-day Forecast")
	# History
	h_dates = [p["date"] for p in history]
	h_prices = [p["price"] for p in history]
	plt.plot(h_dates, h_prices, label="History (fit)", color="C0")
	plt.fill_between(h_dates, [p["lower"] for p in history], [p["upper"] for p in history], color="C0", alpha=0.2)
	# Forecast
	f_dates = [p["date"] for p in forecast]
	f_prices = [p["price"] for p in forecast]
	plt.plot(f_dates, f_prices, label="Forecast", color="C1")
	plt.fill_between(f_dates, [p["lower"] for p in forecast], [p["upper"] for p in forecast], color="C1", alpha=0.2)
	plt.xticks(rotation=45)
	plt.ylabel("Price (INR)")
	plt.legend()
	plt.tight_layout()
	out_path = os.path.join(OUTPUT_DIR, f"{product_id}.png")
	plt.savefig(out_path)
	plt.close()

	return {
		"product_id": product_id,
		"product_name": product_name,
		"history": history,
		"forecast": forecast,
		"great_deal": great_deal,
		"great_deal_reason": reason if great_deal else "",
	}


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description="Forecast product prices")
	parser.add_argument("product_id", type=str, help="Product ID, e.g., P001")
	args = parser.parse_args()
	result = forecast_for_product(args.product_id)
	if result is None:
		print("Product not found or dataset missing")
	else:
		print(f"Saved forecast plot to {os.path.join(OUTPUT_DIR, args.product_id + '.png')}") 