"""
md2term - Parse Markdown and turn it into nicely-formatted text for terminal display.
"""

import sys
import os
import shutil
import re
from typing import Optional, TextIO, List, Dict, Any
from io import StringIO
import click
import mistune
from rich.console import Console
from rich.text import Text
from rich.syntax import Syntax
from rich.rule import Rule
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich import box


__version__ = "0.1.0"


class TerminalRenderer:
    """Custom renderer for converting markdown AST to Rich terminal output."""

    def __init__(self, console: Console):
        self.console = console
        self.in_code_block = False
        self.code_block_lines = []
        self.code_block_lang = None

    def render(self, tokens: List[Dict[str, Any]]) -> None:
        """Render a list of markdown tokens to the terminal."""
        for i, token in enumerate(tokens):
            # Add spacing between elements (but not before the first one)
            if i > 0 and token['type'] != 'blank_line':
                self.console.print()
            self._render_token(token)

    def _render_token(self, token: Dict[str, Any]) -> None:
        """Render a single markdown token."""
        token_type = token['type']

        if token_type == 'heading':
            self._render_heading(token)
        elif token_type == 'paragraph':
            self._render_paragraph(token)
        elif token_type == 'block_text':
            self._render_block_text(token)
        elif token_type == 'block_code':
            self._render_code_block(token)
        elif token_type == 'block_quote':
            self._render_blockquote(token)
        elif token_type == 'list':
            self._render_list(token)
        elif token_type == 'thematic_break':
            self._render_thematic_break()
        elif token_type == 'blank_line':
            self.console.print()

    def _render_heading(self, token: Dict[str, Any]) -> None:
        """Render a heading with appropriate styling."""
        level = token['attrs']['level']
        text = self._render_inline_tokens(token['children'])

        # Different colors and styles for different heading levels
        if level == 1:
            # Bright cyan, bold, with rule above and below
            self.console.print(Rule(style="bright_cyan"))
            self.console.print(text, style="bold bright_cyan", justify="center")
            self.console.print(Rule(style="bright_cyan"))
        elif level == 2:
            # Bright blue, bold, with rule below
            self.console.print(text, style="bold bright_blue")
            self.console.print(Rule(style="blue"))
        elif level == 3:
            # Bright magenta, bold
            self.console.print(text, style="bold bright_magenta")
        elif level == 4:
            # Bright yellow, bold
            self.console.print(text, style="bold bright_yellow")
        elif level == 5:
            # Bright green, bold
            self.console.print(text, style="bold bright_green")
        else:  # level 6
            # Bright white, bold
            self.console.print(text, style="bold bright_white")

    def _render_paragraph(self, token: Dict[str, Any]) -> None:
        """Render a paragraph with proper word wrapping."""
        text = self._render_inline_tokens(token['children'])
        self.console.print(text)

    def _render_block_text(self, token: Dict[str, Any]) -> None:
        """Render block text (used in list items and other contexts)."""
        text = self._render_inline_tokens(token['children'])
        self.console.print(text, end="")

    def _render_code_block(self, token: Dict[str, Any]) -> None:
        """Render a code block with syntax highlighting."""
        code = token['raw'].rstrip()
        lang = token['attrs'].get('info', '').strip() or 'text'

        try:
            # Use Rich's syntax highlighting
            syntax = Syntax(code, lang, theme="monokai", line_numbers=False,
                          background_color="default")
            panel = Panel(syntax, border_style="dim", padding=(0, 1))
            self.console.print(panel)
        except Exception:
            # Fallback to simple code formatting if syntax highlighting fails
            panel = Panel(code, border_style="dim", style="dim white on black",
                         padding=(0, 1))
            self.console.print(panel)

    def _render_blockquote(self, token: Dict[str, Any]) -> None:
        """Render a blockquote with indentation and styling."""
        # Render children into a string buffer
        old_console = self.console
        buffer = StringIO()
        temp_console = Console(file=buffer, width=self.console.size.width - 4)
        self.console = temp_console

        for child in token['children']:
            self._render_token(child)

        self.console = old_console
        content = buffer.getvalue().rstrip()

        # Create GitHub-style blockquote with left border only
        lines = content.split('\n')
        for line in lines:
            if line.strip():  # Only add border to non-empty lines
                self.console.print(f"[dim blue]│[/] [italic dim blue]{line}[/]")
            else:
                self.console.print(f"[dim blue]│[/]")

    def _render_list(self, token: Dict[str, Any]) -> None:
        """Render ordered or unordered lists."""
        ordered = token['attrs'].get('ordered', False)
        start = token['attrs'].get('start', 1)

        for i, item in enumerate(token['children']):
            if ordered:
                marker = f"{start + i}."
                marker_style = "bold cyan"
            else:
                marker = "•"
                marker_style = "bold yellow"

            # Render list item content
            old_console = self.console
            buffer = StringIO()
            temp_console = Console(file=buffer, width=self.console.size.width - 4)
            self.console = temp_console

            for child in item['children']:
                self._render_token(child)

            self.console = old_console
            content = buffer.getvalue().rstrip()

            # Print with proper indentation
            self.console.print(f"[{marker_style}]{marker}[/] {content}")

        self.console.print()

    def _render_thematic_break(self) -> None:
        """Render a horizontal rule."""
        self.console.print(Rule(style="dim"))

    def _render_inline_tokens(self, tokens: List[Dict[str, Any]]) -> Text:
        """Render inline tokens (emphasis, strong, code, links, etc.) into Rich Text."""
        text = Text()

        for token in tokens:
            if token['type'] == 'text':
                text.append(token['raw'])
            elif token['type'] == 'emphasis':
                child_text = self._render_inline_tokens(token['children'])
                child_text.stylize("italic")
                text.append_text(child_text)
            elif token['type'] == 'strong':
                child_text = self._render_inline_tokens(token['children'])
                child_text.stylize("bold")
                text.append_text(child_text)
            elif token['type'] == 'codespan':
                text.append(token['raw'], style="bold red on grey23")
            elif token['type'] == 'link':
                link_text = self._render_inline_tokens(token['children'])
                url = token['attrs']['url']
                link_text.stylize("bold blue underline")
                text.append_text(link_text)
                text.append(f" ({url})", style="dim blue")
            elif token['type'] == 'image':
                alt_text = self._render_inline_tokens(token['children']).plain
                url = token['attrs']['url']
                text.append(f"[IMAGE: {alt_text}]", style="bold magenta")
                text.append(f" ({url})", style="dim magenta")
            elif token['type'] == 'linebreak':
                text.append("\n")
            elif token['type'] == 'softbreak':
                text.append(" ")

        return text


def convert(markdown_text: str, width: Optional[int] = None) -> None:
    """
    Convert markdown text to terminal-formatted text and print it.

    Args:
        markdown_text: The markdown content to convert
        width: Terminal width override (defaults to current terminal width)
    """
    # Get terminal width
    if width is None:
        width = shutil.get_terminal_size().columns

    # Create console with proper width
    console = Console(width=width, force_terminal=True)

    # Parse markdown
    markdown = mistune.create_markdown(renderer=None)
    tokens = markdown(markdown_text)

    # Render to terminal
    renderer = TerminalRenderer(console)
    renderer.render(tokens)


def process_stream(input_stream: TextIO, width: Optional[int] = None) -> None:
    """
    Process markdown from a stream line by line, handling code blocks properly.

    This function reads the input stream and processes it in a way that handles
    multi-line constructs like code blocks correctly.
    """
    buffer = []
    in_code_block = False
    code_fence_pattern = re.compile(r'^```')

    for line in input_stream:
        buffer.append(line)

        # Check for code fence
        if code_fence_pattern.match(line.strip()):
            in_code_block = not in_code_block

        # If we're not in a code block and hit a blank line, process the buffer
        if not in_code_block and line.strip() == '':
            if buffer:
                content = ''.join(buffer)
                if content.strip():  # Only process non-empty content
                    convert(content, width)
                buffer = []

    # Process any remaining content
    if buffer:
        content = ''.join(buffer)
        if content.strip():
            convert(content, width)


@click.command()
@click.argument("input_file", type=click.File("r"), required=False)
@click.option("--width", "-w", type=int, help="Override terminal width")
@click.version_option(version=__version__)
def main(input_file: Optional[TextIO], width: Optional[int]) -> None:
    """
    Parse Markdown and turn it into nicely-formatted text for terminal display.

    If no INPUT_FILE is provided, reads from stdin.

    Features:
    - 256-color support with different shades for headers
    - Syntax highlighting for code blocks
    - Proper word wrapping based on terminal width
    - Support for all standard markdown elements
    - Streaming input processing
    """
    try:
        # Read the input
        if input_file is None:
            # For stdin, we need to process it as a stream to handle large inputs
            # and code blocks properly
            process_stream(sys.stdin, width)
        else:
            # For files, we can read the entire content at once
            content = input_file.read()
            convert(content, width)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
