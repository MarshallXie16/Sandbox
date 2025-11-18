"""
Tests for template rendering functionality.
"""
import pytest
from pathlib import Path
import tempfile
import shutil

from app.utils.template_renderer import TemplateRenderer, EmailRenderer


@pytest.fixture
def temp_template_dir():
    """Create a temporary template directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def renderer(temp_template_dir):
    """Create a TemplateRenderer with temporary directory."""
    return TemplateRenderer(template_dir=temp_template_dir)


def test_render_string_basic(renderer):
    """Test basic string template rendering."""
    template = "Hello {{ name }}!"
    context = {"name": "World"}
    result = renderer.render_string(template, context)
    assert result == "Hello World!"


def test_render_string_with_missing_variable(renderer):
    """Test rendering with missing variable uses empty string."""
    template = "Hello {{ name }}!"
    context = {}
    result = renderer.render_string(template, context)
    assert result == "Hello !"


def test_render_string_with_default_filter(renderer):
    """Test rendering with default filter."""
    template = "Hello {{ name|default('Guest') }}!"
    context = {}
    result = renderer.render_string(template, context)
    assert result == "Hello Guest!"


def test_render_template_file(renderer, temp_template_dir):
    """Test rendering a template file."""
    # Create a template file
    template_path = Path(temp_template_dir) / "test.html"
    template_path.write_text("<h1>Hello {{ name }}!</h1>")

    context = {"name": "World"}
    result = renderer.render_template("test.html", context)
    assert result == "<h1>Hello World!</h1>"


def test_template_exists(renderer, temp_template_dir):
    """Test template_exists method."""
    # Create a template file
    template_path = Path(temp_template_dir) / "test.html"
    template_path.write_text("<h1>Test</h1>")

    assert renderer.template_exists("test.html") is True
    assert renderer.template_exists("nonexistent.html") is False


def test_currency_filter(renderer):
    """Test custom currency filter."""
    template = "Price: {{ price|currency }}"
    context = {"price": 1234.56}
    result = renderer.render_string(template, context)
    assert result == "Price: $1,234.56"


def test_titlecase_filter(renderer):
    """Test custom titlecase filter."""
    template = "Name: {{ name|titlecase }}"
    context = {"name": "john smith"}
    result = renderer.render_string(template, context)
    assert result == "Name: John Smith"


def test_email_renderer(temp_template_dir):
    """Test EmailRenderer for rendering subject and body."""
    # Create a body template
    template_path = Path(temp_template_dir) / "email.html"
    template_path.write_text("<p>Hello {{ first_name }}!</p>")

    email_renderer = EmailRenderer(TemplateRenderer(template_dir=temp_template_dir))

    subject_template = "Welcome {{ first_name }}!"
    merge_fields = {"first_name": "John"}

    subject, body = email_renderer.render_email(
        subject_template,
        "email.html",
        merge_fields
    )

    assert subject == "Welcome John!"
    assert body == "<p>Hello John!</p>"


def test_email_renderer_validation_success(temp_template_dir):
    """Test template validation with valid templates."""
    # Create a body template
    template_path = Path(temp_template_dir) / "email.html"
    template_path.write_text("<p>Hello {{ name }}!</p>")

    email_renderer = EmailRenderer(TemplateRenderer(template_dir=temp_template_dir))

    is_valid, error = email_renderer.validate_template(
        "Hello {{ name }}!",
        "email.html"
    )

    assert is_valid is True
    assert error is None


def test_email_renderer_validation_missing_template(temp_template_dir):
    """Test template validation with missing template file."""
    email_renderer = EmailRenderer(TemplateRenderer(template_dir=temp_template_dir))

    is_valid, error = email_renderer.validate_template(
        "Hello {{ name }}!",
        "nonexistent.html"
    )

    assert is_valid is False
    assert "not found" in error.lower()
