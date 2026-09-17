"""Template rendering engine using Jinja2."""

from pathlib import Path
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, StrictUndefined


class TemplateEngine:
    """Manages template loading and rendering."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            undefined=StrictUndefined,
        )

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a single template with context."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_to_file(
        self,
        template_name: str,
        output_path: Path,
        context: Dict[str, Any],
    ) -> None:
        """Render a template directly to a destination file."""
        rendered = self.render(template_name, context)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
