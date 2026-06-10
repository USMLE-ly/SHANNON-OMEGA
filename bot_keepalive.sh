#!/bin/bash
# 🤖 SHANNON-Ω Bot Keepalive — Probot-inspired health monitoring
# Runs alongside the bot, restarts it if it dies.

BOT_DIR="/root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free"
PID_FILE="$BOT_DIR/bot.pid"
LOG_FILE="$BOT_DIR/bot_keepalive.log"
INTERVAL=60

cd "$BOT_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Keepalive started"

while true; do
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ! kill -0 "$PID" 2>/dev/null; then
            log "Bot died (PID $PID). Restarting..."
            source .venv/bin/activate
            nohup .venv/bin/python run_bot.py > bot_plugin.log 2>&1 &
            echo $! > "$PID_FILE"
            log "Restarted with PID $(cat $PID_FILE)"
        fi
    else
        log "No PID file. Starting..."
        source .venv/bin/activate
        nohup .venv/bin/python run_bot.py > bot_plugin.log 2>&1 &
        echo $! > "$PID_FILE"
        log "Started with PID $(cat $PID_FILE)"
    fi
    sleep $INTERVAL
done
