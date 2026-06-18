#!/bin/bash
# Donut Browser + Camoufox — Quora posting launcher
# Run this AFTER the container is restarted with:
#   --cap-add=SYS_PTRACE --cap-add=SYS_ADMIN --security-opt seccomp=unconfined

set -e

PROJECT="/root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free"
CAMOUFOX_DIR="/root/.local/share/DonutBrowser/binaries/camoufox/v150.0.2-beta.25"
PROFILE_DIR="/root/.camoufox/quora_profile"

cd "$PROJECT"
source .venv/bin/activate

# Start virtual display
echo "[*] Starting Xvfb..."
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &>/dev/null &
XVFB_PID=$!
sleep 2

# Disable content process pool for stability
export MOZ_DISABLE_CONTENT_PROCESS_POOL=1
export LD_LIBRARY_PATH="$CAMOUFOX_DIR:$LD_LIBRARY_PATH"

echo "[*] Launching Camoufox..."
# Launch with remote debugging
"$CAMOUFOX_DIR/camoufox" \
    --profile "$PROFILE_DIR" \
    --new-instance \
    --remote-debugging-port 9222 \
    "about:blank" &
CAMOUFOX_PID=$!
sleep 5

echo "[*] Camoufox PID: $CAMOUFOX_PID"
echo "[*] Remote debugging: http://127.0.0.1:9222"
echo "[*] Profile: $PROFILE_DIR"
echo ""
echo "[!] Extensions installed:"
echo "    - Tampermonkey (firefox@tampermonkey.net)"
echo "    - Cookie-Editor ({c3c10168-4186-445c-9c5b-63f12b8e2c87})"
echo ""
echo "To post to Quora:"
echo "  1. Open Tampermonkey dashboard and install scarab_all_in_one_v4.user.js"
echo "  2. Navigate to a Quora question"
echo "  3. Use the SCARAB panel to extract QID and post"
echo ""
echo "Or use the automated poster:"
echo "  cd $PROJECT && python3 scarab-controller/scarab_controller.py post-quora --topic \"your topic\""
echo ""
echo "Press Ctrl+C to stop."

# Wait for Camoufox
wait $CAMOUFOX_PID 2>/dev/null

# Cleanup
kill $XVFB_PID 2>/dev/null
