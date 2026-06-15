#!/usr/bin/env bash
# omega_orchestrator.sh — Full Instagram automation orchestration
set -euo pipefail

PROJECT="/root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free"
OMEGA="$PROJECT/omega"
LOG_DIR="$OMEGA/logs"
mkdir -p "$LOG_DIR"

source "$PROJECT/.venv/bin/activate"
export IG_USERNAME="${IG_USERNAME:-chip.munk.19}"
export IG_PASSWORD="${IG_PASSWORD:-Hesoyam$18043}"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     OMEGA ORCHESTRATOR                   ║${NC}"
echo -e "${GREEN}║  Instagram Automation Suite               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"

case "${1:-help}" in
    sloth)
        echo -e "${YELLOW}► Phase 1: Sloth (slow, safe)${NC}"
        LOGFILE="$LOG_DIR/sloth_$(date +%Y%m%d_%H%M%S).log"
        python3 "$OMEGA/omega_sloth.py" 2>&1 | tee "$LOGFILE"
        echo -e "${GREEN}✓ Log: $LOGFILE${NC}"
        ;;
    cycle)
        LOGFILE="$LOG_DIR/cycle_$(date +%Y%m%d_%H%M%S).log"
        echo -e "${YELLOW}► Full cycle: sloth → instatakker${NC}" | tee "$LOGFILE"
        python3 "$OMEGA/omega_sloth.py" 2>&1 | tee -a "$LOGFILE"
        python3 "$OMEGA/omega_instatakker.py" 2>&1 | tee -a "$LOGFILE"
        echo -e "${GREEN}✓ Cycle complete: $LOGFILE${NC}"
        ;;
    daemon)
        echo -e "${YELLOW}► Daemon mode (runs every 6h)${NC}"
        while true; do
            "$0" cycle
            echo -e "${YELLOW}Sleeping 6h... (Ctrl+C to stop)${NC}"
            sleep 21600
        done
        ;;
    status)
        echo -e "${YELLOW}► Status${NC}"
        echo "  Account: ${IG_USERNAME}"
        echo "  Target:  @vaulex_watches"
        echo "  Logs:    $(find "$LOG_DIR" -name '*.log' | wc -l) files"
        if [ -f "$OMEGA/omega_status.json" ]; then
            cat "$OMEGA/omega_status.json"
        else
            echo "  Status:  Never run"
        fi
        echo ""
        echo "  Repos:"
        for d in "$OMEGA"/instatakker "$OMEGA"/ai-captcha-bypass "$OMEGA"/uncaptcha2; do
            [ -d "$d" ] && echo "    ✓ $(basename $d)" || echo "    ✗ $(basename $d)"
        done
        ;;
    help|*)
        echo "Omega Orchestrator"
        echo ""
        echo "Commands:"
        echo "  sloth          Phase 1: slow safe automation"
        echo "  cycle          Full cycle (all phases)"
        echo "  daemon         Run continuously (6h intervals)"
        echo "  status         Show system status"
        echo ""
        echo "Set IG_USERNAME and IG_PASSWORD to override defaults"
        ;;
esac
