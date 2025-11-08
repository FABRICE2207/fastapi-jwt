from fastapi import APIRouter, Depends, Request
from typing import List
from schemas.posts import PostUpdateSchema, ResponseSchema, Register, PostOut, PostCountResponse
from sqlalchemy.orm import Session
from config import get_db
from repository.posts import AllPostsRepo, CountPostByUser, DeletePost, PostsRepo, GetOnePostRepo, UpdatePost
from models.models import Post

router = APIRouter(tags={"Posts"})


# ajout du post
@router.post("/add_post")
async def add_post(request: Register, db: Session = Depends(get_db)):
    try:
    # Vérification si les champs sont vides
      if not request.title or not request.content or not request.users_id:
              return ResponseSchema(
                  code="400",
                  status="Error",
                  message="Veuillez remplir tous les champs obligatoires."
              ).dict(exclude_none=True)

          # Vérification si l'email existe déjà
      existing_post = db.query(Post).filter(Post.title == request.title).first()
      if existing_post:
          return ResponseSchema(
                  code="400",
                  status="Error",
                  message="Cet post existe déjà"
              ).dict(exclude_none=True)
      # insert data
      post = Post(
        title = request.title,
        content = request.content,
        users_id = request.users_id)
        
      PostsRepo.insert(db, post)
      return ResponseSchema(code="200", status="Ok", message="Post enregisté avec succès.").dict(exclude_none=True)
    except Exception as error:
      print(error.args)
      return ResponseSchema(code="500", status="Error", message="Erreur du serveur").dict(exclude_none=True)

# get all posts
@router.get("/posts")
async def get_all_posts(db: Session = Depends(get_db)):
    try:
        posts = AllPostsRepo.get_all(db, Post)

        post_out = [PostOut.from_orm(p) for p in posts]
        return ResponseSchema(
            code="200",
            status="Ok",
            message="Liste des postes",
            result=post_out
        ).dict(exclude_none=True)
    except Exception as error:
        print(error.args)
        return ResponseSchema(
            code="500",
            status="Error",
            message="Erreur du serveur"
        ).dict(exclude_none=True)
    
# Obtenir un post
@router.get("/posts/{id}")
async def get_one_post(post_id: int, db: Session = Depends(get_db)):
    post = GetOnePostRepo.get_one_post(db, Post, post_id)

    # Vérifie si le post existe
    if not post:
        return ResponseSchema(code="404", status="Error", message="Post non trouvé").dict(exclude_none=True)

     # Conversion ORM -> Pydantic # Affiche le resultat avec infos users dans post
    post_out = PostOut.from_orm(post)

    # Affiche le resultat
    return ResponseSchema(code="200", status="Ok", message="Post trouvé", result=post_out).dict(exclude_none=True)

@router.get("/count-by-user", response_model=list[PostCountResponse])
def get_posts_count_by_user(db: Session = Depends(get_db)):
    return CountPostByUser.get_post_count_by_user(db)

# Mise à jour du post
@router.put("/update_posts/{id}")
async def update_post(
    id: int,
    post_update: PostUpdateSchema,
    db: Session = Depends(get_db)
):
    try:
        # Convert Pydantic model to dict, excluding unset values
        update_data = post_update.dict(exclude_unset=True)
        
        # First check if post exists
        existing_post = GetOnePostRepo.get_one_post(db, Post, id)
        if not existing_post:
            return ResponseSchema(
                code="404",
                status="Error", 
                message="Post non trouvé"
            ).dict(exclude_none=True)
            
        # Proceed with update if post exists
        updated_post = UpdatePost.update_post(db, Post, id, update_data)
        return ResponseSchema(
            code="200",
            status="Ok",
            message="Post mis à jour avec succès",
            result= updated_post
        ).dict(exclude_none=True)
        
    except Exception as error:
        print(f"Erreur de la mise à jour du post: {str(error)}")
        return ResponseSchema(
            code="500",
            status="Error",
            message="Erreur lors de la mise à jour"
        ).dict(exclude_none=True)
    
# Suppression de l'user par l'id
@router.delete("/delete_post/{id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    user = DeletePost.delete_post(db, post_id)
    if not user:
        return ResponseSchema(code="404", status="Error", message="Post non trouvé").dict(exclude_none=True)

    return ResponseSchema(code="200", status="Ok", message="Post supprimé avec succès").dict(exclude_none=True)