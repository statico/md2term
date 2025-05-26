#!/usr/bin/env python3
"""
Example of using md2term as a library for streaming markdown content.

This demonstrates how to integrate md2term into your Python application
to stream markdown content with proper terminal formatting, similar to
how LLM tools like Simon Willison's llm stream their output.

Usage:
    python example_streaming.py
"""

import time
import shutil
from rich.console import Console

# Import the streaming functionality from md2term
from md2term import StreamingRenderer


def simulate_llm_streaming():
    """
    Simulate an LLM streaming markdown content character by character.

    This is similar to how tools like OpenAI's API or other LLM services
    stream their responses in real-time.
    """
    # Sample markdown content with various features
    markdown_content = """# AI Assistant Response

Thank you for your question! Let me provide a comprehensive answer.

## Key Points

Here are the **most important** things to understand:

1. **Streaming** allows for *real-time* display of content
2. **Markdown formatting** is preserved during streaming
3. **Terminal colors** make the output more readable

### Code Example

Here's a simple Python example:

```python
def hello_world():
    print("Hello, World!")
    return "success"

# Call the function
result = hello_world()
```

### Additional Features

> This is a blockquote that demonstrates
> how multi-line quoted text appears
> in the terminal output.

Some `inline code` and a [link to example](https://example.com) for reference.

---

## Performance Considerations

- Streaming reduces perceived latency
- Users see content as it's generated
- Better user experience for long responses

That's the complete explanation! Hope this helps.
"""

    # Get terminal width
    width = shutil.get_terminal_size().columns

    # Create a Rich console
    console = Console(width=width, force_terminal=True)

    # Create the streaming renderer
    renderer = StreamingRenderer(console)

    print("🤖 Simulating LLM streaming output with md2term...\n")
    time.sleep(1)

    try:
        # Stream the content character by character
        for char in markdown_content:
            renderer.add_text(char)

            # Simulate network delay (like real LLM streaming)
            # Adjust this value to make it faster/slower
            time.sleep(0.02)  # 20ms delay per character

    except KeyboardInterrupt:
        print("\n\n⚠️  Streaming interrupted by user")
    finally:
        # Always finalize to ensure complete rendering
        renderer.finalize()
        print("\n✅ Streaming complete!")


def simulate_chunk_streaming():
    """
    Simulate streaming in larger chunks (more realistic for real applications).

    This is more similar to how actual LLM APIs work - they send chunks
    of text rather than individual characters.
    """
    # Different markdown content for the second example
    chunks = [
        "# Product Documentation\n\n",
        "Welcome to our **API documentation**. ",
        "This guide will help you get started.\n\n",
        "## Authentication\n\n",
        "To authenticate, you'll need an API key:\n\n",
        "```bash\n",
        'curl -H "Authorization: Bearer YOUR_API_KEY" \\\n',
        "     https://api.example.com/v1/data\n",
        "```\n\n",
        "## Rate Limits\n\n",
        "Please note the following limits:\n\n",
        "- **Free tier**: 100 requests/hour\n",
        "- **Pro tier**: 1,000 requests/hour\n",
        "- **Enterprise**: *Unlimited*\n\n",
        "> **Important**: Rate limits reset every hour\n",
        "> at the top of the hour (e.g., 2:00 PM, 3:00 PM).\n\n",
        "For more information, visit our [support page](https://example.com/support).\n",
    ]

    # Get terminal width
    width = shutil.get_terminal_size().columns

    # Create a Rich console
    console = Console(width=width, force_terminal=True)

    # Create the streaming renderer
    renderer = StreamingRenderer(console)

    print("📚 Simulating chunk-based streaming (more realistic)...\n")
    time.sleep(1)

    try:
        # Stream in chunks
        for i, chunk in enumerate(chunks):
            print(f"📦 Chunk {i+1}/{len(chunks)}", end="\r")
            renderer.add_text(chunk)

            # Simulate processing time between chunks
            time.sleep(0.3)  # 300ms between chunks

    except KeyboardInterrupt:
        print("\n\n⚠️  Streaming interrupted by user")
    finally:
        # Clear the chunk counter and finalize
        print(" " * 20, end="\r")  # Clear the chunk counter
        renderer.finalize()
        print("\n✅ Chunk streaming complete!")


def demonstrate_library_usage():
    """
    Show how to integrate md2term into your own application.

    This is the pattern you would use in your own code.
    """
    print("🔧 Library Integration Example\n")

    # Your application's markdown content (could come from anywhere)
    content_parts = [
        "# My Application Output\n\n",
        "Processing your request",
        ".",
        ".",
        ".\n\n",
        "**Results found!**\n\n",
        "Here's what I discovered:\n\n",
        "```json\n",
        '{\n  "status": "success",\n  "data": [\n    {"id": 1, "name": "Item 1"},\n    {"id": 2, "name": "Item 2"}\n  ]\n}\n',
        "```\n\n",
        "Analysis complete! 🎉",
    ]

    # Set up md2term streaming
    console = Console(force_terminal=True)
    renderer = StreamingRenderer(console)

    try:
        for part in content_parts:
            # In a real app, this might come from:
            # - API responses
            # - Database queries
            # - File processing
            # - LLM streaming
            renderer.add_text(part)
            time.sleep(0.5)  # Simulate processing time

    finally:
        renderer.finalize()

    print("\n💡 This is how you'd integrate md2term into your own Python application!")


if __name__ == "__main__":
    print("🚀 md2term Library Streaming Examples\n")
    print(
        "This demonstrates how to use md2term as a library in your Python applications."
    )
    print("Press Ctrl+C at any time to interrupt.\n")

    # Run the examples
    try:
        # Example 1: Character-by-character streaming (like LLM output)
        simulate_llm_streaming()

        print("\n" + "=" * 60 + "\n")

        # Example 2: Chunk-based streaming (more realistic)
        simulate_chunk_streaming()

        print("\n" + "=" * 60 + "\n")

        # Example 3: Library integration pattern
        demonstrate_library_usage()

    except KeyboardInterrupt:
        print("\n\n👋 Examples interrupted. Goodbye!")

    print("\n🎯 Key takeaways:")
    print("  • Import StreamingRenderer from md2term")
    print("  • Create a Rich Console")
    print("  • Use renderer.add_text() for each chunk")
    print("  • Always call renderer.finalize() when done")
    print("  • Perfect for LLM streaming, API responses, and real-time content!")
