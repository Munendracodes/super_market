from logging.config import fileConfig
import os
import sys
from sqlalchemy import create_engine, text
from alembic import context
from dotenv import load_dotenv
import logging

# Ensure project root is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
logger = logging.getLogger("alembic.env")
load_dotenv()
logger.info("🔑 Environment variables loaded")

# Import Base + models
from app.base import Base
import app.models  # make sure all models are imported here
logger.info("📦 Models imported successfully")

# Alembic target metadata
target_metadata = Base.metadata
logger.info(f"🧩 Metadata loaded: {list(Base.metadata.tables.keys())}")

# Read DB settings from .env
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "")

logger.info(
    f"🔧 DB Config -> USER: {MYSQL_USER}, HOST: {MYSQL_HOST}, PORT: {MYSQL_PORT}, DB: {MYSQL_DB}"
)

# Build DB URL
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)
logger.info("🔗 Database URL created")

# Alembic config
config = context.config
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# Logging config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger.info("📝 Alembic config file loaded")

# ----------------- Migration functions -----------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    logger.info("📴 Running migrations in OFFLINE mode...")
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        logger.info("⚡ Starting transaction (offline)...")
        context.run_migrations()

        if not target_metadata.tables:
            logger.info("😴 No schema changes detected (offline). Database is up-to-date.")
        else:
            logger.info("✅ Offline migrations completed")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    logger.info("🌐 Running migrations in ONLINE mode...")
    connectable = create_engine(SQLALCHEMY_DATABASE_URL)
    logger.info("🚀 Database engine created")

    with connectable.connect() as connection:
        logger.info("🔌 Connected to database")

        def process_revision_directives(context, revision, directives):
            if getattr(config.cmd_opts, "autogenerate", False):
                script = directives[0]
                if script.upgrade_ops.is_empty():
                    directives[:] = []
                    logger.info("😴 No schema changes detected (online). Database is up-to-date.")

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            logger.info("⚡ Starting transaction (online)...")
            context.run_migrations()
            logger.info("✅ Online migrations completed (if any changes)")

        # Debug: Show current DB tables
        result = connection.execute(text("SHOW TABLES;"))
        tables = [row[0] for row in result]
        logger.info(f"📊 Tables in DB: {tables}")


# ----------------- Entrypoint -----------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
