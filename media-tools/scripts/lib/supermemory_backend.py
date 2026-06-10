#!/usr/bin/env python3
"""Supermemory backend — local memory store + API client"""
import json, os, sys
from datetime import datetime, timezone

MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".supermemory")
os.makedirs(MEMORY_DIR, exist_ok=True)
MEM_FILE = os.path.join(MEMORY_DIR, "memories.jsonl")

def api_available():
    api_key = os.environ.get("SUPERMEMORY_API_KEY", "")
    if api_key:
        try:
            from supermemory import Supermemory
            return Supermemory(api_key=api_key)
        except Exception:
            return None
    return None

def store_memory(content):
    entry = {"role": "user", "content": content, "timestamp": datetime.now(timezone.utc).isoformat()}
    with open(MEM_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def search_memories(query=None, limit=10):
    if not os.path.exists(MEM_FILE):
        return []
    results = []
    with open(MEM_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if not query or query.lower() in entry.get("content", "").lower():
                results.append(entry)
    return results[-limit:]

def recall(topic=None, limit=10):
    return search_memories(topic, limit)

def status():
    client = api_available()
    local_count = 0
    if os.path.exists(MEM_FILE):
        with open(MEM_FILE) as f:
            local_count = sum(1 for _ in f)
    if client:
        return {"api": "connected", "local_entries": local_count}
    return {"api": "no_key", "local_entries": local_count}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "store":
        content = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read().strip()
        entry = store_memory(content)
        print(json.dumps(entry))
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else None
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        results = search_memories(query, limit)
        print(f"Found {len(results)} memories:")
        for r in results:
            ts = r.get("timestamp", "?")[:19]
            c = r["content"][:120]
            print(f"  [{ts}] {c}")
    elif cmd == "recall":
        topic = sys.argv[2] if len(sys.argv) > 2 else None
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        results = recall(topic, limit)
        if topic:
            print(f"📝 Recalling memories about: {topic}")
        else:
            print(f"📝 All memories ({len(results)}):")
        for r in results:
            ts = r.get("timestamp", "?")[:19]
            c = r["content"][:120]
            print(f"  [{ts}] {c}")
    elif cmd == "status":
        s = status()
        if s["api"] == "connected":
            print(f"✅ Supermemory API: connected")
        else:
            print(f"ℹ️  Supermemory API: not configured (use local mode)")
        print(f"📁 Local memory entries: {s['local_entries']}")
    else:
        print("Supermemory — Memory & Context Engine")
        print()
        print("Commands:")
        print("  store <content>         Store a memory")
        print("  search <query> [limit]  Search memories")
        print("  recall [topic] [limit]  Recall memories")
        print("  status                  Check status")
