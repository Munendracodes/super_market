import subprocess
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

def get_git_branch() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        ).decode().strip()
    except Exception:
        return "dev"

branch = get_git_branch()
load_dotenv()  # load .env

class Settings(BaseSettings):
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: int = 3306
    MYSQL_DB: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    class Config:
        env_file = ".env"
        extra = "ignore"  # ✅ ignore extra vars like MAIN_*, RELEASE_*


if branch == "main":
    settings = Settings(
        MYSQL_USER=os.getenv("MAIN_MYSQL_USER"),
        MYSQL_PASSWORD=os.getenv("MAIN_MYSQL_PASSWORD"),
        MYSQL_HOST=os.getenv("MAIN_MYSQL_HOST"),
        MYSQL_PORT=int(os.getenv("MAIN_MYSQL_PORT", 3306)),
        MYSQL_DB=os.getenv("MAIN_MYSQL_DB"),
        REDIS_HOST=os.getenv("MAIN_REDIS_HOST", "127.0.0.1"),
        REDIS_PORT=int(os.getenv("MAIN_REDIS_PORT", 6379)),
    )
elif branch == "release":
    settings = Settings(
        MYSQL_USER=os.getenv("RELEASE_MYSQL_USER"),
        MYSQL_PASSWORD=os.getenv("RELEASE_MYSQL_PASSWORD"),
        MYSQL_HOST=os.getenv("RELEASE_MYSQL_HOST"),
        MYSQL_PORT=int(os.getenv("RELEASE_MYSQL_PORT", 3306)),
        MYSQL_DB=os.getenv("RELEASE_MYSQL_DB"),
        REDIS_HOST=os.getenv("RELEASE_REDIS_HOST", "127.0.0.1"),
        REDIS_PORT=int(os.getenv("RELEASE_REDIS_PORT", 6379)),
    )
else:  # dev branch defaults
    settings = Settings(
        MYSQL_USER=os.getenv("DEV_MYSQL_USER", "root"),
        MYSQL_PASSWORD=os.getenv("DEV_MYSQL_PASSWORD", "root"),
        MYSQL_HOST=os.getenv("DEV_MYSQL_HOST", "127.0.0.1"),
        MYSQL_PORT=int(os.getenv("DEV_MYSQL_PORT", 3306)),
        MYSQL_DB=os.getenv("DEV_MYSQL_DB", "super_market_dev"),
        REDIS_HOST=os.getenv("DEV_REDIS_HOST", "127.0.0.1"),
        REDIS_PORT=int(os.getenv("DEV_REDIS_PORT", 6379)),
    )
