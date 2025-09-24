import os
from typing import List
from urllib.parse import quote_plus

import crud
import models
import pandas as pd
import schemas
from agents.price_copilot import copilot_app
from auth import (
	create_access_token,
	get_current_user,
	get_db,
	get_password_hash,
	verify_password,
)
from db import Base, engine
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from ml.forecast import forecast_for_product as forecast_baseline
from ml.forecast_enhanced import forecast_for_product as forecast_enhanced
from ml.forecast_enhanced import get_retailer_comparison
from ml.forecast_holidays import forecast_for_product as forecast_holidays
from ml.forecast_holidays import load_and_forecast, train_and_export
from sqlalchemy.orm import Session

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Basketna API", version="0.1.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"http://localhost:5173", 
  "http://localhost:5174",
		"http://127.0.0.1:5173",
		"http://localhost:3000",  # React dev server
		"http://localhost:8081",  # Expo Metro
	],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
)

app.mount("/copilotkit_remote", copilot_app)



# Data loading path
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "ecommerce_price_dataset_corrected.csv"))


def build_site_search_url(site: str, product_name: str) -> str:
	s = site.lower()
	q = quote_plus(product_name)
	if "amazon" in s:
		return f"https://www.amazon.in/s?k={q}"
	if "flipkart" in s:
		return f"https://www.flipkart.com/search?q={q}"
	if "reliance" in s:
		return f"https://www.reliancedigital.in/search?q={q}"
	if "croma" in s:
		return f"https://www.croma.com/search/?text={q}"
	return f"https://www.google.com/search?q={quote_plus(site + ' ' + product_name)}"


def load_data() -> pd.DataFrame:
	if not os.path.exists(DATA_PATH):
		raise HTTPException(status_code=500, detail="E-commerce dataset not found. Please generate data/ecommerce_price_dataset_corrected.csv")
	df = pd.read_csv(DATA_PATH)
	df["date"] = pd.to_datetime(df["date"]).dt.date
	
	# Handle new dataset format - create product_id mapping and rename columns for compatibility
	if "price_inr" in df.columns:
		# Create product_id mapping for the new dataset
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
		
		# Add product_id column
		df["product_id"] = df["product_name"].map(product_mapping)
		
		# Rename columns for compatibility with existing API
		df["price"] = df["price_inr"]
		df["site"] = df["retailer"]
		
		# Remove rows without product_id mapping (shouldn't happen with our dataset)
		df = df.dropna(subset=["product_id"])
	
	return df


@app.post("/user/signup", response_model=schemas.UserOut)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
	if crud.get_user_by_email(db, payload.email):
		raise HTTPException(status_code=400, detail="Email already registered")
	hashed = get_password_hash(payload.password)
	user = crud.create_user(db, payload.email, hashed)
	return user


@app.post("/user/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	user = crud.get_user_by_email(db, form_data.username)
	if not user or not verify_password(form_data.password, user.hashed_password):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
	token = create_access_token({"sub": str(user.id)})
	return {"access_token": token, "token_type": "bearer"}


@app.get("/search", response_model=schemas.SearchResponse)
def search(query: str):
	df = load_data()
	mask = df["product_name"].str.contains(query, case=False, na=False)
	results = df[mask]
	if results.empty:
		return {"query": query, "items": [], "best_price": None}
	
	# Get latest prices for each product-site combination
	latest_date = results.groupby(["product_id", "site"])['date'].transform('max')
	latest_rows = results[results['date'] == latest_date].copy()
	
	items: List[schemas.SearchItem] = []
	for _, row in latest_rows.iterrows():
		url = build_site_search_url(str(row['site']), str(row['product_name']))
		items.append(schemas.SearchItem(
			product_id=str(row["product_id"]),
			product_name=str(row["product_name"]),
			site=str(row["site"]),
			price=float(row["price"]),
			url=url,
		))
	
	# Find best price
	best = min(items, key=lambda x: x.price) if items else None
	return {"query": query, "items": items, "best_price": best}


@app.post("/track/{product_id}", response_model=schemas.TrackOut)
def track(product_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
	df = load_data()
	matches = df[df["product_id"] == product_id]
	if matches.empty:
		raise HTTPException(status_code=404, detail="Product not found")
	name = matches.iloc[0]["product_name"]
	crud.ensure_product(db, product_id, str(name))
	tracked = crud.add_tracked_item(db, current_user.id, product_id)
	return tracked




@app.get("/forecast/{product_id}", response_model=schemas.ForecastResponse)
def forecast(product_id: str, model: str = "enhanced", retailer: str = None):
	# Try enhanced model first (preferred for new dataset)
	if model == "enhanced" and forecast_enhanced is not None:
		result = forecast_enhanced(product_id, retailer)
		if result is not None and "error" not in result:
			return result
	
	# Try holidays model
	if model == "holidays" and forecast_holidays is not None:
		result = forecast_holidays(product_id)
		if result is not None:
			return result
	
	# Fallback to baseline
	if forecast_baseline is None:
		raise HTTPException(status_code=500, detail="Forecasting module not available")
	result = forecast_baseline(product_id)
	if result is None:
		raise HTTPException(status_code=404, detail="Product not found")
	return result


@app.get("/me/tracked", response_model=List[schemas.TrackedItemPublic])
def list_my_tracked(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
	rows = crud.list_tracked_with_products(db, current_user.id)
	return [
		{
			"id": r[0],
			"product_id": r[1],
			"product_name": r[2],
			"created_at": r[3],
		}
		for r in rows
	]


@app.get("/compare/{product_id}")
def compare_retailers(product_id: str, date_str: str = None):
	"""Compare prices across all retailers for a specific product"""
	try:
		result = get_retailer_comparison(product_id, date_str)
		if "error" in result:
			raise HTTPException(status_code=404, detail=result["error"])
		return result
	except ImportError:
		raise HTTPException(status_code=500, detail="Retailer comparison not available")
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@app.post("/forecast/train/{product_id}")
def train_model(product_id: str, model: str = Query("holidays", enum=["holidays"])):
	if model != "holidays":
		raise HTTPException(status_code=400, detail="Unsupported model")


	path = train_and_export(product_id)
	if path is None:
		raise HTTPException(status_code=404, detail="Product not found or no data")
	return {"status": "ok", "model_path": path}


@app.get("/forecast/{product_id}/saved", response_model=schemas.ForecastResponse)
def forecast_saved(product_id: str):
	forecast = load_and_forecast(product_id)
	if forecast is None:
		raise HTTPException(status_code=404, detail="Saved model not found. Train first.")
	# Compose response with current price
	df = load_data()
	matches = df[df["product_id"] == product_id]
	if matches.empty:
		raise HTTPException(status_code=404, detail="Product not found")
	product_name = matches.iloc[0]["product_name"]
	latest_actual = float(matches.sort_values("date").iloc[-1]["price"])
	lower0 = forecast[0]["lower"] if len(forecast) > 0 else None
	great_deal = False
	reason = ""
	if lower0 is not None and latest_actual < float(lower0):
		great_deal = True
		reason = f"Current price {latest_actual:.0f} < forecast lower bound {lower0:.0f}"
	return {
		"product_id": product_id,
		"product_name": product_name,
		"history": [],
		"forecast": forecast,
		"great_deal": great_deal,
		"great_deal_reason": reason,
	}


# ========== NEW RECOMMENDATION ENDPOINTS ==========

from recommendation_engine import PriceRecommendationEngine

# Initialize recommendation engine
recommendation_engine = PriceRecommendationEngine()

@app.get("/recommendations/best-deals")
def get_best_deals(top_n: int = Query(10, ge=1, le=50)):
	"""Get current best deals across all retailers"""
	try:
		deals = recommendation_engine.get_current_best_deals(top_n)
		return {
			"status": "success",
			"count": len(deals),
			"best_deals": deals
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error fetching best deals: {str(e)}")

@app.get("/recommendations/buy-wait")
def get_buy_wait_recommendations(days_ahead: int = Query(30, ge=1, le=30)):
	"""Get buy now vs wait recommendations based on price forecasts"""
	try:
		recommendations = recommendation_engine.get_buy_recommendations(days_ahead)
		return {
			"status": "success",
			"forecast_days": days_ahead,
			"count": len(recommendations),
			"recommendations": recommendations
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/forecast/30-day")
def get_30_day_forecast(product_name: str = Query(None)):
	"""Get 30-day price forecast for all products or specific product"""
	try:
		forecast = recommendation_engine.get_30_day_forecast(product_name)
		return {
			"status": "success",
			"product_filter": product_name,
			"forecast_days": 30,
			"count": len(forecast),
			"forecast": forecast
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error fetching forecast: {str(e)}")

@app.get("/forecast/enhanced/{product_name}")
def get_enhanced_forecast(product_name: str, retailer: str = Query(None), days: int = Query(30, ge=1, le=30)):
	"""Get enhanced price forecast with market insights and confidence intervals"""
	try:
		from enhanced_forecast import EnhancedPriceForecast
		forecaster = EnhancedPriceForecast()
		result = forecaster.generate_enhanced_forecast(product_name, retailer, days)
		
		if "error" in result:
			raise HTTPException(status_code=404, detail=result["error"])
			
		return {
			"status": "success",
			"enhanced_forecast": result
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error generating enhanced forecast: {str(e)}")

@app.get("/analysis/competitive/{product_name}")
def get_competitive_analysis(product_name: str):
	"""Get competitive analysis across all retailers for a product"""
	try:
		from enhanced_forecast import EnhancedPriceForecast
		forecaster = EnhancedPriceForecast()
		result = forecaster.get_competitive_analysis(product_name)
		
		if "error" in result:
			raise HTTPException(status_code=404, detail=result["error"])
			
		return {
			"status": "success",
			"competitive_analysis": result
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error generating competitive analysis: {str(e)}")

@app.get("/analysis/price-trend/{product_name}")
def get_price_trend_analysis(product_name: str, days_back: int = Query(30, ge=7, le=90)):
	"""Get detailed price trend analysis for a specific product"""
	try:
		analysis = recommendation_engine.get_price_trend_analysis(product_name, days_back)
		if "error" in analysis:
			raise HTTPException(status_code=404, detail=analysis["error"])
		return {
			"status": "success",
			"analysis": analysis
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error analyzing price trends: {str(e)}")

@app.get("/products/available")
def get_available_products():
	"""Get list of all available products in the dataset"""
	try:
		df = load_data()
		products = df['product_name'].unique().tolist()
		return {
			"status": "success",
			"count": len(products),
			"products": sorted(products)
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}") 