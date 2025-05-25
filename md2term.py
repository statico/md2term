"""
md2term - Parse Markdown and turn it into nicely-formatted text for terminal display.
"""

import sys
import os
import shutil
import re
import time
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
            # Only add spacing between non-blank-line elements
            if i > 0 and token['type'] != 'blank_line' and tokens[i-1]['type'] != 'blank_line':
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
        # Handle different token structures - some have 'attrs', others have 'info' directly
        if 'attrs' in token:
            lang = token['attrs'].get('info', '').strip() or 'text'
        else:
            lang = token.get('info', '').strip() or 'text'

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


class StreamingRenderer:
    """Unified renderer that handles both streaming and non-streaming with minimal flickering."""

    def __init__(self, console: Console):
        self.console = console
        self.buffer = ""
        self.last_output_lines = 0
        self.last_was_incomplete = False

        # Patterns for detecting incomplete markdown syntax
        self.incomplete_patterns = [
            r'\*[^*\n]*$',         # Incomplete bold/italic (single *)
            r'\*\*[^*\n]*$',       # Incomplete bold (**)
            r'_[^_\n]*$',          # Incomplete italic (single _)
            r'__[^_\n]*$',         # Incomplete italic (__)
            r'`[^`\n]*$',          # Incomplete inline code
            r'\[[^\]\n]*$',        # Incomplete link text
            r'\]\([^)\n]*$',       # Incomplete link URL
            r'^#{1,6}\s*[^\n]*$',  # Incomplete heading (no newline yet)
        ]

    def add_text(self, text: str) -> None:
        """Add new text to the buffer and re-render if needed."""
        self.buffer += text
        self._render_if_needed()

    def render_complete(self, text: str) -> None:
        """Render complete text (for non-streaming mode)."""
        self.buffer = text
        self._render_markdown()

    def _render_if_needed(self) -> None:
        """Only re-render when transitioning between incomplete and complete states."""
        is_incomplete = self._has_incomplete_syntax()

        # Only re-render if:
        # 1. We transition from incomplete to complete (backtracking)
        # 2. We have complete syntax and this is the first render
        # 3. We end with newline (paragraph completion)
        should_render = (
            (self.last_was_incomplete and not is_incomplete) or  # Transition to complete
            (not is_incomplete and self.last_output_lines == 0) or  # First complete render
            self.buffer.endswith('\n')  # Paragraph completion
        )

        if should_render:
            if is_incomplete:
                self._render_plain_text()
            else:
                self._render_markdown()

        self.last_was_incomplete = is_incomplete

    def _has_incomplete_syntax(self) -> bool:
        """Check if the buffer contains incomplete markdown syntax."""
        # Don't treat as incomplete if we end with whitespace or newline
        if self.buffer.endswith(('\n', ' ', '\t')):
            return False

        # Get the current line being typed
        lines = self.buffer.split('\n')
        current_line = lines[-1] if lines else ""

        # Check for incomplete patterns
        for pattern in self.incomplete_patterns:
            if re.search(pattern, current_line):
                return True

        # Special case: check for incomplete code blocks
        code_block_count = self.buffer.count('```')
        if code_block_count % 2 == 1:  # Odd number means incomplete code block
            return True

        return False

    def _render_plain_text(self) -> None:
        """Render the buffer as plain text."""
        self._clear_previous_output()
        self.console.print(self.buffer, end="")
        self.last_output_lines = self.buffer.count('\n')
        if self.buffer and not self.buffer.endswith('\n'):
            self.last_output_lines += 1

    def _render_markdown(self) -> None:
        """Render the buffer as parsed markdown using TerminalRenderer."""
        try:
            self._clear_previous_output()

            # Parse and render the markdown using the same TerminalRenderer
            markdown = mistune.create_markdown(renderer=None)
            tokens = markdown(self.buffer)

            renderer = TerminalRenderer(self.console)
            renderer.render(tokens)

            # Count lines in the output by capturing it
            output_buffer = StringIO()
            temp_console = Console(file=output_buffer, width=self.console.size.width, force_terminal=True)
            temp_renderer = TerminalRenderer(temp_console)
            temp_renderer.render(tokens)
            output = output_buffer.getvalue()

            self.last_output_lines = output.count('\n')
            if output and not output.endswith('\n'):
                self.last_output_lines += 1

        except Exception:
            # Fallback to plain text if parsing fails
            self._render_plain_text()

    def _clear_previous_output(self) -> None:
        """Clear the previous output by moving cursor up and clearing lines."""
        if self.last_output_lines > 0:
            for _ in range(self.last_output_lines):
                self.console.file.write("\033[1A\033[2K")
            self.console.file.flush()

    def finalize(self) -> None:
        """Finalize the rendering (called when input is complete)."""
        # Force a final markdown render
        self._render_markdown()
        # Ensure we end with a newline if we don't already
        if self.buffer and not self.buffer.endswith('\n'):
            self.console.print()


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

    # Use the unified streaming renderer for consistent output
    renderer = StreamingRenderer(console)
    renderer.render_complete(markdown_text)


def process_stream(input_stream: TextIO, width: Optional[int] = None) -> None:
    """
    Process markdown from a stream line by line using the unified streaming renderer.

    This function reads the input stream line by line and uses the streaming
    renderer to provide consistent output with minimal flickering.
    """
    # Get terminal width
    if width is None:
        width = shutil.get_terminal_size().columns

    # Create console with proper width
    console = Console(width=width, force_terminal=True)

    # Create streaming renderer
    renderer = StreamingRenderer(console)

    try:
        # Read line by line and add to renderer
        for line in input_stream:
            renderer.add_text(line)
    except KeyboardInterrupt:
        pass
    finally:
        # Finalize the rendering
        renderer.finalize()


def process_character_stream(input_stream: TextIO, width: Optional[int] = None) -> None:
    """
    Process markdown from a stream character by character with backtracking support.

    This function is designed for LLM streaming where text arrives in small chunks
    and markdown syntax may be incomplete until more text arrives.
    """
    # Get terminal width
    if width is None:
        width = shutil.get_terminal_size().columns

    # Create console with proper width
    console = Console(width=width, force_terminal=True)

    # Create streaming renderer
    renderer = StreamingRenderer(console)

    try:
        # Read character by character
        while True:
            char = input_stream.read(1)
            if not char:  # EOF
                break

            renderer.add_text(char)

            # Small delay to simulate streaming (can be removed in production)
            # time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        # Finalize the rendering
        renderer.finalize()


@click.command()
@click.argument("input_file", type=click.File("r"), required=False)
@click.option("--width", "-w", type=int, help="Override terminal width")
@click.option("--stream", "-s", is_flag=True, help="Enable character-by-character streaming mode with backtracking")
@click.version_option(version=__version__)
def main(input_file: Optional[TextIO], width: Optional[int], stream: bool) -> None:
    """
    Parse Markdown and turn it into nicely-formatted text for terminal display.

    If no INPUT_FILE is provided, reads from stdin.

    Features:
    - 256-color support with different shades for headers
    - Syntax highlighting for code blocks
    - Proper word wrapping based on terminal width
    - Support for all standard markdown elements
    - Unified streaming renderer for consistent output
    - Character-based streaming with backtracking (--stream mode)

    The --stream mode is designed for LLM output where text arrives in small
    chunks and markdown syntax may be incomplete until more text arrives.
    All modes now use the same renderer for consistent beautiful output.
    """
    try:
        # Read the input
        if input_file is None:
            # For stdin, choose processing mode
            if stream:
                # Character-by-character streaming mode
                process_character_stream(sys.stdin, width)
            elif hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
                # Real terminal - use line-based streaming processing
                process_stream(sys.stdin, width)
            else:
                # Test input or pipe - read all at once
                content = sys.stdin.read()
                if content.strip():
                    convert(content, width)
        else:
            # For files, choose processing mode
            if stream:
                # Character-by-character streaming mode
                process_character_stream(input_file, width)
            else:
                # Read the entire content at once
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
