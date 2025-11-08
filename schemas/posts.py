from datetime import datetime
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

# Register
class Register(BaseModel):
  title: str = Field(..., min_length=3, description="Titre du post requis")
  content: str = Field(..., min_length=10, description="Contenu du post requis")
  users_id: int

# PostUpdate
class PostUpdateSchema(BaseModel):
  title: Optional[str] = None
  content: Optional[str] = None
  users_id: Optional[int] = None

class UserBase(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

# PostOut
class PostOut(BaseModel):
    id: int
    title: str
    content: str
    users: UserBase
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes=True

# UserUpdate
class UserPostSchema(BaseModel):
  title: Optional[str] = None
  content: Optional[str] = None
  users_id: Optional[int] = None

# Post total
class PostCountResponse(BaseModel):
    users: UserBase
    total_posts: int

    class Config:
        from_attributes = True

# Model de reponse
class ResponseSchema(BaseModel, Generic[T]):
  code: str
  status: str
  message: str
  result: Optional[T] = None

  class Config:
        from_attributes = True  # permet de convertir automatiquement les objets ORM