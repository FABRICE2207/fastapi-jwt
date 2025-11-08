from datetime import datetime
from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel
from pydantic import BaseModel, Field, EmailStr

T = TypeVar('T')

# Login
class Login(BaseModel):
  username: str
  password: str

# Register
class Register(BaseModel):
  username: str = Field(..., min_length=3, description="Nom d'utilisateur requis")
  email: EmailStr
  phone: str = Field(..., min_length=10, description="Téléphone requis")
  password: str = Field(..., min_length=8, description="Mot de passe requis")

# UserUpdate
class UserUpdateSchema(BaseModel):
  username: Optional[str] = None
  email: Optional[str] = None
  phone: Optional[str] = None
  password: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    phone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Permet de convertir un objet SQLAlchemy en Pydantic automatiquement

# Model de reponse
class ResponseSchema(BaseModel, Generic[T]):
  code: str
  status: str
  message: str
  result: Optional[T] = None

  class Config:
        from_attributes = True  # permet de convertir automatiquement les objets ORM
        

#Token
class TokenResponse(BaseModel):
  access_token: str
  token_type: str