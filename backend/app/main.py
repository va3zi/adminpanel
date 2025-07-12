from fastapi import FastAPI
from .core.config import settings
from .api.v1 import api_v1_router
# Potentially add CORS middleware if frontend is on a different domain
# from fastapi.middleware.cors import CORSMiddleware

# Initialize database tables (optional, Alembic handles migrations)
# from .db.base import Base # To get all models
# from .db.session import engine
# Base.metadata.create_all(bind=engine) # Creates tables if they don't exist, Alembic is preferred

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS (Cross-Origin Resource Sharing) - Uncomment and configure if needed
# origins = [
#     "http://localhost",
#     "http://localhost:8080", # Example frontend dev server
#     # Add your frontend production domain here
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API. Docs at /docs or /redoc."}

# For development, you might want a way to create an initial superuser if none exists.
# This could be a CLI command or a special endpoint (use with caution).
# Example:
# from .db.session import SessionLocal
# from . import crud, schemas
# from .core.security import get_password_hash

# @app.on_event("startup")
# async def startup_event():
#     db = SessionLocal()
#     super_user = crud.super_admin.get_by_username(db, username="superadmin")
#     if not super_user:
#         print("Creating initial superuser: superadmin / password")
#         initial_super_admin = schemas.SuperAdminCreate(
#             username="superadmin",
#             password="password", # Change in production!
#             email="superadmin@example.com"
#         )
#         crud.super_admin.create(db, obj_in=initial_super_admin)
#     db.close()
