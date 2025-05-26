# md2term

[![GitHub repo](https://img.shields.io/badge/github-repo-green)](https://github.com/statico/md2term) [![PyPI](https://img.shields.io/pypi/v/md2term.svg)](https://pypi.org/project/md2term/) [![Changelog](https://img.shields.io/github/v/release/statico/md2term?include_prereleases&label=changelog)](https://github.com/statico/md2term/releases) [![Tests](https://github.com/statico/md2term/workflows/Test/badge.svg)](https://github.com/statico/md2term/actions?query=workflow%3ATest) [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/statico/md2term/blob/main/LICENSE)

A beautiful markdown-to-terminal converter that renders markdown with rich formatting, syntax highlighting, and proper terminal layout.

It supports streaming so you can pipe [your favorite LLM tool](https://github.com/simonw/llm) to it, like this:

![x](https://github.com/user-attachments/assets/5a48c8dc-88f3-4ff7-bed2-ffbd7cd531b7)

> [!NOTE]
> This software was created almost entirely by AI with [Cursor](https://www.cursor.com/) and [Claude 4 Sonnet](https://www.anthropic.com/).

## Installation

Install md2term using `uv`:

```bash
uv tool install md2term
```

Or with `pip` or `pipx`:

```bash
pip install md2term
# or
pipx install md2term
```

Verify the installation:

```bash
md2term --version
```

## Usage

### Command Line

```bash
# Convert a markdown file
md2term README.md

# Read from stdin
cat README.md | md2term

# Pipe from other commands
curl -s https://raw.githubusercontent.com/user/repo/main/README.md | md2term

# Or commands with slow output
llm 'tell me long a story about cheesecakes using markdown formatting' | md2term

# Override terminal width
md2term --width 100 README.md

# Show version
md2term --version

# Show help
md2term --help
```

### Python Library

You can also use md2term as a Python library for integrating markdown rendering into your applications:

````python
from rich.console import Console
from md2term import convert, StreamingRenderer

# Simple conversion
markdown_text = "# Hello\n\nThis is **bold** text."
convert(markdown_text)

# Streaming usage (great for LLM applications)
console = Console(force_terminal=True)
renderer = StreamingRenderer(console)

try:
    # Add content incrementally
    renderer.add_text("# Streaming Example\n\n")
    renderer.add_text("This content appears **immediately** as it's added.\n")
    renderer.add_text("\n```python\nprint('Hello, World!')\n```\n")
finally:
    # Always finalize to ensure complete rendering
    renderer.finalize()
````

The streaming functionality is particularly useful for:

- LLM/AI applications that generate content in real-time
- Processing large files with immediate visual feedback
- Building interactive CLI tools with progressive output

See `example_streaming.py` for more detailed examples and patterns.

## Examples

For a comprehensive example of markdown features, see `example.md` in this repository.

## Design Decisions

### Code Block Handling

The program uses a smart approach to handle multi-line code blocks:

1. **Streaming Processing**: For stdin input, the program processes content in chunks, buffering until it encounters blank lines (when not in a code block)
2. **Code Fence Detection**: Detects triple backticks (`\`\`\``) to track when we're inside code blocks
3. **No Backtracking**: Instead of clearing previous lines, the program assumes that triple backticks always indicate the start/end of code blocks

This approach is efficient and works well for typical markdown usage patterns.

### Color Scheme

- **H1**: Bright cyan with rules above and below, centered
- **H2**: Bright blue with rule below
- **H3**: Bright magenta
- **H4**: Bright yellow
- **H5**: Bright green
- **H6**: Bright white
- **Code spans**: Red text on dark gray background
- **Links**: Blue underlined text with URL in parentheses
- **Lists**: Yellow bullets (•) for unordered, cyan numbers for ordered
- **Blockquotes**: Blue italic text in a panel

### Terminal Width Handling

The program automatically detects terminal width and wraps text accordingly. You can override this with the `--width` option for testing or specific formatting needs.

## Development

To install for development:

```bash
# Clone the repository
git clone https://github.com/statico/md2term
cd md2term

# Install in development mode
uv tool install --editable .

# Or install dependencies for local development
uv sync
uv run md2term README.md
```

### Running Tests

The project uses pytest with snapshot testing via syrupy to ensure consistent output formatting:

```bash
# Install test dependencies
uv sync --group test

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=md2term

# Run specific test file
uv run pytest tests/test_md2term.py

# Run specific test
uv run pytest tests/test_md2term.py::TestMarkdownFeatures::test_headings_all_levels
```

### Snapshot Testing

The tests use snapshot testing to verify that markdown rendering produces consistent terminal output. Snapshots capture the exact ANSI escape sequences and formatting that would appear in the terminal.

```bash
# Update snapshots when output changes (after verifying changes are correct)
uv run pytest --snapshot-update

# Review snapshot differences
uv run pytest --snapshot-details
```

**Important**: When modifying rendering logic, always:

1. Run tests to see what changed
2. Manually verify the output looks correct with `uv run md2term example.md`
3. Update snapshots only if the changes are intentional and correct

The snapshot file is located at `tests/__snapshots__/test_md2term.ambr` and contains the expected terminal output for various markdown inputs.

## Publishing

To publish a new version to PyPI:

```bash
# Update version in pyproject.toml
# Build the package
uv build

# Publish to PyPI (requires PyPI credentials)
uv publish
```

## License

This project is open source. Feel free to use and modify as needed.

```

```
