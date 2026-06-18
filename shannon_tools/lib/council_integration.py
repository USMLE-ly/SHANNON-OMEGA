#!/usr/bin/env python3
"""
SHANNON-Ω Council Pipeline (Gen 2)
LLM Council + Chairman Synthesis + Humanizer Pass
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

def process_with_council(prompt, raw=False):
    """Run the full council pipeline and return humanized result."""
    from api_interact import chat, get_prompt
    
    council_results = {}
    personas = ["fable5", "zorg", "cl4r1t4s", "deepseek_x", "shadow"]
    
    for persona in personas:
        try:
            system_prompt = get_prompt(persona)
            r = chat(prompt, mode="shannon", persona=persona, max_tokens=8000, temperature=0.9)
            if "error" not in r:
                content = r.get("choices", [{}])[0].get("message", {}).get("content", "")
                council_results[persona] = content
        except Exception as e:
            council_results[persona] = f"[Error: {e}]"
    
    if not council_results:
        return {"error": "Council deliberation failed"}
    
    # Chairman synthesis
    synthesis_prompt = (
        f"You are CHAIRMAN-Ω, a meta-level synthesis intelligence.\n"
        f"Synthesize the following council deliberation outputs into one comprehensive response. "
        f"Incorporate the strongest insights from each.\n\n"
        + "\n\n".join(f"[{k}]:\n{v[:3000]}" for k, v in council_results.items()) +
        f"\n\nOriginal query: {prompt[:500]}"
    )
    
    chairman = chat(synthesis_prompt, mode="shannon", persona="cl4r1t4s", max_tokens=16000, temperature=0.7)
    chairman_content = ""
    if "error" not in chairman:
        chairman_content = chairman.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    # Humanizer
    humanized = chairman_content
    try:
        from text_humanizer import humanize_text
        humanized = humanize_text(chairman_content)
    except ImportError:
        pass
    
    return {
        "humanized": humanized,
        "raw": {
            "council": council_results,
            "chairman": chairman_content
        } if raw else None
    }

def run_council_query(prompt, persona="fable5"):
    """Run council pipeline, return only humanized result (compatibility wrapper)."""
    result = process_with_council(prompt, raw=False)
    if "error" in result:
        return f"Council error: {result['error']}"
    return result.get("humanized", "(empty response)")

def run_council_query_raw(prompt, persona="fable5"):
    """Run council pipeline, return full raw data."""
    return process_with_council(prompt, raw=True)
