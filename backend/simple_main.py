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
		"http://localhost:5176",  # Current Vite server
	],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
)

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "ecommerce_price_dataset.csv"))

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
		raise HTTPException(status_code=500, detail="E-commerce dataset not found. Please generate data/ecommerce_price_dataset.csv")
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

@app.get("/")
def root():
	return {"message": "Basketna API with Enhanced Dataset", "version": "0.2.0"}

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

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="127.0.0.1", port=8003)