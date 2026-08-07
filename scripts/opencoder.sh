#!/bin/bash

################################################################################
# OpEncoder Script
# Runs code optimization and encoding tasks for Claude Code
################################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.opencoder/logs"
OPENCODER_HOME="${OPENCODER_HOME:-$HOME/.opencoder}"

mkdir -p "$LOG_DIR"

case "$1" in
    run)
        echo "⚙️  Running OpEncoder..."
        
        # Check if opencoder is available
        if ! command -v opencoder &> /dev/null && [ ! -f "$OPENCODER_HOME/bin/opencoder" ]; then
            echo "⚠️  OpEncoder not found at ~/.opencoder"
            echo "Checking for Python module..."
            if ! python3 -c "import opencoder" 2>/dev/null; then
                echo "❌ Install with: pip install opencoder"
                exit 1
            fi
        fi
        
        # Run encoding job
        nohup python3 -m opencoder \
            --mode optimize \
            --recursive \
            --log-level info \
            . > "$LOG_DIR/opencoder.log" 2>&1 &
        
        PID=$!
        echo "✅ OpEncoder job started (PID: $PID)"
        echo "$PID" > "$LOG_DIR/opencoder.pid"
        ;;
        
    background)
        echo "⚙️  Starting OpEncoder in background..."
        
        # Start as a daemon
        nohup bash "$0" run \
            > /dev/null 2>&1 &
        
        echo "✅ OpEncoder running in background"
        ;;
        
    stop)
        echo "🛑 Stopping OpEncoder..."
        if [ -f "$LOG_DIR/opencoder.pid" ]; then
            PID=$(cat "$LOG_DIR/opencoder.pid")
            kill "$PID" 2>/dev/null && echo "✅ OpEncoder stopped" || echo "⚠️  Already stopped"
            rm -f "$LOG_DIR/opencoder.pid"
        fi
        ;;
        
    status)
        if [ -f "$LOG_DIR/opencoder.pid" ]; then
            PID=$(cat "$LOG_DIR/opencoder.pid")
            if ps -p "$PID" > /dev/null; then
                echo "✅ OpEncoder running (PID: $PID)"
                tail -5 "$LOG_DIR/opencoder.log"
            else
                echo "❌ OpEncoder not running (stale PID: $PID)"
            fi
        else
            echo "⚠️  OpEncoder not started"
        fi
        ;;
        
    logs)
        tail -f "$LOG_DIR/opencoder.log"
        ;;
        
    *)
        echo "Usage: $0 {run|background|stop|status|logs}"
        exit 1
        ;;
esac
