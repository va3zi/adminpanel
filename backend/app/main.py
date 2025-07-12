from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from .database import engine, Base, get_db, SessionLocal
from . import models # Import models to ensure they are registered with Base
from .api.v1.api import api_router_v1 # Import the v1 API router
from .security import get_password_hash # For initial super admin creation
from .schemas import SuperAdminCreate # For initial super admin creation

load_dotenv()

# Create database tables (For development only. Use Alembic for production.)
# This is a synchronous call, ensure your DB is up when the app starts.
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully (if they didn't exist).")
except Exception as e:
    print(f"Error creating database tables: {e}")


app = FastAPI(
    title="VPN Admin Panel API",
    version="0.1.0",
    description="API for managing VPN services, admins, and users.",
    # openapi_url="/api/v1/openapi.json" # If you want to move default docs
)

# Include the v1 router
app.include_router(api_router_v1, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    # Create initial SuperAdmin if it doesn't exist
    # This is a simple way for initial setup. A CLI command is better for production.
    db: Session = SessionLocal()
    try:
        super_admin_username = os.getenv("INITIAL_SUPER_ADMIN_USERNAME", "superadmin")
        existing_super_admin = db.query(models.SuperAdmin).filter(models.SuperAdmin.username == super_admin_username).first()
        if not existing_super_admin:
            print(f"Initial SuperAdmin '{super_admin_username}' not found, creating one...")
            super_admin_email = os.getenv("INITIAL_SUPER_ADMIN_EMAIL", "superadmin@example.com")
            super_admin_password = os.getenv("INITIAL_SUPER_ADMIN_PASSWORD", "ChangeMeSuperSecure!123")

            if super_admin_password == "ChangeMeSuperSecure!123":
                print("WARNING: Using default insecure password for initial SuperAdmin. Please change this via environment variables.")

            hashed_password = get_password_hash(super_admin_password)
            initial_super_admin = models.SuperAdmin(
                username=super_admin_username,
                email=super_admin_email,
                hashed_password=hashed_password
            )
            db.add(initial_super_admin)
            db.commit()
            print(f"Initial SuperAdmin '{super_admin_username}' created successfully.")
        else:
            print(f"Initial SuperAdmin '{super_admin_username}' already exists.")
    except Exception as e:
        print(f"Error during initial SuperAdmin creation: {e}")
        # It's important to rollback in case of error during transaction
        db.rollback()
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Welcome to the VPN Admin Panel API. Docs at /docs or /redoc."}

# Placeholder for health check or other root-level utility endpoints if needed
@app.get("/health")
async def health_check():
    return {"status": "ok"}
