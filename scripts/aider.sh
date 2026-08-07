#!/bin/bash

################################################################################
# Aider Startup Script
# Manages Claude Code + Aider integration for collaborative coding
################################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.aider/logs"
AIDER_PORT=${AIDER_PORT:-9000}

mkdir -p "$LOG_DIR"

case "$1" in
    start)
        echo "🚀 Starting Aider..."
        
        # Check if aider is installed
        if ! command -v aider &> /dev/null; then
            echo "❌ Aider not installed. Install with: pip install aider-chat"
            exit 1
        fi
        
        # Start aider in the background with Claude Code
        nohup aider \
            --model claude-opus \
            --no-auto-commits \
            --auto-test \
            > "$LOG_DIR/aider.log" 2>&1 &
        
        AIDER_PID=$!
        echo "✅ Aider started (PID: $AIDER_PID)"
        echo "$AIDER_PID" > "$LOG_DIR/aider.pid"
        ;;
        
    stop)
        echo "🛑 Stopping Aider..."
        if [ -f "$LOG_DIR/aider.pid" ]; then
            PID=$(cat "$LOG_DIR/aider.pid")
            kill "$PID" 2>/dev/null && echo "✅ Aider stopped" || echo "⚠️  Already stopped"
            rm -f "$LOG_DIR/aider.pid"
        fi
        ;;
        
    status)
        if [ -f "$LOG_DIR/aider.pid" ]; then
            PID=$(cat "$LOG_DIR/aider.pid")
            if ps -p "$PID" > /dev/null; then
                echo "✅ Aider running (PID: $PID)"
                tail -5 "$LOG_DIR/aider.log"
            else
                echo "❌ Aider not running (stale PID: $PID)"
            fi
        else
            echo "⚠️  Aider not started"
        fi
        ;;
        
    logs)
        tail -f "$LOG_DIR/aider.log"
        ;;
        
    *)
        echo "Usage: $0 {start|stop|status|logs}"
        exit 1
        ;;
esac
