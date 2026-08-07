#!/bin/bash

################################################################################
# OpenClaw Startup Script
# Manages OpenClaw local API server for Claude Code integration
################################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.openclaw/logs"
OPENCLAW_PORT=${OPENCLAW_PORT:-8000}
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"

mkdir -p "$LOG_DIR"

case "$1" in
    start)
        echo "🚀 Starting OpenClaw..."
        
        # Check if OpenClaw is installed
        if ! command -v openclaw &> /dev/null; then
            echo "❌ OpenClaw not found. Check installation at ~/.openclaw"
            exit 1
        fi
        
        # Start OpenClaw in the background
        nohup openclaw server \
            --host 0.0.0.0 \
            --port "$OPENCLAW_PORT" \
            --log-level info \
            > "$LOG_DIR/openclaw.log" 2>&1 &
        
        OPENCLAW_PID=$!
        echo "✅ OpenClaw started (PID: $OPENCLAW_PID) on port $OPENCLAW_PORT"
        echo "$OPENCLAW_PID" > "$LOG_DIR/openclaw.pid"
        
        sleep 2
        if curl -s "http://localhost:$OPENCLAW_PORT/health" > /dev/null; then
            echo "✅ OpenClaw health check: OK"
        else
            echo "⚠️  OpenClaw starting, health check pending..."
        fi
        ;;
        
    stop)
        echo "🛑 Stopping OpenClaw..."
        if [ -f "$LOG_DIR/openclaw.pid" ]; then
            PID=$(cat "$LOG_DIR/openclaw.pid")
            kill "$PID" 2>/dev/null && echo "✅ OpenClaw stopped" || echo "⚠️  Already stopped"
            rm -f "$LOG_DIR/openclaw.pid"
        fi
        ;;
        
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
        
    status)
        if [ -f "$LOG_DIR/openclaw.pid" ]; then
            PID=$(cat "$LOG_DIR/openclaw.pid")
            if ps -p "$PID" > /dev/null; then
                echo "✅ OpenClaw running (PID: $PID)"
                HEALTH=$(curl -s "http://localhost:$OPENCLAW_PORT/health" 2>/dev/null)
                if [ -n "$HEALTH" ]; then
                    echo "✅ Health: $HEALTH"
                fi
                echo ""
                echo "Recent logs:"
                tail -3 "$LOG_DIR/openclaw.log"
            else
                echo "❌ OpenClaw not running (stale PID: $PID)"
            fi
        else
            echo "⚠️  OpenClaw not started"
        fi
        ;;
        
    logs)
        tail -f "$LOG_DIR/openclaw.log"
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
