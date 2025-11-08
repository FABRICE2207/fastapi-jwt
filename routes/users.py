from fastapi import APIRouter, Depends
from typing import List
from schemas.users import  ResponseSchema, UserUpdateSchema
from sqlalchemy.orm import Session
from config import get_db
from passlib.context import CryptContext
from repository.users import AllUsersRepo, GetOneUserRepo, UpdateUser, DeleteUser
from models.models import Users

router = APIRouter(tags={"Users"})
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# get all users
@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    try:
        users = AllUsersRepo.get_all(db, Users)
        return ResponseSchema(
            code="200",
            status="Ok",
            message="Liste des utilisateurs",
            result=users
        ).dict(exclude_none=True)
    except Exception as error:
        print(error.args)
        return ResponseSchema(
            code="500",
            status="Error",
            message="Erreur du serveur"
        ).dict(exclude_none=True)   
    

# Obtenir un user par son id
@router.get("/users/{id}")
async def get_one_user(user_id: int, db: Session = Depends(get_db)):
    user = GetOneUserRepo.get_one_user(db, Users, user_id)
    
    if not user:
        return ResponseSchema(code="404", status="Error", message="Utilisateur non trouvé").dict(exclude_none=True)

    return ResponseSchema(code="200", status="Ok", message="Utilisateur trouvé", result=user).dict(exclude_none=True)

# Mise à jour de l'user
@router.put("/update_users/{id}")
async def update_user(
    id: int,
    user_update: UserUpdateSchema,
    db: Session = Depends(get_db)
):
    try:
        # Convertit le modèle Pydantic en dictionnaire, sans les champs non définis
        update_data = user_update.dict(exclude_unset=True)

        # Vérifie si l'utilisateur existe
        existing_user = GetOneUserRepo.get_one_user(db, Users, id)
        if not existing_user:
            return ResponseSchema(
                code="404",
                status="Error",
                message="Utilisateur non trouvé"
            ).dict(exclude_none=True)

        # Si le mot de passe est présent, on le hash avant la mise à jour
        if "password" in update_data and update_data["password"]:
            update_data["password"] = pwd_context.hash(update_data["password"])

        # Effectue la mise à jour
        updated_user = UpdateUser.update_user(db, Users, id, update_data)

        return ResponseSchema(
            code="200",
            status="Ok",
            message="Utilisateur mis à jour avec succès",
            result=updated_user
        ).dict(exclude_none=True)

    except Exception as error:
        print(f"Error updating user: {str(error)}")
        return ResponseSchema(
            code="500",
            status="Error",
            message="Erreur lors de la mise à jour"
        ).dict(exclude_none=True)

# Suppression de l'user par l'id
@router.delete("/delete_users/{id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = DeleteUser.delete_user(db, user_id)
    if not user:
        return ResponseSchema(code="404", status="Error", message="Utilisateur non trouvé").dict(exclude_none=True)

    return ResponseSchema(code="200", status="Ok", message="Utilisateur supprimé avec succès").dict(exclude_none=True)