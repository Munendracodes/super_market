from logging.config import fileConfig
import os
import sys
import subprocess
import logging
from sqlalchemy import create_engine, text
from alembic import context

# Ensure project root is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Import branch-aware settings
from app.base import Base
import app.models  # make sure all models are imported
from app.config import settings  # 👈 branch-aware config

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# Detect Git branch
def get_git_branch() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        ).decode().strip()
    except Exception:
        return "dev"

branch = get_git_branch()
logger.info(f"🌿 Current Git branch detected: {branch}")

# 🚨 Safety check: prevent accidental migrations on main
if branch == "main" and os.getenv("FORCE_MAIN_MIGRATION", "false").lower() != "true":
    logger.error("🚨 Migration blocked! You're on MAIN branch but FORCE_MAIN_MIGRATION is not set.")
    raise SystemExit(
        "❌ Aborting migration: Running migrations on MAIN requires $env:FORCE_MAIN_MIGRATION='true'"
    )

if branch == "main" and os.getenv("FORCE_MAIN_MIGRATION", "false").lower() == "true":   
    logger.warning("⚠️ Running migrations on MAIN branch with FORCE_MAIN_MIGRATION enabled. Proceed with caution!")

# Build DB URL from settings
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
)
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

logger.info("🔧 Database config:")
logger.info(f"   👤 User: {settings.MYSQL_USER}")
logger.info(f"   🏠 Host: {settings.MYSQL_HOST}")
logger.info(f"   🗄️ DB:   {settings.MYSQL_DB}")

# Target metadata (all models)
target_metadata = Base.metadata
logger.info(f"🧩 Loaded models: {list(Base.metadata.tables.keys())}")

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
        logger.info("✅ Offline migrations completed")

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    logger.info("🌐 Running migrations in ONLINE mode...")
    connectable = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

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

        # Debug: Show tables
        result = connection.execute(text("SHOW TABLES;"))
        tables = [row[0] for row in result]
        logger.info(f"📊 Current tables in DB: {tables}")

# ----------------- Entrypoint -----------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
