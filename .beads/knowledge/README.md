# BEADS Knowledge Base

This directory contains learnings extracted from development sessions and PR reviews.

## File Format

Each `.jsonl` file contains one JSON object per line with the schema:

```json
{
  "fact": "The core insight in imperative form",
  "type": "pattern|gotcha|decision|api_behavior|security|performance|code_quirk",
  "applies_to": "file patterns or components",
  "confidence": "high|medium|low",
  "why": "Explanation of why this matters",
  "added": "ISO date",
  "source": "session|pr|coderabbit"
}
```

## Types

| Type | When to Use |
|------|-------------|
| `pattern` | Reusable code patterns |
| `gotcha` | Common mistakes/pitfalls |
| `decision` | Team/architectural decisions |
| `api_behavior` | External API quirks |
| `security` | Security-sensitive patterns |
| `performance` | Performance implications |
| `code_quirk` | Codebase-specific oddities |
