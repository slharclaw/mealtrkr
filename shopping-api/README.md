# Shopping API

A REST API that integrates with Kroger for product search and cart management.

## Features

- **User Management**: Create and manage multiple users
- **Shopping Lists**: Create and manage persistent shopping lists per user
- **Product Search**: Search Kroger products via their API
- **Local Cart**: Build a cart locally before sending to Kroger
- **Substitution Management**: Track item substitutions (remembered or one-time)
- **Purchase History**: Track costs and purchase history
- **Kroger Integration**: Search products, locations, and process purchases

## Project Structure

```
shopping-api/
├── main.py              # FastAPI application
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic validation schemas
├── database.py          # Database connection setup
├── kroger_client.py     # Kroger API client wrapper
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Installation

```bash
cd shopping-api
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with your Kroger API credentials:

```bash
KROGER_CLIENT_ID=your_client_id_here
KROGER_CLIENT_SECRET=your_client_secret_here
KROGER_REDIRECT_URI=http://localhost:8000/callback
KROGER_USER_ZIP_CODE=10001
```

## Running the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------|
| GET | `/` | Health check |

### Users
| Method | Endpoint | Description |
|--------|----------|-------|
| POST | `/users` | Create a new user |
| GET | `/users/{id}` | Get a user by ID |

### Shopping Lists
| Method | Endpoint | Description |
|--------|----------|-------|
| GET | `/users/{user_id}/lists` | List shopping lists |
| POST | `/users/{user_id}/lists` | Create a shopping list |
| GET | `/lists/{list_id}` | Get a shopping list |
| DELETE | `/lists/{list_id}` | Delete a shopping list |
| GET | `/lists/{list_id}/items` | List items in a list |
| POST | `/lists/{list_id}/items` | Add an item to a list |
| DELETE | `/items/{item_id}` | Delete a list item |

### Substitutions
| Method | Endpoint | Description |
|--------|----------|-------|
| POST | `/items/{item_id}/substitute` | Create a substitution |
| GET | `/items/{item_id}/substitutions` | List substitutions |

### Carts
| Method | Endpoint | Description |
|--------|----------|-------|
| GET | `/users/{user_id}/carts` | List carts |
| POST | `/users/{user_id}/carts` | Create a cart |
| GET | `/carts/{cart_id}` | Get a cart |
| GET | `/carts/{cart_id}/items` | List cart items |
| POST | `/carts/{cart_id}/items` | Add item to cart |
| DELETE | `/cart-items/{item_id}` | Remove item from cart |
| POST | `/carts/{cart_id}/total` | Calculate cart total |
| POST | `/carts/{cart_id}/buy` | Process cart purchase |

### Products (Kroger)
| Method | Endpoint | Description |
|--------|----------|-------|
| GET | `/products/search` | Search products |
| GET | `/products/{product_id}` | Get product details |
| GET | `/locations/search` | Search store locations |

### Purchases
| Method | Endpoint | Description |
|--------|----------|-------|
| GET | `/purchases` | Get purchase history |
| GET | `/purchases/{purchase_id}` | Get purchase details |

## Example Usage

### Create a User

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "djlosh",
    "email": "dj@losh.com",
    "zip_code": "90210"
  }'
```

### Create a Shopping List

```bash
curl -X POST http://localhost:8000/users/1/lists \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Groceries",
    "description": "Weekly shopping list"
  }'
```

### Search Products

```bash
curl "http://localhost:8000/products/search?term=milk&zip_code=90210&limit=5"
```

### Add Item to Cart

```bash
curl -X POST http://localhost:8000/carts/1/items \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "123456",
    "product_name": "Whole Milk",
    "product_brand": "Kroger",
    "quantity": 2,
    "unit_price": 3.99
  }'
```

### Calculate Cart Total

```bash
curl -X POST http://localhost:8000/carts/1/total
```

### Buy Cart

```bash
curl -X POST http://localhost:8000/carts/1/buy \
  -H "Content-Type: application/json" \
  -d '{
    "kroger_location_id": "0123456"
  }'
```

## Notes

- The Kroger API has rate limits: 10,000 calls/day for products, 5,000 for cart/identity
- SQLite is used for simplicity; consider PostgreSQL for production
- Token management is handled automatically by the Kroger client
- Carts are local until you call `/buy` to send to Kroger
