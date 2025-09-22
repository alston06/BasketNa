from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
	email: EmailStr
	password: str


class UserLogin(BaseModel):
	email: EmailStr
	password: str


class UserOut(BaseModel):
	id: int
	email: EmailStr
	created_at: datetime

	class Config:
		from_attributes = True


class Token(BaseModel):
	access_token: str
	token_type: str = "bearer"


class SearchItem(BaseModel):
	product_id: str
	product_name: str
	site: str
	price: float
	url: str


class SearchResponse(BaseModel):
	query: str
	items: List[SearchItem]
	best_price: Optional[SearchItem] = None


class TrackOut(BaseModel):
	id: int
	product_id: str
	user_id: int
	created_at: datetime

	class Config:
		from_attributes = True


class TrackedItemPublic(BaseModel):
	id: int
	product_id: str
	product_name: str
	created_at: datetime


class ForecastPoint(BaseModel):
	date: date
	price: float
	lower: float
	upper: float


class ForecastResponse(BaseModel):
	product_id: str
	product_name: str
	history: List[ForecastPoint]
	forecast: List[ForecastPoint]
	great_deal: bool
	great_deal_reason: str 


class ProductSummary(BaseModel):
	product_id: str
	product_name: str
	latest_price: Optional[float] = None
	views: Optional[int] = None


class RecommendationResponse(BaseModel):
	source: str
	items: List[ProductSummary]