from pydantic import BaseModel, EmailStr, Field
from typing import List

class UserSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class RecipeSchema(BaseModel):
    title: str = Field(min_length=1)
    cooking_time: int = Field(gt=0)
    ingredients: List[str]