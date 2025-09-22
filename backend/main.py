import os
import sys
from datetime import date, timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import pandas as pd
from urllib.parse import quote_plus

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.db import Base, engine
from backend import models, schemas, crud
from backend.auth import get_db, get_password_hash, verify_password, create_access_token, get_current_user

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Basketna API", version="0.1.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"http://localhost:5173", 
		"http://127.0.0.1:5173",
		"http://localhost:3000",  # React dev server
		"http://localhost:8081",  # Expo Metro
	],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
)

# Add CopilotKit integration with Gemini
try:
	from copilotkit.integrations.fastapi import add_fastapi_endpoint
	from backend.agents.price_copilot import copilot_kit
	
	add_fastapi_endpoint(app, copilot_kit, "/copilotkit")
	print("✅ CopilotKit endpoint added at /copilotkit with Google Gemini")
except Exception as e:
	print(f"⚠️ Failed to initialize CopilotKit: {e}")
	print("💡 Make sure GOOGLE_API_KEY is set and copilotkit is installed")

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sample_prices.csv"))


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
		raise HTTPException(status_code=500, detail="Sample dataset not found. Please generate data/sample_prices.csv")
	df = pd.read_csv(DATA_PATH)
	df["date"] = pd.to_datetime(df["date"]).dt.date
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
	latest_date = results.groupby(["product_id", "site"])['date'].transform('max')
	latest_rows = results[results['date'] == latest_date]
	items: List[schemas.SearchItem] = []
	for _, row in latest_rows.iterrows():
		url = build_site_search_url(str(row['site']), str(row['product_name']))
		items.append(schemas.SearchItem(
			product_id=row["product_id"],
			product_name=row["product_name"],
			site=row["site"],
			price=float(row["price"]),
			url=url,
		))
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


# ML/Forecast utilities
try:
	from ml.forecast import forecast_for_product as forecast_baseline
except Exception:
	forecast_baseline = None

try:
	from ml.forecast_holidays import forecast_for_product as forecast_holidays
except Exception:
	forecast_holidays = None


@app.get("/forecast/{product_id}", response_model=schemas.ForecastResponse)
def forecast(product_id: str, model: str = "baseline"):
	# choose model
	if model == "holidays" and forecast_holidays is not None:
		result = forecast_holidays(product_id)
		if result is not None:
			return result
	# fallback to baseline
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


@app.post("/forecast/train/{product_id}")
def train_model(product_id: str, model: str = Query("holidays", enum=["holidays"])):
	if model != "holidays":
		raise HTTPException(status_code=400, detail="Unsupported model")
	try:
		from ml.forecast_holidays import train_and_export
	except Exception:
		raise HTTPException(status_code=500, detail="Training utility not available")
	path = train_and_export(product_id)
	if path is None:
		raise HTTPException(status_code=404, detail="Product not found or no data")
	return {"status": "ok", "model_path": path}


@app.get("/forecast/{product_id}/saved", response_model=schemas.ForecastResponse)
def forecast_saved(product_id: str):
	try:
		from ml.forecast_holidays import load_and_forecast
	except Exception:
		raise HTTPException(status_code=500, detail="Load utility not available")
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