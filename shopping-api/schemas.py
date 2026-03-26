from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    zip_code: Optional[str] = Field(default="10001", max_length=10)


class UserCreate(UserBase):
    password: Optional[str] = Field(default=None)


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Shopping List Schemas
class ShoppingListBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class ShoppingListCreate(ShoppingListBase):
    pass


class ShoppingList(ShoppingListBase):
    id: int
    is_active: bool
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Shopping List Item Schemas
class ShoppingListItemBase(BaseModel):
    product_id: str = Field(..., min_length=1)
    product_name: str = Field(..., min_length=1, max_length=255)
    product_brand: Optional[str] = Field(default=None, max_length=255)
    quantity: int = Field(default=1, ge=1)
    unit_price: Optional[float] = Field(default=None, ge=0)
    is_substitute_accepted: bool = Field(default=False)
    is_one_time_substitute: bool = Field(default=False)


class ShoppingListItemCreate(ShoppingListItemBase):
    pass


class ShoppingListItem(ShoppingListItemBase):
    id: int
    shopping_list_id: int
    last_known_price: Optional[float]
    added_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Substitution Schemas
class SubstitutionBase(BaseModel):
    substitute_product_id: str
    substitute_product_name: str
    substitute_product_brand: Optional[str] = None
    substitution_type: str = Field(..., pattern="^(remembered|one-time)$")
    reason: Optional[str] = Field(default=None, max_length=500)


class SubstitutionCreate(SubstitutionBase):
    pass


class Substitution(SubstitutionBase):
    id: int
    original_item_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Cart Schemas
class CartBase(BaseModel):
    name: str = Field(default="Current Cart", max_length=100)


class CartCreate(CartBase):
    pass


class Cart(CartBase):
    id: int
    user_id: int
    is_frozen: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartItemBase(BaseModel):
    product_id: str
    product_name: str
    product_brand: Optional[str] = None
    product_image: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    unit_price: Optional[float] = Field(default=None, ge=0)
    is_substituted: bool = Field(default=False)
    original_item_id: Optional[int] = None
    substitution_id: Optional[int] = None


class CartItemCreate(BaseModel):
    product_id: str
    product_name: str
    product_brand: Optional[str] = None
    product_image: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    unit_price: Optional[float] = Field(default=None, ge=0)


class CartItem(CartItemBase):
    id: int
    cart_id: int
    added_at: datetime

    class Config:
        from_attributes = True


# Purchase Schemas
class PurchaseItemBase(BaseModel):
    product_id: str
    product_name: str
    product_brand: Optional[str] = None
    quantity: int = Field(ge=1)
    unit_price: Optional[float] = Field(ge=0)
    total_price: Optional[float] = Field(ge=0)
    was_substituted: bool = Field(default=False)


class PurchaseBase(BaseModel):
    total_cost: float = Field(ge=0)
    subtotal: Optional[float] = Field(ge=0)
    taxes: Optional[float] = Field(ge=0)
    rewards_used: float = Field(default=0, ge=0)
    items_count: int = Field(ge=0)


class Purchase(PurchaseBase):
    id: int
    user_id: int
    cart_id: Optional[int]
    kroger_order_id: Optional[str]
    purchased_at: datetime
    items: List[PurchaseItemBase] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Kroger API Response Schemas (simplified)
class Location(BaseModel):
    location_id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: Optional[str] = None


class Product(BaseModel):
    product_id: str
    name: str
    brand: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    image_url: Optional[str] = None
    upc: Optional[str] = None


class SearchProductsResponse(BaseModel):
    data: List[Product]


# API Request/Response Schemas
class SubstituteRequest(BaseModel):
    substitute_product_id: str
    substitution_type: str = Field(pattern="^(remembered|one-time)$", default="remembered")
    reason: Optional[str] = Field(default=None, max_length=500)


class CartTotal(BaseModel):
    total_cost: float
    subtotal: float
    taxes: float
    items_count: int


class AddToCartResponse(BaseModel):
    success: bool
    cart_id: int
    added_items: List[CartItem]
    total: CartTotal


class BuyCartRequest(BaseModel):
    cart_id: int
    kroger_location_id: str
    use_rewards: bool = True


class BuyCartResponse(BaseModel):
    success: bool
    purchase_id: int
    kroger_order_id: Optional[str]
    total_cost: float
