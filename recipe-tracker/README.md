# Recipe Tracker API

A REST API built with FastAPI for tracking recipes with ingredients, amounts, and directions.

## Features

- **Recipe Management**: Create, read, update, and delete recipes
- **Ingredient Tracking**: Add ingredients with amounts to recipes
- **Direction Tracking**: Step-by-step cooking instructions with ordering
- **Web Import**: Import recipes from web URLs (basic schema.org support)
- **JSON Import**: Import recipes from structured JSON data
- **Recipe Usage Tracking**: Track when a recipe was last used and total uses
- **Holiday Recipes**: Assign holiday-specific recipes to holidays (e.g., "Thanksgiving", "Christmas")
- **Family Recipe Flags**: Mark recipes as passed-down family recipes
- **Tags & Categories**: Organize recipes with tags and categories
- **Kid Approval System**: Mark recipes as kid-approved or rejected with comments
- **SQLite Persistence**: Local database using SQLAlchemy

## Project Structure

```
recipe-tracker/
├── main.py          # FastAPI application
├── models.py        # SQLAlchemy database models
├── schemas.py       # Pydantic validation schemas
├── database.py      # Database connection setup
├── scraper.py       # Web scraping and import logic
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Installation

```bash
cd recipe-tracker
pip install -r requirements.txt
```

## Running the Server

```bash
python main.py
```

Or manually:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Recipes
- `GET /recipes` - List all recipes
- `GET /recipes/{id}` - Get a specific recipe
- `POST /recipes` - Create a new recipe
- `PUT /recipes/{id}` - Update a recipe
- `DELETE /recipes/{id}` - Delete a recipe

### Ingredients
- `GET /recipes/{id}/ingredients` - List ingredients for a recipe
- `POST /recipes/{id}/ingredients` - Add an ingredient
- `DELETE /ingredients/{id}` - Delete an ingredient

### Directions
- `GET /recipes/{id}/directions` - List directions for a recipe
- `POST /recipes/{id}/directions` - Add a direction
- `DELETE /directions/{id}` - Delete a direction

### Import
- `POST /recipes/import` - Import recipe from URL or JSON

## Example Usage

### Create a Recipe

```bash
curl -X POST http://localhost:8000/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Spaghetti Carbonara",
    "description": "Classic Italian pasta dish",
    "servings": 4,
    "prep_time_minutes": 30,
    "ingredients": [
      {"name": "Spaghetti", "amount": "400g"},
      {"name": "Pancetta", "amount": "200g"},
      {"name": "Eggs", "amount": "4 large"},
      {"name": "Parmesan cheese", "amount": "100g"}
    ],
    "directions": [
      {"step_text": "Boil water and cook spaghetti according to package directions", "step_number": 1},
      {"step_text": "Fry pancetta until crispy", "step_number": 2},
      {"step_text": "Beat eggs with grated parmesan", "step_number": 3},
      {"step_text": "Combine hot pasta with pancetta, then stir in egg mixture", "step_number": 4}
    ]
  }'
```

### Import from URL

```bash
curl -X POST http://localhost:8000/recipes/import \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/recipe"
  }'
```

### Import from JSON

```bash
curl -X POST http://localhost:8000/recipes/import \
  -H "Content-Type: application/json" \
  -d '{
    "json_data": {
      "title": "My Recipe",
      "description": "A quick meal",
      "ingredients": [{"name": "Pasta", "amount": "200g"}],
      "directions": [{"step_text": "Cook pasta", "step_number": 1}]
    }
  }'
```

## Recipe Usage Tracking

Mark a recipe as used to track when it was last cooked and how many times:

```bash
curl -X POST http://localhost:8000/recipes/1/used
```

Response includes updated use count and timestamp.

## Additional Tools

- **API Docs**: Visit `/docs` for Swagger UI
- **Postman Collection**: Import `API-Documentation.json`
