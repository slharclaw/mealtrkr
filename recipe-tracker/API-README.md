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
├── README.md        # This file
├── API-Documentation.json  # Postman collection
└── docs/            # Additional documentation
```

## Installation

```bash
cd recipe-tracker
pip install -r requirements.txt
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
- **Postman Collection**: Import `API-Documentation.json`

## API Endpoints

### Recipes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recipes` | List all recipes |
| GET | `/recipes/{id}` | Get a specific recipe |
| POST | `/recipes` | Create a new recipe |
| PUT | `/recipes/{id}` | Update a recipe |
| DELETE | `/recipes/{id}` | Delete a recipe |

### Ingredients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recipes/{id}/ingredients` | List ingredients for a recipe |
| POST | `/recipes/{id}/ingredients` | Add an ingredient |
| DELETE | `/ingredients/{id}` | Delete an ingredient |

### Directions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recipes/{id}/directions` | List directions for a recipe |
| POST | `/recipes/{id}/directions` | Add a direction |
| DELETE | `/directions/{id}` | Delete a direction |

### Recipe Use Tracking
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recipes/{id}/used` | Mark a recipe as used (increment count) |
| PATCH | `/recipes/{id}` | Update recipe flags (e.g., `is_holiday_recipe`, `is_family_recipe`) |
| GET | `/recipes/holiday` | Get all holiday recipes |
| GET | `/recipes/family` | Get all family recipes |
| GET | `/recipes/most-used` | Get top recipes by usage count |
| GET | `/recipes/last-used` | Get recently used recipes |

### Tags
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tags` | List all tags |
| POST | `/tags` | Create a new tag |
| DELETE | `/tags/{tag_id}` | Delete a tag |
| POST | `/recipes/{id}/tags` | Add tags to a recipe |
| DELETE | `/recipes/{id}/tags/{tag_id}` | Remove tag from recipe |

### Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recipes/{id}/categories` | List categories for a recipe |
| POST | `/recipes/{id}/categories` | Add a category to a recipe |
| DELETE | `/categories/{id}` | Delete a category |

### Holidays
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/holidays` | List all holidays |
| POST | `/holidays` | Create a new holiday |
| DELETE | `/holidays/{id}` | Delete a holiday |
| POST | `/recipes/{id}/holidays` | Add holidays to a recipe |
| DELETE | `/recipes/{id}/holidays/{holiday_id}` | Remove holiday from recipe |
| GET | `/recipes/search` | Search by tag, category, holiday, or kid_approved |

### Ratings (Kid Approval)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recipes/{id}/ratings` | List kid approval records |
| GET | `/recipes/{id}` | Get recipe with kid approval status |
| POST | `/recipes/{id}/ratings` | Add approval (true=approved, false=rejected) |
| DELETE | `/ratings/{id}` | Remove approval record |
| GET | `/recipes/search` | Search by tag, category, holiday, or kid_approved |

### Import
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recipes/import` | Import recipe from URL or JSON |

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
    "is_holiday_recipe": false,
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

### Mark Recipe as Used

```bash
curl -X POST http://localhost:8000/recipes/1/used
````

Response:
```json
{
  "recipe_id": 1,
  "use_count": 5,
  "last_used": "2026-03-18T05:55:00Z"
}
```

### Set Recipe Flags

#### Set as holiday recipe

```bash
curl -X PATCH http://localhost:8000/recipes/1 \
  -H "Content-Type: application/json" \
  -d '{"is_holiday_recipe": true}'
````

#### Set as family recipe

```bash
curl -X PATCH http://localhost:8000/recipes/1 \
  -H "Content-Type: application/json" \
  -d '{"is_family_recipe": true}'
````

#### Get all holiday recipes

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

### Track Recipe Usage

#### Mark a recipe as used

```bash
curl -X POST http://localhost:8000/recipes/1/used
```

Response:
```json
{
  "recipe_id": 1,
  "use_count": 5,
  "last_used": "2026-03-18T05:55:00Z"
}
```

#### Set a recipe as holiday recipe

```bash
curl -X PATCH http://localhost:8000/recipes/1 \
  -H "Content-Type: application/json" \
  -d '{"is_holiday_recipe": true}'
```

#### Get all holiday recipes

```bash
curl http://localhost:8000/recipes/holiday
```

#### Get most used recipes

```bash
curl http://localhost:8000/recipes/most-used
````

#### Get last used recipes

```bash
curl http://localhost:8000/recipes/last-used
```

## Tags

#### Create a tag

```bash
curl -X POST http://localhost:8000/tags \
  -H "Content-Type: application/json" \
  -d '{"name": "Dinner", "color": "green"}'
```

#### Add tags to a recipe

```bash
curl -X POST http://localhost:8000/recipes/1/tags \
  -H "Content-Type: application/json" \
  -d '[1, 2]'
```

#### Remove a tag from a recipe

```bash
curl -X DELETE http://localhost:8000/recipes/1/tags/1
```

#### List all tags

```bash
curl http://localhost:8000/tags
```

## Categories

#### Add a category to a recipe

```bash
curl -X POST http://localhost:8000/recipes/1/categories \
  -H "Content-Type: application/json" \
  -d '{"name": "Main Course"}'
```

#### List categories for a recipe

```bash
curl http://localhost:8000/recipes/1/categories
```

#### Delete a category

```bash
curl -X DELETE http://localhost:8000/categories/1
```

## Kid Approval

#### Add kid approval to a recipe

```bash
curl -X POST http://localhost:8000/recipes/1/ratings \
  -H "Content-Type: application/json" \
  -d '{"is_kid_approved": true, "comment": "Kids loved this!"}'
```

Response includes updated recipe approval status.

#### Add kid rejection

```bash
curl -X POST http://localhost:8000/recipes/1/ratings \
  -H "Content-Type: application/json" \
  -d '{"is_kid_approved": false, "comment": "Kids turned up their noses"}'
````

#### List kid approval records

```bash
curl http://localhost:8000/recipes/1/ratings
````

#### Delete a kid approval record

```bash
curl -X DELETE http://localhost:8000/ratings/1
````

#### Search recipes by kid approval status

```bash
# Only kid-approved recipes
curl http://localhost:8000/recipes/search?kid_approved=true

# Only kid-rejected recipes
curl http://localhost:8000/recipes/search?kid_approved=false

# Combined search
curl http://localhost:8000/recipes/search?tag=Dinner&kid_approved=true
```

## Notes
