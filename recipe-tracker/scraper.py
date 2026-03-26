import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from models import Recipe, Ingredient, Direction
from schemas import RecipeCreate, RecipeImportResponse
import re


def extract_recipe_from_url(url: str) -> dict:
    """Extract recipe data from a web page (basic extraction)."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RecipeTracker/1.0)"
        }
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try to extract title
            title_tag = soup.find("title")
            title = title_tag.get_text().strip() if title_tag else "Untitled Recipe"
            
            # Look for common recipe schema
            recipe_data = {
                "title": title,
                "description": None,
                "ingredients": [],
                "directions": []
            }
            
            # Try schema.org Recipe markup
            script = soup.find("script", type="application/ld+json")
            if script:
                import json
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        data = data[0]
                    if data.get("@type") == "Recipe":
                        if data.get("name"):
                            recipe_data["title"] = data["name"]
                        if data.get("description"):
                            recipe_data["description"] = data["description"]
                        if data.get("recipeIngredient"):
                            recipe_data["ingredients"] = data["recipeIngredient"]
                        if data.get("recipeInstructions"):
                            steps = data["recipeInstructions"]
                            if isinstance(steps, list) and steps:
                                if isinstance(steps[0], dict):
                                    recipe_data["directions"] = [str(i+1) + ". " + s.get("text", "") for i, s in enumerate(steps)]
                                else:
                                    recipe_data["directions"] = [str(i+1) + ". " + str(s) for i, s in enumerate(steps)]
                except (json.JSONDecodeError, AttributeError):
                    pass
            
            # Fallback: try to find ingredients and directions by common patterns
            if not recipe_data["ingredients"]:
                ingredient_keywords = ["ingredient", "ingredients"]
                for keyword in ingredient_keywords:
                    el = soup.find(lambda tag: tag.name in ["h3", "h4", "p", "div"] and keyword in tag.get_text().lower())
                    if el:
                        # Find next list or paragraph with ingredients
                        next_el = el.find_next(["ul", "ol", "p", "div"])
                        if next_el:
                            items = next_el.find_all(["li", "p"])
                            if items:
                                recipe_data["ingredients"] = [item.get_text().strip() for item in items[:20]]
            
            if not recipe_data["directions"]:
                direction_keywords = ["direction", "instructions", "steps", "method"]
                for keyword in direction_keywords:
                    el = soup.find(lambda tag: tag.name in ["h3", "h4"] and keyword in tag.get_text().lower())
                    if el:
                        next_el = el.find_next(["ol", "ul"])
                        if next_el:
                            items = next_el.find_all("li")
                            if items:
                                recipe_data["directions"] = [str(i+1) + ". " + item.get_text().strip() for i, item in enumerate(items)]
            
            return recipe_data
    
    except Exception as e:
        return {
            "title": "Failed to extract recipe",
            "description": f"Error: {str(e)}",
            "ingredients": [],
            "directions": []
        }


async def import_recipe_from_url(db: Session, url: str) -> RecipeImportResponse:
    """Import a recipe from a URL and save to database."""
    recipe_data = extract_recipe_from_url(url)
    
    if not recipe_data["ingredients"] and not recipe_data["directions"]:
        return RecipeImportResponse(
            success=False,
            message="Could not extract ingredients or directions from the URL."
        )
    
    # Create recipe
    db_recipe = Recipe(
        title=recipe_data["title"][:255],
        description=recipe_data.get("description", "")[:1000] if recipe_data.get("description") else None
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    
    # Add ingredients
    for ing in recipe_data["ingredients"][:50]:  # Limit to 50 ingredients
        ingredient = Ingredient(
            name=str(ing)[:255],
            amount="",  # Web scraping may not parse amounts well
            recipe_id=db_recipe.id
        )
        db.add(ingredient)
    
    # Add directions
    for i, step in enumerate(recipe_data["directions"][:20]):  # Limit to 20 steps
        direction = Direction(
            step_text=step[:1000],
            step_number=i + 1,
            recipe_id=db_recipe.id
        )
        db.add(direction)
    
    db.commit()
    db.refresh(db_recipe)
    
    return RecipeImportResponse(
        success=True,
        recipe_id=db_recipe.id,
        message=f"Recipe '{db_recipe.title}' imported successfully."
    )


async def import_recipe_from_json(db: Session, json_data: dict) -> RecipeImportResponse:
    """Import a recipe from JSON data."""
    if not json_data.get("title"):
        return RecipeImportResponse(
            success=False,
            message="Recipe JSON must include a 'title' field."
        )
    
    # Create recipe
    db_recipe = Recipe(
        title=json_data["title"][:255],
        description=json_data.get("description", "")[:1000] if json_data.get("description") else None,
        servings=json_data.get("servings"),
        prep_time_minutes=json_data.get("prep_time_minutes"),
        is_holiday_recipe=json_data.get("is_holiday_recipe", False),
        is_family_recipe=json_data.get("is_family_recipe", False),
        is_kid_approved=json_data.get("is_kid_approved", False)
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    
    # Add ingredients
    for ing in json_data.get("ingredients", [])[:50]:
        if isinstance(ing, dict):
            ingredient = Ingredient(
                name=ing.get("name", "")[:255],
                amount=ing.get("amount", "")[:255],
                recipe_id=db_recipe.id
            )
        else:
            ingredient = Ingredient(
                name=str(ing)[:255],
                amount="",
                recipe_id=db_recipe.id
            )
        db.add(ingredient)
    
    # Add holidays
    if json_data.get("holidays"):
        for holiday_name in json_data["holidays"][:10]:  # Limit to 10 holidays
            holiday = db.query(Holiday).filter(Holiday.name == holiday_name).first()
            if not holiday:
                holiday = Holiday(name=holiday_name[:100], color="red")
                db.add(holiday)
                db.commit()
                db.refresh(holiday)
            if holiday not in db_recipe.holidays:
                db_recipe.holidays.append(holiday)
    
    # Add directions
    for i, step in enumerate(json_data.get("directions", [])[:20]):
        direction = Direction(
            step_text=str(step)[:1000],
            step_number=i + 1,
            recipe_id=db_recipe.id
        )
        db.add(direction)
    
    # Add tags
    if json_data.get("tags"):
        for tag_name in json_data["tags"][:10]:  # Limit to 10 tags
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name[:50], color="blue")
                db.add(tag)
                db.commit()
                db.refresh(tag)
            if tag not in db_recipe.tags:
                db_recipe.tags.append(tag)
    
    # Add categories
    if json_data.get("categories"):
        for cat_name in json_data["categories"][:5]:  # Limit to 5 categories
            category = Category(name=cat_name[:50], recipe_id=db_recipe.id)
            db.add(category)
    
    db.commit()
    db.refresh(db_recipe)
    
    return RecipeImportResponse(
        success=True,
        recipe_id=db_recipe.id,
        message=f"Recipe '{db_recipe.title}' imported successfully."
    )
