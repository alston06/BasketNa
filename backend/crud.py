from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models


def get_user_by_email(db: Session, email: str):
	return db.execute(select(models.User).where(models.User.email == email)).scalar_one_or_none()


def create_user(db: Session, email: str, hashed_password: str) -> models.User:
	user = models.User(email=email, hashed_password=hashed_password)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


def ensure_product(db: Session, product_id: str, name: str) -> models.Product:
	product = db.get(models.Product, product_id)
	if not product:
		product = models.Product(id=product_id, name=name)
		db.add(product)
		db.commit()
		db.refresh(product)
	return product


def add_tracked_item(db: Session, user_id: int, product_id: str) -> models.TrackedItem:
	tracked = models.TrackedItem(user_id=user_id, product_id=product_id)
	db.add(tracked)
	db.commit()
	db.refresh(tracked)
	return tracked


def list_tracked_items(db: Session, user_id: int):
	return db.query(models.TrackedItem).filter(models.TrackedItem.user_id == user_id).all()


def list_tracked_with_products(db: Session, user_id: int):
	stmt = (
		select(models.TrackedItem.id, models.TrackedItem.product_id, models.Product.name, models.TrackedItem.created_at)
		.join(models.Product, models.Product.id == models.TrackedItem.product_id)
		.where(models.TrackedItem.user_id == user_id)
	)
	return db.execute(stmt).all() 