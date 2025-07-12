from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "VPN Admin Panel"
    API_V1_STR: str = "/api/v1"

    # JWT Settings
    # openssl rand -hex 32
    SECRET_KEY: str = secrets.token_hex(32) # Replace with a fixed key in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database - will be loaded from env in a real setup
    # For now, matching alembic.ini placeholder. Actual connection will be setup in main.py or db.session
    DATABASE_URL: str = "mysql+mysqlconnector://user:password@host:3306/dbname"

    # Marzban Settings
    MARZBAN_API_URL: str = "http://127.0.0.1:8000/api" # Example: http://your_marzban_domain/api
    MARZBAN_USERNAME: str = "marzban_user" # Username for Marzban API
    MARZBAN_PASSWORD: str = "marzban_password" # Password for Marzban API
    MARZBAN_BEARER_TOKEN: Optional[str] = None # To store the obtained token

    class Config:
        case_sensitive = True
        # env_file = ".env" # Uncomment to load from .env file

settings = Settings()
