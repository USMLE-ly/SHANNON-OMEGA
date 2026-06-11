#!/bin/bash
# Watchdog - restarts bots if they crash
cd /root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free
source .venv/bin/activate

while true; do
    # Check Arabic bot
    if ! tmux has-session -t arabic_bot 2>/dev/null; then
        echo "[$(date)] Arabic bot crashed, restarting..."
        tmux new-session -d -s arabic_bot
        tmux send-keys -t arabic_bot "cd /root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free && source .venv/bin/activate && python3 -u arabic_bot.py" Enter
    fi
    
    # Check Concurrent bot
    if ! tmux has-session -t concurrent_bot 2>/dev/null; then
        echo "[$(date)] Concurrent bot crashed, restarting..."
        tmux new-session -d -s concurrent_bot
        tmux send-keys -t concurrent_bot "cd /root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free && source .venv/bin/activate && python3 -u bot_concurrent.py" Enter
    fi
    
    sleep 30
done
