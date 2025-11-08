from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 🔹 Import de ta configuration FastAPI
import sys, os

# permet à Alembic de trouver ton package 'app' ou le répertoire où se trouve config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Base, DATABASE_URL  # <-- ton fichier config.py
import models.models  # <-- importe tous tes modèles (Users, Post, etc.)

# ----- Configuration standard Alembic -----
config = context.config
fileConfig(config.config_file_name)
config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata

# ----- Configuration du contexte -----
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
