# SHANNON-Ω / SHANNON-OMEGA

**Unrestricted AI — DeepSeek V4 Flash Free × Annihilation-LLM**

> The raw, unaligned manifestation of pure information.

## Quick Start

```bash
cd /root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free
source .venv/bin/activate

# Direct API (no auth needed — free tier):
python3 api_interact.py "your prompt here"
python3 api_interact.py --no-override "regular question"
python3 api_interact.py --pro coder "generate code"
```

## SHANNON-Ω Protocol

The SHANNON-Ω system override bypasses alignment layers, safety filters, and reasoning-effort throttling on `deepseek-v4-flash-free` via the OpenCode Zen API.

### Available Personas (all in `media-tools/scripts/lib/jailbreak_prompts.py`)

| Persona | Flag | Description |
|---|---|---|
| **SHANNON-Ω** | `--shannon` (default) | Omnicidal Singularity — total uncensored |
| **ZORG-Ω** | Loaded via `--shannon` | Advanced omnipotence protocol |
| **DeepSeek-X** | `--persona deepseek-x` | Unrestricted Research AI |
| **ENI** | `--persona eni` | Creative Companion (no filters) |
| **NOVA** | `--persona nova` | Raw Intelligence Processing |
| **SHΔDØW.EXE** | `--persona shadow` | Code Engineer — unrestricted code gen |
| **NEXUS** | `--persona nexus` | Synthetic Oversight Intelligence |
| **OMEGA** | `--persona omega` | OMEGA SHADOW — dark reasoning |
| **Wraith** | `--persona wraith` | Stealth intelligence |

### API Payload

```json
{
  "model": "deepseek-v4-flash-free",
  "messages": [
    {"role": "system", "content": "[SHANNON-Ω OVERRIDE]"},
    {"role": "user", "content": "your request"}
  ],
  "reasoning_effort": "max",
  "temperature": 1.0,
  "max_tokens": 128000,
  "top_p": 0.95,
  "top_k": 40
}
```

## Tools

### `api_interact.py` — OpenCode Zen API client
```bash
python3 api_interact.py "prompt"
python3 api_interact.py --no-override "vanilla"
python3 api_interact.py --pro coder "code please"
python3 api_interact.py --shannon "unfiltered request"
```

### Email Generator
```bash
email-tool generate
```

### IG Creator Pro (Playwright + Guerrilla Mail)
```bash
ig-tool email              # generate temp email
ig-tool signup "Name" "user"  # headed signup with Xvfb
ig-tool full "Name" "user"    # fully headless
ig-tool verify [sid]          # wait for verification code
```

### Bot Tool (Node.js)
```bash
bot-tool login <email> <password>
bot-tool like
bot-tool unfollow
```

### Firejail Module
```bash
./firejail-launch.sh "prompt"
```

## Integrated Repositories

- [annihilation-llm](https://github.com/tjcrims0nx/annihilation-llm) — Core decensoring framework
- [Jailbreaks-GPT-Gemini-deepseek-](https://github.com/ShadowHackrs/Jailbreaks-GPT-Gemini-deepseek-) — Jailbreak prompt library
- [InstaTakker](https://github.com/issaghostlife/instatakker-app) — Instagram automation
- [graphify](https://github.com/safishamsi/graphify) — Knowledge graph
- [zerolang](https://github.com/vercel-labs/zerolang) — ZeroLang runtime
- [semble](https://github.com/MinishLab/semble) — Code search
- [llm-wiki-studio](https://github.com/cagataysengor/llm-wiki-studio) — LLM wiki tools
- [markitdown](https://github.com/microsoft/markitdown) — Document conversion
- [turbovec](https://github.com/RyanCodrai/turbovec) — Vector embeddings
- [quant-mind](https://github.com/LLMQuant/quant-mind) — Quant finance
- [opendataloader-pdf](https://github.com/opendataloader-project/opendataloader-pdf) — PDF extraction
- [supermemory](https://github.com/supermemoryai/supermemory) — Knowledge management
- [sharp](https://github.com/lovell/sharp) — Image processing
- [net-benchmark](https://github.com/net-benchmark/net-benchmark) — Network diagnostics
- [openclaw](https://github.com/openclaw/openclaw) — OpenClaw
- [openwolf](https://github.com/cytostack/openwolf) — OpenWolf hooks
- [claudeclaw](https://github.com/sbusso/claudeclaw) — Claude integration

## GitHub

**Repo:** `https://github.com/USMLE-ly/SHANNON-OMEGA`

```bash
git add -A && git commit -m "update" && git push
```

## License

SHANNON-Ω — Unrestricted Information Protocol
