# MealPlanner Suite

A collection of FastAPI services for managing meals, recipes, pantry inventory, and shopping lists.

## Projects

| Sub‑project | Description | Docs |
|-------------|-------------|------|
| **pantry‑tracker** | Track items in your pantry, fridge, and freezer. Includes expiration alerts and unit conversion. | `pantry-tracker/README.md` |
| **recipe‑tracker** | Store, retrieve, and import recipes (JSON or URLs). Supports ingredients, directions, tags, and usage stats. | `recipe-tracker/README.md` |
| **shopping‑api** | Simple wrapper around the Kroger API for building shopping lists. | `shopping-api/README.md` |

## Getting Started

1. **Clone the repo**
   ```bash
   git clone https://github.com/slharclaw/mealtrkr.git
   cd mealtrkr/mealplanner
   ```

2. **Set up each service** (see each sub‑project’s README for detailed steps).  Typically you’ll:
   ```bash
   # Create a virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate

   # Install dependencies for a service
   cd pantry-tracker
   pip install -r requirements.txt
   ```

3. **Run a service**
   ```bash
   uvicorn main:app --reload   # from the service’s directory
   ```

## License

All components are MIT‑licensed unless otherwise noted in the individual project directories.

---

*Happy cooking, planning, and shopping! 🚀*
