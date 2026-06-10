#!/usr/bin/env python3
"""
🎭 Text Humanizer — Makes AI text sound human + formats it professionally
Inspired by blader/humanizer, agency-agents, ai-marketing-skills.

Features:
  - Removes AI-isms (inflated language, filler, clichés)
  - Adds natural voice variation and personality
  - Professional formatting: bullets, numbers, spacing
  - Color-coded emoji highlights (pink, blue, yellow, orange)
  - Structured template layout for readability
"""

import re
import random

# ─── Emoji Color Palette ────────────────────────────────────────
COLORS = {
    "pink": "❤️", "blue": "💙", "yellow": "💛",
    "orange": "🧡", "green": "💚", "purple": "💜",
}

BULLETS = ["🎯", "💎", "⭐", "🔥", "✅", "📌"]

SALES_FIELD_COLORS = {
    "guarantee": "pink", "risk reversal": "pink",
    "retention": "blue", "lifetime value": "blue",
    "grand slam offer": "yellow", "starving crowd": "yellow",
    "value equation": "orange", "pricing strategy": "orange",
    "lead generation": "green", "cold outreach": "green",
    "sales script": "purple",
}

# ─── AI Pattern Removal ─────────────────────────────────────────
AI_REPLACEMENTS = [
    # Inflated / grandiose
    (r'\b(serves|stands)\s+as\s+(a\s+)?(\w+\s+)?(cornerstone|testament|beacon)\b', 'is a cornerstone'),
    (r'\bplays?\s+(a\s+)?(\w+\s+)?(vital|critical|crucial|key|pivotal|significant)?\s*role\b', 'matters'),
    (r'\b(underscores|highlights)\s+(the\s+)?(significance|importance)\b', 'shows'),
    (r'\breflects?\s+broader\s+(trends|patterns)\b', 'fits into'),
    (r'\b(mark|represent)s?\s+(a\s+)?(significant|major|key)\s+(shift|turning.point)\b', 'changes'),
    (r'\bevolving\s+landscape\b', 'world'),
    (r'\bcrucial\b', 'important'),
    (r'\bparamount\b', 'essential'),
    (r'\bundoubtedly\b', ''),
    
    # Filler
    (r'\bin\s+order\s+to\b', 'to'),
    (r'\bit\s+(is|was)\s+(important|worth|critical|essential)\s+to\s+(note|mention|remember|consider)\s+that\b', ''),
    (r'\bit\s+should\s+be\s+noted\s+that\b', ''),
    (r'\bneedless\s+to\s+say\b', ''),
    (r'\bwhen\s+it\s+comes\s+to\b', 'for'),
    (r'\bin\s+terms\s+of\b', 'in'),
    (r'\bat\s+the\s+end\s+of\s+the\s+day\b', ''),
    (r'\ball\s+things\s+considered\b', ''),
    (r'\bin\s+summary\b', ''),
    (r'\bin\s+conclusion\b', ''),
    (r'\boverall\b', ''),
    (r'\bultimately\b', ''),
    
    # AI vocabulary (overused by LLMs)
    (r'\bdelves?\s+(into|in)\b', 'explores'),
    (r'\bnavigate\b', 'handle'),
    (r'\bintricate\b', 'detailed'),
    (r'\btapestry\b', 'mix'),
    (r'\bfoster(s|ed|ing)?\b', 'build'),
    (r'\bempower(s|ed|ing)?\b', 'help'),
    (r'\brealm\b', 'area'),
    (r'\btransformative\b', 'powerful'),
    (r'\bparadigm\b', 'approach'),
    (r'\bjourney\b', 'process'),
    
    # Cliché business speak
    (r'\bsynerg(y|ize|istic|ies)\b', 'teamwork'),
    (r'\bleverage\b', 'use'),
    (r'\bdrill\s+down\b', 'dig in'),
    (r'\bpivot\b', 'shift'),
    (r'\bcircle\s+back\b', 'revisit'),
    (r'\btouch\s+base\b', 'check in'),
    (r'\bthought\s+lead(er|ership)\b', 'expert'),
    (r'\bbest.?.?.?class\b', 'top-tier'),
    (r'\bcutting.?\w*edge\b', 'modern'),
    (r'\brevolutionary\b', 'new'),
    (r'\bgame.?\w*changer?\b', 'breakthrough'),
    
    # Weak hedging
    (r'\bit\s+could\s+be\s+argued\s+that\b', ''),
    (r'\bsome\s+might\s+say\b', ''),
    (r'\bin\s+many\s+ways\b', ''),
    (r'\bfor\s+the\s+most\s+part\b', ''),
    (r'\bit\s+is\s+worth\s+noting\s+that\b', ''),
]


def _fix_caps(text: str) -> str:
    """Capitalize sentences after replacements."""
    parts = re.split(r'(?<=[.!?])\s+', text)
    parts = [p[0].upper() + p[1:] if p and p[0].islower() else p for p in parts if p]
    result = ' '.join(parts)
    if result and result[0].islower():
        result = result[0].upper() + result[1:]
    return result


def remove_ai_patterns(text: str) -> str:
    """Strip AI-generated writing patterns from text."""
    if not text:
        return text
    
    result = text
    for pattern, replacement in AI_REPLACEMENTS:
        try:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        except re.error:
            pass
    
    result = _fix_caps(result)
    result = re.sub(r' {2,}', ' ', result)
    result = re.sub(r'\s+\.', '.', result)
    result = re.sub(r'\s+,', ',', result)
    return result.strip()


def add_variety(text: str) -> str:
    """Vary sentence rhythm."""
    if not text or len(text) < 60:
        return text
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) < 2:
        return text
    
    result = []
    for i, sent in enumerate(sentences):
        sent = sent.strip()
        if not sent:
            continue
        
        if i > 0 and i % 4 == 0 and len(sent) > 120:
            mid = len(sent) // 2
            bp = sent.rfind('. ', 0, mid)
            if bp > 20:
                result.append(sent[:bp+1])
                result.append(sent[bp+1:].strip().capitalize())
                continue
        
        if i > 1 and random.random() < 0.12:
            if not sent.startswith(('And ', 'But ', 'So ', 'Or ')):
                c = random.choice(['And ', 'But ', 'So '])
                result.append(c + sent[0].lower() + sent[1:])
                continue
        
        result.append(sent)
    
    return ' '.join(result)


# ─── Professional Formatting ────────────────────────────────────

def format_text(text: str) -> str:
    """Apply professional formatting to text."""
    if not text:
        return text
    
    lines = text.split('\n')
    out = []
    
    for line in lines:
        s = line.strip()
        if not s:
            out.append('')
            continue
        
        # Template fields
        if re.match(r'^[❤️💙💛🧡💚💜]?\s?\*{1,2}\w.*?\*{1,2}:', s):
            out.append(s)
            continue
        
        # Bullet points
        if re.match(r'^[\-\*•]\s', s):
            content = re.sub(r'^[\-\*•]\s+', '', s)
            bullet = BULLETS[hash(content) % len(BULLETS)]
            out.append(f"  {bullet} *{content}*")
            continue
        
        # Numbered items
        m = re.match(r'^(\d+)[\.\)]\s+(.*)', s)
        if m:
            out.append(f"  **{m.group(1)}.** {m.group(2)}")
            continue
        
        out.append(s)
    
    return '\n'.join(out)


def colorize_template(text: str) -> str:
    """Add color emoji to template fields."""
    if not text:
        return text
    
    lines = text.split('\n')
    out = []
    
    for line in lines:
        s = line.strip()
        m = re.match(r'^[❤️💙💛🧡💚💜]?\s?\*{1,2}([\w\s]+?)\*{1,2}:\s*(.*)', s)
        if m:
            field, value = m.group(1).strip(), m.group(2).strip()
            fl = field.lower()
            color = 'pink'
            for key, c in SALES_FIELD_COLORS.items():
                if key in fl:
                    color = c
                    break
            out.append(f"\n{COLORS[color]} **{field}:**")
            out.append(f"   {value if value != '[Fill from context]' else ''}")
            continue
        out.append(s)
    
    return '\n'.join(out)


# ─── Complete Humanizer ─────────────────────────────────────────

class TextHumanizer:
    """Full pipeline: humanize AI text → format → highlight."""
    
    def process(self, text: str, is_structured: bool = False) -> str:
        if not text:
            return text if text is not None else ''
        
        text = remove_ai_patterns(text)
        text = add_variety(text)
        text = format_text(text)
        
        if is_structured:
            text = colorize_template(text)
        
        return text.strip()
    
    def format_template(self, text: str) -> str:
        return self.process(text, is_structured=True)
    
    def format_casual(self, text: str) -> str:
        return self.process(text, is_structured=False)


if __name__ == "__main__":
    h = TextHumanizer()
    
    test = "It serves as a vital cornerstone for businesses looking to establish thought leadership. It is important to note that creating high-quality content plays a pivotal role in attracting customers. In order to leverage cutting-edge tools and foster a culture of innovation, companies must navigate the complex realm of modern marketing."
    
    print("=== BEFORE ===")
    print(test)
    print("\n=== AFTER ===")
    print(h.process(test))
    
    print("\n\n=== STRUCTURED TEMPLATE ===")
    tmpl = "🎯 **Guarantee:** A strong guarantee removes all risk.\n🔒 **Retention:** Keep customers by delivering value.\n🏆 **Grand Slam Offer:** Stack value, reverse all risk."
    print(h.format_template(tmpl))
