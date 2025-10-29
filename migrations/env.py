import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, MetaData
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the Base class from database.py
from app.database import Base
from app.config import get_settings

# Exclude PostGIS schemas from autogenerate
# This prevents Alembic from trying to manage PostGIS tables
def include_object(object, name, type_, reflected, compare_to):
    # Exclude tiger schema tables (PostGIS geocoder tables)
    if hasattr(object, 'schema') and object.schema in ['tiger', 'tiger_data', 'topology']:
        return False
    
    # For tables and indexes, check if the table is in tiger schema
    if hasattr(object, 'table'):
        table_schema = getattr(object.table, 'schema', None)
        if table_schema in ['tiger', 'tiger_data', 'topology']:
            return False
    
    # Exclude specific PostGIS tables from public schema
    if type_ == "table" and name in ['spatial_ref_sys']:
        return False
    
    # Include all our application tables
    return True

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get the database URL from settings
settings = get_settings()
config.set_main_option('sqlalchemy.url', settings.SYNC_DATABASE_URL)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_schemas=True,
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Configure context with our filtered metadata
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
