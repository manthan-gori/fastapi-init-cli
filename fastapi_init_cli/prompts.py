"""Interactive questionnaire and prompt flows for fastapi-init-cli."""

import re
import sys
from pathlib import Path
from typing import Optional

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from fastapi_init_cli.context import (
    ArchitectureMode,
    AuthMethod,
    DatabaseType,
    ProjectContext,
)

console = Console()


def show_welcome_banner() -> None:
    """Render the welcome banner."""
    title = Text("FastAPI Init CLI", style="bold cyan")
    subtitle = Text("\nCreate a production-ready FastAPI backend in seconds.", style="dim")
    panel = Panel(
        title + subtitle,
        border_style="bright_blue",
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


def validate_project_name(name: str) -> bool | str:
    """Validate project / directory name."""
    name = name.strip()
    if not name:
        return "Project name cannot be empty."
    if not re.match(r"^[a-zA-Z0-9_\-\.]+$", name):
        return "Project name can only contain letters, numbers, underscores, dashes, and periods."
    return True


def check_existing_directory(target_path: Path) -> bool:
    """Check if directory exists and is non-empty; prompt to continue if needed."""
    if target_path.exists() and any(target_path.iterdir()):
        console.print(
            f"[yellow]Warning:[/yellow] Directory '[bold]{target_path.name}[/bold]' already exists and is not empty."
        )
        should_continue = questionary.confirm(
            f"Directory '{target_path.name}' already exists. Do you want to continue?",
            default=False,
        ).ask()
        if should_continue is None or not should_continue:
            console.print("[red]Aborted project generation.[/red]")
            return False
    return True


def collect_project_configuration(
    default_name: Optional[str] = None,
) -> Optional[ProjectContext]:
    """Interactively collect all configuration options from the developer."""
    show_welcome_banner()

    # 1. Project / Folder name
    project_name = questionary.text(
        "Project / Folder name:",
        default=default_name or "backend",
        validate=validate_project_name,
    ).ask()

    if project_name is None:
        return None

    project_name = project_name.strip()
    target_dir = Path(project_name).resolve()

    if not check_existing_directory(target_dir):
        return None

    # 2. Database
    db_choice = questionary.select(
        "Select database engine:",
        choices=[
            DatabaseType.POSTGRESQL.value,
            DatabaseType.MYSQL.value,
            DatabaseType.SQLITE.value,
        ],
        default=DatabaseType.POSTGRESQL.value,
    ).ask()

    if db_choice is None:
        return None

    database = DatabaseType(db_choice)

    # 3. Architecture Mode (Async / Sync)
    arch_choice = questionary.select(
        "Select execution architecture:",
        choices=[
            ArchitectureMode.ASYNC.value,
            ArchitectureMode.SYNC.value,
        ],
        default=ArchitectureMode.ASYNC.value,
    ).ask()

    if arch_choice is None:
        return None

    architecture = ArchitectureMode(arch_choice)

    # 4. Authentication
    auth_enabled = questionary.confirm(
        "Do you want authentication?",
        default=True,
    ).ask()

    if auth_enabled is None:
        return None

    auth_method = AuthMethod.JWT
    include_google_oauth = False
    include_email_verification = False
    include_forgot_password = False

    if auth_enabled:
        # 5. Auth Method
        method_choice = questionary.select(
            "Select authentication method:",
            choices=[
                AuthMethod.JWT.value,
                AuthMethod.JWT_GOOGLE.value,
            ],
            default=AuthMethod.JWT.value,
        ).ask()

        if method_choice is None:
            return None

        auth_method = AuthMethod(method_choice)
        include_google_oauth = auth_method == AuthMethod.JWT_GOOGLE

        # 6. Email verification
        include_email_verification = questionary.confirm(
            "Do you want email verification? (OTP-based)",
            default=True,
        ).ask()

        if include_email_verification is None:
            return None

        # 7. Forgot password
        include_forgot_password = questionary.confirm(
            "Do you want forgot-password functionality? (OTP-based)",
            default=True,
        ).ask()

        if include_forgot_password is None:
            return None

    # 8. Database Migrations (Alembic)
    include_alembic = questionary.confirm(
        "Do you want database migrations with Alembic?",
        default=True,
    ).ask()

    if include_alembic is None:
        return None

    return ProjectContext(
        project_name=project_name,
        target_dir=target_dir,
        database=database,
        architecture=architecture,
        auth_enabled=auth_enabled,
        auth_method=auth_method,
        include_google_oauth=include_google_oauth,
        include_email_verification=include_email_verification,
        include_forgot_password=include_forgot_password,
        include_alembic=include_alembic,
    )
