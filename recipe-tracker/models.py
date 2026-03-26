from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, func, Table
from sqlalchemy.orm import relationship
from database import Base


# Association table for many-to-many relationship between recipes and tags
recipe_tags_table = Table(
    "recipe_tags",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)


# Association table for many-to-many relationship between recipes and holidays
recipe_holidays_table = Table(
    "recipe_holidays",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
    Column("holiday_id", Integer, ForeignKey("holidays.id", ondelete="CASCADE"), primary_key=True)
)


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    date = Column(String(20), nullable=True)  # e.g., "Dec 25" or "4th Thursday in November"
    color = Column(String(20), default="red")  # For UI display

    recipes = relationship(
        "Recipe",
        secondary=recipe_holidays_table,
        back_populates="holidays"
    )


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    servings = Column(Integer, nullable=True)
    prep_time_minutes = Column(Integer, nullable=True)
    is_family_recipe = Column(Boolean, default=False)
    use_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    is_kid_approved = Column(Boolean, default=False)  # Most recent kid approval status
    kid_approved_count = Column(Integer, default=0)  # Total approvals
    kid_rejected_count = Column(Integer, default=0)  # Total rejections

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    ingredients = relationship(
        "Ingredient",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )
    directions = relationship(
        "Direction",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )
    tags = relationship(
        "Tag",
        secondary=recipe_tags_table,
        back_populates="recipes",
        cascade="all, delete"
    )
    holidays = relationship(
        "Holiday",
        secondary=recipe_holidays_table,
        back_populates="recipes",
        cascade="all, delete"
    )
    categories = relationship(
        "Category",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )
    ratings = relationship(
        "Rating",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    def increment_use(self):
        """Increment use count and update last_used timestamp."""
        self.use_count += 1
        from datetime import datetime
        self.last_used = datetime.utcnow()
        return self

    def update_rating(self, new_rating: int):
        """Update average rating when a new rating is added."""
        total = self.average_rating * self.rating_count + new_rating
        self.rating_count += 1
        self.average_rating = round(total / self.rating_count)
        return self


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    amount = Column(String(255), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"))

    recipe = relationship("Recipe", back_populates="ingredients")


class Direction(Base):
    __tablename__ = "directions"

    id = Column(Integer, primary_key=True, index=True)
    step_text = Column(Text, nullable=False)
    step_number = Column(Integer, nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"))

    recipe = relationship("Recipe", back_populates="directions")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(20), default="blue")  # For UI display

    recipes = relationship(
        "Recipe",
        secondary=recipe_tags_table,
        back_populates="tags"
    )


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"))

    recipe = relationship("Recipe", back_populates="categories")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    is_kid_approved = Column(Boolean, nullable=False)  # True if kid approved, False if rejected
    comment = Column(Text, nullable=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"))
    created_at = Column(DateTime, server_default=func.now())

    recipe = relationship("Recipe", back_populates="ratings")
