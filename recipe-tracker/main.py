from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db, engine
import models
from schemas import (
    Recipe, RecipeCreate, RecipeImportRequest, RecipeImportResponse,
    Ingredient, IngredientCreate,
    Direction, DirectionCreate,
    RecipeUseRequest, RecipeUseCount,
    Tag, TagCreate, Holiday, HolidayCreate,
    Category, CategoryCreate, Rating, RatingCreate
)
import scraper

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recipe Tracker API",
    description="A REST API for tracking recipes with ingredients and directions.",
    version="1.0.0"
)


# ============== Helper Functions ==============
def get_recipe_or_404(db: Session, recipe_id: int) -> models.Recipe:
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


# ============== Recipe Endpoints ==============
@app.get("/", summary="Health Check")
async def root():
    return {"message": "Recipe Tracker API", "status": "online"}


@app.get("/recipes", response_model=List[Recipe], summary="List all recipes")
def list_recipes(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    recipes = db.query(models.Recipe).offset(skip).limit(limit).all()
    return recipes


@app.get("/recipes/{recipe_id}", response_model=Recipe, summary="Get a recipe by ID")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = get_recipe_or_404(db, recipe_id)
    return recipe


@app.post("/recipes", response_model=Recipe, status_code=201, summary="Create a new recipe")
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = models.Recipe(
        title=recipe.title[:255],
        description=recipe.description[:1000] if recipe.description else None,
        servings=recipe.servings,
        prep_time_minutes=recipe.prep_time_minutes,
        is_holiday_recipe=recipe.is_holiday_recipe,
        is_family_recipe=recipe.is_family_recipe
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    
    # Add ingredients
    for ing in recipe.ingredients[:50]:
        db_ing = models.Ingredient(
            name=ing.name[:255],
            amount=ing.amount[:255],
            recipe_id=db_recipe.id
        )
        db.add(db_ing)
    
    # Add directions
    for i, dir_step in enumerate(recipe.directions[:20]):
        db_dir = models.Direction(
            step_text=dir_step.step_text[:1000],
            step_number=dir_step.step_number,
            recipe_id=db_recipe.id
        )
        db.add(db_dir)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@app.put("/recipes/{recipe_id}", response_model=Recipe, summary="Update a recipe")
def update_recipe(recipe_id: int, recipe: RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = get_recipe_or_404(db, recipe_id)
    
    # Update recipe fields
    db_recipe.title = recipe.title[:255]
    db_recipe.description = recipe.description[:1000] if recipe.description else None
    db_recipe.servings = recipe.servings
    db_recipe.prep_time_minutes = recipe.prep_time_minutes
    db_recipe.is_holiday_recipe = recipe.is_holiday_recipe
    db_recipe.is_family_recipe = recipe.is_family_recipe
    
    # Clear existing ingredients and directions
    db.query(models.Ingredient).filter(models.Ingredient.recipe_id == recipe_id).delete()
    db.query(models.Direction).filter(models.Direction.recipe_id == recipe_id).delete()
    
    # Add new ingredients
    for ing in recipe.ingredients[:50]:
        db_ing = models.Ingredient(
            name=ing.name[:255],
            amount=ing.amount[:255],
            recipe_id=db_recipe.id
        )
        db.add(db_ing)
    
    # Add new directions
    for i, dir_step in enumerate(recipe.directions[:20]):
        db_dir = models.Direction(
            step_text=dir_step.step_text[:1000],
            step_number=dir_step.step_number,
            recipe_id=db_recipe.id
        )
        db.add(db_dir)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@app.delete("/recipes/{recipe_id}", summary="Delete a recipe")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = get_recipe_or_404(db, recipe_id)
    db.delete(db_recipe)
    db.commit()
    return {"message": "Recipe deleted successfully"}


# ============== Ingredient Endpoints ==============
@app.post("/recipes/{recipe_id}/ingredients", response_model=Ingredient, status_code=201, summary="Add an ingredient to a recipe")
def add_ingredient(recipe_id: int, ingredient: IngredientCreate, db: Session = Depends(get_db)):
    get_recipe_or_404(db, recipe_id)  # Verify recipe exists
    
    db_ingredient = models.Ingredient(
        name=ingredient.name[:255],
        amount=ingredient.amount[:255],
        recipe_id=recipe_id
    )
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


@app.get("/recipes/{recipe_id}/ingredients", response_model=List[Ingredient], summary="List ingredients for a recipe")
def list_ingredients(recipe_id: int, db: Session = Depends(get_db)):
    get_recipe_or_404(db, recipe_id)
    ingredients = db.query(models.Ingredient).filter(models.Ingredient.recipe_id == recipe_id).all()
    return ingredients


@app.delete("/ingredients/{ingredient_id}", summary="Delete an ingredient")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.delete(ingredient)
    db.commit()
    return {"message": "Ingredient deleted successfully"}


# ============== Direction Endpoints ==============
@app.post("/recipes/{recipe_id}/directions", response_model=Direction, status_code=201, summary="Add a direction to a recipe")
def add_direction(recipe_id: int, direction: DirectionCreate, db: Session = Depends(get_db)):
    get_recipe_or_404(db, recipe_id)  # Verify recipe exists
    
    db_direction = models.Direction(
        step_text=direction.step_text[:1000],
        step_number=direction.step_number,
        recipe_id=recipe_id
    )
    db.add(db_direction)
    db.commit()
    db.refresh(db_direction)
    return db_direction


@app.get("/recipes/{recipe_id}/directions", response_model=List[Direction], summary="List directions for a recipe")
def list_directions(recipe_id: int, db: Session = Depends(get_db)):
    get_recipe_or_404(db, recipe_id)
    directions = db.query(models.Direction).filter(models.Direction.recipe_id == recipe_id).order_by(models.Direction.step_number).all()
    return directions


@app.delete("/directions/{direction_id}", summary="Delete a direction")
def delete_direction(direction_id: int, db: Session = Depends(get_db)):
    direction = db.query(models.Direction).filter(models.Direction.id == direction_id).first()
    if not direction:
        raise HTTPException(status_code=404, detail="Direction not found")
    db.delete(direction)
    db.commit()
    return {"message": "Direction deleted successfully"}


# ============== Holiday Endpoints ==============
@app.get("/holidays", response_model=List[Holiday], summary="List all holidays")
def list_holidays(db: Session = Depends(get_db)):
    """List all existing holidays."""
    holidays = db.query(models.Holiday).all()
    return holidays


@app.post("/holidays", response_model= Holiday, status_code=201, summary="Create a new holiday")
def create_holiday(holiday: HolidayCreate, db: Session = Depends(get_db)):
    """Create a new holiday."""
    db_holiday = models.Holiday(
        name=holiday.name[:100],
        date=holiday.date[:20] if holiday.date else None,
        color=holiday.color[:20]
    )
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)
    return db_holiday


@app.delete("/holidays/{holiday_id}", summary="Delete a holiday")
def delete_holiday(holiday_id: int, db: Session = Depends(get_db)):
    holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    db.delete(holiday)
    db.commit()
    return {"message": "Holiday deleted successfully"}


@app.post("/recipes/{recipe_id}/holidays", response_model=List[Holiday], summary="Add holidays to a recipe")
def add_holidays_to_recipe(recipe_id: int, holiday_names: List[str], db: Session = Depends(get_db)):
    """Add holidays to a recipe by holiday name."""
    db_recipe = get_recipe_or_404(db, recipe_id)
    
    for holiday_name in holiday_names:
        holiday = db.query(models.Holiday).filter(models.Holiday.name == holiday_name).first()
        if not holiday:
            # Create holiday if it doesn't exist
            holiday = models.Holiday(name=holiday_name[:100], color="red")
            db.add(holiday)
            db.commit()
            db.refresh(holiday)
        if holiday not in db_recipe.holidays:
            db_recipe.holidays.append(holiday)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe.holidays


@app.delete("/recipes/{recipe_id}/holidays/{holiday_id}", summary="Remove a holiday from a recipe")
def remove_holiday_from_recipe(recipe_id: int, holiday_id: int, db: Session = Depends(get_db)):
    """Remove a holiday from a recipe."""
    db_recipe = get_recipe_or_404(db, recipe_id)
    holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    
    if holiday and holiday in db_recipe.holidays:
        db_recipe.holidays.remove(holiday)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe.holidays


# ============== Import Endpoints ==============
@app.post("/recipes/import", response_model=RecipeImportResponse, summary="Import a recipe from URL or JSON")
async def import_recipe(import_request: RecipeImportRequest, db: Session = Depends(get_db)):
    if import_request.url:
        return await scraper.import_recipe_from_url(db, import_request.url)
    elif import_request.json_data:
        return await scraper.import_recipe_from_json(db, import_request.json_data)
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'url' or 'json_data' must be provided in the request."
        )


# ============== Recipe Use Tracking Endpoints ==============
@app.post("/recipes/{recipe_id}/used", response_model=RecipeUseCount, summary="Mark recipe as used")
def recipe_used(recipe_id: int, db: Session = Depends(get_db)):
    """Increment use count and update last_used timestamp."""
    db_recipe = get_recipe_or_404(db, recipe_id)
    db_recipe.increment_use()
    db.commit()
    db.refresh(db_recipe)
    return RecipeUseCount(
        recipe_id=db_recipe.id,
        use_count=db_recipe.use_count,
        last_used=db_recipe.last_used
    )


@app.patch("/recipes/{recipe_id}", response_model=Recipe, summary="Update recipe flags")
def update_recipe_flags(
    recipe_id: int,
    is_holiday_recipe: Optional[bool] = None,
    is_family_recipe: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Update recipe flags (is_holiday_recipe or is_family_recipe) without affecting other fields."""
    db_recipe = get_recipe_or_404(db, recipe_id)
    
    if is_holiday_recipe is not None:
        db_recipe.is_holiday_recipe = is_holiday_recipe
    if is_family_recipe is not None:
        db_recipe.is_family_recipe = is_family_recipe
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@app.get("/recipes/family", response_model=List[Recipe], summary="Get all family recipes")
def get_family_recipes(db: Session = Depends(get_db)):
    """List all recipes marked as family recipes."""
    recipes = db.query(models.Recipe).filter(models.Recipe.is_family_recipe == True).all()
    return recipes


@app.get("/recipes/most-used", response_model=List[Recipe], summary="Get recipes by use count (descending)")
def get_most_used_recipes(db: Session = Depends(get_db), limit: int = 10):
    """Get top recipes by most used."""
    recipes = db.query(models.Recipe).order_by(models.Recipe.use_count.desc()).limit(limit).all()
    return recipes


@app.get("/recipes/last-used", response_model=List[Recipe], summary="Get recently used recipes")
def get_last_used_recipes(db: Session = Depends(get_db), limit: int = 10):
    """Get recipes sorted by last used (most recent first)."""
    recipes = db.query(models.Recipe).filter(
        models.Recipe.last_used != None
    ).order_by(models.Recipe.last_used.desc()).limit(limit).all()
    return recipes


# ============== Tag Endpoints ==============
@app.get("/tags", response_model=List[Tag], summary="List all tags")
def list_tags(db: Session = Depends(get_db)):
    """List all existing tags."""
    tags = db.query(models.Tag).all()
    return tags


@app.post("/tags", response_model=Tag, status_code=201, summary="Create a new tag")
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    db_tag = models.Tag(name=tag.name[:50], color=tag.color[:20])
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.delete("/tags/{tag_id}", summary="Delete a tag")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
    return {"message": "Tag deleted successfully"}


@app.post("/recipes/{recipe_id}/tags", response_model=List[Tag], summary="Add tags to a recipe")
def add_tags_to_recipe(recipe_id: int, tag_ids: List[int], db: Session = Depends(get_db)):
    """Add tags to a recipe by tag ID."""
    db_recipe = get_recipe_or_404(db, recipe_id)
    
    for tag_id in tag_ids:
        tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
        if tag and tag not in db_recipe.tags:
            db_recipe.tags.append(tag)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe.tags


@app.delete("/recipes/{recipe_id}/tags/{tag_id}", summary="Remove a tag from a recipe")
def remove_tag_from_recipe(recipe_id: int, tag_id: int, db: Session = Depends(get_db)):
    """Remove a tag from a recipe."""
    db_recipe = get_recipe_or_404(db, recipe_id)
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    
    if tag and tag in db_recipe.tags:
        db_recipe.tags.remove(tag)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe.tags


# ============== Category Endpoints ==============
@app.get("/recipes/{recipe_id}/categories", response_model=List[Category], summary="List categories for a recipe")
def list_categories(recipe_id: int, db: Session = Depends(get_db)):
    """List all categories for a recipe."""
    get_recipe_or_404(db, recipe_id)
    categories = db.query(models.Category).filter(models.Category.recipe_id == recipe_id).all()
    return categories


@app.post("/recipes/{recipe_id}/categories", response_model=Category, status_code=201, summary="Add a category to a recipe")
def add_category(recipe_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    """Add a category to a recipe."""
    get_recipe_or_404(db, recipe_id)
    
    db_category = models.Category(
        name=category.name[:50],
        recipe_id=recipe_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.delete("/categories/{category_id}", summary="Delete a category")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category."""
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}


# ============== Rating Endpoints ==============
@app.get("/recipes/{recipe_id}/ratings", response_model=List[Rating], summary="List ratings for a recipe")
def list_ratings(recipe_id: int, db: Session = Depends(get_db)):
    """List all ratings for a recipe."""
    get_recipe_or_404(db, recipe_id)
    ratings = db.query(models.Rating).filter(models.Rating.recipe_id == recipe_id).all()
    return ratings


@app.post("/recipes/{recipe_id}/ratings", response_model=Rating, status_code=201, summary="Add kid approval status to a recipe")
def add_rating(recipe_id: int, rating: RatingCreate, db: Session = Depends(get_db)):
    """Add kid approval status to a recipe."""
    db_recipe = get_recipe_or_404(db, recipe_id)
    
    db_rating = models.Rating(
        is_kid_approved=rating.is_kid_approved,
        comment=rating.comment[:500] if rating.comment else None,
        recipe_id=recipe_id
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    
    # Update recipe's kid approval stats
    if rating.is_kid_approved:
        db_recipe.is_kid_approved = True
        db_recipe.kid_approved_count += 1
    else:
        db_recipe.kid_rejected_count += 1
        # Recalculate overall approval status based on majority
        total = db_recipe.kid_approved_count + db_recipe.kid_rejected_count + 1
        if db_recipe.kid_approved_count >= total / 2:
            db_recipe.is_kid_approved = True
        else:
            db_recipe.is_kid_approved = False
    
    db.commit()
    db.refresh(db_recipe)
    
    return db_rating


@app.delete("/ratings/{rating_id}", summary="Delete a kid approval record")
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    """Delete a kid approval record."""
    rating = db.query(models.Rating).filter(models.Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Kid approval record not found")
    
    db_recipe = db.query(models.Recipe).filter(models.Recipe.id == rating.recipe_id).first()
    if db_recipe:
        if rating.is_kid_approved:
            db_recipe.kid_approved_count = max(0, db_recipe.kid_approved_count - 1)
        else:
            db_recipe.kid_rejected_count = max(0, db_recipe.kid_rejected_count - 1)
        
        # Recalculate overall approval status
        total = db_recipe.kid_approved_count + db_recipe.kid_rejected_count
        if total > 0 and db_recipe.kid_approved_count >= total / 2:
            db_recipe.is_kid_approved = True
        else:
            db_recipe.is_kid_approved = False
    
    db.delete(rating)
    db.commit()
    return {"message": "Kid approval record deleted successfully"}


@app.get("/recipes/search", response_model=List[Recipe], summary="Search recipes by tag, category, holiday, or kid approval status")
def search_recipes(
    tag: Optional[str] = None,
    category: Optional[str] = None,
    holiday: Optional[str] = None,
    kid_approved: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Search recipes by tag name, category name, holiday name, or kid approval status."""
    query = db.query(models.Recipe)
    
    if tag:
        query = query.join(models.recipe_tags_table).join(models.Tag).filter(models.Tag.name == tag)
    
    if category:
        query = query.join(models.Category).filter(models.Category.name == category)
    
    if holiday:
        query = query.join(models.recipe_holidays_table).join(models.Holiday).filter(models.Holiday.name == holiday)
    
    if kid_approved is not None:
        query = query.filter(models.Recipe.is_kid_approved == kid_approved)
    
    return query.distinct().all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
