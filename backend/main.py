import os
from typing import List
from urllib.parse import quote_plus

import crud
import models
import pandas as pd
import schemas
# from agents.price_copilot import copilot_app  # Commented out due to missing pydantic_ai dependency
from auth import (
	create_access_token,
	get_current_user,
	get_db,
	get_password_hash,
	verify_password,
)

# Optional authentication dependency - commented out for now
# async def get_current_user_optional(db: Session = Depends(get_db)):
# 	"""Get current user if authenticated, otherwise return None"""
# 	try:
# 		from fastapi import Request
# 		# This would need to be implemented properly with request context
# 		# For now, we'll handle authentication in the endpoint
# 		return None
# 	except:
# 		return None
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
from agents.price_copilot import copilot_app  # Commented out due to missing pydantic_ai dependency

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

app.mount("/copilotkit_remote", copilot_app)  # Commented out due to missing pydantic_ai dependency



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


# ========== AI AGENT TOOLS INTEGRATION ==========

try:
    from agents.tools.tool_integration import tools_integration
    TOOLS_AVAILABLE = True
except ImportError:
    print("⚠️ AI agent tools not available - some endpoints will be disabled")
    TOOLS_AVAILABLE = False

# ========== NEW RECOMMENDATION ENDPOINTS ==========

from recommendation_engine import PriceRecommendationEngine
from personalized_recommendations import PersonalizedRecommendationEngine

# Initialize recommendation engines
recommendation_engine = PriceRecommendationEngine()
personalized_engine = PersonalizedRecommendationEngine()

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

# ========== PERSONALIZED RECOMMENDATION ENDPOINTS ==========

@app.get("/recommendations/personalized")
def get_personalized_recommendations(
	limit: int = Query(10, ge=1, le=20),
	current_user: models.User = Depends(get_current_user),
	db: Session = Depends(get_db)
):
	"""Get personalized product recommendations for authenticated user"""
	try:
		recommendation_set = personalized_engine.generate_product_recommendations(
			db=db, 
			user_id=current_user.id, 
			limit=limit
		)
		
		# Convert to response format
		recommendations = []
		for rec in recommendation_set.recommendations:
			recommendations.append({
				"product_id": rec.product_id,
				"product_name": rec.product_name,
				"category": rec.category,
				"current_price": rec.current_price,
				"best_retailer": rec.best_retailer,
				"description": rec.description,
				"score": round(rec.score, 3),
				"reasons": rec.reasons,
				"rating": rec.rating,
				"trending_score": round(rec.trending_score, 3),
				"price_trend": rec.price_trend,
				"potential_savings": rec.potential_savings,
				"website_url": rec.website_url,
				"all_retailer_links": rec.all_retailer_links
			})
		
		return {
			"status": "success",
			"user_id": current_user.id,
			"personalization_score": round(recommendation_set.personalization_score, 3),
			"total_recommendations": recommendation_set.total_count,
			"generated_at": recommendation_set.generated_at.isoformat(),
			"recommendations": recommendations
		}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error generating personalized recommendations: {str(e)}")

@app.get("/recommendations/session")
def get_session_recommendations(
	session_id: str = Query(..., description="Session ID for anonymous users"),
	limit: int = Query(10, ge=1, le=20),
	db: Session = Depends(get_db)
):
	"""Get personalized product recommendations for anonymous users based on session activity"""
	try:
		recommendation_set = personalized_engine.generate_product_recommendations(
			db=db,
			session_id=session_id,
			limit=limit
		)
		
		# Convert to response format
		recommendations = []
		for rec in recommendation_set.recommendations:
			recommendations.append({
				"product_id": rec.product_id,
				"product_name": rec.product_name,
				"category": rec.category,
				"current_price": rec.current_price,
				"best_retailer": rec.best_retailer,
				"description": rec.description,
				"score": round(rec.score, 3),
				"reasons": rec.reasons,
				"rating": rec.rating,
				"trending_score": round(rec.trending_score, 3),
				"price_trend": rec.price_trend,
				"potential_savings": rec.potential_savings,
				"website_url": rec.website_url,
				"all_retailer_links": rec.all_retailer_links
			})
		
		return {
			"status": "success",
			"session_id": session_id,
			"personalization_score": round(recommendation_set.personalization_score, 3),
			"total_recommendations": recommendation_set.total_count,
			"generated_at": recommendation_set.generated_at.isoformat(),
			"recommendations": recommendations
		}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error generating session recommendations: {str(e)}")

@app.post("/activity/view/{product_id}")
def record_product_view(
	product_id: str,
	session_id: str = Query(None, description="Session ID for anonymous users"),
	db: Session = Depends(get_db)
):
	"""Record a product view for recommendation personalization"""
	try:
		# For now, we'll only support session-based tracking for simplicity
		# In a full implementation, you'd extract user_id from JWT token if present
		user_id = None  # Would be extracted from Authorization header if present
		
		# Ensure the product exists in our database
		df = load_data()
		product_match = df[df["product_id"] == product_id]
		if product_match.empty:
			raise HTTPException(status_code=404, detail="Product not found")
		
		product_name = product_match.iloc[0]["product_name"]
		crud.ensure_product(db, product_id, str(product_name))
		
		# Record the view (requires either user_id or session_id)
		if not user_id and not session_id:
			raise HTTPException(status_code=400, detail="Either user authentication or session_id is required")
		
		view = crud.record_product_view(db, product_id, user_id, session_id)
		
		return {
			"status": "success",
			"message": "Product view recorded successfully",
			"view_id": view.id,
			"product_id": product_id,
			"user_id": user_id,
			"session_id": session_id
		}
		
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error recording product view: {str(e)}")

@app.get("/recommendations/category/{category}")
def get_category_recommendations(
	category: str,
	limit: int = Query(5, ge=1, le=10),
	exclude_products: List[str] = Query([], description="Product IDs to exclude")
):
	"""Get recommendations within a specific category"""
	try:
		df = load_data()
		
		# Get products in the specified category
		category_products = []
		for product_name, prod_category in personalized_engine.product_categories.items():
			if prod_category.lower() == category.lower():
				product_data = df[df['product_name'] == product_name]
				if not product_data.empty:
					# Get latest price
					latest_data = product_data[product_data['date'] == product_data['date'].max()]
					best_price_row = latest_data.loc[latest_data['price_inr'].idxmin()]
					
					# Calculate scores
					rating = personalized_engine.product_ratings.get(product_name, 4.0)
					trending_score = personalized_engine.calculate_trending_score(df, product_name)
					price_trend, potential_savings = personalized_engine.calculate_price_trend(df, product_name)
					
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
					
					if product_id not in exclude_products:
						# Generate website links
						website_url = build_site_search_url(str(best_price_row['retailer']), product_name)
						all_retailer_links = {}
						product_retailers = df[df['product_name'] == product_name]['retailer'].unique()
						for retailer in product_retailers:
							all_retailer_links[retailer] = build_site_search_url(retailer, product_name)
						
						category_products.append({
							"product_id": product_id,
							"product_name": product_name,
							"category": category,
							"current_price": float(best_price_row['price_inr']),
							"best_retailer": str(best_price_row['retailer']),
							"rating": rating,
							"trending_score": round(trending_score, 3),
							"price_trend": price_trend,
							"potential_savings": potential_savings,
							"score": rating / 5.0 + trending_score * 0.3,
							"website_url": website_url,
							"all_retailer_links": all_retailer_links
						})
		
		# Sort by score and return top recommendations
		category_products.sort(key=lambda x: x['score'], reverse=True)
		top_recommendations = category_products[:limit]
		
		return {
			"status": "success",
			"category": category,
			"total_found": len(category_products),
			"total_recommendations": len(top_recommendations),
			"recommendations": top_recommendations
		}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error getting category recommendations: {str(e)}")

@app.get("/recommendations/trending")
def get_trending_recommendations(
	limit: int = Query(10, ge=1, le=20)
):
	"""Get trending product recommendations based on price activity"""
	try:
		df = load_data()
		
		# Calculate trending scores for all products
		trending_products = []
		for product_name in personalized_engine.product_categories.keys():
			product_data = df[df['product_name'] == product_name]
			if not product_data.empty:
				trending_score = personalized_engine.calculate_trending_score(df, product_name)
				
				if trending_score > 0.1:  # Only include products with meaningful trending activity
					# Get current best price
					latest_data = product_data[product_data['date'] == product_data['date'].max()]
					best_price_row = latest_data.loc[latest_data['price_inr'].idxmin()]
					
					rating = personalized_engine.product_ratings.get(product_name, 4.0)
					category = personalized_engine.product_categories.get(product_name, "Electronics")
					price_trend, potential_savings = personalized_engine.calculate_price_trend(df, product_name)
					
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
					
					# Generate website links
					website_url = build_site_search_url(str(best_price_row['retailer']), product_name)
					all_retailer_links = {}
					product_retailers = df[df['product_name'] == product_name]['retailer'].unique()
					for retailer in product_retailers:
						all_retailer_links[retailer] = build_site_search_url(retailer, product_name)
					
					trending_products.append({
						"product_id": product_id,
						"product_name": product_name,
						"category": category,
						"current_price": float(best_price_row['price_inr']),
						"best_retailer": str(best_price_row['retailer']),
						"rating": rating,
						"trending_score": round(trending_score, 3),
						"price_trend": price_trend,
						"potential_savings": potential_savings,
						"description": f"Trending {category.lower()} with active price movements",
						"website_url": website_url,
						"all_retailer_links": all_retailer_links
					})
		
		# Sort by trending score
		trending_products.sort(key=lambda x: x['trending_score'], reverse=True)
		top_trending = trending_products[:limit]
		
		return {
			"status": "success",
			"total_trending": len(trending_products),
			"total_recommendations": len(top_trending),
			"trending_recommendations": top_trending
		}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error getting trending recommendations: {str(e)}") 


# ========== AI AGENT TOOLS ENDPOINTS ==========

@app.get("/ai-tools/coupons/{product_name}")
async def get_product_coupons(product_name: str):
	"""Get available coupons and deals for a specific product using AI agent tools"""
	if not TOOLS_AVAILABLE:
		raise HTTPException(status_code=503, detail="AI agent tools are not available")
	
	try:
		result = await tools_integration.get_product_coupons(product_name)
		return {
			"status": "success",
			"coupon_data": result
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error fetching coupons: {str(e)}")

@app.get("/ai-tools/reviews/{product_name}")
async def get_product_reviews_summary(product_name: str, site: str = Query("all", enum=["all", "amazon", "flipkart"])):
	"""Get AI-powered review summary and sentiment analysis for a product"""
	if not TOOLS_AVAILABLE:
		raise HTTPException(status_code=503, detail="AI agent tools are not available")
	
	try:
		result = await tools_integration.get_product_reviews_summary(product_name, site)
		return {
			"status": "success",
			"review_analysis": result
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error analyzing reviews: {str(e)}")

@app.get("/ai-tools/comprehensive/{product_name}")
async def get_comprehensive_product_analysis(product_name: str):
	"""Get comprehensive product analysis including coupons, reviews, and insights"""
	if not TOOLS_AVAILABLE:
		raise HTTPException(status_code=503, detail="AI agent tools are not available")
	
	try:
		result = await tools_integration.get_comprehensive_product_info(product_name)
		return {
			"status": "success",
			"comprehensive_analysis": result
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error performing comprehensive analysis: {str(e)}")

@app.get("/ai-tools/health")
async def check_ai_tools_health():
	"""Check the health and availability of AI agent tools"""
	return {
		"status": "healthy" if TOOLS_AVAILABLE else "unavailable",
		"tools_available": TOOLS_AVAILABLE,
		"available_endpoints": [
			"/ai-tools/coupons/{product_name}",
			"/ai-tools/reviews/{product_name}",
			"/ai-tools/comprehensive/{product_name}"
		] if TOOLS_AVAILABLE else [],
		"message": "AI agent tools are ready for use" if TOOLS_AVAILABLE else "AI agent tools require additional setup"
	}