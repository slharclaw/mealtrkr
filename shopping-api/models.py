from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    zip_code = Column(String(10), default="10001")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lists = relationship("ShoppingList", back_populates="user", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    purchase_history = relationship("Purchase", back_populates="user", cascade="all, delete-orphan")


# Shopping list model (persistent selection list per user)
class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="lists")
    items = relationship("ShoppingListItem", back_populates="list", cascade="all, delete-orphan")


# Shopping list item model (remembers user's preferred items)
class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)
    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id", ondelete="CASCADE"))
    product_id = Column(String(255), nullable=False)  # Kroger product ID
    product_name = Column(String(255), nullable=False)
    product_brand = Column(String(255), nullable=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=True)
    last_known_price = Column(Float, nullable=True)
    is_substitute_accepted = Column(Boolean, default=False)  # Can we substitute this item?
    is_one_time_substitute = Column(Boolean, default=False)  # One-time substitution?
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    list = relationship("ShoppingList", back_populates="items")
    substitutions = relationship("Substitution", back_populates="original_item", cascade="all, delete-orphan")


# Substitution model (remembers substitutions made)
class Substitution(Base):
    __tablename__ = "substitutions"

    id = Column(Integer, primary_key=True, index=True)
    original_item_id = Column(Integer, ForeignKey("shopping_list_items.id", ondelete="CASCADE"))
    substitute_product_id = Column(String(255), nullable=False)  # Kroger product ID
    substitute_product_name = Column(String(255), nullable=False)
    substitute_product_brand = Column(String(255), nullable=True)
    substitution_type = Column(String(20), nullable=False)  # "remembered" or "one-time"
    reason = Column(Text, nullable=True)  # Why this substitution?
    created_at = Column(DateTime, default=datetime.utcnow)

    original_item = relationship("ShoppingListItem", back_populates="substitutions")


# Cart model (local cart before sending to Kroger)
class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(100), default="Current Cart")
    is_frozen = Column(Boolean, default=False)  # True when sent to Kroger
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


# Cart item model (items in local cart)
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"))
    product_id = Column(String(255), nullable=False)
    product_name = Column(String(255), nullable=False)
    product_brand = Column(String(255), nullable=True)
    product_image = Column(Text, nullable=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=True)
    is_substituted = Column(Boolean, default=False)
    original_item_id = Column(Integer, ForeignKey("shopping_list_items.id", nullable=True))
    substitution_id = Column(Integer, ForeignKey("substitutions.id", nullable=True))
    added_at = Column(DateTime, default=datetime.utcnow)

    cart = relationship("Cart", back_populates="items")


# Purchase model (tracks completed purchases with costs)
class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="SET NULL"), nullable=True)
    kroger_order_id = Column(String(100), nullable=True)  # Order ID from Kroger
    total_cost = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=True)
    taxes = Column(Float, nullable=True)
    rewards_used = Column(Float, default=0)
    items_count = Column(Integer, default=0)
    purchased_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="purchase_history")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


# Purchase item model (individual items in a purchase)
class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id", ondelete="CASCADE"))
    product_id = Column(String(255), nullable=False)
    product_name = Column(String(255), nullable=False)
    product_brand = Column(String(255), nullable=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)
    was_substituted = Column(Boolean, default=False)

    purchase = relationship("Purchase", back_populates="items")
