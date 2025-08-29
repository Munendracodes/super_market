# alembic/env.py
from logging.config import fileConfig
import os
import sys
import subprocess
import logging
from sqlalchemy import create_engine, text
from alembic import context
from dotenv import load_dotenv  # ✅ ensures .env is loaded

# Load environment variables from .env
load_dotenv()

# Ensure app modules are available
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.base import Base
import app.models  # noqa: F401
from app.config import settings

# Alembic Config
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")


def get_git_branch() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        ).decode().strip()
    except Exception:
        return "dev"


branch = get_git_branch()
logger.info(f"🌿 Current Git branch: {branch}")

if branch == "main" and os.getenv("FORCE_MAIN_MIGRATION", "false").lower() != "true":
    raise SystemExit(
        "❌ Aborting migration: On MAIN branch. Set FORCE_MAIN_MIGRATION=true to override."
    )

# ✅ Safe env loading with defaults
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))  # cast to int
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "testdb")

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

    with connectable.connect() as connection:
        def process_revision_directives(context, revision, directives):
            if getattr(config.cmd_opts, "autogenerate", False):
                script = directives[0]
                if script.upgrade_ops.is_empty():
                    directives[:] = []
                    logger.info("😴 No schema changes detected — migration skipped.")

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()

        result = connection.execute(text("SHOW TABLES;"))
        tables = [row[0] for row in result]
        logger.info(f"📊 Current tables in DB: {tables}")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
