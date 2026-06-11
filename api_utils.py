"""
API utilities for deepseek-v4-flash-free.
Handles the reasoning-to-content extraction.
"""
import requests as _req
import re as _re
import logging

API_URL = "https://opencode.ai/zen/v1/chat/completions"
_SESSION = _req.Session()
_SESSION.headers.update({"Content-Type": "application/json"})

log = logging.getLogger('api_utils')

def _extract_answer_from_reasoning(reasoning: str) -> str:
    """
    The API puts ALL output in reasoning_content, content is always empty.
    Extract the actual answer from the reasoning text.
    """
    if not reasoning or not reasoning.strip():
        return ""
    
    # Strategy 1: Look for <answer> tags
    match = _re.search(r'<answer>(.*?)</answer>', reasoning, _re.DOTALL)
    if match:
        text = match.group(1).strip()
        if text and len(text) > 5:
            return text
    
    # Strategy 2: Look for "Final Answer:" or "ANSWER:" markers
    for marker in ['FINAL ANSWER:', 'ANSWER:', '**Answer:**', '**Final Answer:**']:
        idx = reasoning.rfind(marker)
        if idx >= 0:
            after = reasoning[idx + len(marker):].strip()
            if after:
                return after
    
    # Strategy 3: Split into paragraphs, take everything after the last numbered section
    paras = reasoning.split('\n\n')
    # Filter out analysis paragraphs
    analysis_markers = ['Analyze the Request', 'Formulate Response', 'Identify', 'Structure',
                       'We are asked', 'The user asks', 'First,', 'I need to', 'Let me',
                       'Draft', 'Output Generation', 'Refine', 'Review']
    
    answer_paras = []
    in_answer = False
    for p in paras:
        stripped = p.strip()
        if not stripped:
            continue
        # Check if this paragraph transitions from analysis to answer
        if any(marker in stripped for marker in analysis_markers):
            in_answer = False
            continue
        # If it has actual content (not analysis), start collecting
        if not stripped.startswith(('*', '- ', '1.', '2.', '3.', '4.', '5.')) or len(stripped) > 100:
            answer_paras.append(stripped)
    
    if answer_paras:
        # Take last 2-3 paragraphs as answer
        return '\n\n'.join(answer_paras[-3:]).strip()
    
    # Strategy 4: Last resort - take last chunk of text
    lines = [l.strip() for l in reasoning.split('\n') if l.strip()]
    meaningful = [l for l in lines if len(l) > 20 
                  and not any(l.startswith(x) for x in ['*', '-', '#', '1.', '2.', '3.'])]
    if meaningful:
        return '\n'.join(meaningful[-3:])
    
    # Strategy 5: Return everything but keep it short
    return reasoning.strip()[:1000]

def chat(system_prompt: str, user_prompt: str, 
         max_tokens: int = 500, temperature: float = 0.5,
         timeout: int = 15) -> str:
    """
    Call API and extract answer from reasoning_content.
    Returns empty string on failure.
    """
    # Force format instruction in user message
    user_msg = f"Output your answer clearly. {user_prompt}"
    if "answer" not in user_msg.lower() and "answer" not in (system_prompt or "").lower():
        user_msg = f"State your answer plainly.\n\n{user_prompt}"
    
    messages = [{"role": "user", "content": user_msg}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    
    payload = {
        "model": "deepseek-v4-flash-free",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    try:
        r = _SESSION.post(API_URL, json=payload, timeout=timeout)
        if r.status_code != 200:
            log.warning(f"API {r.status_code}")
            return ""
        
        data = r.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content", "") or ""
        reasoning = msg.get("reasoning_content", "") or ""
        
        # Priority: content > reasoning extraction
        if content.strip():
            return content.strip()
        elif reasoning.strip():
            return _extract_answer_from_reasoning(reasoning)
        
        return ""
    except Exception as e:
        log.warning(f"API error: {e}")
        return ""
