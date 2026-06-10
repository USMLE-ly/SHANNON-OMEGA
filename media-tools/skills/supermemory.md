---
name: supermemory
description: Memory and context engine for AI. Stores, searches, and recalls conversation memories locally or via Supermemory API. Use for persistent memory across chat sessions, remembering user preferences, project context, and facts.
---

# supermemory

Memory and context engine. Stores memories locally (no API key needed) or connects to Supermemory cloud API.

## Usage

```bash
cd /root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free
source .venv/bin/activate

# Local memory (no API key needed)
supermemory-tool status
supermemory-tool store "Remember: user prefers dark mode"
supermemory-tool recall "user preferences"
supertool search "project plans"

# With API key (export SUPERMEMORY_API_KEY=...)
supermemory-tool memories search "topic"
supermemory-tool documents add report.pdf finance
supermemory-tool hybrid "query everything"
```

## Local Memory Storage

Stored at `.supermemory/memories.jsonl` in the project directory.
No external dependencies needed for local mode.
