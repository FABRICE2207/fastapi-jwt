from typing import TypeVar, Generic, Optional, Type
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from jose import JWTError, jwt
from config import SECRET_KEY, ALGORITHM

from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import json

from models.models import Users

T = TypeVar('T')

# cryté le pwd
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# users
class BaseRepo():
  @staticmethod
  def insert(db: Session, model: Generic[T]):
    db.add(model)
    db.commit()
    db.refresh(model)

# users
class UsersRepo(BaseRepo):
  @staticmethod
  def find_by_username(db: Session, username: str):
    return db.query(Users).filter(Users.username == username).first()
  
# get all users sauf password
class AllUsersRepo(BaseRepo):
    @staticmethod
    def get_all(db: Session, model: Generic[T]):
        users = db.query(model).all()
        for user in users:
          user.__dict__.pop('password', None) # Retourne tout sauf le password
        return users
    
# get one users
class GetOneUserRepo(BaseRepo):
  @staticmethod
  def get_one_user(db: Session, model: Generic[T], id: int):
    user = db.query(model).filter(model.id == id).first()
    if user:
      user.__dict__.pop('password', None)
    return user

class UpdateUser(BaseRepo):
    @staticmethod
    def update_user(db: Session, model: Generic[T], id: int, update_data: dict):
        user = db.query(model).filter(model.id == id).first()
        if not user:
            return None

        # Hash password if it exists in update data
        if "password" in update_data and update_data["password"] is not None:
            update_data["password"] = pwd_context.hash(update_data["password"])

        for key, value in update_data.items():
            if not hasattr(user, key):
                continue
            # Convert dict/list to JSON string to avoid psycopg2 adaptation error
            if isinstance(value, (dict, list, tuple)):
                try:
                    setattr(user, key, json.dumps(value))
                except Exception:
                    # skip problematic fields (or handle as needed)
                    continue
            else:
                setattr(user, key, value)

        db.commit()
        db.refresh(user)

        # Remove password from response
        user.__dict__.pop('password', None)
        return user

# Suppression de l'user
class DeleteUser:
    @staticmethod
    def delete_user(db: Session, id: int):
        # On filtre par id
        user = db.query(Users).filter(Users.id == id).first()
        if not user:
            return None  # Utilisateur non trouvé
        db.delete(user)   # Supprime l'utilisateur
        db.commit()       # Applique la suppression
        return True
   
# Générer le token
class JWTRepo():
  def generate_token(data: dict, expire_delta: Optional[timedelta]=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expire_delta if expire_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

  def decode_token(token: str):
    try:
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      return payload
    except JWTError:
      return None

# Authorisation du token
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[dict]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=403, detail="Authorization header manquant.")

        if credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=403, detail="Scheme d’authentification invalide.")

        payload = JWTRepo.decode_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=403, detail="Token invalide ou expiré.")

        # Attacher les infos du token à la requête pour les handlers ultérieurs
        request.state.user = payload
        return payload

    def verify_jwt(self, token: str) -> bool:
        """
        Vérifie si le token JWT est valide (non expiré, signature correcte).
        """
        return JWTRepo.decode_token(token) is not None

