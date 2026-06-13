#!/bin/bash
# Ultra-persistent bot launcher - survives session death
cd /root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free

# Double-fork to fully detach from parent process
launch_bot() {
    local name=$1
    local script=$2
    local log=$3
    local pidfile=$4
    
    # First fork
    (
        # Second fork - fully detached
        (
            # Detach from process group
            exec 0</dev/null
            exec 1>$log
            exec 2>&1
            echo "[$(date)] Starting $name..."
            cd /root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free
            exec .venv/bin/python3 -u "$script"
        ) &
        echo $! > "$pidfile"
    ) &
}

# Launch both bots
launch_bot "Arabic" "arabic_bot.py" "bot_arabic_out.log" "bot_arabic.pid"
launch_bot "Concurrent" "bot_concurrent.py" "bot_concurrent_out.log" "bot_concurrent.pid"

echo "Bots launched. PIDs: $(cat bot_arabic.pid 2>/dev/null) $(cat bot_concurrent.pid 2>/dev/null)"
