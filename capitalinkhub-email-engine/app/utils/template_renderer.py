"""
Template rendering utilities using Jinja2.
"""
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
from app.core.logging import logger


class TemplateRenderer:
    """
    Jinja2 template renderer for email content.

    Handles loading and rendering of email templates with merge fields.
    """

    def __init__(self, template_dir: str = "templates"):
        """
        Initialize template renderer.

        Args:
            template_dir: Directory containing email templates
        """
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,  # Auto-escape HTML for security
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters if needed
        self.env.filters["currency"] = self._currency_filter
        self.env.filters["titlecase"] = lambda s: s.title() if s else ""

        logger.debug(f"Template renderer initialized with directory: {self.template_dir}")

    @staticmethod
    def _currency_filter(value: float) -> str:
        """Format number as currency."""
        try:
            return f"${value:,.2f}"
        except (ValueError, TypeError):
            return str(value)

    def render_template(self, template_path: str, context: Dict[str, Any]) -> str:
        """
        Render a template file with the given context.

        Args:
            template_path: Path to template file (relative to template_dir)
            context: Dictionary of variables for template rendering

        Returns:
            Rendered template as string

        Raises:
            TemplateNotFound: If template file doesn't exist
            Exception: If rendering fails
        """
        try:
            template = self.env.get_template(template_path)
            rendered = template.render(**context)
            logger.debug(f"Successfully rendered template: {template_path}")
            return rendered
        except TemplateNotFound:
            logger.error(f"Template not found: {template_path}")
            raise
        except Exception as e:
            logger.error(f"Error rendering template {template_path}: {e}")
            raise

    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template string with the given context.

        Args:
            template_string: Template string to render
            context: Dictionary of variables for template rendering

        Returns:
            Rendered template as string

        Raises:
            Exception: If rendering fails
        """
        try:
            template = self.env.from_string(template_string)
            rendered = template.render(**context)
            logger.debug("Successfully rendered template string")
            return rendered
        except Exception as e:
            logger.error(f"Error rendering template string: {e}")
            raise

    def template_exists(self, template_path: str) -> bool:
        """
        Check if a template file exists.

        Args:
            template_path: Path to template file (relative to template_dir)

        Returns:
            True if template exists, False otherwise
        """
        full_path = self.template_dir / template_path
        return full_path.exists() and full_path.is_file()

    def get_template_path(self, template_path: str) -> Path:
        """
        Get the full path to a template file.

        Args:
            template_path: Path to template file (relative to template_dir)

        Returns:
            Full Path object
        """
        return self.template_dir / template_path

    def list_templates(self, extension: str = ".html") -> list:
        """
        List all template files in the template directory.

        Args:
            extension: File extension to filter (default: .html)

        Returns:
            List of template file paths
        """
        templates = []
        for file_path in self.template_dir.rglob(f"*{extension}"):
            relative_path = file_path.relative_to(self.template_dir)
            templates.append(str(relative_path))
        return sorted(templates)


class EmailRenderer:
    """
    High-level email rendering service.

    Combines subject and body rendering with merge fields.
    """

    def __init__(self, template_renderer: Optional[TemplateRenderer] = None):
        """
        Initialize email renderer.

        Args:
            template_renderer: TemplateRenderer instance (creates new if None)
        """
        self.renderer = template_renderer or TemplateRenderer()

    def render_email(
        self,
        subject_template: str,
        body_template_path: str,
        merge_fields: Dict[str, Any]
    ) -> tuple:
        """
        Render both subject and body for an email.

        Args:
            subject_template: Subject line template string
            body_template_path: Path to body template file
            merge_fields: Dictionary of merge fields for rendering

        Returns:
            Tuple of (rendered_subject, rendered_body)

        Raises:
            Exception: If rendering fails
        """
        try:
            # Render subject (it's a string template)
            subject = self.renderer.render_string(subject_template, merge_fields)

            # Render body (it's a file template)
            body = self.renderer.render_template(body_template_path, merge_fields)

            return subject, body

        except Exception as e:
            logger.error(f"Error rendering email: {e}")
            raise

    def validate_template(
        self,
        subject_template: str,
        body_template_path: str,
        sample_fields: Optional[Dict[str, Any]] = None
    ) -> tuple:
        """
        Validate that templates can be rendered successfully.

        Args:
            subject_template: Subject line template string
            body_template_path: Path to body template file
            sample_fields: Sample merge fields for validation (uses defaults if None)

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Use sample fields or defaults
            fields = sample_fields or {
                "name": "Test User",
                "email": "test@example.com",
                "first_name": "Test",
                "company_name": "Test Company",
            }

            # Try rendering
            self.render_email(subject_template, body_template_path, fields)

            return True, None

        except TemplateNotFound as e:
            return False, f"Template not found: {e}"
        except Exception as e:
            return False, f"Template error: {e}"
