from datetime import datetime
from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel
from pydantic import BaseModel, Field, EmailStr, validator

T = TypeVar('T')

# Login
class Login(BaseModel):
  username: str
  password: str

# Register
class Register(BaseModel):
  username: str = Field(..., min_length=3, description="Nom d'utilisateur requis")
  email: EmailStr
  phone: str = Field(..., min_length=10, max_length=10, description="Téléphone requis")
  password: str = Field(..., min_length=8, max_length=8, description="Mot de passe requis")

# UserUpdate
class UserUpdateSchema(BaseModel):
  username: Optional[str] = None
  email: Optional[str] = None
  phone: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    phone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Permet de convertir un objet SQLAlchemy en Pydantic automatiquement

# Schemas pour changer le password
class ChangePassword(BaseModel):
   email: EmailStr = Field(..., description="Email de l'utilisateur")
   old_password: str = Field(..., min_length=8, max_length=8, description="Le mot de passe doit être de 8 caractères")
   new_password: str = Field(..., min_length=8, max_length=8)
   confirm_password: str = Field(..., min_length=8, max_length=8)

   @validator('confirm_password')
   def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError("Le nouveau mot de passe et la confirmation doivent correspondre")
        return v
   
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