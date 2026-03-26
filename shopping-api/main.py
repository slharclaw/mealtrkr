from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db, engine
import models
from schemas import (
    # Users
    UserCreate, UserRead,
    # Shopping Lists
    ShoppingListCreate, ShoppingList, ShoppingListBase,
    ShoppingListItemCreate, ShoppingListItem,
    # Substitutions
    SubstitutionCreate, Substitution,
    # Carts
    CartCreate, Cart, CartItemCreate, CartItem, AddToCartResponse, CartTotal,
    # Purchases
    Purchase, PurchaseBase, BuyCartRequest, BuyCartResponse,
    # Kroger
    Location, Product, SearchProductsResponse
)
import kroger_client

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Shopping API",
    description="A shopping API that integrates with Kroger for product search and cart management.",
    version="1.0.0"
)

kroger = kroger_client.KrogerClient()


# ============== Helper Functions ==============
def get_user_or_404(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============== Health Check ==============
@app.get("/", summary="Health Check")
async def root():
    return {"message": "Shopping API", "status": "online", "version": "1.0.0"}


# ============== User Endpoints ==============
@app.post("/users", response_model=UserRead, status_code=201, summary="Create a new user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    db_user = models.User(
        username=user.username,
        email=user.email,
        zip_code=user.zip_code
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserRead, summary="Get a user by ID")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a user by ID."""
    return get_user_or_404(db, user_id)


# ============== Shopping List Endpoints ==============
@app.get("/users/{user_id}/lists", response_model=List[ShoppingList], summary="List all shopping lists for a user")
def list_shopping_lists(user_id: int, db: Session = Depends(get_db), active_only: bool = True):
    """List all shopping lists for a user."""
    get_user_or_404(db, user_id)

    query = db.query(models.ShoppingList).filter(models.ShoppingList.user_id == user_id)
    if active_only:
        query = query.filter(models.ShoppingList.is_active == True)

    return query.all()


@app.post("/users/{user_id}/lists", response_model=ShoppingList, status_code=201, summary="Create a new shopping list")
def create_shopping_list(user_id: int, list_data: ShoppingListCreate, db: Session = Depends(get_db)):
    """Create a new shopping list for a user."""
    get_user_or_404(db, user_id)

    db_list = models.ShoppingList(
        name=list_data.name[:100],
        description=list_data.description[:500] if list_data.description else None,
        user_id=user_id
    )
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


@app.get("/lists/{list_id}", response_model=ShoppingList, summary="Get a shopping list by ID")
def get_shopping_list(list_id: int, db: Session = Depends(get_db)):
    """Get a shopping list by ID."""
    shopping_list = db.query(models.ShoppingList).filter(models.ShoppingList.id == list_id).first()
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return shopping_list


@app.delete("/lists/{list_id}", summary="Delete a shopping list")
def delete_shopping_list(list_id: int, db: Session = Depends(get_db)):
    """Delete a shopping list."""
    list_item = db.query(models.ShoppingList).filter(models.ShoppingList.id == list_id).first()
    if not list_item:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    db.delete(list_item)
    db.commit()
    return {"message": "Shopping list deleted successfully"}


# ============== Shopping List Item Endpoints ==============
@app.get("/lists/{list_id}/items", response_model=List[ShoppingListItem], summary="List items in a shopping list")
def list_shopping_list_items(list_id: int, db: Session = Depends(get_db)):
    """List all items in a shopping list."""
    shopping_list = db.query(models.ShoppingList).filter(models.ShoppingList.id == list_id).first()
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")

    return db.query(models.ShoppingListItem).filter(models.ShoppingListItem.shopping_list_id == list_id).all()


@app.post("/lists/{list_id}/items", response_model=ShoppingItem, status_code=201, summary="Add an item to a shopping list")
def add_shopping_list_item(list_id: int, item: ShoppingItemCreate, db: Session = Depends(get_db)):
    """Add an item to a shopping list."""
    shopping_list = db.query(models.ShoppingList).filter(models.ShoppingList.id == list_id).first()
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")

    db_item = models.ShoppingListItem(
        shopping_list_id=list_id,
        product_id=item.product_id[:255],
        product_name=item.product_name[:255],
        product_brand=item.product_brand[:255] if item.product_brand else None,
        quantity=item.quantity,
        unit_price=item.unit_price,
        last_known_price=item.unit_price,
        is_substitute_accepted=item.is_substitute_accepted,
        is_one_time_substitute=item.is_one_time_substitute
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/items/{item_id}", summary="Delete a shopping list item")
def delete_shopping_list_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a shopping list item."""
    item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Shopping list item not found")
    db.delete(item)
    db.commit()
    return {"message": "Shopping list item deleted successfully"}


# ============== Substitution Endpoints ==============
@app.post("/items/{item_id}/substitute", response_model=Substitution, status_code=201, summary="Create a substitution for a shopping list item")
def create_substitution(item_id: int, substitution: SubstitutionCreate, db: Session = Depends(get_db)):
    """Create a substitution for a shopping list item."""
    item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Shopping list item not found")

    db_sub = models.Substitution(
        original_item_id=item_id,
        substitute_product_id=substitution.substitute_product_id[:255],
        substitute_product_name=substitution.substitute_product_name[:255],
        substitute_product_brand=substitution.substitute_product_brand[:255] if substitution.substitute_product_brand else None,
        substitution_type=substitution.substitution_type[:20],
        reason=substitution.reason[:500] if substitution.reason else None
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


@app.get("/items/{item_id}/substitutions", response_model=List[Substitution], summary="List substitutions for a shopping list item")
def list_item_substitutions(item_id: int, db: Session = Depends(get_db)):
    """List all substitutions for a shopping list item."""
    item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Shopping list item not found")

    return db.query(models.Substitution).filter(models.Substitution.original_item_id == item_id).all()


# ============== Cart Endpoints ==============
@app.get("/users/{user_id}/carts", response_model=List[Cart], summary="List all carts for a user")
def list_carts(user_id: int, db: Session = Depends(get_db), frozen_only: bool = False):
    """List all carts for a user."""
    get_user_or_404(db, user_id)

    query = db.query(models.Cart).filter(models.Cart.user_id == user_id)
    if frozen_only:
        query = query.filter(models.Cart.is_frozen == True)

    return query.all()


@app.post("/users/{user_id}/carts", response_model=Cart, status_code=201, summary="Create a new cart")
def create_cart(user_id: int, cart: CartCreate, db: Session = Depends(get_db)):
    """Create a new cart for a user."""
    get_user_or_404(db, user_id)

    db_cart = models.Cart(
        name=cart.name[:100],
        user_id=user_id
    )
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart


@app.get("/carts/{cart_id}", response_model=Cart, summary="Get a cart by ID")
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    """Get a cart by ID."""
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


@app.get("/carts/{cart_id}/items", response_model=List[CartItem], summary="List items in a cart")
def list_cart_items(cart_id: int, db: Session = Depends(get_db)):
    """List all items in a cart."""
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    return db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).all()


@app.post("/carts/{cart_id}/items", response_model=CartItem, summary="Add an item to a cart")
def add_item_to_cart(cart_id: int, item: CartItemCreate, db: Session = Depends(get_db)):
    """Add an item to a cart."""
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    if cart.is_frozen:
        raise HTTPException(status_code=400, detail="Cannot modify a frozen cart")

    db_item = models.CartItem(
        cart_id=cart_id,
        product_id=item.product_id[:255],
        product_name=item.product_name[:255],
        product_brand=item.product_brand[:255] if item.product_brand else None,
        product_image=item.product_image[:500] if item.product_image else None,
        quantity=item.quantity,
        unit_price=item.unit_price
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/cart-items/{item_id}", summary="Remove an item from a cart")
def remove_cart_item(item_id: int, db: Session = Depends(get_db)):
    """Remove an item from a cart."""
    item = db.query(models.CartItem).filter(models.CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if item.cart.is_frozen:
        raise HTTPException(status_code=400, detail="Cannot modify a frozen cart")

    db.delete(item)
    db.commit()
    return {"message": "Cart item removed successfully"}


# ============== Product Search (Kroger Integration) ==============
@app.get("/products/search", response_model=SearchProductsResponse, summary="Search products via Kroger")
async def search_products(
    term: str,
    location_id: Optional[str] = None,
    zip_code: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Search for products via Kroger API."""
    # Use location_id if provided, otherwise search by zip
    if not location_id:
        if not zip_code:
            raise HTTPException(status_code=400, detail="Either location_id or zip_code is required")
        # Search for first location matching zip
        locations = await kroger.search_locations(zip_code=zip_code, limit=1)
        if not locations.get("data"):
            raise HTTPException(status_code=404, detail="No locations found for this zip code")
        location_id = locations["data"][0]["locationId"]

    products = await kroger.search_products(
        term=term,
        location_id=location_id,
        limit=limit,
        offset=offset
    )

    # Enrich products with image URLs
    for product in products.data:
        if product.image_url is None:
            product.image_url = await kroger.get_product_images(product.product_id)

    return products


@app.get("/products/{product_id}", response_model=Product, summary="Get product details via Kroger")
async def get_product_details(product_id: str):
    """Get detailed product information from Kroger."""
    product = await kroger.get_product_details(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/locations/search", response_model=Dict, summary="Search store locations")
async def search_locations(zip_code: str, radius: int = 10, limit: int = 5):
    """Search for Kroger store locations by zip code."""
    return await kroger.search_locations(zip_code=zip_code, radius=radius, limit=limit)


# ============== Cart Actions ==========----
@app.post("/carts/{cart_id}/total", response_model=CartTotal, summary="Calculate cart total")
def calculate_cart_total(cart_id: int, db: Session = Depends(get_db)):
    """Calculate the total cost of items in a cart."""
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    items = db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).all()
    subtotal = sum((item.unit_price or 0) * item.quantity for item in items)
    taxes = subtotal * 0.08  # 8% estimated tax
    total = subtotal + taxes

    return CartTotal(
        total_cost=round(total, 2),
        subtotal=round(subtotal, 2),
        taxes=round(taxes, 2),
        items_count=len(items)
    )


@app.post("/carts/{cart_id}/buy", response_model=BuyCartResponse, summary="Process cart purchase")
async def buy_cart(cart_id: int, request: BuyCartRequest, db: Session = Depends(get_db)):
    """Process a cart purchase and send to Kroger."""
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    if cart.is_frozen:
        raise HTTPException(status_code=400, detail="Cart already processed")

    # Calculate total
    items = db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).all()
    subtotal = sum((item.unit_price or 0) * item.quantity for item in items)
    taxes = subtotal * 0.08  # 8% estimated tax
    total = subtotal + taxes

    # In production, this would call Kroger's cart API
    # For now, create a purchase record
    db_purchase = models.Purchase(
        user_id=cart.user_id,
        cart_id=cart_id,
        kroger_order_id=f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        total_cost=round(total, 2),
        subtotal=round(subtotal, 2),
        taxes=round(taxes, 2),
        items_count=len(items)
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)

    # Add purchase items
    for item in items:
        db_purchase_item = models.PurchaseItem(
            purchase_id=db_purchase.id,
            product_id=item.product_id[:255],
            product_name=item.product_name[:255],
            product_brand=item.product_brand[:255] if item.product_brand else None,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=(item.unit_price or 0) * item.quantity,
            was_substituted=item.is_substituted
        )
        db.add(db_purchase_item)

    # Mark cart as frozen
    cart.is_frozen = True
    db.commit()
    db.refresh(cart)

    return BuyCartResponse(
        success=True,
        purchase_id=db_purchase.id,
        kroger_order_id=db_purchase.kroger_order_id,
        total_cost=db_purchase.total_cost
    )


@app.get("/purchases", response_model=List[Purchase], summary="Get purchase history")
def get_purchase_history(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get purchase history for a user."""
    get_user_or_404(db, user_id)

    purchases = db.query(models.Purchase).filter(models.Purchase.user_id == user_id).offset(skip).limit(limit).all()
    return purchases


@app.get("/purchases/{purchase_id}", response_model=Purchase, summary="Get purchase details")
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    """Get details of a specific purchase."""
    purchase = db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    # Add items to the response
    purchase.items = db.query(models.PurchaseItem).filter(models.PurchaseItem.purchase_id == purchase_id).all()
    return purchase


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
