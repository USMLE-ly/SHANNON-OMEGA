#!/usr/bin/env python3
"""
omega_instatakker.py — Phase 2: Mass follow/unfollow via instatakker
High-volume but still respects rate limits to avoid blocks.
"""
import os, sys, json, time, random, subprocess
from pathlib import Path

CONFIG = {
    "username": os.environ.get("IG_USERNAME", "chip.munk.19"),
    "password": os.environ.get("IG_PASSWORD", "Hesoyam$18043"),
    "target": "vaulex_watches",
    "follow_per_hour": 20,
    "like_per_hour": 30,
    "min_delay_seconds": 90,
    "max_delay_seconds": 180,
}

INSTATAKKER_DIR = Path(__file__).parent / "instatakker"

def run_instatakker(action, target, count=10):
    """Run an instatakker action if available."""
    script = INSTATAKKER_DIR / "instatakker.py"
    if not script.exists():
        print(f"instatakker not found at {script}")
        return False
    
    cmd = [
        sys.executable, str(script),
        "--username", CONFIG["username"],
        "--password", CONFIG["password"],
        "--action", action,
        "--target", target,
        "--count", str(count),
    ]
    
    print(f"  ∟ Running instatakker {action} on @{target} (x{count})")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"  ✓ Success")
            return True
        else:
            print(f"  ✗ Failed: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("╔══════════════════════════════════════════╗")
    print("║     OMEGA INSTATAKKER — Phase 2          ║")
    print("║  Mass follow/unfollow automation          ║")
    print("╚══════════════════════════════════════════╝")
    print(f"  Account: {CONFIG['username']}")
    print(f"  Target:  @{CONFIG['target']}")
    print()
    
    actions_done = 0
    max_actions = CONFIG["follow_per_hour"]
    
    while actions_done < max_actions:
        batch = min(5, max_actions - actions_done)
        
        # Follow target's followers
        run_instatakker("follow_followers", CONFIG["target"], batch)
        actions_done += batch
        
        # Delay
        delay = random.uniform(CONFIG["min_delay_seconds"], CONFIG["max_delay_seconds"])
        print(f"  Waiting {delay:.0f}s...")
        time.sleep(delay)
        
        # Like target's posts
        run_instatakker("like", CONFIG["target"], batch * 2)
        
        delay = random.uniform(CONFIG["min_delay_seconds"], CONFIG["max_delay_seconds"])
        print(f"  Waiting {delay:.0f}s...")
        time.sleep(delay)
    
    print(f"\n✓ Phase 2 complete. {actions_done} actions executed.")

if __name__ == "__main__":
    main()
