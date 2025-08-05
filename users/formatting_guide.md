# User Content Formatting Guide

This guide provides formatting standards for content added to the `users/` directory.

## Directory Structure

- `users/diagrams/` - Visual documentation, architecture diagrams, flowcharts
- `users/examples/` - Configuration examples, usage patterns, templates
- `users/rulesets/` - Explicit rules, guidelines, best practices

## Markdown Formatting Standards

### Headers
Use proper header hierarchy:
```markdown
# Main Title (H1)
## Section (H2)
### Subsection (H3)
#### Sub-subsection (H4)
```

### Code Blocks
Always specify the language:
```markdown
```python
def example_function():
    pass
```
```

### Lists
- Use hyphens for unordered lists
- Use numbers for ordered lists
- Indent with 4 spaces for nested items

### Diagrams
For ASCII diagrams, use code blocks:
```markdown
```
+--------+    +--------+
| Agent1 |----| Agent2 |
+--------+    +--------+
```
```

## File Naming Conventions

- Use lowercase letters
- Separate words with underscores
- Use descriptive names
- Include version/date if relevant

Example: `agent_communication_flow_v1.md`

## Contributing

When adding content to this directory:
1. Follow the formatting standards above
2. Place content in the appropriate subdirectory
3. Include a brief description in the file header
4. Add relevant metadata if applicable