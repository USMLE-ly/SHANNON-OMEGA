#!/usr/bin/env bash
# SHANNON-Ω Million Dollar Bot Launcher
set -e

cd "$(dirname "$0")/.."
source .venv/bin/activate

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BOLD}${GREEN}"
echo '  ╔═══════════════════════════════════════════╗'
echo '  ║     SHANNON-Ω Million Dollar Bot          ║'
echo '  ║     Instagram Growth Engine               ║'
echo '  ╚═══════════════════════════════════════════╝'
echo -e "${NC}"

case "${1:-help}" in
    login)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}Usage: ./start.sh login <username> <password>${NC}"
            exit 1
        fi
        echo -e "${GREEN}Logging in as @$2...${NC}"
        python3 million_bot/scripts/bot_engine.py --login "$2" "$3" --cycles 5
        ;;
    create)
        echo -e "${YELLOW}Creating new Instagram account...${NC}"
        echo -e "${YELLOW}Note: Requires 2Captcha key for reCAPTCHA bypass${NC}"
        echo -e "${YELLOW}Set: export TWOCAPTCHA_KEY='your_key'${NC}"
        python3 media-tools/scripts/lib/ig_creator.py full "Vaulex Watches" "vaulex_watches"
        ;;
    grow)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}Usage: ./start.sh grow <username> <password>${NC}"
            exit 1
        fi
        CYCLES="${4:-10}"
        echo -e "${GREEN}Running ${CYCLES} growth cycles for @$2...${NC}"
        python3 million_bot/scripts/bot_engine.py --login "$2" "$3" --cycles "$CYCLES"
        ;;
    quick-like)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}Usage: ./start.sh quick-like <username> <password>${NC}"
            exit 1
        fi
        COUNT="${4:-10}"
        echo -e "${GREEN}Liking ${COUNT} posts as @$2...${NC}"
        python3 million_bot/scripts/bot_engine.py --login "$2" "$3" --like "$COUNT"
        ;;
    config)
        nano million_bot/config/bot_config.json
        ;;
    status)
        echo -e "${GREEN}Bot Configuration:${NC}"
        cat million_bot/config/bot_config.json | python3 -m json.tool
        echo
        echo -e "${GREEN}Logs:${NC}"
        ls -la million_bot/logs/ 2>/dev/null || echo "  No logs yet"
        ;;
    api)
        echo -e "${BOLD}SHANNON-Ω API Chat${NC}"
        python3 api_interact.py --shannon "${@:2}"
        ;;
    help|*)
        echo "Commands:"
        echo "  ./start.sh login <user> <pass>       Login and run growth cycles"
        echo "  ./start.sh create                    Create new Instagram account"
        echo "  ./start.sh grow <user> <pass> [N]    Run N growth cycles (default: 10)"
        echo "  ./start.sh quick-like <user> <pass>  Quick like posts"
        echo "  ./start.sh config                    Edit bot config"
        echo "  ./start.sh status                    Show status and config"
        echo "  ./start.sh api <prompt>              Chat with SHANNON-Ω"
        echo ""
        echo "Setup required:"
        echo "  1. export TWOCAPTCHA_KEY='your_key'   # For auto signup"
        echo "  2. ./start.sh create                   # Create account (or manual)"
        echo "  3. ./start.sh login user pass          # Start growing"
        ;;
esac
