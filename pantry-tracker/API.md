# Pantry & Refrigerator Inventory Tracker API

A REST API for tracking pantry and refrigerator inventory with support for unit conversions, expiration tracking, and multiple categories.

## Base URL

```
http://localhost:8000
```

## Authentication

None required (local use only).

---

## Endpoints

### GET `/items`

List all inventory items.

**Query Parameters:**

| Parameter | Type    | Default | Description         |
|-----------|---------|---------|---------------------|
| skip      | integer | 0       | Number of items to skip |
| limit     | integer | 100     | Maximum items to return |

**Response:** `200 OK` — Array of Item objects

```json
[
  {
    "id": 1,
    "name": "Milk",
    "category": "fridge",
    "quantity": 1.0,
    "unit": "L",
    "expiration_date": "2026-04-01"
  }
]
```

---

### GET `/items/{item_id}`

Get a specific item by ID.

**Path Parameters:**

| Parameter | Type    | Description    |
|-----------|---------|----------------|
| item_id   | integer | Item ID        |

**Responses:**
- `200 OK` — Item object
- `404 Not Found` — Item doesn't exist

---

### POST `/items`

Add a new item to inventory.

**Request Body:**

| Field            | Type   | Required | Description                                      |
|------------------|--------|----------|--------------------------------------------------|
| name             | string | Yes      | Item name                                        |
| category         | enum   | Yes      | One of: `pantry`, `fridge`, `freezer`            |
| quantity         | float  | Yes      | Must be greater than 0                           |
| unit             | string | Yes      | Unit of measure (see below)                      |
| expiration_date  | date   | No       | ISO 8601 date (must be in the future if provided) |

**Supported Units:**

*Weight:* `g`, `kg`, `oz`, `lb`, `lbs`  
*Volume:* `ml`, `L`, `oz` (fluid), `cup`, `cups`  
*Count:* `count`, `each`, `can`, `bottle`, `piece`

**Example Request:**

```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Whole Milk",
    "category": "fridge",
    "quantity": 1.0,
    "unit": "L",
    "expiration_date": "2026-04-01"
  }'
```

**Response:** `201 Created` — Created Item object

---

### PATCH `/items/{item_id}`

Update an item's quantity and/or unit. Supports unit conversion.

**Path Parameters:**

| Parameter | Type    | Description    |
|-----------|---------|----------------|
| item_id   | integer | Item ID        |

**Request Body (optional fields):**

| Field    | Type   | Description                                           |
|----------|--------|-------------------------------------------------------|
| quantity | float  | New quantity (must be positive)                      |
| unit     | string | New unit (converts quantity if provided with quantity)|

**Conversion Rules:**
- If both `quantity` and `unit` are provided, converts the new quantity to the item's original unit
- If only `unit` is provided, converts the existing quantity to the new unit
- Units must be compatible (weight↔weight, volume↔volume, count↔count)

**Example: Use 4 oz from a 16 oz bottle**

Item has: `quantity: 16, unit: "oz"`

```bash
curl -X PATCH http://localhost:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 4,
    "unit": "oz"
  }'
```

Result: item quantity updated to `12 oz`

**Alternative: Convert unit only**

```bash
curl -X PATCH http://localhost:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{
    "unit": "lbs"
  }'
```

If item has 12 oz, converts to 0.75 lbs.

**Responses:**
- `200 OK` — Updated Item object
- `400 Bad Request` — Incompatible units or invalid quantity
- `404 Not Found` — Item doesn't exist

---

### DELETE `/items/{item_id}`

Remove an item from inventory.

**Path Parameters:**

| Parameter | Type    | Description    |
|-----------|---------|----------------|
| item_id   | integer | Item ID        |

**Responses:**
- `204 No Content` — Successfully deleted
- `404 Not Found` — Item doesn't exist

---

### GET `/items/expiring-soon`

Get items expiring within N days.

**Query Parameters:**

| Parameter | Type    | Default | Description         |
|-----------|---------|---------|---------------------|
| days      | integer | 3       | Number of days to look ahead (≥0) |

**Response:** `200 OK` — Array of Item objects

```json
[
  {
    "id": 1,
    "name": "Whole Milk",
    "category": "fridge",
    "quantity": 0.75,
    "unit": "L",
    "expiration_date": "2026-03-20"
  }
]
```

---

### GET `/categories`

Get summary of items by category.

**Response:** `200 OK`

```json
[
  {
    "category": "fridge",
    "count": 5
  },
  {
    "category": "pantry",
    "count": 12
  },
  {
    "category": "freezer",
    "count": 3
  }
]
```

---

## Errors

| Status | Error Code    | Description                     |
|--------|---------------|---------------------------------|
| 400    | InvalidUnit   | Incompatible or unsupported unit|
| 404    | ItemNotFound  | Item ID doesn't exist           |
| 422    | ValidationError| Missing required field          |

---

## Example Workflow

1. **Add items:**
```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Eggs", "category": "fridge", "quantity": 12, "unit": "each"}'

curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Pasta Sauce", "category": "pantry", "quantity": 24, "unit": "oz", "expiration_date": "2026-06-15"}'
```

2. **Check expiring items (next 7 days):**
```bash
curl http://localhost:8000/items/expiring-soon?days=7
```

3. **Use 8 oz of sauce:**
```bash
curl -X PATCH http://localhost:8000/items/2 \
  -H "Content-Type: application/json" \
  -d '{"quantity": 8, "unit": "oz"}'
```

4. **View remaining inventory:**
```bash
curl http://localhost:8000/items
```

---

## Running the Server

```bash
cd pantry-tracker
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs will be available at `http://localhost:8000/docs`
