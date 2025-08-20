import os
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
import holidays
import joblib

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "sample_prices.csv")
EVENTS_PATH = os.path.join(PROJECT_ROOT, "data", "events.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "forecasts")
MODEL_DIR = os.path.join(PROJECT_ROOT, "data", "models")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


@dataclass
class ForecastPoint:
	date: date
	price: float
	lower: float
	upper: float


def _prepare_series(df: pd.DataFrame, product_id: str) -> Optional[pd.DataFrame]:
	if df.empty:
		return None
	df = df[df["product_id"] == product_id].copy()
	if df.empty:
		return None
	# Aggregate by date across sites (mean price)
	agg = df.groupby("date", as_index=False)["price"].mean()
	agg = agg.sort_values("date")
	agg["date"] = pd.to_datetime(agg["date"]).dt.date
	return agg


def _load_events() -> pd.DataFrame:
	if not os.path.exists(EVENTS_PATH):
		return pd.DataFrame(columns=["date", "event", "weight"])  # empty
	df = pd.read_csv(EVENTS_PATH)
	df["date"] = pd.to_datetime(df["date"]).dt.date
	if "weight" not in df.columns:
		df["weight"] = 1.0
	return df[["date", "weight"]]


def _build_design(dates: List[date], events_df: pd.DataFrame):
	# Calendar features
	dow = np.array([d.weekday() for d in dates])  # 0=Mon
	month = np.array([pd.to_datetime(d).month for d in dates])
	t = np.arange(len(dates))
	# One-hot for day-of-week and month (to keep simple)
	dow_oh = np.eye(7)[dow]
	month_oh = np.eye(12)[month - 1]
	# Holidays India
	in_holidays = holidays.country_holidays('IN')
	hol = np.array([1 if d in in_holidays else 0 for d in dates]).reshape(-1, 1)
	# Events weight
	event_weight = np.array([float(events_df[events_df["date"] == d]["weight"].sum()) if not events_df.empty else 0.0 for d in dates]).reshape(-1, 1)
	# Trend terms
	trend = t.reshape(-1, 1)
	trend2 = (t**2).reshape(-1, 1)
	X = np.hstack([trend, trend2, dow_oh, month_oh, hol, event_weight])
	return X


def _fit(series: pd.DataFrame, events_df: pd.DataFrame):
	dates = series["date"].tolist()
	X = _build_design(dates, events_df)
	y = series["price"].values
	model = Ridge(alpha=1.0).fit(X, y)
	pred = model.predict(X)
	residual_std = float(np.std(y - pred))
	return model, residual_std


def _predict(model: Ridge, residual_std: float, dates: List[date], events_df: pd.DataFrame):
	X = _build_design(dates, events_df)
	pred = model.predict(X)
	z = 1.96
	lower = pred - z * residual_std
	upper = pred + z * residual_std
	return pred, lower, upper


def train_and_export(product_id: str) -> Optional[str]:
	if not os.path.exists(DATA_PATH):
		return None
	df = pd.read_csv(DATA_PATH)
	df["date"] = pd.to_datetime(df["date"]).dt.date
	series = _prepare_series(df, product_id)
	if series is None or series.empty:
		return None
	events_df = _load_events()
	model, residual_std = _fit(series, events_df)
	out_path = os.path.join(MODEL_DIR, f"{product_id}_holidays_model.joblib")
	joblib.dump({
		"model": model,
		"residual_std": residual_std,
		"last_date": series["date"].iloc[-1],
	}, out_path)
	return out_path


def load_and_forecast(product_id: str, horizon_days: int = 14):
	model_path = os.path.join(MODEL_DIR, f"{product_id}_holidays_model.joblib")
	if not os.path.exists(model_path):
		return None
	bundle = joblib.load(model_path)
	model: Ridge = bundle["model"]
	residual_std: float = float(bundle["residual_std"])
	last_date: date = bundle["last_date"]
	future_dates = [last_date + timedelta(days=i) for i in range(1, horizon_days + 1)]
	events_df = _load_events()
	pred, lower, upper = _predict(model, residual_std, future_dates, events_df)
	forecast = [
		{"date": d, "price": float(p), "lower": float(l), "upper": float(u)}
		for d, p, l, u in zip(future_dates, pred.tolist(), lower.tolist(), upper.tolist())
	]
	return forecast


def _great_deal_flags(df: pd.DataFrame, product_id: str, current_price: float, forecast_lower0: Optional[float]) -> (bool, str):
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
	events_df = _load_events()
	history, forecast = _fit_and_forecast(series, events_df)
	product_name = df[df["product_id"] == product_id]["product_name"].iloc[0]
	latest_actual = df[df["product_id"] == product_id].sort_values("date").iloc[-1]["price"]
	forecast_lower0 = forecast[0]["lower"] if len(forecast) > 0 else None
	great_deal, reason = _great_deal_flags(df, product_id, float(latest_actual), forecast_lower0)

	# Plot
	plt.figure(figsize=(10, 5))
	plt.title(f"{product_name} — Holiday-aware Forecast (14d)")
	h_dates = [p["date"] for p in history]
	h_prices = [p["price"] for p in history]
	plt.plot(h_dates, h_prices, label="History (fit)", color="C0")
	plt.fill_between(h_dates, [p["lower"] for p in history], [p["upper"] for p in history], color="C0", alpha=0.2)
	f_dates = [p["date"] for p in forecast]
	f_prices = [p["price"] for p in forecast]
	plt.plot(f_dates, f_prices, label="Forecast", color="C1")
	plt.fill_between(f_dates, [p["lower"] for p in forecast], [p["upper"] for p in forecast], color="C1", alpha=0.2)
	plt.xticks(rotation=45)
	plt.ylabel("Price (INR)")
	plt.legend()
	plt.tight_layout()
	out_path = os.path.join(OUTPUT_DIR, f"{product_id}_holidays.png")
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
	parser = argparse.ArgumentParser(description="Holiday-aware forecast")
	parser.add_argument("product_id", type=str)
	args = parser.parse_args()
	res = forecast_for_product(args.product_id)
	if res is None:
		print("Product not found or dataset missing")
	else:
		print("Saved plot with holiday-aware forecast.") 