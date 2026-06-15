#!/usr/bin/env python3
"""Enter Instagram verification code into the signup session."""
import sys, json
from pathlib import Path

state_path = Path(__file__).resolve().parent / '.ig_state.json'

if not state_path.exists():
    print('❌ No signup session found. Run signup_v2.py first.')
    sys.exit(1)

code = sys.argv[1] if len(sys.argv) > 1 else input('Verification code: ').strip()
if not code or not code.isdigit():
    print('❌ Must be a numeric code')
    sys.exit(1)

with open(state_path) as f:
    state = json.load(f)

state['step'] = 'code_received'
state['code'] = code

with open(state_path, 'w') as f:
    json.dump(state, f, indent=2)

print(f'✅ Code {code} registered! The running script will enter it.')
