from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.users import  ResponseSchema, UserUpdateSchema, ChangePassword
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

# Mise à jour 
@router.put("/update_users/{id}")
async def update_user(
    id: int,
    user_update: UserUpdateSchema,
    db: Session = Depends(get_db)
):
    try:
        update_data = user_update.dict(exclude_unset=True)

        # Vérifie si l'utilisateur existe
        existing_user = GetOneUserRepo.get_one_user(db, Users, id)
        if not existing_user:
            return ResponseSchema(
                code="404",
                status="Error",
                message="Utilisateur non trouvé"
            ).dict(exclude_none=True)

        # Mise à jour dans la base
        updated_user = UpdateUser.update_user(db, Users, id, update_data)

        return ResponseSchema(
            code="200",
            status="OK",
            message="Utilisateur mis à jour avec succès",
            result=updated_user
        ).dict(exclude_none=True)

    except Exception as error:
        print(f"Erreur lors de la mise à jour de l'utilisateur : {str(error)}")
        return ResponseSchema(
            code="500",
            status="Error",
            message="Erreur interne du serveur"
        ).dict(exclude_none=True)

# Modifier le password par l'email
@router.put("/change_password_by_email")
async def change_password_by_email(data: ChangePassword, db: Session = Depends(get_db)):
    try:
        # Cherche l'utilisateur par email
        user = db.query(Users).filter(Users.email == data.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        # Vérifie l'ancien mot de passe
        if not pwd_context.verify(data.old_password, user.password):
            raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")

        # Hash le nouveau mot de passe
        user.password = pwd_context.hash(data.new_password)

        # Met à jour en base
        db.add(user)
        db.commit()
        db.refresh(user)

        # Réponse
        return ResponseSchema(
            code="200",
            status="OK",
            message="Mot de passe changé avec succès"
        ).dict(exclude_none=True)

    except HTTPException as http_error:
        return ResponseSchema(
            code=str(http_error.status_code),
            status="Error",
            message=http_error.detail
        ).dict(exclude_none=True)

    except Exception as e:
        print(f"Erreur serveur: {e}")
        return ResponseSchema(
            code="500",
            status="Error",
            message="Erreur interne du serveur"
        ).dict(exclude_none=True)


# Suppression de l'user par l'id
@router.delete("/delete_users/{id}")
async def delete_user(id: int, db: Session = Depends(get_db)):
    try:
        # Tentative de suppression de l'utilisateur
        deleted = DeleteUser.delete_user(db, id)

        if not deleted:
            return ResponseSchema(
                code="404",
                status="Error",
                message="Utilisateur non trouvé"
            ).dict(exclude_none=True)

        return ResponseSchema(
            code="200",
            status="OK",
            message="Utilisateur supprimé avec succès"
        ).dict(exclude_none=True)
    except Exception as error:
        print(f"Erreur lors de la suppression de l'utilisateur : {str(error)}")
        return ResponseSchema(
            code="500",
            status="Error",
            message="Erreur interne du serveur"
        ).dict(exclude_none=True)