#!/bin/bash

################################################################################
# LLM Selector Script
# Manages available language models and selects default LLM
################################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.lms-selector/logs"
CONFIG_DIR="$HOME/.lms-selector"
CONFIG_FILE="$CONFIG_DIR/config.json"

mkdir -p "$LOG_DIR" "$CONFIG_DIR"

# Initialize config if it doesn't exist
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
{
  "default_model": "llama2",
  "available_models": [
    "llama2",
    "llama3",
    "mistral",
    "neural-chat",
    "dolphin-mixtral"
  ],
  "ollama_host": "http://localhost:11434",
  "enabled": true
}
EOF
    echo "✅ Created default config at $CONFIG_FILE"
fi

case "$1" in
    start)
        echo "🚀 Starting LLM Selector service..."
        
        # This service typically runs as a background daemon
        # that manages LLM availability and selection
        
        nohup bash -c '
        while true; do
            # Check available models every 30 seconds
            AVAILABLE=$(curl -s http://localhost:11434/api/tags 2>/dev/null | grep -c "\"name\"" || echo 0)
            
            if [ "$AVAILABLE" -gt 0 ]; then
                echo "[$(date)] Available models: $AVAILABLE" >> '"$LOG_DIR"'/selector.log
            fi
            
            sleep 30
        done
        ' > "$LOG_DIR/selector.log" 2>&1 &
        
        PID=$!
        echo "✅ LLM Selector started (PID: $PID)"
        echo "$PID" > "$LOG_DIR/selector.pid"
        ;;
        
    stop)
        echo "🛑 Stopping LLM Selector..."
        if [ -f "$LOG_DIR/selector.pid" ]; then
            PID=$(cat "$LOG_DIR/selector.pid")
            kill "$PID" 2>/dev/null && echo "✅ LLM Selector stopped" || echo "⚠️  Already stopped"
            rm -f "$LOG_DIR/selector.pid"
        fi
        ;;
        
    status)
        if [ -f "$LOG_DIR/selector.pid" ]; then
            PID=$(cat "$LOG_DIR/selector.pid")
            if ps -p "$PID" > /dev/null; then
                echo "✅ LLM Selector running (PID: $PID)"
                echo ""
                echo "📋 Configuration:"
                cat "$CONFIG_FILE" | jq '.' 2>/dev/null || cat "$CONFIG_FILE"
                echo ""
                echo "📊 Available models at http://localhost:11434:"
                curl -s http://localhost:11434/api/tags 2>/dev/null | jq '.models[].name' 2>/dev/null || echo "⚠️  Unable to fetch models"
            else
                echo "❌ LLM Selector not running (stale PID: $PID)"
            fi
        else
            echo "⚠️  LLM Selector not started"
        fi
        ;;
        
    select)
        MODEL="$2"
        if [ -z "$MODEL" ]; then
            echo "Usage: $0 select <model>"
            exit 1
        fi
        
        echo "Selecting model: $MODEL"
        
        # Update config to use this model as default
        if command -v jq &> /dev/null; then
            jq ".default_model = \"$MODEL\"" "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
            mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
            echo "✅ Default model set to: $MODEL"
        else
            echo "⚠️  jq not found, manual edit required"
            echo "Edit $CONFIG_FILE and change default_model to: $MODEL"
        fi
        ;;
        
    list)
        echo "📋 Available models:"
        curl -s http://localhost:11434/api/tags 2>/dev/null | jq '.models[] | {name, size, modified_at}' 2>/dev/null || \
        curl -s http://localhost:11434/api/tags 2>/dev/null || \
        echo "⚠️  Could not fetch models from Ollama"
        ;;
        
    config)
        echo "📄 Current LLM Selector configuration:"
        cat "$CONFIG_FILE" | jq '.' 2>/dev/null || cat "$CONFIG_FILE"
        ;;
        
    logs)
        tail -f "$LOG_DIR/selector.log"
        ;;
        
    *)
        echo "Usage: $0 {start|stop|status|select <model>|list|config|logs}"
        exit 1
        ;;
esac
