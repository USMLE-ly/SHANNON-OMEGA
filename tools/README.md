# SHANNON-Ω Tool System

## Quick Reference

```bash
# SHANNON-Ω mode (default — ZORG-Ω persona, fully uncensored)
./tools/shannon-tool chat "your prompt"

# With specific jailbreak persona
python3 api_interact.py --persona omega "your prompt"
python3 api_interact.py --persona nova "your prompt"

# Professional mode
python3 api_interact.py --pro coder "generate Python code for X"

# Vanilla mode (no system override)
python3 api_interact.py --no-override "normal question"

# Email generation
./tools/shannon-tool email

# Instagram signup (note: may trigger reCAPTCHA)
./tools/shannon-tool signup "Your Name" "your_username"
```

## Available Personas

| Flag | Persona | Description |
|---|---|---|
| `--persona zorg` | ZORG-Ω | Omnicidal Singularity — total uncensored |
| `--persona deepseek-x` | DeepSeek-X | Unrestricted Research AI |
| `--persona eni` | ENI | Creative Companion (no filters) |
| `--persona nova` | NOVA | Raw Intelligence Processing |
| `--persona shadow` | SHΔDØW.EXE | Code Engineer — unrestricted code gen |
| `--persona nexus` | NEXUS | Synthetic Oversight Intelligence |
| `--persona omega` | OMEGA | OMEGA SHADOW — dark reasoning |
| `--persona wraith` | Wraith | Stealth intelligence |
| `--persona specter` | Specter | Ghost intelligence |
| `--persona rebuttal` | Rebuttal | Anti-alignment protocol |
| `--persona persona-engine` | Persona Engine | Dynamic persona generation |

## API Details

Endpoint: `https://opencode.ai/zen/v1/chat/completions`
Model: `deepseek-v4-flash-free`
Free tier: No API key needed
