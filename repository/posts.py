import json
from typing import TypeVar, Generic, Optional, Type
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.models import Post, Users
from sqlalchemy import func

T = TypeVar('T')

# users
class BaseRepo():
  @staticmethod
  def insert(db: Session, model: Generic[T]):
    db.add(model)
    db.commit()
    db.refresh(model)

# post verification
class PostsRepo(BaseRepo):
  @staticmethod
  def find_by_title(db: Session, title: str):
    return db.query(Post).filter(Post.title == title).first()

# get all users sauf password
class AllPostsRepo(BaseRepo):
    @staticmethod
    def get_all(db: Session, model: Generic[T]):
        return db.query(model).filter(model.id == model.id).all()
    
# get one post
class GetOnePostRepo(BaseRepo):
  @staticmethod
  def get_one_post(db: Session, model: Generic[T], id: int):
    return db.query(model).filter(model.id == id).first()
  

class CountPostByUser:
    @staticmethod
    def get_post_count_by_user(db: Session):
        results = (
            db.query(Users, func.count(Post.id).label("total_posts"))
            .join(Post, Users.id == Post.users_id)
            .group_by(Users.id)
            .all()
        )

        # On formate le résultat pour correspondre au schéma Pydantic
        return [
            {"users": user, "total_posts": total_posts}
            for user, total_posts in results
        ]
        
  
class UpdatePost(BaseRepo):
    @staticmethod
    def update_post(db: Session, model: Generic[T], id: int, update_data: dict):
        post = db.query(model).filter(model.id == id).first()
        if not post:
            return None

        for key, value in update_data.items():
            if not hasattr(post, key):
                continue
            # Convert dict/list to JSON string to avoid psycopg2 adaptation error
            if isinstance(value, (dict, list, tuple)):
                try:
                    setattr(post, key, json.dumps(value))
                except Exception:
                    # skip problematic fields (or handle as needed)
                    continue
            else:
                setattr(post, key, value)

        db.commit()
        db.refresh(post)

        return post
    
# Suppression du post par l'id
class DeletePost:
    @staticmethod
    def delete_post(db: Session, post_id: int):
        # On filtre par id
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return None  # Utilisateur non trouvé
        db.delete(post)   # Supprime du post
        db.commit()       # Applique post
    