import os
import random
from datetime import datetime, timedelta
import csv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_CSV = os.path.join(DATA_DIR, "sample_prices.csv")
os.makedirs(DATA_DIR, exist_ok=True)

products = [
	{"id": "P001", "name": "Apple iPhone 14 128GB" , "base": 57999},
	{"id": "P002", "name": "Samsung Galaxy S23 128GB", "base": 54999},
	{"id": "P003", "name": "OnePlus 11R 256GB", "base": 39999},
	{"id": "P004", "name": "Sony WH-1000XM5 Headphones", "base": 29999},
	{"id": "P005", "name": "Apple MacBook Air M2 8GB/256GB", "base": 99999},
]

sites = ["Amazon", "Flipkart", "Reliance Digital", "Croma"]

random.seed(42)

def gen_prices(base, day_idx):
	trend = (random.random() - 0.5) * 50  # small daily drift
	season = 200 * (1 if (day_idx % 7) in (5, 6) else 0)  # weekend bump
	noise = random.gauss(0, base * 0.01)
	return max(1000, base + trend + season + noise)

start_date = datetime.today().date() - timedelta(days=30)
rows = []
for p in products:
	for d in range(30):
		cur_date = start_date + timedelta(days=d)
		for site in sites:
			price = gen_prices(p["base"], d) * random.uniform(0.98, 1.02)
			rows.append([
				p["id"],
				p["name"],
				cur_date.isoformat(),
				site,
				round(price, 2),
			])

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
	writer = csv.writer(f)
	writer.writerow(["product_id", "product_name", "date", "site", "price"])
	writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}") 