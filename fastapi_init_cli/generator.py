"""Project generation engine that orchestrates file scaffolding from templates."""

from pathlib import Path
from typing import List

from fastapi_init_cli.context import ProjectContext
from fastapi_init_cli.template_engine import TemplateEngine


class ProjectGenerator:
    """Orchestrates creating the FastAPI project files and directories."""

    def __init__(self, context: ProjectContext, engine: TemplateEngine | None = None) -> None:
        self.context = context
        self.engine = engine or TemplateEngine()
        self.target_dir = context.target_dir
        self.template_ctx = {
            "ctx": context,
            "project_name": context.project_name,
            "database": context.database.value,
            "architecture": context.architecture.value,
            "is_async": context.is_async,
            "auth_enabled": context.auth_enabled,
            "auth_method": context.auth_method.value,
            "include_google_oauth": context.include_google_oauth,
            "include_email_verification": context.include_email_verification,
            "include_forgot_password": context.include_forgot_password,
            "include_alembic": context.include_alembic,
            "alembic": context.include_alembic,
            "include_auth": context.auth_enabled,
            "include_email_otp": context.include_email_verification,
            "db_driver": context.db_driver,
            "default_database_url": context.default_database_url,
            "default_database_url_example": context.default_database_url_example,
            "needs_email_service": context.needs_email_service,
            "needs_otp_model": context.needs_otp_model,
        }

    def generate(self) -> List[Path]:
        """Generate all files according to project configuration."""
        generated_files: List[Path] = []
        self.target_dir.mkdir(parents=True, exist_ok=True)

        # 1. Root files
        root_files = [
            ("root/env.example.jinja", self.target_dir / ".env.example"),
            ("root/gitignore.jinja", self.target_dir / ".gitignore"),
            ("root/README.md.jinja", self.target_dir / "README.md"),
            ("root/requirements.txt.jinja", self.target_dir / "requirements.txt"),
        ]

        for tmpl, dest in root_files:
            self.engine.render_to_file(tmpl, dest, self.template_ctx)
            generated_files.append(dest)

        # 2. Core App files
        app_files = [
            ("app/__init__.py.jinja", self.target_dir / "app" / "__init__.py"),
            ("app/main.py.jinja", self.target_dir / "app" / "main.py"),
            ("app/core/__init__.py.jinja", self.target_dir / "app" / "core" / "__init__.py"),
            ("app/core/config.py.jinja", self.target_dir / "app" / "core" / "config.py"),
            ("app/core/database.py.jinja", self.target_dir / "app" / "core" / "database.py"),
            ("app/core/dependencies.py.jinja", self.target_dir / "app" / "core" / "dependencies.py"),
            ("app/models/__init__.py.jinja", self.target_dir / "app" / "models" / "__init__.py"),
            ("app/models/base.py.jinja", self.target_dir / "app" / "models" / "base.py"),
            ("app/schemas/__init__.py.jinja", self.target_dir / "app" / "schemas" / "__init__.py"),
            ("app/services/__init__.py.jinja", self.target_dir / "app" / "services" / "__init__.py"),
            ("app/routes/__init__.py.jinja", self.target_dir / "app" / "routes" / "__init__.py"),
            ("app/routes/router.py.jinja", self.target_dir / "app" / "routes" / "router.py"),
            ("app/routes/v1/__init__.py.jinja", self.target_dir / "app" / "routes" / "v1" / "__init__.py"),
            ("app/routes/v1/health.py.jinja", self.target_dir / "app" / "routes" / "v1" / "health.py"),
        ]

        # Conditional Auth Files
        if self.context.auth_enabled:
            app_files.extend([
                ("app/core/security.py.jinja", self.target_dir / "app" / "core" / "security.py"),
                ("app/models/user.py.jinja", self.target_dir / "app" / "models" / "user.py"),
                ("app/schemas/user.py.jinja", self.target_dir / "app" / "schemas" / "user.py"),
                ("app/schemas/auth.py.jinja", self.target_dir / "app" / "schemas" / "auth.py"),
                ("app/services/user_service.py.jinja", self.target_dir / "app" / "services" / "user_service.py"),
                ("app/services/auth_service.py.jinja", self.target_dir / "app" / "services" / "auth_service.py"),
                ("app/routes/v1/users.py.jinja", self.target_dir / "app" / "routes" / "v1" / "users.py"),
                ("app/routes/v1/auth.py.jinja", self.target_dir / "app" / "routes" / "v1" / "auth.py"),
            ])

        # Conditional OTP & Email Files
        if self.context.needs_otp_model:
            app_files.extend([
                ("app/models/otp.py.jinja", self.target_dir / "app" / "models" / "otp.py"),
                ("app/schemas/otp.py.jinja", self.target_dir / "app" / "schemas" / "otp.py"),
                ("app/services/otp_service.py.jinja", self.target_dir / "app" / "services" / "otp_service.py"),
            ])

        if self.context.needs_email_service:
            app_files.append(
                ("app/services/email_service.py.jinja", self.target_dir / "app" / "services" / "email_service.py")
            )

        for tmpl, dest in app_files:
            self.engine.render_to_file(tmpl, dest, self.template_ctx)
            generated_files.append(dest)

        # 3. Alembic Migrations
        if self.context.include_alembic:
            alembic_files = [
                ("root/alembic.ini.jinja", self.target_dir / "alembic.ini"),
                ("alembic/env.py.jinja", self.target_dir / "alembic" / "env.py"),
                ("alembic/script.py.mako.jinja", self.target_dir / "alembic" / "script.py.mako"),
            ]
            for tmpl, dest in alembic_files:
                self.engine.render_to_file(tmpl, dest, self.template_ctx)
                generated_files.append(dest)
            
            # Versions folder
            versions_dir = self.target_dir / "alembic" / "versions"
            versions_dir.mkdir(parents=True, exist_ok=True)
            gitkeep = versions_dir / ".gitkeep"
            gitkeep.write_text("", encoding="utf-8")
            generated_files.append(gitkeep)

        return generated_files
