#!/bin/bash

################################################################################
# Master Startup Script for Claude Code Services
# Orchestrates: Hermes, Ollama, Aider, OpenClaw, OpEncoder, LLM Selector
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.startup-logs"
STARTUP_LOG="$LOG_DIR/startup-$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$LOG_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging function
log() {
    local level=$1
    shift
    local msg="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${!level}[$timestamp] $msg${NC}" | tee -a "$STARTUP_LOG"
}

# Service startup function
start_service() {
    local name=$1
    local script=$2
    local action=${3:-start}
    
    log BLUE "→ Starting $name..."
    
    if [ ! -f "$script" ]; then
        log RED "❌ $name script not found: $script"
        return 1
    fi
    
    if [ ! -x "$script" ]; then
        log YELLOW "⚠️  Making $name script executable..."
        chmod +x "$script"
    fi
    
    if "$script" "$action" >> "$STARTUP_LOG" 2>&1; then
        log GREEN "✅ $name started"
        return 0
    else
        log RED "❌ Failed to start $name"
        return 1
    fi
}

# Main startup sequence
main() {
    log BLUE "╔════════════════════════════════════════════════════════════════╗"
    log BLUE "║     Claude Code Services Startup Orchestrator                  ║"
    log BLUE "║     $(date '+%Y-%m-%d %H:%M:%S UTC')                                  ║"
    log BLUE "╚════════════════════════════════════════════════════════════════╝"
    
    log BLUE ""
    log BLUE "📋 Startup Plan:"
    log BLUE "  1. Hermes Agent (launchd)"
    log BLUE "  2. Ollama LLM Server"
    log BLUE "  3. Aider (AI Pair Programmer)"
    log BLUE "  4. OpenClaw (Local API Server)"
    log BLUE "  5. OpEncoder (Code Optimization)"
    log BLUE "  6. LLM Selector (Model Manager)"
    log BLUE ""
    
    # Counter for results
    STARTED=0
    FAILED=0
    
    # Step 1: Hermes Agent
    log BLUE "🔵 Step 1/6: Hermes Agent"
    if launchctl load ~/Library/LaunchAgents/com.hermes.hertxplore.plist 2>/dev/null; then
        log GREEN "✅ Hermes Agent loaded"
        ((STARTED++))
    elif launchctl list | grep -q "com.hermes.hertxplore"; then
        log YELLOW "⚠️  Hermes Agent already loaded"
        ((STARTED++))
    else
        log YELLOW "⚠️  Hermes Agent not available (not critical)"
    fi
    
    # Step 2: Ollama
    log BLUE "🔵 Step 2/6: Ollama LLM Server"
    if pgrep -f "ollama serve" > /dev/null; then
        log GREEN "✅ Ollama already running"
        ((STARTED++))
    else
        log BLUE "Starting Ollama..."
        mkdir -p ~/.ollama/logs
        nohup ollama serve > ~/.ollama/logs/ollama.log 2>&1 &
        sleep 3
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            log GREEN "✅ Ollama started"
            ((STARTED++))
        else
            log YELLOW "⚠️  Ollama starting (may take a moment)"
            ((STARTED++))
        fi
    fi
    
    # Step 3: Aider
    log BLUE "🔵 Step 3/6: Aider AI Pair Programmer"
    if start_service "Aider" "$HOME/scripts/aider.sh" "start"; then
        ((STARTED++))
    else
        log YELLOW "⚠️  Aider not critical, continuing..."
        ((FAILED++))
    fi
    
    # Step 4: OpenClaw
    log BLUE "🔵 Step 4/6: OpenClaw API Server"
    if start_service "OpenClaw" "$HOME/scripts/openclaw_start.sh" "start"; then
        ((STARTED++))
    else
        log YELLOW "⚠️  OpenClaw not critical, continuing..."
        ((FAILED++))
    fi
    
    # Step 5: OpEncoder
    log BLUE "🔵 Step 5/6: OpEncoder Code Optimization"
    if start_service "OpEncoder" "$HOME/scripts/opencoder.sh" "background"; then
        ((STARTED++))
    else
        log YELLOW "⚠️  OpEncoder not critical, continuing..."
        ((FAILED++))
    fi
    
    # Step 6: LLM Selector
    log BLUE "🔵 Step 6/6: LLM Selector Model Manager"
    if start_service "LLM Selector" "$HOME/scripts/lms-selector.sh" "start"; then
        ((STARTED++))
    else
        log YELLOW "⚠️  LLM Selector not critical, continuing..."
        ((FAILED++))
    fi
    
    # Summary
    log BLUE ""
    log BLUE "╔════════════════════════════════════════════════════════════════╗"
    log BLUE "║                      STARTUP SUMMARY                          ║"
    
    if [ $FAILED -eq 0 ]; then
        log GREEN "║  Status: ✅ ALL SERVICES STARTED                             ║"
    elif [ $FAILED -lt 3 ]; then
        log YELLOW "║  Status: ⚠️  PARTIAL START ($(($STARTED)) OK, $((FAILED)) non-critical)   ║"
    else
        log RED "║  Status: ❌ STARTUP FAILED                                   ║"
    fi
    
    log BLUE "║                                                                ║"
    log BLUE "║  Services Running: $STARTED/6                                       ║"
    log BLUE "║  Issues: $FAILED                                                    ║"
    log BLUE "║  Log: $STARTUP_LOG                          ║"
    log BLUE "╚════════════════════════════════════════════════════════════════╝"
    
    log BLUE ""
    log BLUE "📊 Service Status Commands:"
    log BLUE "  ~/scripts/aider.sh status"
    log BLUE "  ~/scripts/openclaw_start.sh status"
    log BLUE "  ~/scripts/opencoder.sh status"
    log BLUE "  ~/scripts/lms-selector.sh status"
    
    log BLUE ""
    log BLUE "📋 View Logs:"
    log BLUE "  tail -f ~/.aider/logs/aider.log"
    log BLUE "  tail -f ~/.openclaw/logs/openclaw.log"
    log BLUE "  tail -f ~/.opencoder/logs/opencoder.log"
    log BLUE "  tail -f ~/.lms-selector/logs/selector.log"
    
    log BLUE ""
    log BLUE "💾 Full startup log: tail -f $STARTUP_LOG"
    log BLUE ""
    
    return $FAILED
}

# Run main startup
main
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log GREEN "✅ Startup completed successfully"
    exit 0
else
    log YELLOW "⚠️  Startup completed with $EXIT_CODE non-critical issues"
    exit 0  # Don't fail on non-critical issues
fi
