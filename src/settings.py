from pydantic import BaseSettings


class Settings(BaseSettings):
    db_url: str = "postgresql+asyncpg://root:root@localhost:5432/challenger_transaction"
    db_url_test: str = "sqlite+aiosqlite:///tests/db.sqlite"
