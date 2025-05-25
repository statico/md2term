"""
Tests for md2term module.
"""

from click.testing import CliRunner

from md2term import convert, main


def test_convert_basic():
    """Test basic conversion functionality."""
    input_text = "# Hello World\n\nThis is a test."
    result = convert(input_text)
    # For now, it should just return the input
    assert result == input_text


def test_cli_basic():
    """Test basic CLI functionality."""
    runner = CliRunner()
    result = runner.invoke(main, input="# Test\n\nHello world!")
    assert result.exit_code == 0
    assert "# Test" in result.output
    assert "Hello world!" in result.output


def test_cli_version():
    """Test CLI version option."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_help():
    """Test CLI help option."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Parse Markdown" in result.output
