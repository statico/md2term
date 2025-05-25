# md2term

[![PyPI](https://img.shields.io/pypi/v/md2term.svg)](https://pypi.org/project/md2term/)
[![Python Version](https://img.shields.io/pypi/pyversions/md2term.svg)](https://pypi.org/project/md2term/)
[![License](https://img.shields.io/pypi/l/md2term.svg)](https://github.com/statico/md2term/blob/main/LICENSE)

Parse Markdown and turn it into nicely-formatted text that can be read in the terminal.

## Installation

Install this tool using `pip` or `uv`:

```bash
pip install md2term
```

Or with `uv`:

```bash
uv add md2term
```

## Usage

### Command Line

```bash
# Read from a file
md2term README.md

# Read from stdin
cat README.md | md2term

# Read from a URL (if supported)
md2term https://example.com/document.md
```

### Python API

```python
import md2term

# Convert markdown string to terminal-formatted text
markdown_text = "# Hello\n\nThis is **bold** text."
formatted = md2term.convert(markdown_text)
print(formatted)

# Stream conversion (useful for large documents)
for chunk in md2term.stream_convert(markdown_text):
    print(chunk, end='')
```

## Features

- Convert Markdown to beautifully formatted terminal output
- Support for common Markdown elements:
  - Headers
  - Bold and italic text
  - Code blocks and inline code
  - Lists (ordered and unordered)
  - Links
  - Blockquotes
  - Tables
- Streaming output for large documents
- Configurable color schemes
- Works with pipes and redirects

## Development

To set up for development:

```bash
git clone https://github.com/statico/md2term.git
cd md2term
uv sync --dev
```

Run tests:

```bash
uv run pytest
```

Format code:

```bash
uv run black .
uv run ruff check --fix .
```

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
