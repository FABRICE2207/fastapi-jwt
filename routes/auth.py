from fastapi import APIRouter, Depends, Request
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
    # insert data
    user = UsersRepo.find_by_username(db, request.username)

    if not pwd_context.verify(request.password, user.password):
      return ResponseSchema(code="400", status="Bad Request", message="Username ou mot de passe incorrect.").dict(exclude_none=True)
    token = JWTRepo.generate_token({'sub': user.username})
    return ResponseSchema(code="200", status="OK", message="Connexion réussit", result=TokenResponse(access_token=token, token_type="bearer").dict(exclude_none=True))
  except Exception as error:
    error_message = str(error.args)
    print(error_message)
    return ResponseSchema(code="500", status="Error", message="Erreur du serveur").dict(exclude_none=True)
  
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