from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    amount: str = Field(..., min_length=1, max_length=255)


class IngredientCreate(IngredientBase):
    pass


class Ingredient(IngredientBase):
    id: int
    recipe_id: int

    class Config:
        from_attributes = True


class DirectionBase(BaseModel):
    step_text: str = Field(..., min_length=1)


class DirectionCreate(DirectionBase):
    step_number: int = Field(..., gt=0)


class Direction(DirectionBase):
    id: int
    recipe_id: int
    step_number: int

    class Config:
        from_attributes = True


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(default="blue", max_length=20)


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True


class HolidayBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    date: Optional[str] = Field(default=None, max_length=20)
    color: Optional[str] = Field(default="red", max_length=20)


class HolidayCreate(HolidayBase):
    pass


class Holiday(HolidayBase):
    id: int

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    recipe_id: int

    class Config:
        from_attributes = True


class RatingBase(BaseModel):
    is_kid_approved: bool  # True = kid approved, False = kid rejected
    comment: Optional[str] = Field(default=None, max_length=500)


class RatingCreate(RatingBase):
    pass


class Rating(RatingBase):
    id: int
    recipe_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    servings: Optional[int] = Field(default=None, gt=0)
    prep_time_minutes: Optional[int] = Field(default=None, gt=0)
    tags: List[str] = Field(default_factory=list)
    holidays: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)


class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate] = Field(default_factory=list)
    directions: List[DirectionCreate] = Field(default_factory=list)
    is_family_recipe: bool = Field(default=False)


class Recipe(RecipeBase):
    id: int
    is_family_recipe: bool
    use_count: int
    last_used: Optional[datetime] = None
    is_kid_approved: bool  # Current overall kid approval status
    kid_approved_count: int  # Total approvals
    kid_rejected_count: int  # Total rejections
    created_at: datetime
    updated_at: datetime
    ingredients: List[Ingredient] = Field(default_factory=list)
    directions: List[Direction] = Field(default_factory=list)
    tags: List[Tag] = Field(default_factory=list)
    holidays: List[Holiday] = Field(default_factory=list)
    categories: List[Category] = Field(default_factory=list)
    ratings: List[Rating] = Field(default_factory=list)

    class Config:
        from_attributes = True


class RecipeUseCount(BaseModel):
    recipe_id: int
    use_count: int
    last_used: Optional[datetime] = None


class RecipeUseRequest(BaseModel):
    recipe_id: int
    increment: bool = True


class RecipeImportRequest(BaseModel):
    url: Optional[str] = Field(default=None)
    json_data: Optional[dict] = Field(default=None)


class RecipeImportResponse(BaseModel):
    success: bool
    recipe_id: Optional[int] = None
    message: str
