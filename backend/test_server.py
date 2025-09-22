import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Simple test to see if basic FastAPI works
app = FastAPI(title="Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/search")
async def search(query: str):
    return {
        "query": query,
        "items": [
            {
                "product_id": "P001",
                "product_name": f"Test {query} Product",
                "site": "Amazon",
                "price": 500,
                "url": "https://amazon.in"
            }
        ],
        "best_price": {
            "product_id": "P001", 
            "product_name": f"Test {query} Product",
            "site": "Amazon",
            "price": 500,
            "url": "https://amazon.in"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)