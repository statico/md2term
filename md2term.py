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

import mistune
import rich_click as click
from rich.console import Console
from rich.text import Text
from rich.syntax import Syntax
from rich.rule import Rule
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich import box

# Configure rich-click for better readability
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.STYLE_HELPTEXT = ""  # Remove dim styling from help text


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
    """Simple streaming renderer that minimizes flickering with reduced update frequency."""

    def __init__(self, console: Console):
        self.console = console
        self.buffer = ""
        self.current_output_lines = 0
        self.last_was_incomplete = False
        self.char_count = 0

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
        """Add new text to the buffer and render with reduced frequency."""
        self.buffer += text
        self.char_count += len(text)

        # Only update every 20 characters or on newlines to reduce flickering
        should_update = (
            self.char_count >= 20 or
            text.endswith('\n') or
            len(text) > 50  # Large chunks (bulk input)
        )

        if should_update:
            self._render_current_state()
            self.char_count = 0

    def render_complete(self, text: str) -> None:
        """Render complete text (for non-streaming mode)."""
        self.buffer = text
        self._render_final()

    def _render_current_state(self) -> None:
        """Render the current buffer state."""
        is_incomplete = self._has_incomplete_syntax_in_text(self.buffer)

        # Only re-render if state changed or we have significant new content
        if self.last_was_incomplete != is_incomplete or self.char_count >= 20:
            self._clear_output()

            if is_incomplete:
                # Show as plain text while incomplete
                self.console.print(self.buffer, end="")
                self.current_output_lines = self.buffer.count('\n')
                if self.buffer and not self.buffer.endswith('\n'):
                    self.current_output_lines += 1
            else:
                # Render as markdown when complete
                self._render_markdown_content(self.buffer)

            self.last_was_incomplete = is_incomplete

    def _has_incomplete_syntax_in_text(self, text: str) -> bool:
        """Check if the given text contains incomplete markdown syntax."""
        # Don't treat as incomplete if we end with whitespace or newline
        if text.endswith(('\n', ' ', '\t')):
            return False

        # Get the current line being typed
        lines = text.split('\n')
        current_line = lines[-1] if lines else ""

        # Check for incomplete patterns
        for pattern in self.incomplete_patterns:
            if re.search(pattern, current_line):
                return True

        # Special case: check for incomplete code blocks
        code_block_count = text.count('```')
        if code_block_count % 2 == 1:  # Odd number means incomplete code block
            return True

        return False

    def _render_markdown_content(self, content: str) -> None:
        """Render markdown content and track the number of lines."""
        if not content.strip():
            return

        try:
            # Parse and render the markdown
            markdown = mistune.create_markdown(renderer=None)
            tokens = markdown(content)

            # Capture output to count lines
            output_buffer = StringIO()
            temp_console = Console(file=output_buffer, width=self.console.size.width, force_terminal=True)
            temp_renderer = TerminalRenderer(temp_console)
            temp_renderer.render(tokens)
            output = output_buffer.getvalue()

            # Print the actual output
            renderer = TerminalRenderer(self.console)
            renderer.render(tokens)

            # Update line count
            self.current_output_lines = output.count('\n')
            if output and not output.endswith('\n'):
                self.current_output_lines += 1

        except Exception:
            # Fallback to plain text if parsing fails
            self.console.print(content, end="")
            self.current_output_lines = content.count('\n')
            if content and not content.endswith('\n'):
                self.current_output_lines += 1

    def _clear_output(self) -> None:
        """Clear the current output."""
        if self.current_output_lines > 0:
            for _ in range(self.current_output_lines):
                self.console.file.write("\033[1A\033[2K")
            self.console.file.flush()
            self.current_output_lines = 0

    def _render_final(self) -> None:
        """Render the final complete content."""
        # Clear any current output
        self._clear_output()

        # Render everything as markdown
        try:
            markdown = mistune.create_markdown(renderer=None)
            tokens = markdown(self.buffer)
            renderer = TerminalRenderer(self.console)
            renderer.render(tokens)
        except Exception:
            # Fallback to plain text
            self.console.print(self.buffer, end="")

    def finalize(self) -> None:
        """Finalize the rendering (called when input is complete)."""
        # Clear current output and render final content
        self._clear_output()
        if self.buffer.strip():
            self._render_markdown_content(self.buffer)

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


def process_smart_stream(input_stream: TextIO, width: Optional[int] = None) -> None:
    """
    Process markdown from a stream with character-by-character reading.

    Simple and reliable approach that works for all input types.
    """
    # Get terminal width
    if width is None:
        width = shutil.get_terminal_size().columns

    # Create console with proper width
    console = Console(width=width, force_terminal=True)

    # Create streaming renderer
    renderer = StreamingRenderer(console)

    try:
        # Try to read in small chunks first, fall back to character-by-character
        import select

        if hasattr(select, 'select') and hasattr(input_stream, 'fileno'):
            # Use select to optimize reading
            while True:
                # Check if data is available
                ready, _, _ = select.select([input_stream], [], [], 0.01)

                if ready:
                    # Read a small chunk
                    chunk = input_stream.read(64)  # Smaller chunks for better streaming
                    if not chunk:  # EOF
                        break
                    renderer.add_text(chunk)
                else:
                    # No data available, try single character read
                    char = input_stream.read(1)
                    if not char:  # EOF
                        break
                    renderer.add_text(char)
        else:
            # Fallback to character-by-character reading
            while True:
                char = input_stream.read(1)
                if not char:  # EOF
                    break
                renderer.add_text(char)

    except KeyboardInterrupt:
        pass
    finally:
        # Finalize the rendering
        renderer.finalize()


@click.command()
@click.argument("input_file", type=click.File("r"), required=False)
@click.option("--width", "-w", type=int, help="Override terminal width")
@click.version_option(version=__version__)
def main(input_file: Optional[TextIO], width: Optional[int]) -> None:
    """
    Parse Markdown and turn it into nicely-formatted text for terminal display.

    If no INPUT_FILE is provided, reads from stdin.

    \b
    Features:
    • 256-color support with different shades for headers
    • Syntax highlighting for code blocks
    • Proper word wrapping based on terminal width
    • Support for all standard markdown elements
    • Streaming renderer with backtracking for LLM output
    • Character-by-character processing with minimal flickering

    \b
    Examples:
    md2term README.md                    # Render a markdown file
    echo "# Hello" | md2term             # Render from stdin
    cat file.md | pv -qL 20 | md2term    # Simulate streaming input
    md2term --width 60 README.md         # Set custom width

    The renderer automatically handles both complete files and streaming input,
    with intelligent backtracking when markdown syntax is incomplete.
    """
    try:
        # Read the input
        if input_file is None:
            # For stdin, just use character streaming for simplicity and reliability
            process_smart_stream(sys.stdin, width)
        else:
            # For files, read all at once and use the unified renderer
            content = input_file.read()
            if content.strip():
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
