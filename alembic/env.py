# alembic/env.py

import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Añadir la carpeta principal al path para importar `app`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar Base y DATABASE_URL de tu proyecto
from app.core.database import Base, DATABASE_URL

# Agrega tus modelos para que Alembic los detecte
from app.models.models import *

# Configuración de logging de Alembic
config = context.config
fileConfig(config.config_file_name)

# Metadata de tus modelos para autogenerar migraciones
target_metadata = Base.metadata

# Configurar URL
config.set_main_option("sqlalchemy.url", DATABASE_URL)

def run_migrations_offline():
    """Migraciones en modo offline"""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Migraciones en modo online"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

# Ejecutar migraciones según modo
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
