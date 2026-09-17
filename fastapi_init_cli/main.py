"""CLI Entry point for fastapi-init-cli."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from fastapi_init_cli import __version__
from fastapi_init_cli.generator import ProjectGenerator
from fastapi_init_cli.prompts import collect_project_configuration

app = typer.Typer(
    name="fastapi-init-cli",
    help="Production-ready interactive CLI generator for modern FastAPI backends.",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold cyan]fastapi-init-cli[/bold cyan] version: [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    project_name: Optional[str] = typer.Argument(
        None,
        help="Optional name of the project folder to scaffold.",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        help="Show fastapi-init-cli version and exit.",
    ),
) -> None:
    """Interactively scaffold a new FastAPI project."""
    try:
        context = collect_project_configuration(default_name=project_name)
        if context is None:
            sys.exit(0)

        console.print()
        with console.status("[bold green]Scaffolding your FastAPI project...[/bold green]", spinner="dots"):
            generator = ProjectGenerator(context)
            generated_files = generator.generate()

        # Success message
        console.print(f"[bold green]✓ Successfully created FastAPI project at:[/bold green] [bold cyan]{context.target_dir}[/bold cyan]\n")

        # Next steps instructions
        next_steps_text = Text()
        next_steps_text.append("1. Navigate to your project:\n", style="bold")
        next_steps_text.append(f"   cd {context.project_name}\n\n", style="cyan")
        
        next_steps_text.append("2. Create and activate a virtual environment:\n", style="bold")
        next_steps_text.append("   python -m venv .venv\n", style="cyan")
        next_steps_text.append("   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate\n\n", style="dim")
        
        next_steps_text.append("3. Install dependencies:\n", style="bold")
        next_steps_text.append("   pip install -r requirements.txt\n\n", style="cyan")
        
        step_num = 4
        if context.include_alembic:
            next_steps_text.append(f"{step_num}. Database setup (Alembic migrations):\n", style="bold")
            next_steps_text.append("   # 1. Generate the initial migration from models\n", style="dim")
            next_steps_text.append("   alembic revision --autogenerate -m \"Initial migration\"\n\n", style="cyan")
            next_steps_text.append("   # 2. Apply migrations to create database tables\n", style="dim")
            next_steps_text.append("   alembic upgrade head\n\n", style="cyan")
            step_num += 1

        next_steps_text.append(f"{step_num}. Start the development server:\n", style="bold")
        next_steps_text.append("   uvicorn app.main:app --reload\n", style="green")

        panel = Panel(
            next_steps_text,
            title="[bold yellow]Next Steps[/bold yellow]",
            border_style="green",
            padding=(1, 2),
        )
        console.print(panel)
        console.print("[dim]Happy coding with FastAPI![/dim]\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Generation cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error during generation:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()
