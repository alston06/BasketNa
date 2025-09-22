from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from .db import Base


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String, unique=True, index=True, nullable=False)
	hashed_password = Column(String, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)

	tracked_items = relationship("TrackedItem", back_populates="user", cascade="all, delete-orphan")


class Product(Base):
	__tablename__ = "products"

	id = Column(String, primary_key=True, index=True)  # e.g., P001
	name = Column(String, index=True, nullable=False)

	price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")


class TrackedItem(Base):
	__tablename__ = "tracked_items"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	product_id = Column(String, ForeignKey("products.id"), nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)

	user = relationship("User", back_populates="tracked_items")
	product = relationship("Product")

	__table_args__ = (
		UniqueConstraint("user_id", "product_id", name="uq_user_product"),
	)


class PriceHistory(Base):
	__tablename__ = "price_history"

	id = Column(Integer, primary_key=True, index=True)
	product_id = Column(String, ForeignKey("products.id"), nullable=False)
	date = Column(Date, index=True, nullable=False)
	site = Column(String, index=True, nullable=False)
	price = Column(Float, nullable=False)

	product = relationship("Product", back_populates="price_history")

	__table_args__ = (
		UniqueConstraint("product_id", "date", "site", name="uq_product_date_site"),
	) 


class ProductView(Base):
	__tablename__ = "product_views"

	id = Column(Integer, primary_key=True, index=True)
	# Either user_id or session_id will be used to attribute the view
	user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
	session_id = Column(String, nullable=True, index=True)
	product_id = Column(String, ForeignKey("products.id"), nullable=False, index=True)
	viewed_at = Column(DateTime, default=datetime.utcnow, index=True)

	# Quick index to query by session or user and product
	__table_args__ = (
		Index("ix_views_user_product", "user_id", "product_id"),
		Index("ix_views_session_product", "session_id", "product_id"),
	)