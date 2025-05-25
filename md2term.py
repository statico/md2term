"""
md2term - Parse Markdown and turn it into nicely-formatted text for terminal display.
"""

import sys
from typing import Optional, TextIO
import click


__version__ = "0.1.0"


def convert(markdown_text: str) -> str:
    """
    Convert markdown text to terminal-formatted text.

    For now, this is a stub that simply returns the input.
    """
    return markdown_text


@click.command()
@click.argument("input_file", type=click.File("r"), required=False)
@click.version_option(version=__version__)
def main(input_file: Optional[TextIO]) -> None:
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

        # Convert and output
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
