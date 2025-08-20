import os, sys
# Ensure project root is on sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def main():
	# search
	r = client.get("/search", params={"query": "iphone"})
	print("/search status:", r.status_code)
	print(r.json())
	# forecast for P001
	r2 = client.get("/forecast/P001")
	print("/forecast status:", r2.status_code)
	print("forecast keys:", list(r2.json().keys()))

if __name__ == "__main__":
	main() 