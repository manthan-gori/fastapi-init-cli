import ast
from pathlib import Path
import pytest

from fastapi_init_cli.context import (
    ArchitectureMode,
    AuthMethod,
    DatabaseType,
    ProjectContext,
)
from fastapi_init_cli.generator import ProjectGenerator


def validate_python_files(directory: Path) -> None:
    """Ensure all generated .py files have valid Python syntax."""
    py_files = list(directory.rglob("*.py"))
    assert len(py_files) > 0, "No Python files were generated!"
    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8")
        try:
            ast.parse(content, filename=str(py_file))
        except SyntaxError as e:
            pytest.fail(f"Syntax error in generated file {py_file}:\n{e}\n\nContent:\n{content}")


def test_full_async_postgres_scaffold(tmp_path: Path) -> None:
    """Test generating a full-featured async PostgreSQL project."""
    target_dir = tmp_path / "backend_full"
    context = ProjectContext(
        project_name="backend_full",
        target_dir=target_dir,
        database=DatabaseType.POSTGRESQL,
        architecture=ArchitectureMode.ASYNC,
        auth_enabled=True,
        auth_method=AuthMethod.JWT_GOOGLE,
        include_google_oauth=True,
        include_email_verification=True,
        include_forgot_password=True,
        include_alembic=True,
    )

    generator = ProjectGenerator(context)
    generated = generator.generate()

    assert len(generated) > 0
    assert not (target_dir / ".env").exists()
    assert (target_dir / ".env.example").exists()
    assert (target_dir / ".gitignore").exists()
    assert (target_dir / "README.md").exists()
    assert (target_dir / "requirements.txt").exists()
    assert (target_dir / "alembic.ini").exists()
    assert (target_dir / "alembic" / "env.py").exists()
    assert (target_dir / "app" / "main.py").exists()
    assert (target_dir / "app" / "models" / "user.py").exists()
    assert (target_dir / "app" / "models" / "otp.py").exists()
    assert (target_dir / "app" / "services" / "email_service.py").exists()
    assert (target_dir / "app" / "routes" / "v1" / "auth.py").exists()
    assert (target_dir / "app" / "routes" / "v1" / "users.py").exists()
    assert (target_dir / "app" / "routes" / "v1" / "health.py").exists()

    readme = (target_dir / "README.md").read_text()
    assert 'alembic revision --autogenerate -m "Initial migration"' in readme
    assert "alembic upgrade head" in readme
    assert "https://www.linkedin.com/in/manthan-gori/" in readme
    assert "## API Endpoints" in readme

    reqs = (target_dir / "requirements.txt").read_text()
    assert "asyncpg" in reqs
    assert "alembic" in reqs
    assert "httpx" in reqs
    assert "python-jose" in reqs
    assert "pydantic[email]" in reqs
    assert "email-validator" not in reqs
    assert "passlib" not in reqs
    assert "bcrypt" in reqs

    security_py = (target_dir / "app" / "core" / "security.py").read_text()
    assert "passlib" not in security_py
    assert "import bcrypt" in security_py
    assert "pwd_bytes = plain_password.encode(\"utf-8\")[:72]" in security_py

    deps_py = (target_dir / "app" / "core" / "dependencies.py").read_text()
    assert "HTTPBearer" in deps_py
    assert "HTTPAuthorizationCredentials" in deps_py
    assert "OAuth2PasswordBearer" not in deps_py

    auth_py = (target_dir / "app" / "routes" / "v1" / "auth.py").read_text()
    assert '@router.get("/me"' not in auth_py

    users_py = (target_dir / "app" / "routes" / "v1" / "users.py").read_text()
    assert '@router.get("/me"' in users_py

    user_schema_py = (target_dir / "app" / "schemas" / "user.py").read_text()
    assert 'examples=["password"]' in user_schema_py

    auth_schema_py = (target_dir / "app" / "schemas" / "auth.py").read_text()
    assert 'password: str = Field(..., examples=["password"])' in auth_schema_py

    otp_schema_py = (target_dir / "app" / "schemas" / "otp.py").read_text()
    assert 'examples=["new_password"]' in otp_schema_py

    otp_model_py = (target_dir / "app" / "models" / "otp.py").read_text()
    assert "if expires.tzinfo is None:" in otp_model_py
    assert "expires = expires.replace(tzinfo=timezone.utc)" in otp_model_py

    env_content = (target_dir / ".env.example").read_text()
    assert "postgresql+asyncpg://" in env_content
    assert "JWT_SECRET_KEY=super-secret-jwt-key-change-this-in-production" in env_content
    assert "GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com" in env_content
    assert "SMTP_HOST=smtp.gmail.com" in env_content

    validate_python_files(target_dir)


def test_minimal_sync_sqlite_scaffold(tmp_path: Path) -> None:
    """Test generating a minimal sync SQLite project (No auth, No alembic)."""
    target_dir = tmp_path / "backend_minimal"
    context = ProjectContext(
        project_name="backend_minimal",
        target_dir=target_dir,
        database=DatabaseType.SQLITE,
        architecture=ArchitectureMode.SYNC,
        auth_enabled=False,
        include_alembic=False,
    )

    generator = ProjectGenerator(context)
    generated = generator.generate()

    assert len(generated) > 0
    assert not (target_dir / ".env").exists()
    assert (target_dir / ".env.example").exists()
    assert (target_dir / "app" / "main.py").exists()
    assert not (target_dir / "alembic.ini").exists()
    assert not (target_dir / "app" / "models" / "user.py").exists()
    assert not (target_dir / "app" / "models" / "otp.py").exists()
    assert not (target_dir / "app" / "services" / "email_service.py").exists()
    assert not (target_dir / "app" / "routes" / "v1" / "auth.py").exists()

    reqs = (target_dir / "requirements.txt").read_text()
    assert "fastapi" in reqs
    assert "pydantic>=" in reqs
    assert "pydantic[email]" not in reqs
    assert "email-validator" not in reqs
    assert "alembic" not in reqs
    assert "python-jose" not in reqs
    main_py = (target_dir / "app" / "main.py").read_text()
    assert "Base.metadata.create_all(bind=engine)" in main_py
    assert "from app.models.base import Base" in main_py
    assert "from app.core.database import engine" in main_py
    assert "import app.models.user" not in main_py

    validate_python_files(target_dir)


def test_async_mysql_jwt_scaffold(tmp_path: Path) -> None:
    """Test generating an async MySQL project with standard JWT (no google oauth, no email)."""
    target_dir = tmp_path / "backend_mysql"
    context = ProjectContext(
        project_name="backend_mysql",
        target_dir=target_dir,
        database=DatabaseType.MYSQL,
        architecture=ArchitectureMode.ASYNC,
        auth_enabled=True,
        auth_method=AuthMethod.JWT,
        include_google_oauth=False,
        include_email_verification=False,
        include_forgot_password=False,
        include_alembic=True,
    )

    generator = ProjectGenerator(context)
    generator.generate()

    assert (target_dir / "app" / "models" / "user.py").exists()
    assert not (target_dir / "app" / "models" / "otp.py").exists()
    assert not (target_dir / "app" / "services" / "email_service.py").exists()

    reqs = (target_dir / "requirements.txt").read_text()
    assert "aiomysql" in reqs
    assert "httpx" not in reqs

    validate_python_files(target_dir)


def test_sync_postgres_jwt_otp_scaffold(tmp_path: Path) -> None:
    """Test generating a sync PostgreSQL project with JWT and OTP flows."""
    target_dir = tmp_path / "backend_sync_pg"
    context = ProjectContext(
        project_name="backend_sync_pg",
        target_dir=target_dir,
        database=DatabaseType.POSTGRESQL,
        architecture=ArchitectureMode.SYNC,
        auth_enabled=True,
        auth_method=AuthMethod.JWT,
        include_google_oauth=False,
        include_email_verification=True,
        include_forgot_password=True,
        include_alembic=True,
    )

    generator = ProjectGenerator(context)
    generator.generate()

    assert (target_dir / "app" / "models" / "user.py").exists()
    assert (target_dir / "app" / "models" / "otp.py").exists()
    assert (target_dir / "app" / "services" / "email_service.py").exists()

    reqs = (target_dir / "requirements.txt").read_text()
    assert "psycopg" in reqs
    assert "asyncpg" not in reqs

    validate_python_files(target_dir)


def test_async_sqlite_no_alembic_with_auth(tmp_path: Path) -> None:
    """Test generating an async project without Alembic to ensure async table creation is rendered."""
    target_dir = tmp_path / "backend_async_no_alembic"
    context = ProjectContext(
        project_name="backend_async_no_alembic",
        target_dir=target_dir,
        database=DatabaseType.SQLITE,
        architecture=ArchitectureMode.ASYNC,
        auth_enabled=True,
        include_email_verification=True,
        include_forgot_password=True,
        include_alembic=False,
    )

    generator = ProjectGenerator(context)
    generator.generate()

    main_py = (target_dir / "app" / "main.py").read_text()
    assert "from app.core.database import engine" in main_py
    assert "from app.models.base import Base" in main_py
    assert "import app.models.user" in main_py
    assert "import app.models.otp" in main_py
    assert "async with engine.begin() as conn:" in main_py
    assert "await conn.run_sync(Base.metadata.create_all)" in main_py

    validate_python_files(target_dir)


def test_security_bcrypt_hashing():
    """Verify that the bcrypt implementation hashes and verifies correctly, even with >72 byte passwords."""
    import bcrypt

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))

    def get_password_hash(password: str) -> str:
        pwd_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

    # Standard password
    pwd = "my_secure_password_123!"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong_password", hashed) is False

    # Password longer than 72 bytes (should not raise ValueError)
    long_pwd = "a" * 150
    long_hashed = get_password_hash(long_pwd)
    assert verify_password(long_pwd, long_hashed) is True
    assert verify_password("a" * 72, long_hashed) is True  # Truncated match
    assert verify_password("b" * 150, long_hashed) is False

