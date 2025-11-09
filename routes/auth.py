from fastapi import APIRouter, Depends, Request, HTTPException, status
from schemas.users import  ResponseSchema, TokenResponse, Register, Login, UserOut
from sqlalchemy.orm import Session
from config import get_db
from passlib.context import CryptContext
from repository.users import UsersRepo, JWTRepo, JWTBearer
from models.models import Users

router = APIRouter(tags={"Auth"})

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

#register
@router.post('/signup')
async def signup(request: Register, db: Session = Depends(get_db)):
  try:
    # Vérification si les champs sont vides
    if not request.username or not request.email or not request.password:
            return ResponseSchema(
                code="400",
                status="Error",
                message="Veuillez remplir tous les champs obligatoires."
            ).dict(exclude_none=True)

        # Vérification si l'email existe déjà
    existing_user = db.query(Users).filter(Users.email == request.email).first()
    if existing_user:
        return ResponseSchema(
                code="400",
                status="Error",
                message="Cet email est déjà utilisé."
            ).dict(exclude_none=True)
    # insert data
    user = Users(
      username = request.username,
      password = pwd_context.hash(request.password),
      email = request.email,
      phone = request.phone)
    UsersRepo.insert(db, user)
    return ResponseSchema(code="200", status="Ok", message="Enregistrement réussit").dict(exclude_none=True)
  except Exception as error:
    print(error.args)
    return ResponseSchema(code="500", status="Error", message="Erreur du serveur").dict(exclude_none=True)
  
# login
@router.post('/login')
async def login(request: Login, db: Session = Depends(get_db)):
    try:
        # Vérification de l'existence de l'utilisateur
        user = UsersRepo.find_by_username(db, request.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nom d'utilisateur ou mot de passe incorrect."
            )

        # Vérification du mot de passe
        if not pwd_context.verify(request.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nom d'utilisateur ou mot de passe incorrect."
            )

        # Génération du token JWT
        token = JWTRepo.generate_token({'sub': user.username})

        # Réponse de succès
        return ResponseSchema(
            code="200",
            status="OK",
            message="Connexion réussie",
            result=TokenResponse(
                access_token=token,
                token_type="bearer"
            ).dict(exclude_none=True)
        ).dict(exclude_none=True)

    except HTTPException as http_error:
        # Gestion propre des erreurs d'authentification
        return ResponseSchema(
            code=str(http_error.status_code),
            status="Bad Request",
            message=http_error.detail
        ).dict(exclude_none=True)

    except Exception as error:
        # Gestion d'erreurs serveur
        print(f"Erreur serveur: {error}")
        return ResponseSchema(
            code="500",
            status="Error",
            message="Erreur interne du serveur."
        ).dict(exclude_none=True)
  
@router.get("/me", response_model=ResponseSchema[UserOut], dependencies=[Depends(JWTBearer())])
async def me(request: Request, db: Session = Depends(get_db)):
    try:
        # On récupère le username depuis le payload du token
        payload = request.state.user
        username = payload.get("sub")
        if not username:
            return ResponseSchema(code="401", status="Error", message="Token invalide").model_dump(exclude_none=True)

        # On récupère l'utilisateur dans la base
        user = UsersRepo.find_by_username(db, username)
        if not user:
            return ResponseSchema(code="404", status="Error", message="Utilisateur non trouvé").model_dump(exclude_none=True)

        # Convertir en modèle Pydantic (UserOut) pour exclure le mot de passe
        user_out = UserOut.model_validate(user)

        return ResponseSchema(
            code="200",
            status="Ok",
            message="Utilisateur connecté",
            result=user_out
        ).model_dump(exclude_none=True)

    except Exception as error:
        print(error.args)
        return ResponseSchema(
            code="500",
            status="Error",
            message="Erreur du serveur"
        ).model_dump(exclude_none=True)