#!/usr/bin/env python3
"""
🦇 SYNK-IA Ecosystem Agent - Main Orchestrator
Autonomous system manager for LLM ecosystem
- Monitors all providers
- Tracks resource usage
- Discovers new models
- Auto-updates configurations
- Generates reports
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Local imports
from health_checker import ProviderHealthChecker, ProviderStatus as ProviderStatusModel
from metrics import MetricsCollector
from scheduler import SchedulerManager

# ============================================================================
# Configuration & Constants
# ============================================================================

AGENT_PORT = 8009
DASHBOARD_PORT = 8011
CONFIG_DIR = Path("/Users/davidnows/Agentes-Pro/ecosystem-agent")
DATA_DIR = Path("/Users/davidnows/.synkia/ecosystem-data")

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Pydantic Models
# ============================================================================

class ProviderStatus(BaseModel):
    """Provider health status (Pydantic model)"""
    name: str
    status: str  # "healthy", "degraded", "down"
    latency_ms: float
    uptime_percent: float
    last_check: str
    error_message: Optional[str] = None

class SystemMetrics(BaseModel):
    """System resource metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_percent: float
    temperature_c: Optional[float] = None

class EcosystemStatus(BaseModel):
    """Overall ecosystem health"""
    timestamp: str
    providers: List[ProviderStatus]
    metrics: SystemMetrics
    uptime_percent: float
    total_models: int
    active_models: int

class DiscoveryRecommendation(BaseModel):
    """Recommendation from discovery engine"""
    type: str  # "new_provider", "new_model", "optimization", "security"
    title: str
    description: str
    impact: str  # "high", "medium", "low"
    action: Optional[str] = None
    source: str

# ============================================================================
# Main Ecosystem Agent
# ============================================================================

class EcosystemAgent:
    """
    Main orchestrator for autonomous ecosystem management
    """
    
    def __init__(self):
        self.app = FastAPI(
            title="🦇 SYNK-IA Ecosystem Agent",
            description="Autonomous LLM Ecosystem Management System",
            version="1.0.0"
        )
        self.setup_routes()
        
        # Initialize components
        self.health_checker = ProviderHealthChecker()
        self.metrics_collector = MetricsCollector()
        self.scheduler_manager = SchedulerManager()
        
        # State
        self.ecosystem_status: Optional[EcosystemStatus] = None
        self.recommendations: List[DiscoveryRecommendation] = []
        self.start_time = datetime.now()
        
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @self.app.get("/health")
        async def health():
            """Agent health check"""
            return {
                "status": "alive",
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "version": "1.0.0"
            }
        
        @self.app.get("/ecosystem/status")
        async def get_ecosystem_status():
            """Get full ecosystem status"""
            if self.ecosystem_status is None:
                await self.update_ecosystem_status()
            return self.ecosystem_status
        
        @self.app.get("/ecosystem/providers")
        async def get_providers():
            """Get all provider statuses"""
            return await self.health_checker.check_all_providers()
        
        @self.app.get("/ecosystem/metrics")
        async def get_metrics():
            """Get system metrics"""
            return self.metrics_collector.get_current_metrics()
        
        @self.app.get("/recommendations")
        async def get_recommendations():
            """Get discovery recommendations"""
            return {"recommendations": self.recommendations}
        
        @self.app.post("/ecosystem/update")
        async def trigger_update():
            """Manually trigger ecosystem update"""
            result = await self.scheduler_manager.run_update_check()
            return {"status": "update_triggered", "result": result}
        
        @self.app.get("/metrics/prometheus")
        async def prometheus_metrics():
            """Prometheus-format metrics"""
            return self.metrics_collector.get_prometheus_format()
        
        @self.app.get("/logs")
        async def get_logs(limit: int = 100):
            """Get recent logs"""
            log_file = DATA_DIR / "ecosystem.log"
            if not log_file.exists():
                return {"logs": []}
            
            with open(log_file, "r") as f:
                lines = f.readlines()[-limit:]
            return {"logs": lines}
    
    async def update_ecosystem_status(self):
        """Update complete ecosystem status"""
        providers_data = await self.health_checker.check_all_providers()
        
        # Convertir ProviderStatusModel a ProviderStatus Pydantic
        providers = [
            ProviderStatus(
                name=p.name,
                status=p.status,
                latency_ms=p.latency_ms,
                uptime_percent=p.uptime_percent,
                last_check=p.last_check,
                error_message=p.error_message
            )
            for p in providers_data
        ]
        
        metrics = self.metrics_collector.get_current_metrics()
        # Convertir dict a SystemMetrics
        metrics_obj = SystemMetrics(
            timestamp=metrics["timestamp"],
            cpu_percent=metrics["cpu_percent"],
            memory_percent=metrics["memory_percent"],
            memory_mb=metrics["memory_mb"],
            disk_percent=metrics["disk_percent"],
            temperature_c=metrics.get("temperature_c")
        )
        
        self.ecosystem_status = EcosystemStatus(
            timestamp=datetime.now().isoformat(),
            providers=providers,
            metrics=metrics_obj,
            uptime_percent=self._calculate_uptime(providers),
            total_models=self._count_total_models(),
            active_models=self._count_active_models()
        )
    
    def _calculate_uptime(self, providers: List[ProviderStatus] = None) -> float:
        """Calculate ecosystem uptime percentage"""
        if not providers:
            providers = self.ecosystem_status.providers if self.ecosystem_status else []
        
        if not providers:
            return 100.0
        
        healthy = sum(1 for p in providers if p.status == "healthy")
        total = len(providers)
        return (healthy / total * 100) if total > 0 else 0.0
    
    def _count_total_models(self) -> int:
        """Count total available models"""
        # Read from litellm config
        config_file = Path("/Users/davidnows/Agentes-Pro/litellm/config.yaml")
        if config_file.exists():
            # Simple count of model_name entries
            with open(config_file) as f:
                content = f.read()
                return content.count("model_name:")
        return 0
    
    def _count_active_models(self) -> int:
        """Count currently active/loaded models"""
        # Check Ollama and LM Studio
        active = 0
        try:
            import requests
            # Check Ollama
            resp = requests.get("http://localhost:11434/api/tags", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                active += len(data.get("models", []))
        except:
            pass
        
        return active
    
    async def start_background_tasks(self):
        """Start all background monitoring tasks"""
        print("🦇 Starting ecosystem agent background tasks...")
        
        # Health check every 5 minutes
        async def health_check_loop():
            while True:
                try:
                    await self.update_ecosystem_status()
                    print(f"✅ Ecosystem status updated: {self.ecosystem_status.uptime_percent:.1f}% uptime")
                except Exception as e:
                    print(f"❌ Health check error: {e}")
                await asyncio.sleep(300)  # 5 minutes
        
        # Metrics collection every minute
        async def metrics_loop():
            while True:
                try:
                    self.metrics_collector.collect()
                except Exception as e:
                    print(f"❌ Metrics error: {e}")
                await asyncio.sleep(60)  # 1 minute
        
        # Discovery check weekly
        async def discovery_loop():
            while True:
                try:
                    # Run discovery (weekly)
                    print("🔍 Running discovery check...")
                    # TODO: Implement discovery engine
                except Exception as e:
                    print(f"❌ Discovery error: {e}")
                await asyncio.sleep(604800)  # 1 week
        
        # Start all loops
        asyncio.create_task(health_check_loop())
        asyncio.create_task(metrics_loop())
        asyncio.create_task(discovery_loop())
    
    async def on_startup(self):
        """Called when FastAPI starts"""
        await self.start_background_tasks()
        print("🦇 SYNK-IA Ecosystem Agent started!")
    
    def run(self, host: str = "0.0.0.0", port: int = AGENT_PORT):
        """Run the agent"""
        self.app.add_event_handler("startup", self.on_startup)
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    agent = EcosystemAgent()
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║  🦇 SYNK-IA ECOSYSTEM AGENT                       ║
    ║  Autonomous Ecosystem Management System            ║
    ║                                                   ║
    ║  Starting on http://localhost:8009                ║
    ║  Dashboard: http://localhost:8011                 ║
    ╚═══════════════════════════════════════════════════╝
    """)
    agent.run()
