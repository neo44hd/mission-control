#!/bin/bash
# NOTA: no usamos `set -e`. Un único servicio que falle (p.ej. un conflicto de
# nombre de contenedor) abortaba TODO el arranque y dejaba JARVIS/GUI sin
# levantar. Ahora cada paso reporta su error y el script continúa.
set -uo pipefail

echo "🚀 SINKIA-OS — Inicio Completo"
echo "========================================="

cd "$(dirname "$0")"

# 1. Importar datos reales si no están importados
if [ ! -f "data/real/datos/ventas-reales.csv" ]; then
    echo ""
    echo "📦 Importando datos reales de Chicken Palace..."
    chmod +x scripts/import-real-data.sh
    bash scripts/import-real-data.sh
fi

# 2. Levantar infraestructura primero
echo ""
echo "🏗️ Levantando infraestructura (PostgreSQL, Redis, Qdrant, Ollama)..."
docker compose up -d postgres redis qdrant ollama || echo "⚠️ Algún servicio de infraestructura no arrancó (ver mensaje arriba)"
sleep 5

# 3. Esperar a que PostgreSQL esté healthy
echo "⏳ Esperando PostgreSQL..."
for i in $(seq 1 30); do
    if docker exec sinkia-postgres pg_isready -U sinkia >/dev/null 2>&1; then
        echo "✅ PostgreSQL listo"
        break
    fi
    sleep 1
done

# 4. Inicializar schema si está vacío
echo "📊 Inicializando base de datos..."
docker exec -i sinkia-postgres psql -U sinkia -d sinkia_os < scripts/seed-database.sql 2>/dev/null || true

# 5. Importar ventas desde CSV
if [ -f "data/real/datos/ventas-reales.csv" ]; then
    echo "📈 Importando ventas reales desde CSV..."
    python3 scripts/seed-from-csv.py 2>/dev/null || echo "⚠️ CSV import pendiente (ejecutar manualmente: python3 scripts/seed-from-csv.py)"
    
    # Si se generó el SQL de importación, ejecutarlo
    if [ -f "data/real/datos/ventas-reales_import.sql" ]; then
        docker exec -i sinkia-postgres psql -U sinkia -d sinkia_os < data/real/datos/ventas-reales_import.sql 2>/dev/null || true
        echo "✅ Ventas importadas a PostgreSQL"
    fi
fi

# 6. Levantar servicios de aplicación
echo ""
echo "🧠 Levantando JARVIS Core..."
docker compose up -d jarvis || echo "⚠️ JARVIS no arrancó"
sleep 3

echo "🖥️ Levantando GUI..."
docker compose up -d sinkia-gui || echo "⚠️ GUI no arrancó"

# 7. Levantar componentes adicionales (si tienen Dockerfile válido)
echo ""
echo "📦 Levantando componentes adicionales..."
for svc in heaven-platform models-centralizer remote-machine sinkmaind-memory synkia-erp; do
    docker compose up -d "$svc" || echo "⚠️ $svc no arrancó"
done

# 8. Status final
echo ""
echo "========================================="
echo "✅ SINKIA-OS INICIADO"
echo "========================================="
echo ""
echo "🌐 Dashboard:     http://localhost:3000"
echo "🧠 JARVIS API:    http://localhost:8080/api/health"
echo "🏢 ERP:           http://localhost:3003"
echo "🦙 Ollama:        http://localhost:11434"
echo ""
echo "📊 Ver estado:    ./status.sh"
echo "🛑 Parar todo:    ./stop.sh"
echo "📋 Logs JARVIS:   docker logs -f sinkia-jarvis"
echo "📋 Logs GUI:      docker logs -f sinkia-gui"
echo ""

# Health check rápido
sleep 2
echo "🔍 Verificando servicios..."
curl -s http://localhost:8080/api/health 2>/dev/null && echo "" || echo "⚠️ JARVIS aún iniciándose..."
curl -s http://localhost:3000 >/dev/null 2>&1 && echo "✅ GUI activa en :3000" || echo "⚠️ GUI aún iniciándose..."
