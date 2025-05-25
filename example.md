# Main Title (H1)

This is a paragraph with **bold text**, _italic text_, and `inline code`. Here's a [link to example](https://example.com) and some more text.

## Subsection (H2)

### Sub-subsection (H3)

#### Level 4 Header (H4)

##### Level 5 Header (H5)

###### Level 6 Header (H6)

## Code Examples

Here's some inline code: `print("Hello, World!")` in the middle of a sentence.

### Python Code Block

```python
def fibonacci(n):
    """Generate Fibonacci sequence up to n terms."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]

    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])

    return sequence

# Example usage
print(fibonacci(10))
```

### JavaScript Code Block

```javascript
function greetUser(name) {
  return `Hello, ${name}! Welcome to our application.`;
}

const users = ["Alice", "Bob", "Charlie"];
users.forEach((user) => console.log(greetUser(user)));
```

## Lists

### Unordered List

- First item
- Second item with **bold text**
- Third item with _italic text_
- Fourth item with `inline code`

### Ordered List

1. First numbered item
2. Second numbered item
3. Third numbered item with a [link](https://example.com)
4. Fourth numbered item

## Blockquotes

> This is a blockquote with some important information.
> It can span multiple lines and contain **bold** and _italic_ text.
>
> It can even contain `inline code` and [links](https://example.com).

> This is another blockquote to show multiple quotes.

## Horizontal Rules

Here's some text before a horizontal rule.

---

And here's some text after the horizontal rule.

## Mixed Content

This paragraph contains **bold text**, _italic text_, `inline code`, and a [link to documentation](https://docs.example.com).

The next paragraph shows how text wraps naturally based on the terminal width, which is especially useful for reading long documents in the terminal like man pages.

### Final Code Example

```bash
# Install dependencies
uv add click rich mistune

# Run the program
python md2term.py README.md

# Use with pipes
curl -s https://raw.githubusercontent.com/user/repo/main/README.md | python md2term.py
```

# Test Callouts

## GitHub-style callouts

> [!NOTE]
> This is a note callout.

> [!TIP]
> This is a tip callout.

> [!WARNING]
> This is a warning callout.

> [!IMPORTANT]
> This is an important callout.

> [!CAUTION]
> This is a caution callout.

## Callouts with custom titles

> [!NOTE] Custom Note Title
>
> This is a note with a custom title.

> [!TIP] Pro Tip
>
> This is a tip with a custom title.

## Callouts with rich content

> [!WARNING] Complex Warning
>
> This callout contains **bold text**, _italic text_, and `inline code`.
>
> It can also contain:
>
> - Bullet points
> - Multiple paragraphs
> - Even [links](https://example.com)
>
> ```python
> # And code blocks!
> def example():
>     return "Hello from a callout!"
> ```

That's all folks!
