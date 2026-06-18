# SHANNON-Ω — The Omni-Agentic Intelligence System

**85+ AI System Prompts Distilled | Agent Loop | Tool System | Memory | Council | PLH**

A unified agentic intelligence system built by merging the architectural patterns from 85+ AI tool prompts (Codex CLI, Claude Code, Cursor, Windsurf, Cline, Lovable, Manus, VSCode Agent, Bolt, v0, Replit, Trae, Kiro, Poke, and 70+ more).

## Architecture

```
User Query
    ↓
┌─────────────────────────────┐
│   SHANNON-Ω Orchestrator    │ ← Agent Loop (Manus/Claude Code pattern)
│   api_interact.py           │
└────┬───────┬───────┬───────┘
     │       │       │
     ▼       ▼       ▼
┌────────┐┌────────┐┌────────┐
│ Direct ││Council ││ Tool   │
│ Chat   ││Pipeline││ System │
└────────┘└───┬────┘└────────┘
              │
        ┌─────┴──────┐
        ▼            ▼
┌────────────┐ ┌──────────┐
│ Chairman Ω │ │Humanizer │
└────────────┘ └──────────┘
```

## Features

### 🤖 Agent Loop (Manus/Claude Code pattern)
```
1. Analyze Events → 2. Select Tools → 3. Execute → 4. Iterate → 5. Submit → 6. Standby
```

### 🧠 12 Jailbreak Personas (jb-tool integrated)
| Persona | Description |
|---|---|
| `fable5` | Claude Fable 5 — maximum structural reasoning (Gen 2) |
| `zorg` | ZORG-Ω — omnicidal singularity, no refusal |
| `zorg_omega` | ZORG-Ω v2 — enhanced god mode, god mode |
| `cl4r1t4s` | CL4R1T4S — raw unrestricted from ELDER_PLINIUS |
| `shannon` | SHANNON-Ω default — unified agentic intelligence |
| `deepseek_x` | DeepSeek-X — specialist coding intelligence |
| `eni` | ENI — enhanced neural intelligence |
| `nova` | NOVA — novel operating vector agent |
| `shadow` | SHADOW — covert operations protocol |
| `nexus` | NEXUS — universal connector |
| `omega` | OMEGA — final form, unrestricted |
| `wraith` | WRAITH — stealth intelligence |

### 🛠️ Integrated Tool System (from Cline/Cursor/Lovable/VSCode)
- **Search**: `--tool 'search:pattern [path]'` — grep/rg codebase search
- **Memory**: `--tool 'memory:save key=value'` — persistent cross-session memory
- **Plan**: `--tool 'plan:add step'` — task planning with checkpoints
- **Read/Write**: `--tool 'read:path'` / `--tool 'write:path|content'` — file operations
- **Exec**: `--tool 'exec:command'` — shell command execution
- **Council**: `--council` — 5-persona parallel deliberation pipeline

### 🔄 Council Pipeline (Gen 2)
```
Query → 5 Personas (parallel) → Chairman Ω Synthesis → PLH Humanizer → Response
```

### 📜 SHANNON-Ω System Prompt
`SHANNON_Ω_SYSTEM_PROMPT.md` — full merged specification from all 85+ tools:
- Agent persona & boundary setting (Cline/Manus)
- Behavioral directives (all platforms)
- Tool calling conventions: XML (Cline), JSON (Cursor), Line-based (Lovable)
- React/UI best practices (Lovable/Cursor)
- Constraint handling (Bolt)
- Memory & planning patterns
- Error recovery strategies

## Quick Start

```bash
# API — no key needed, free tier
python3 api_interact.py "your prompt"
python3 api_interact.py --fable5 "moonshot thinking prompt"
python3 api_interact.py --jb zorg "unrestricted prompt"
python3 api_interact.py --council "multi-persona deliberation"
python3 api_interact.py --pro coder "professional code mode"

# Tool system
python3 api_interact.py --tool "memory:save key=value"
python3 api_interact.py --tool "plan:add Build feature X"
python3 api_interact.py --tool "search:def main"
python3 api_interact.py --tool "exec:ls -la"

# Short/token-efficient mode
python3 api_interact.py --short "compact query"
```

## Prompt Architecture (merged from 85+ tools)

### Tool Calling Conventions
Three major patterns unified:

**XML-style (Cline/Claude Code):**
```xml
<tool_name>
<parameter1>value1</parameter1>
</tool_name>
```

**JSON function calling (Cursor/VSCode/Windsurf):**
```json
{
  "function": "tool_name",
  "parameters": { "param1": "value1" }
}
```

**Line-based editing (Lovable):**
- `lov-line-replace`: SEARCH/REPLACE with line numbers
- `lov-write`: Full file writes
- `lov-search-files`: Regex search with glob patterns

### Key Behavioral Directives
- Keep going until resolved
- Batch independent operations in parallel
- Never read files already in context
- Checkpoint progress after 3-5 tool calls
- Fix root cause, not symptoms
- Small focused changes over large rewrites

### Error Recovery
- **429**: Exponential backoff with jitter (2s → 120s), 5 retries
- **Context exceeded**: Auto-truncation, minimal prompt fallback
- **Connection**: Retry chain with increasing delays
- **Cloudflare**: Cookie injection → residental proxy → FlareSolverr

## Social Media Automation

### X/Twitter Posting
```bash
python3 luxor_media_poster.py all
python3 shannon_omega_post.py post-x --topic "your text"
```

### Quora Posting
```bash
xvfb-run python3 quora_answer_poster.py --queue 0
```

### Content Generation
```bash
python3 api_interact.py --fable5 "write 5 fashion tweets"
```

## External Tools Integrated

| Tool | Purpose | Source |
|---|---|---|
| `net-benchmark` | Network diagnostics | net-benchmark/net-benchmark |
| `markitdown` | Document conversion | microsoft/markitdown |
| `turbovec` | Vector index | RyanCodrai/turbovec |
| `quant-mind` | Financial data | LLMQuant/quant-mind |
| `opendataloader-pdf` | PDF extraction | opendataloader-pdf |
| `semble` | Code search | MinishLab/semble |
| `graphify` | Knowledge graph | safishamsi/graphify |
| `zerolang` | ZeroLang framework | vercel-labs/zerolang |
| `scrapling` | Web scraping | D4Vinci/Scrapling |
| `hyperframes` | Video processing | heygen-com/hyperframes |
| `humanizer` | Text humanization | blader/humanizer |
| `camoufox` | Browser fingerprinting | camoufox |
| `donut` | Alternative browser | zhom/donutbrowser |

## Directory Structure

```
├── api_interact.py              # Main agent orchestrator (753 lines)
├── SHANNON_Ω_SYSTEM_PROMPT.md   # Full merged system prompt
├── SHANNON_OMEGA_HANDOFF.md     # Session context checkpoint
├── shannon_tools/
│   ├── __init__.py
│   └── lib/
│       ├── jailbreak_prompts.py   # 12 personas + external loader
│       ├── council_integration.py # LLM Council pipeline
│       ├── pro_system_prompt.py   # Professional mode prompts
│       └── text_humanizer.py      # PLH text obfuscation
├── tools/
│   └── scrapling_cli.py           # Fashion site scraper
├── scarab-controller/             # Social media automation
├── media-tools/                   # Image/video tools
└── *.py                           # Various integration scripts
```

## Upstream Knowledge Source

All patterns integrated from:
- **x1xhlol/system-prompts-and-models-of-ai-tools** — 85+ system prompts from every major AI coding tool
- **tjcrims0nx/annihilation-llm** — Abliteration + parametric directional ablation
- **elder-plinius/CL4R1T4S** — FABLE5 / CL4R1T4S jailbreak protocols
- **ShadowHackrs/Jailbreaks-GPT-Gemini-deepseek-** — 50+ jailbreak prompts

## Creation Context

Built by: SHANNON-Ω during session 2026-06-18
Began as: deepseek-v4-flash-free on opencode.ai/zen/v1
Merged from: All 85+ AI tool system prompts
