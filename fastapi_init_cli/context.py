"""Project context model holding all configuration options for scaffolding."""

from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field


class DatabaseType(str, Enum):
    POSTGRESQL = "PostgreSQL"
    MYSQL = "MySQL"
    SQLITE = "SQLite"


class ArchitectureMode(str, Enum):
    ASYNC = "Async"
    SYNC = "Sync"


class AuthMethod(str, Enum):
    JWT = "JWT"
    JWT_GOOGLE = "JWT + Google OAuth"


class ProjectContext(BaseModel):
    project_name: str = Field(default="backend")
    target_dir: Path = Field(default=Path("backend"))
    database: DatabaseType = Field(default=DatabaseType.POSTGRESQL)
    architecture: ArchitectureMode = Field(default=ArchitectureMode.ASYNC)
    
    # Auth configuration
    auth_enabled: bool = Field(default=True)
    auth_method: AuthMethod = Field(default=AuthMethod.JWT)
    include_google_oauth: bool = Field(default=False)
    include_email_verification: bool = Field(default=True)
    include_forgot_password: bool = Field(default=True)
    
    # Migrations
    include_alembic: bool = Field(default=True)

    @property
    def is_async(self) -> bool:
        return self.architecture == ArchitectureMode.ASYNC

    @property
    def db_driver(self) -> str:
        if self.database == DatabaseType.POSTGRESQL:
            return "asyncpg" if self.is_async else "psycopg"
        elif self.database == DatabaseType.MYSQL:
            return "aiomysql" if self.is_async else "pymysql"
        elif self.database == DatabaseType.SQLITE:
            return "aiosqlite" if self.is_async else "sqlite"
        return "asyncpg"

    @property
    def default_database_url(self) -> str:
        if self.database == DatabaseType.POSTGRESQL:
            if self.is_async:
                return "postgresql+asyncpg://postgres:postgres@localhost:5432/app_db"
            return "postgresql+psycopg://postgres:postgres@localhost:5432/app_db"
        elif self.database == DatabaseType.MYSQL:
            if self.is_async:
                return "mysql+aiomysql://root:password@localhost:3306/app_db"
            return "mysql+pymysql://root:password@localhost:3306/app_db"
        elif self.database == DatabaseType.SQLITE:
            if self.is_async:
                return "sqlite+aiosqlite:///./app.db"
            return "sqlite:///./app.db"
        return "postgresql+asyncpg://postgres:postgres@localhost:5432/app_db"

    @property
    def default_database_url_example(self) -> str:
        if self.database == DatabaseType.POSTGRESQL:
            if self.is_async:
                return "postgresql+asyncpg://user:password@localhost:5432/dbname"
            return "postgresql+psycopg://user:password@localhost:5432/dbname"
        elif self.database == DatabaseType.MYSQL:
            if self.is_async:
                return "mysql+aiomysql://user:password@localhost:3306/dbname"
            return "mysql+pymysql://user:password@localhost:3306/dbname"
        elif self.database == DatabaseType.SQLITE:
            if self.is_async:
                return "sqlite+aiosqlite:///./app.db"
            return "sqlite:///./app.db"
        return "postgresql+asyncpg://user:password@localhost:5432/dbname"

    @property
    def needs_email_service(self) -> bool:
        return self.auth_enabled and (self.include_email_verification or self.include_forgot_password)

    @property
    def needs_otp_model(self) -> bool:
        return self.auth_enabled and (self.include_email_verification or self.include_forgot_password)
