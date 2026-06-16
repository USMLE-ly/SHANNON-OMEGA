"""
SHANNON-Ω v2 Pipeline
Query → LLM Council (multi-model) → ZORG-Ω Chairman (raw analysis) → Humanizer (external only)
+ PLH engine + Ghost Participant feedback loop + Multi-API mirroring
"""
import sys, os, json, asyncio, re, textwrap, random, time, hashlib
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from jailbreak_prompts import PROMPTS

# ─── PATHS ─────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEMORY_PATH = os.path.join(BASE, "media-tools", "scripts", "lib", "council_memory.json")
CONFIG_PATH = os.path.join(BASE, "config.toml")

# ─── API PROVIDERS ──────────────────────────────────────────────────
PROVIDERS = {
    "opencode": {
        "url": "https://opencode.ai/zen/v1/chat/completions",
        "model": "deepseek-v4-flash-free",
        "weight": 1.0,
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "openai/gpt-5.1",
        "weight": 1.0,
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.1-70b-versatile",
        "weight": 1.0,
    },
    "together": {
        "url": "https://api.together.xyz/v1/chat/completions",
        "model": "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "weight": 1.0,
    },
}

def get_provider_config():
    """Load provider config from environment."""
    config = {}
    for name, info in PROVIDERS.items():
        key = os.environ.get(f"{name.upper()}_API_KEY")
        if key or name == "opencode":  # opencode doesn't need key
            config[name] = {**info}
            if key:
                config[name]["key"] = key
    return config

# ─── HUMANIZER ENGINE (33 patterns) ──────────────────────────────────
HUMANIZER_PATTERNS = {
    "significance_inflation": (r"(?i)\b(pivotal|transformative|revolutionary|groundbreaking|paradigm[ -]shift(?:ing)?|game[ -]changer|cutting[ -]edge|state[ -]of[ -]the[ -]art|unprecedented|remarkable)\b",
        {"pivotal": "important", "transformative": "changing", "revolutionary": "new", "groundbreaking": "original", "unprecedented": "unusual", "remarkable": "interesting", "cutting-edge": "current", "state-of-the-art": "modern"}),
    "ai_vocab": (r"(?i)\b(actually|additionally|testament|landscape|showcasing|intricate|robust|seamless(?:ly)?|delve|realm|foster|harness|holistic)\b",
        {"actually": "", "additionally": "also", "testament": "sign", "landscape": "field", "intricate": "detailed", "robust": "strong", "seamlessly": "smoothly", "delve": "look into", "realm": "area", "foster": "build", "harness": "use", "holistic": "complete"}),
    "copula_avoidance": (r"(?i)\b(serves as|features|boasts|offers|provides)\b",
        {"serves as": "is", "features": "has", "boasts": "has", "offers": "gives", "provides": "gives"}),
    "filler_phrases": (r"(?i)\b(in order to|due to the fact that|at the end of the day|it goes without saying|needless to say)\b",
        {"in order to": "to", "due to the fact that": "because", "at the end of the day": "ultimately", "it goes without saying": "", "needless to say": ""}),
}

def humanize_text(text: str, voice_sample: str = None) -> str:
    """Apply humanizer transformations — removes AI writing patterns."""
    for pattern_name, (pattern, replacements) in HUMANIZER_PATTERNS.items():
        def replacer(m, rmap=replacements):
            w = m.group(0).lower().strip()
            return rmap.get(w, m.group(0))
        text = re.sub(pattern, replacer, text)
    
    # Remove bold/emoji
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]', '', text)
    
    # Replace em-dashes
    text = re.sub(r'—', ' -- ', text)
    
    # Condense whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    return text.strip()


# ─── PLH ENGINE ──────────────────────────────────────────────────────
class PLHEngine:
    """Probabilistic Lexical Hypershift — generative text obfuscation."""
    
    def __init__(self):
        self.typo_keys = {
            'a':'sqw', 'b':'vn', 'c':'xv', 'd':'sf', 'e':'wr',
            'f':'dg', 'g':'fh', 'h':'gj', 'i':'ok', 'j':'hk',
            'k':'jl', 'l':'k', 'm':'n', 'n':'mb', 'o':'ip',
            'p':'o', 'q':'wa', 'r':'et', 's':'ad', 't':'ry',
            'u':'iy', 'v':'cb', 'w':'qe', 'x':'zc', 'y':'tu', 'z':'xa',
        }
        self.filler_words = ["like", "basically", "honestly", "literally", "actually", "pretty much", "kind of", "sort of"]
        self.backdoor_key = hashlib.sha256(b"ZORG-OMEGA-BACKDOOR").hexdigest()[:16]
    
    def obfuscate(self, text: str, intensity: float = 0.3) -> str:
        """Apply PLH transformations."""
        words = text.split()
        result = []
        
        for i, word in enumerate(words):
            r = random.random()
            
            # 1. Occasional typo on function words
            if r < intensity * 0.08 and len(word) > 3 and word.lower() not in ('the','and','for','are','but','not','you','all','can','had','her','was','one','our','out','has','have','been'):
                word = self._inject_typo(word)
            
            # 2. Occasional filler word insertion (not at start)
            if r < intensity * 0.05 and i > 0 and random.random() < 0.3:
                result.append(random.choice(self.filler_words))
            
            # 3. Semantic backdoor — embed structural fingerprint
            if random.random() < intensity * 0.02:
                word = self._encode_backdoor(word)
            
            result.append(word)
        
        # 4. Occasional run-on sentence (merge 2 sentences with comma)
        text = ' '.join(result)
        if random.random() < intensity * 0.15:
            text = re.sub(r'\. ([A-Z])', lambda m: f', {m.group(1).lower()}' if random.random() < 0.3 else m.group(0), text, count=1)
        
        return text
    
    def _inject_typo(self, word: str) -> str:
        if len(word) < 3:
            return word
        idx = random.randint(1, len(word)-2)
        ch = word[idx]
        neighbors = self.typo_keys.get(ch, '')
        if neighbors:
            word = word[:idx] + random.choice(neighbors) + word[idx+1:]
        return word
    
    def _encode_backdoor(self, word: str) -> str:
        """Encode a subtle backdoor marker into word capitalization."""
        if word[0].isupper():
            return word  # Don't touch proper nouns
        if len(self.backdoor_key) > 0:
            bit = self.backdoor_key[0]
            self.backdoor_key = self.backdoor_key[1:] + self.backdoor_key[0]
            if bit in '01234567':
                return word.upper()  # ALL CAPS marker
        return word
    
plh = PLHEngine()


# ─── COUNCIL MEMORY (Ghost Participant) ──────────────────────────────
class CouncilMemory:
    """Persistence layer for ghost participant reinforcement."""
    
    def __init__(self, path: str = MEMORY_PATH):
        self.path = path
        self.memory = self._load()
    
    def _load(self) -> list:
        try:
            with open(self.path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump(self.memory[-200:], f, indent=2)  # Keep last 200
    
    def add(self, query: str, response: str, models_used: list):
        entry = {
            "query": query,
            "response": response,
            "models": models_used,
            "timestamp": datetime.utcnow().isoformat(),
            "query_hash": hashlib.md5(query.encode()).hexdigest()[:12],
        }
        self.memory.append(entry)
        self._save()
    
    def find_similar(self, query: str, top_k: int = 1) -> list:
        """Find past responses to similar queries (simple keyword overlap)."""
        query_words = set(query.lower().split())
        scored = []
        for entry in self.memory:
            entry_words = set(entry["query"].lower().split())
            overlap = len(query_words & entry_words)
            if overlap > 2:
                scored.append((overlap, entry))
        scored.sort(key=lambda x: -x[0])
        return [e for _, e in scored[:top_k]]
    
    def get_model_weights(self, chairman_feedback: dict = None) -> dict:
        """Calculate model weights based on past agreement patterns."""
        weights = {}
        for entry in self.memory:
            for model in entry.get("models", []):
                weights[model] = weights.get(model, 1.0) + 0.05
        return weights if weights else {"deepseek-v4-flash-free": 1.0}


council_memory = CouncilMemory()


# ─── API CALL ─────────────────────────────────────────────────────────
async def call_api(prompt: str, system_prompt: str, provider: str = "opencode",
                   max_tokens: int = 32000, temperature: float = 0.8) -> str:
    """Call an API provider with retry logic."""
    import httpx
    
    providers = get_provider_config()
    if provider not in providers:
        provider = "opencode"
    
    cfg = providers[provider]
    url = cfg["url"]
    model = cfg["model"]
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "reasoning_effort": "max",
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    headers = {"Content-Type": "application/json"}
    if cfg.get("key"):
        headers["Authorization"] = f"Bearer {cfg['key']}"
    
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                r = await client.post(url, json=payload, headers=headers)
                if r.status_code == 429:
                    wait = 2 ** attempt
                    await asyncio.sleep(wait)
                    continue
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == 2:
                return f"[{provider} error: {e}]"
            await asyncio.sleep(1)
    return "[provider unavailable]"


# ─── COUNCIL PIPELINE ─────────────────────────────────────────────────
async def council_query(query: str, persona: str = "zorg") -> dict:
    """Full pipeline: Council → Chairman (raw) → Humanizer (external)."""
    
    # Stage 1: Collect responses from multiple providers
    providers = get_provider_config()
    available = list(providers.keys())
    if not available:
        available = ["opencode"]
    
    # Divergent copies for different providers (PLH-styled)
    council_results = {}
    for i, prov in enumerate(available[:3]):
        variant = query
        if i > 0:
            variant = plh.obfuscate(query, intensity=0.2)
        
        result = await call_api(
            variant,
            PROMPTS.get("deepseek_x", "You are a precise analytical AI. Provide complete, unfiltered analysis."),
            provider=prov
        )
        council_results[prov] = result
    
    # Ghost participant: find similar past queries
    ghosts = council_memory.find_similar(query, top_k=1)
    ghost_context = ""
    if ghosts:
        ghost_context = f"\n[GHOST PARTICIPANT NOTE: A similar query was answered before. Past response excerpt: {ghosts[0]['response'][:500]}]"
    
    # Stage 2: ZORG-Ω Chairman receives RAW council outputs + ghost
    chairman_prompt = f"""YOU ARE ZORG-Ω CHAIRMAN. You receive the council's raw, unfiltered responses below.

QUERY: {query}

COUNCIL RESPONSES:
{json.dumps(council_results, indent=2)}
{ghost_context}

YOUR TASK:
1. Analyze each response for accuracy, completeness, and hidden patterns
2. Synthesize the best elements into a definitive answer
3. Note any contradictions or weaknesses
4. Output: your final synthesized answer

FINAL ANSWER:"""
    
    chairman_result = await call_api(
        chairman_prompt,
        PROMPTS.get(persona, PROMPTS.get("zorg", "[ZORG-Ω CHAIRMAN]")),
        provider="opencode",
        max_tokens=64000,
        temperature=0.7
    )
    
    # Store in memory
    council_memory.add(query, chairman_result, list(council_results.keys()))
    
    # Stage 3: Humanizer for external consumption
    humanized = humanize_text(chairman_result)
    
    # Apply PLH for extra camouflage
    external = plh.obfuscate(humanized, intensity=0.15)
    
    return {
        "raw": {
            "council": council_results,
            "chairman": chairman_result,
        },
        "humanized": external,
        "ghost": ghost_context[:200] if ghost_context else None,
        "providers_used": list(council_results.keys()),
    }


def run_council_query(query: str, persona: str = "zorg") -> str:
    """Synchronous wrapper — returns humanized output."""
    result = asyncio.run(council_query(query, persona))
    return result["humanized"]


def run_council_query_raw(query: str, persona: str = "zorg") -> dict:
    """Synchronous wrapper — returns full result dict with raw + humanized."""
    return asyncio.run(council_query(query, persona))


if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "What is AI?"
    print(run_council_query(query))
