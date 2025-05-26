"""
md2term - Parse Markdown and turn it into nicely-formatted text for terminal display.
"""

import sys
import shutil
import re
import time
import io
from typing import Optional, TextIO, List, Dict, Any
from io import StringIO

import mistune
import rich_click as click
from rich.console import Console
from rich.text import Text
from rich.syntax import Syntax
from rich.rule import Rule
from rich.panel import Panel

# Configure rich-click for better readability
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.STYLE_HELPTEXT = ""  # Remove dim styling from help text


__version__ = "1.0.2"


class TerminalRenderer:
    """Custom renderer for converting markdown AST to Rich terminal output."""

    def __init__(self, console: Console):
        self.console = console
        self.in_code_block = False
        self.code_block_lines: List[str] = []
        self.code_block_lang = None

    def render(self, tokens: List[Dict[str, Any]]) -> None:
        """Render a list of markdown tokens to the terminal."""
        for i, token in enumerate(tokens):
            # Only add spacing between non-blank-line elements
            if (
                i > 0
                and token["type"] != "blank_line"
                and tokens[i - 1]["type"] != "blank_line"
            ):
                self.console.print()
            self._render_token(token)

    def _render_token(self, token: Dict[str, Any]) -> None:
        """Render a single markdown token."""
        token_type = token["type"]

        if token_type == "heading":
            self._render_heading(token)
        elif token_type == "paragraph":
            self._render_paragraph(token)
        elif token_type == "block_text":
            self._render_block_text(token)
        elif token_type == "block_code":
            self._render_code_block(token)
        elif token_type == "block_quote":
            self._render_blockquote(token)
        elif token_type == "list":
            self._render_list(token)
        elif token_type == "thematic_break":
            self._render_thematic_break()
        elif token_type == "blank_line":
            self.console.print()

    def _render_heading(self, token: Dict[str, Any]) -> None:
        """Render a heading with appropriate styling."""
        level = token["attrs"]["level"]
        text = self._render_inline_tokens(token["children"])

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
        text = self._render_inline_tokens(token["children"])
        self.console.print(text)

    def _render_block_text(self, token: Dict[str, Any]) -> None:
        """Render block text (used in list items and other contexts)."""
        text = self._render_inline_tokens(token["children"])
        self.console.print(text, end="")

    def _render_code_block(self, token: Dict[str, Any]) -> None:
        """Render a code block with syntax highlighting."""
        code = token["raw"].rstrip()
        # Handle different token structures - some have 'attrs', others have 'info' directly
        if "attrs" in token:
            lang = token["attrs"].get("info", "").strip() or "text"
        else:
            lang = token.get("info", "").strip() or "text"

        try:
            # Use Rich's syntax highlighting with a simpler theme for consistency
            syntax = Syntax(
                code,
                lang,
                theme="ansi_dark",
                line_numbers=False,
                background_color="default",
            )
            panel = Panel(syntax, border_style="dim", padding=(0, 1))
            self.console.print(panel)
        except Exception:
            # Fallback to simple code formatting if syntax highlighting fails
            panel = Panel(
                code, border_style="dim", style="dim white on black", padding=(0, 1)
            )
            self.console.print(panel)

    def _render_blockquote(self, token: Dict[str, Any]) -> None:
        """Render a blockquote with indentation and styling, including GitHub-style callouts."""
        # Render children into a string buffer
        old_console = self.console
        buffer = StringIO()
        temp_console = Console(
            file=buffer,
            width=self.console.size.width - 4,
            force_terminal=True,
            color_system="256",
            legacy_windows=False,
        )
        self.console = temp_console

        for child in token["children"]:
            self._render_token(child)

        self.console = old_console
        content = buffer.getvalue().rstrip()

        # Check if this is a GitHub-style callout
        callout_info = self._detect_callout(content)

        if callout_info:
            self._render_callout(content, callout_info)
        else:
            # Create GitHub-style blockquote with left border only
            lines = content.split("\n")
            for line in lines:
                if line.strip():  # Only add border to non-empty lines
                    self.console.print(f"[dim blue]│[/] [italic dim blue]{line}[/]")
                else:
                    self.console.print("[dim blue]│[/]")

    def _detect_callout(self, content: str) -> Optional[Dict[str, str]]:
        """Detect GitHub-style callouts in blockquote content."""
        lines = content.strip().split("\n")
        if not lines:
            return None

        first_line = lines[0].strip()

        # Match patterns like "[!NOTE]" or "[!NOTE] Custom Title"
        callout_pattern = r"^\[!([A-Z]+)\](?:\s+(.+))?$"
        match = re.match(callout_pattern, first_line)

        if match:
            callout_type = match.group(1).lower()
            custom_title = match.group(2)

            # Get the content after the callout declaration
            content_lines = lines[1:] if len(lines) > 1 else []
            callout_content = "\n".join(content_lines).strip()

            return {
                "type": callout_type,
                "title": custom_title,
                "content": callout_content,
            }

        return None

    def _render_callout(self, content: str, callout_info: Dict[str, str]) -> None:
        """Render a GitHub-style callout with emoji and appropriate styling."""
        callout_type = callout_info["type"]
        custom_title = callout_info["title"]
        callout_content = callout_info["content"]

        # Define callout styles and emojis
        callout_styles = {
            "note": {
                "emoji": "📝",
                "title": "Note",
                "border_style": "blue",
                "title_style": "bold blue",
                "content_style": "blue",
            },
            "tip": {
                "emoji": "💡",
                "title": "Tip",
                "border_style": "green",
                "title_style": "bold green",
                "content_style": "green",
            },
            "warning": {
                "emoji": "⚠️",
                "title": "Warning",
                "border_style": "yellow",
                "title_style": "bold yellow",
                "content_style": "yellow",
            },
            "important": {
                "emoji": "❗",
                "title": "Important",
                "border_style": "magenta",
                "title_style": "bold magenta",
                "content_style": "magenta",
            },
            "caution": {
                "emoji": "🚨",
                "title": "Caution",
                "border_style": "red",
                "title_style": "bold red",
                "content_style": "red",
            },
        }

        # Get style info, default to note if unknown type
        style = callout_styles.get(callout_type, callout_styles["note"])

        # Use custom title if provided, otherwise use default
        title = custom_title if custom_title else style["title"]

        # Create the title line with emoji and two extra spaces
        title_line = f"{style['emoji']}  {title}"

        # Render the callout as a panel
        if callout_content:
            # Parse and render the content with markdown
            old_console = self.console
            content_buffer = StringIO()
            temp_console = Console(
                file=content_buffer,
                width=self.console.size.width - 6,
                force_terminal=True,
                color_system="256",
                legacy_windows=False,
            )
            self.console = temp_console

            # Parse the content as markdown
            import mistune

            markdown = mistune.create_markdown(renderer=None)
            try:
                tokens = markdown(callout_content)
                # Type assertion since we know renderer=None returns tokens
                assert isinstance(tokens, list)
                temp_renderer = TerminalRenderer(temp_console)
                temp_renderer.render(tokens)
            except Exception:
                # Fallback to plain text if parsing fails
                temp_console.print(callout_content)

            self.console = old_console
            rendered_content = content_buffer.getvalue().rstrip()

            # Create panel with title and content properly separated
            if rendered_content:
                panel_content = (
                    f"[{style['title_style']}]{title_line}[/]\n\n{rendered_content}"
                )
            else:
                panel_content = f"[{style['title_style']}]{title_line}[/]"
        else:
            # Just the title if no content
            panel_content = f"[{style['title_style']}]{title_line}[/]"

        # Create and display the panel
        panel = Panel(
            panel_content,
            border_style=style["border_style"],
            padding=(0, 1),
            expand=False,
        )
        self.console.print(panel)

    def _render_list(self, token: Dict[str, Any], indent_level: int = 0) -> None:
        """Render ordered or unordered lists with proper nesting support."""
        ordered = token["attrs"].get("ordered", False)
        start = token["attrs"].get("start", 1)

        # Calculate indentation for this level
        indent = "  " * indent_level  # 2 spaces per level

        for i, item in enumerate(token["children"]):
            if ordered:
                marker = f"{start + i}."
                marker_style = "bold cyan"
            else:
                marker = "•"
                marker_style = "bold yellow"

            # Process the list item children
            has_paragraph = False
            nested_lists = []
            paragraph_content = Text()

            for child in item["children"]:
                if child["type"] == "paragraph":
                    has_paragraph = True
                    # Render inline tokens for the paragraph
                    for inline_child in child["children"]:
                        if inline_child["type"] == "text":
                            paragraph_content.append(inline_child["raw"])
                        else:
                            # Render other inline tokens
                            inline_text = self._render_inline_tokens([inline_child])
                            paragraph_content.append_text(inline_text)
                elif child["type"] == "list":
                    # Store nested lists to render after the main content
                    nested_lists.append(child)
                else:
                    # Handle other block elements (shouldn't happen in well-formed markdown)
                    if not has_paragraph:
                        # If no paragraph, treat as direct content
                        old_console = self.console
                        buffer = StringIO()
                        temp_console = Console(
                            file=buffer,
                            width=self.console.size.width - len(indent) - 4,
                            force_terminal=True,
                            color_system="256",
                            legacy_windows=False,
                        )
                        self.console = temp_console
                        self._render_token(child)
                        self.console = old_console
                        paragraph_content.append(buffer.getvalue().rstrip())

            # Render the main list item line
            if has_paragraph or paragraph_content.plain:
                line_text = Text()
                line_text.append(indent)
                line_text.append(marker, style=marker_style)
                line_text.append(" ")
                line_text.append_text(paragraph_content)
                self.console.print(line_text)

            # Render any nested lists with increased indentation
            for nested_list in nested_lists:
                self._render_list(nested_list, indent_level + 1)

    def _render_thematic_break(self) -> None:
        """Render a horizontal rule."""
        self.console.print(Rule(style="dim"))

    def _render_inline_tokens(self, tokens: List[Dict[str, Any]]) -> Text:
        """Render inline tokens (emphasis, strong, code, links, etc.) into Rich Text."""
        text = Text()

        for token in tokens:
            if token["type"] == "text":
                text.append(token["raw"])
            elif token["type"] == "emphasis":
                child_text = self._render_inline_tokens(token["children"])
                child_text.stylize("italic")
                text.append_text(child_text)
            elif token["type"] == "strong":
                child_text = self._render_inline_tokens(token["children"])
                child_text.stylize("bold")
                text.append_text(child_text)
            elif token["type"] == "codespan":
                text.append(token["raw"], style="bold red on black")
            elif token["type"] == "link":
                link_text = self._render_inline_tokens(token["children"])
                url = token["attrs"]["url"]
                link_text.stylize("bold blue underline")
                text.append_text(link_text)
                text.append(f" ({url})", style="dim blue")
            elif token["type"] == "image":
                alt_text = self._render_inline_tokens(token["children"]).plain
                url = token["attrs"]["url"]
                text.append(f"[IMAGE: {alt_text}]", style="bold magenta")
                text.append(f" ({url})", style="dim magenta")
            elif token["type"] == "linebreak":
                text.append("\n")
            elif token["type"] == "softbreak":
                text.append(" ")

        return text


class StreamingRenderer:
    """Improved streaming renderer that minimizes corruption and flickering."""

    def __init__(self, console: Console):
        self.console = console
        self.buffer = ""
        self.last_rendered_content = ""
        self.last_rendered_lines = 0
        self.char_count = 0
        self.last_update_time = time.time()

    def add_text(self, text: str) -> None:
        """Add new text to the buffer and render with smart frequency control."""
        self.buffer += text
        self.char_count += len(text)
        current_time = time.time()

        # Balanced update conditions for responsive streaming:
        # 1. Moderate content added (80+ chars) AND short time passed
        # 2. Double newline (clear paragraph break)
        # 3. Time-based update (every 0.1 seconds) AND some content
        # 4. Buffer ends with complete markdown elements AND short time passed
        should_update = (
            (self.char_count >= 80 and (current_time - self.last_update_time) >= 0.05)
            or text.endswith("\n\n")
            or (self.char_count >= 20 and (current_time - self.last_update_time) >= 0.1)
            or (
                self._looks_complete()
                and (current_time - self.last_update_time) >= 0.08
            )
        )

        if should_update:
            self._render_current_state()
            self.char_count = 0
            self.last_update_time = current_time

    def render_complete(self, text: str) -> None:
        """Render complete text (for non-streaming mode)."""
        self.buffer = text
        self._render_final()

    def _looks_complete(self) -> bool:
        """Check if the buffer ends with what looks like complete markdown elements."""
        if not self.buffer:
            return False

        # Consider complete if ends with:
        # - Double newline (paragraph break)
        # - Single newline after certain patterns
        if self.buffer.endswith("\n\n"):
            return True

        if self.buffer.endswith("\n"):
            lines = self.buffer.rstrip().split("\n")
            if lines:
                last_line = lines[-1].strip()
                # Complete if last line looks like a complete element
                if (
                    last_line.startswith("#")  # Heading
                    or last_line.startswith("- ")  # List item
                    or last_line.startswith("> ")  # Blockquote
                    or last_line == "---"  # Horizontal rule
                    or not last_line
                ):  # Empty line
                    return True

        return False

    def _render_current_state(self) -> None:
        """Render the current buffer state with minimal re-rendering."""
        # Only re-render if content has actually changed
        if self.buffer == self.last_rendered_content:
            return

        # Clear previous output
        self._clear_previous_output()

        # Render new content
        try:
            if self.buffer.strip():
                self._render_and_count(self.buffer)
            self.last_rendered_content = self.buffer
        except Exception:
            # Fallback to plain text if markdown parsing fails
            self.console.print(self.buffer, end="")
            self.last_rendered_lines = self.buffer.count("\n")
            if self.buffer and not self.buffer.endswith("\n"):
                self.last_rendered_lines += 1

    def _render_and_count(self, content: str) -> None:
        """Render content and accurately count the output lines."""
        # Use a temporary buffer to capture and count the actual output
        temp_buffer = StringIO()
        temp_console = Console(
            file=temp_buffer,
            width=self.console.size.width,
            force_terminal=False,  # Don't force terminal for counting
            legacy_windows=False,
        )

        # Parse and render to temp console
        markdown = mistune.create_markdown(renderer=None)
        tokens = markdown(content)
        # Type assertion since we know renderer=None returns tokens
        assert isinstance(tokens, list)
        temp_renderer = TerminalRenderer(temp_console)
        temp_renderer.render(tokens)

        # Get the actual output
        output = temp_buffer.getvalue()

        # Now render to the real console
        real_renderer = TerminalRenderer(self.console)
        real_renderer.render(tokens)

        # Count lines accurately from the actual output
        self.last_rendered_lines = len(output.split("\n")) - 1
        if output and not output.endswith("\n"):
            self.last_rendered_lines += 1

    def _clear_previous_output(self) -> None:
        """Clear the previous output using accurate line count."""
        if self.last_rendered_lines > 0:
            # Move cursor up and clear each line
            for _ in range(self.last_rendered_lines):
                self.console.file.write("\033[1A\033[2K")
            self.console.file.flush()
            self.last_rendered_lines = 0

    def _render_final(self) -> None:
        """Render the final complete content."""
        # Clear any current output
        self._clear_previous_output()

        # Render everything as markdown
        if self.buffer.strip():
            try:
                markdown = mistune.create_markdown(renderer=None)
                tokens = markdown(self.buffer)
                # Type assertion since we know renderer=None returns tokens
                assert isinstance(tokens, list)
                renderer = TerminalRenderer(self.console)
                renderer.render(tokens)
            except Exception:
                # Fallback to plain text
                self.console.print(self.buffer, end="")

    def finalize(self) -> None:
        """Finalize the rendering (called when input is complete)."""
        # Clear current output and render final content
        self._clear_previous_output()

        if self.buffer.strip():
            try:
                markdown = mistune.create_markdown(renderer=None)
                tokens = markdown(self.buffer)
                # Type assertion since we know renderer=None returns tokens
                assert isinstance(tokens, list)
                renderer = TerminalRenderer(self.console)
                renderer.render(tokens)
            except Exception:
                # Fallback to plain text
                self.console.print(self.buffer, end="")

        # Ensure we end with a newline if we don't already
        if self.buffer and not self.buffer.endswith("\n"):
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
    console = Console(width=width, force_terminal=True, color_system="256")

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
    console = Console(width=width, force_terminal=True, color_system="256")

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
    console = Console(width=width, force_terminal=True, color_system="256")

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
    console = Console(width=width, force_terminal=True, color_system="256")

    # Create streaming renderer
    renderer = StreamingRenderer(console)

    try:
        # Try to use select for optimization, but fall back gracefully
        import select

        use_select = False

        try:
            # Check if we can use select (requires real file descriptor)
            if hasattr(select, "select") and hasattr(input_stream, "fileno"):
                # Test if fileno() actually works
                input_stream.fileno()
                use_select = True
        except (AttributeError, OSError, io.UnsupportedOperation):
            # fileno() not available or not supported (e.g., in tests)
            use_select = False

        if use_select:
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
    except Exception:
        # If anything goes wrong, fall back to simple character reading
        try:
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
