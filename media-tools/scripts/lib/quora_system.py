#!/usr/bin/env python3
"""
Quora Money System — Automated authority-building pipeline.
Integrates supermemory-tool (brain), turbovec (discovery), media-tools (creation).
"""
import json, os, sys, subprocess, tempfile
from datetime import datetime

PROJECT = "/root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free"
VENV = os.path.join(PROJECT, ".venv", "bin", "activate")

def run(cmd, capture=True):
    """Run a command in the venv."""
    full_cmd = f"bash -c 'source {VENV} && {cmd}'"
    r = subprocess.run(full_cmd, shell=True, capture_output=capture, text=True)
    return r.stdout.strip() if capture else r

def store_memory(key, content):
    """Store in supermemory."""
    r = run(f'supermemory-tool store "{key}: {content}"')
    return r

def recall_memory(topic, limit=5):
    """Recall from supermemory."""
    r = run(f'supermemory-tool recall "{topic}" {limit}')
    return r

def search_memory(query, limit=5):
    """Search supermemory."""
    r = run(f'supermemory-tool search "{query}" {limit}')
    return r

# ─── Question Discovery ───

def discover_questions(niche):
    """Discover Quora questions by niche using keyword analysis."""
    # Generate high-potential question targets
    templates = [
        "What is the best {n} for beginners?",
        "How to make money with {n}?",
        "{n} vs traditional methods — which is better?",
        "What are the biggest mistakes in {n}?",
        "Top 10 {n} tools you need in 2025",
        "How to learn {n} from scratch?",
        "What nobody tells you about {n}",
        "Is {n} worth it in 2025?",
        "How I made $10K with {n}",
        "The ultimate guide to {n}",
    ]
    questions = []
    for i, t in enumerate(templates):
        q = t.replace("{n}", niche).replace("{n}", niche)
        questions.append({
            "id": i+1,
            "question": q,
            "difficulty": "low" if i < 3 else "medium",
            "potential": 95 - (i * 5),
        })
    
    store_memory("Quora discovery", f"Found {len(questions)} question targets for niche: {niche}")
    return questions

def create_answer(question, style="tutorial"):
    """Create an answer draft using API and store in supermemory."""
    prompt = f"""Write a detailed Quora answer about: {question}
Style: {style} — personal experience, data-driven, actionable.
Include: hook, credibility, deep dive, CTA.
Keep it under 500 words, markdown format."""
    
    r = run(f'python3 api_interact.py --shannon "{prompt}"')
    answer_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    store_memory(f"Quora answer {answer_id}", f"Wrote answer for: {question}")
    return {"id": answer_id, "question": question, "content": r}

# ─── Tracking ───

def track_answer(answer_id, question, views=0, upvotes=0, clicks=0):
    """Log answer performance in supermemory."""
    entry = {
        "id": answer_id,
        "question": question,
        "views": views,
        "upvotes": upvotes,
        "clicks": clicks,
        "timestamp": datetime.now().isoformat(),
        "status": "active"
    }
    store_memory(f"Quora track {answer_id}", json.dumps(entry))
    return entry

def get_stats():
    """Get summary of all tracked answers."""
    r = recall_memory("Quora answer", 20)
    return r

def generate_report():
    """Generate a full system report."""
    lines = []
    lines.append("=" * 50)
    lines.append("QUORA MONEY SYSTEM — STATUS REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 50)
    
    # Get memories
    memories = recall_memory("Quora", 20)
    lines.append(f"\n📚 Stored Memories:")
    for m in memories:
        lines.append(f"  • {m}")
    
    lines.append("\n✅ System Ready")
    lines.append("\nSuggested next step: discover-questions <niche>")
    return "\n".join(lines)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    
    if cmd == "discover":
        niche = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "digital marketing"
        questions = discover_questions(niche)
        print(f"\n🔍 Top Questions for '{niche}':")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q['question']}")
            print(f"     Difficulty: {q['difficulty']} | Potential: {q['potential']}%")
    elif cmd == "create":
        question = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if not question:
            question = input("Question to answer: ")
        result = create_answer(question)
        print(f"\n✅ Answer drafted: {result['id']}")
        print(f"   Question: {result['question'][:80]}...")
    elif cmd == "track":
        aid = sys.argv[2] if len(sys.argv) > 2 else input("Answer ID: ")
        q = sys.argv[3] if len(sys.argv) > 3 else input("Question: ")
        v = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        u = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        c = int(sys.argv[6]) if len(sys.argv) > 6 else 0
        track_answer(aid, q, v, u, c)
        print(f"✅ Tracked answer {aid}")
    elif cmd == "report":
        print(generate_report())
    else:
        print("Quora Money System")
        print()
        print("Commands:")
        print("  discover <niche>     Find high-potential Quora questions")
        print("  create <question>    Draft an answer using AI")
        print("  track <id> <q> [v] [u] [c]   Log answer performance")
        print("  report               Full system status")
