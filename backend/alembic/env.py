import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here
# for 'autogenerate' support
import sys
current_path = os.path.dirname(os.path.abspath(__file__)) # backend/alembic
backend_path = os.path.dirname(current_path) # backend/
sys.path.append(backend_path) # To allow imports like 'from app.db.base...'
sys.path.append(os.path.dirname(backend_path)) # Add project root for broader imports if needed

from app.db.base import Base
# Import all models here so Base.metadata correctly reflects them
from app.models import SuperAdmin, Admin, Plan, VPNUser, PaymentTransaction, ActionLog


target_metadata = Base.metadata

def get_db_url_from_env_or_config():
    """
    Returns the database URL.
    Priority: DATABASE_URL environment variable, then sqlalchemy.url from config's [alembic] section.
    """
    db_url_env = os.getenv("DATABASE_URL")
    if db_url_env:
        print(f"Using DATABASE_URL from environment: {db_url_env}")
        return db_url_env

    # Get sqlalchemy.url from the [alembic] section (default section_name for config_ini_section)
    # config.get_main_option might not work if it's not in the 'main' (top-level) part of ini.
    ini_url = config.get_section_option(config.config_ini_section, "sqlalchemy.url")
    if ini_url:
        print(f"Using sqlalchemy.url from alembic.ini [{config.config_ini_section}] section: {ini_url}")
    else:
        print(f"Warning: sqlalchemy.url not found in alembic.ini [{config.config_ini_section}] section.")
    return ini_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_db_url_from_env_or_config()
    if not url:
        raise ValueError("Database URL is not set for offline migration. Provide DATABASE_URL or set sqlalchemy.url in alembic.ini.")

    print(f"Offline mode configured with URL: {url}")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get the [alembic] section (or whatever config.config_ini_section is)
    # This dictionary should contain 'sqlalchemy.url' if set in ini's [alembic] section
    connectable_configuration = config.get_section(config.config_ini_section)

    # Override with DATABASE_URL from environment if it exists
    db_url_env = os.getenv("DATABASE_URL")
    if db_url_env:
        print(f"Overriding sqlalchemy.url with DATABASE_URL from environment: {db_url_env}")
        connectable_configuration["sqlalchemy.url"] = db_url_env

    # Ensure the URL is actually present in the configuration for engine_from_config
    final_url_for_engine = connectable_configuration.get("sqlalchemy.url")
    if not final_url_for_engine:
        # This should ideally not be hit if alembic.ini is correct and DATABASE_URL is not set
        # Or if the key in alembic.ini is somehow different from "sqlalchemy.url"
        print(f"ERROR: sqlalchemy.url is missing from configuration for engine_from_config. Section: [{config.config_ini_section}]")
        print(f"Current configuration dictionary being used: {connectable_configuration}")
        raise ValueError("Database URL is not configured for online migration.")

    print(f"Online mode: Final sqlalchemy.url for engine_from_config: {final_url_for_engine}")

    connectable = engine_from_config(
        connectable_configuration, # This dictionary must contain 'sqlalchemy.url'
        prefix="sqlalchemy.",      # Looks for 'sqlalchemy.url', 'sqlalchemy.echo', etc.
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
