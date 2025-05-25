---
name: Bug report
about: Create a report to help us improve md2term
title: ""
labels: bug
assignees: ""
---

## Bug Description

A clear and concise description of what the bug is.

## Reproduction Steps

Please provide the exact steps to reproduce the issue:

1.
2.
3.

## Minimal Markdown Example

**Please provide the exact, minimal markdown content that reproduces the issue:**

```markdown
<!-- Paste your minimal markdown example here -->
<!-- Remove any unnecessary content - keep only what's needed to reproduce the bug -->
```

## Expected Behavior

A clear and concise description of what you expected to happen.

## Actual Behavior

A clear and concise description of what actually happened.

## Environment

- **md2term version**: (run `md2term --version`)
- **Operating System**: (e.g., macOS 14.0, Ubuntu 22.04, Windows 11)
- **Terminal**: (e.g., iTerm2, Terminal.app, Windows Terminal, etc.)
- **Terminal width**: (run `tput cols` or specify if using `--width`)

## Streaming Issues

If your issue is related to streaming input (stdin), please test with the `pv` utility to simulate streaming:

```bash
# Install pv if you don't have it:
# macOS: brew install pv
# Ubuntu/Debian: sudo apt install pv
# Other systems: check your package manager

# Test with simulated streaming (adjust speed as needed):
cat your_file.md | pv -sL 200 | md2term

# Or test with a specific example:
echo "your markdown content here" | pv -sL 200 | md2term
```

**Streaming test results:**

- [ ] Issue occurs with direct file input (`md2term file.md`)
- [ ] Issue occurs with piped input (`cat file.md | md2term`)
- [ ] Issue occurs with simulated streaming (`cat file.md | pv -sL 200 | md2term`)

## Additional Context

Add any other context about the problem here, such as:

- Screenshots of the terminal output (if visual)
- Any error messages
- Whether the issue is consistent or intermittent
- Any workarounds you've found
