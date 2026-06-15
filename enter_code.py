#!/usr/bin/env python3
"""Enter Instagram verification code into the running signup session."""
import sys, json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
state_path = PROJECT_ROOT / '.ig_signup_state.json'

if not state_path.exists():
    print('❌ No signup session found. Run create_account.py first.')
    sys.exit(1)

code = sys.argv[1] if len(sys.argv) > 1 else input('Verification code: ').strip()
if not code or not code.isdigit():
    print('❌ Please provide a numeric verification code')
    sys.exit(1)

# Update state file
with open(state_path) as f:
    state = json.load(f)

state['step'] = 'code_received'
state['code'] = code

with open(state_path, 'w') as f:
    json.dump(state, f, indent=2)

print(f'✅ Code {code} registered! The signup script will pick it up.')
