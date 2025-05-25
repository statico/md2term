# md2term

A beautiful markdown-to-terminal converter that renders markdown with rich formatting, syntax highlighting, and proper terminal layout.

## Features

- **256-color support** with different shades for headers (H1-H6)
- **Syntax highlighting** for code blocks using Pygments
- **Proper word wrapping** based on terminal width (like man pages)
- **Streaming input processing** for handling large files and stdin
- **Smart code block handling** - detects triple backticks and processes blocks correctly
- **Rich formatting** for all markdown elements:
  - Headers with different colors and styles
  - Bold and italic text
  - Code spans with highlighting
  - Blockquotes with panels
  - Ordered and unordered lists
  - Links with URLs
  - Images with alt text
  - Horizontal rules

## Installation

Install the required dependencies:

```bash
uv add click rich mistune
```

Or if you prefer pip:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Convert a markdown file
uv run python md2term.py README.md

# Read from stdin
cat README.md | uv run python md2term.py

# Pipe from other commands
curl -s https://raw.githubusercontent.com/user/repo/main/README.md | uv run python md2term.py
```

### Options

```bash
# Override terminal width
uv run python md2term.py --width 100 README.md

# Show version
uv run python md2term.py --version

# Show help
uv run python md2term.py --help
```

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

## Dependencies

- **click**: Command-line interface framework
- **rich**: Terminal formatting and rendering library
- **mistune**: Fast markdown parser

## Examples

### Sample Markdown

```markdown
# Main Title

This is a paragraph with **bold text** and _italic text_.

## Subsection

Here's some `inline code` and a [link](https://example.com).

### Code Block

\`\`\`python
def hello_world():
print("Hello, World!")
\`\`\`

> This is a blockquote with some important information.

- Unordered list item 1
- Unordered list item 2

1. Ordered list item 1
2. Ordered list item 2

---

That's a horizontal rule above this text.
```

### Terminal Output

The above markdown will be rendered with:

- Bright cyan title with decorative rules
- Blue subsection header with underline
- Magenta code block header
- Syntax-highlighted Python code in a panel
- Blue italic blockquote in a panel
- Yellow bullet points for unordered list
- Cyan numbers for ordered list
- Horizontal rule separator

## Caveat

This software created almost entirely with [Cursor](https://www.cursor.com/) and [Claude 4 Sonnet](https://www.anthropic.com/).

## License

This project is open source. Feel free to use and modify as needed.
