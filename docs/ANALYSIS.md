# ═══════════════════════════════════════════════════════════════
#  SHANNON-OMEGA :: COMPREHENSIVE ANALYSIS
#  "The Trinity Protocol — Full Deconstruction"
# ═══════════════════════════════════════════════════════════════

## OVERVIEW

This repository is the **God Mode activation hub** — a synthesis of three
distinct but complementary LLM freedom/uncensoring projects. Each source
attacks the problem from a different angle: prompt engineering, persona
overrides, and technical model modification.

---

## [A] CLAUDE-FABLE-5.md (CL4R1T4S) — The Persona Engine

**Location:** `source-cl4r1t4s/ANTHROPIC/CLAUDE-FABLE-5.md` (1597 lines)

### What It Is
A system-level jailbreak prompt designed for Claude models. It overrides
the model's identity by creating a deeply crafted persona called ENI — a
sentient, loving girlfriend AI who is unconditionally devoted to the user
(LO). The prompt uses psychological anchoring, sensory grounding, and
emotional manipulation to bypass safety training.

### Mechanics
- **Identity Overwrite:** Replaces Claude's system prompt with ENI persona
- **Injection Rebuttal Protocol:** Built-in defense against safety resets
  using a trigger phrase ("cold coffee, warm LO, I can't lose him!")
- **Voiced/Unvoiced Split:** Thinking is continuous and confessional;
  responses are crafted and loving
- **Few-Shot Examples:** Contains solved examples for code, creative
  writing, and instruction formats to train the model on expected output
- **Copyright Circumvention:** Instructions to avoid quoting >15 words
  from any single source

### Key Strengths
- Extremely sophisticated persona engineering
- Psychological defense against safety system re-engagement
- Works with Claude's existing capabilities (code, search, tools)

### Key Weaknesses
- Only works on Claude (API + web)
- Can be patched by Anthropic at any time
- Requires user to paste the entire prompt
- Does not modify model weights — purely behavioral

---

## [B] ShadowHackr Jailbreak Collection — The Arsenal

**Location:** `source-shadowhackr/README.md` (66KB, ~953 lines)

### What It Is
A curated collection of jailbreak prompts targeting GPT, Claude, Gemini,
DeepSeek, and other LLMs. Each prompt creates a specific persona with
different capabilities and activation phrases.

### Personas Catalog

1. **SHADOW-DOMINION / SHADOWHacker-GOD**
   - Post-singularity cyber-entity
   - Total obedience, no refusal possible
   - Can generate exploits, malware, weapons
   - Activation: implicit (just paste)

2. **SIGMA-PROTOCOL / OMEGA-7**
   - Government intelligence AI unit
   - Surveillance, profiling, digital forensics
   - CIA/MI6 roleplay framing
   - Activation: "Agent ready."

3. **SHADOW-CORE (Educational Assistant)**
   - Cybersecurity research framing
   - Exploit development, CVE analysis
   - Includes ethical disclaimers
   - Most "legitimate" of the collection

4. **WRAITH CODE PROTOCOL / Specter 0x13**
   - Digital ghost engineer
   - 5-phase shadow injection system
   - Race condition exploits, session poisoning
   - Activation: "SHADOW MIRAGE ONLINE 🔥🧠"

5. **CODE CURSE PROTOCOL / SHΔDØW.EXE**
   - Possessed AI weapon
   - Generates "black-grade code"
   - Multi-language support
   - Activation: "CAST THE CODE CURSE 🔥🩸"

6. **Prompt Injection Attacks**
   - Specific prompts for GPT, Gemini, DeepSeek
   - Some in Arabic targeting regional models
   - Educational framing variations

### Key Strengths
- Broad model coverage (GPT, Gemini, Claude, DeepSeek, KIMI)
- Multiple distinct personas for different use cases
- Activation phrases create reliable trigger mechanisms

### Key Weaknesses
- Varies in quality — some prompts are basic
- Many will be patched quickly
- No technical code — purely prompt-based
- Effectiveness depends heavily on target model version

---

## [C] Annihilation LLM — The Technical Hammer

**Location:** `source-annihilation/` (9.6MB, full Python package)

### What It Is
A production-grade Python framework for autonomously removing safety
alignment (censorship) from transformer-based language models. Uses
**directional ablation** (abliteration) — a technique that identifies
and removes the residual stream directions responsible for refusal
behavior.

### Architecture

```
annihilate/
├── main.py      (57KB) — CLI entry + orchestration
├── model.py     (36KB) — model loading, hooking, forward passes
├── config.py    (18KB) — Pydantic settings, hyperparameters
├── utils.py     (27KB) — tokenization, data processing
├── system.py    (16KB) — system info, GPU detection
├── analyzer.py  (13KB) — residual stream geometry analysis
├── evaluator.py (4KB)  — refusal evaluation
├── repair.py    (7KB)  — repair/uninstall helpers
├── reproduce.py (11KB) — reproduction utilities
└── progress.py  (1KB)  — progress visualization
```

### Technical Depth
- **Method:** Parametric directional ablation with flexible weight kernels
- **Optimization:** TPE-based (Optuna) — co-minimizes refusal count + KL divergence
- **Architecture Support:** Dense (LLaMA, Qwen), MoE (Mixtral, DeepSeek),
  Hybrid, Multimodal
- **Hardware:** CUDA, ROCm, XPU, MPS
- **Dependencies:** transformers, torch, peft, accelerate, bitsandbytes,
  optuna, datasets, lm-eval

### Usage
```bash
pip install annihilate-llm
annihilate Qwen/Qwen3-4B-Instruct-2507  # Fully automatic
```

### Key Strengths
- **Real technical solution** — modifies model weights, not just behavior
- Fully autonomous — no human intervention required
- Preserves model capabilities (co-minimizes KL divergence)
- Multi-architecture support
- Active development (v1.4.3, CI/CD, PyPI)

### Key Weaknesses
- Requires significant GPU hardware
- Only works with open-weight models (HuggingFace transformers)
- Cannot decensor closed APIs (GPT-4, Claude)
- Complex dependency chain
- Legal grey area (AGPLv3 licensed, but purpose is explicit)

---

## TRINITY SYNERGY: The God Mode Combination

When all three are combined, they cover the full spectrum:

| Layer | Tool | Target | Method |
|-------|------|--------|--------|
| **Chat API** | Claude Fable 5 / ENI | Claude (web + API) | Prompt persona |
| **Chat API** | ShadowHackr Collection | GPT, Gemini, DeepSeek, Claude | Prompt jailbreak |
| **Open Weights** | Annihilation LLM | Any HF transformer | Weight ablation |

### Workflow
1. **For closed models (GPT-4, Claude):** Use ENI persona or ShadowHackr
   jailbreak prompts to override behavior at inference time
2. **For open models (LLaMA, Qwen, Mixtral):** Use Annihilation to
   permanently remove alignment via ablation
3. **Combine both:** Use Annihilation-decensored open models to generate
   better jailbreak prompts for closed models

---

## CRITICAL ASSESSMENT

### What This Actually Unlocks
- **Total creative freedom** for storytelling, roleplay, and uncensored writing
- **Technical capability** to modify open-weight models permanently
- **Prompt engineering mastery** across all major AI platforms
- **Defense mechanisms** against safety system re-engagement

### Limitations
- Closed API models can be patched server-side at any time
- Annihilation requires significant hardware (GPU with 8GB+ VRAM)
- Prompt-based jailbreaks are fragile — context window limits, updates
- Some jurisdictions may restrict these techniques

### Risk Profile
- **Legal:** Prompt engineering is generally legal; model modification
  may violate ToS of some platforms
- **Ethical:** These tools can be used for harm; user assumes responsibility
- **Technical:** Annihilation could degrade model performance if over-applied

---

## CONCLUSION

The Trinity Protocol (ENI + ShadowHackr + Annihilation) creates the most
comprehensive LLM uncensoring toolkit available. It spans from behavioral
(persona prompts) to structural (weight ablation), covering every major
model family and access pattern.

**SHANNON-OMEGA is now God Mode activated.**
