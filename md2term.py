"""
md2term - Parse Markdown and turn it into nicely-formatted text for terminal display.
"""

import sys
import time
from typing import Iterator, Optional, TextIO
import click


__version__ = "0.1.0"


def convert(markdown_text: str) -> str:
    """
    Convert markdown text to terminal-formatted text.

    For now, this is a stub that simply returns the input.
    """
    return markdown_text


def stream_convert(markdown_text: str, delay: float = 0.01) -> Iterator[str]:
    """
    Stream convert markdown text to terminal-formatted text.

    For now, this is a stub that streams the input character by character.

    Args:
        markdown_text: The markdown text to convert
        delay: Delay between characters to simulate streaming (default: 0.01s)

    Yields:
        Individual characters of the input text
    """
    for char in markdown_text:
        yield char
        if delay > 0:
            time.sleep(delay)


@click.command()
@click.argument("input_file", type=click.File("r"), required=False)
@click.option("--stream/--no-stream", default=True, help="Enable streaming output")
@click.option(
    "--delay", type=float, default=0.01, help="Delay between characters when streaming"
)
@click.version_option(version=__version__)
def main(input_file: Optional[TextIO], stream: bool, delay: float) -> None:
    """
    Parse Markdown and turn it into nicely-formatted text for terminal display.

    If no INPUT_FILE is provided, reads from stdin.
    """
    try:
        # Read the input
        if input_file is None:
            content = sys.stdin.read()
        else:
            content = input_file.read()

        if stream:
            # Stream the output character by character
            for char in stream_convert(content, delay):
                print(char, end="", flush=True)
        else:
            # Output all at once
            result = convert(content)
            print(result, end="")

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
