from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from config import engine
import models.models as users_model
import routes.auth as auth_routes
import routes.users as users_routes
import routes.posts as posts_routes

# Charger les variables d'environnement
load_dotenv()
ENV = os.getenv("ENV", "development")

# users_model.Base.metadata.create_all(bind=engine)  # seulement sans Alembic

# ========================
# 🔧 CONFIGURATION CORS DYNAMIQUE
# ========================
if ENV == "development":
    origins = ["*"]
else:
    origins = [
        "https://sdnconstruction.com",
        "https://app.sdnconstruction.com"
    ]

app = FastAPI(
    title="Authentication API JWT FastAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# ROUTES
# ========================
app.include_router(auth_routes.router, prefix="/auth")
app.include_router(users_routes.router, prefix="/api")
app.include_router(posts_routes.router, prefix="/api")

# @app.get("/")
# async def root():
#     return {"message": f"Bienvenue sur l'API  ({ENV})"}
