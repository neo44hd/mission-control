#!/bin/bash
echo "🔍 SINKIA-OS — Estado del Sistema"
echo "========================================="

# Contenedores Docker
echo ""
echo "🐳 Contenedores Docker:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  docker compose no disponible"

# Health checks HTTP
echo ""
echo "🌐 Servicios HTTP:"
for svc in "JARVIS Core|http://localhost:8080/api/health" "GUI|http://localhost:3000" "ERP|http://localhost:3003/api/health" "Ollama|http://localhost:11434/api/tags" "HEAVEN|http://localhost:8009/health"; do
    name=$(echo "$svc" | cut -d'|' -f1)
    url=$(echo "$svc" | cut -d'|' -f2)
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "$url" 2>/dev/null)
    if [ "$status" = "200" ]; then
        echo "  ✅ $name ($url)"
    else
        echo "  ❌ $name ($url) → HTTP $status"
    fi
done

# Datos en DB
echo ""
echo "📊 Datos en PostgreSQL:"
docker exec sinkia-postgres psql -U sinkia -d sinkia_os -c "
SELECT 'Ventas' as tabla, COUNT(*) as registros FROM sales_daily
UNION ALL SELECT 'Proveedores', COUNT(*) FROM providers
UNION ALL SELECT 'Facturas compra', COUNT(*) FROM purchase_invoices
UNION ALL SELECT 'Empleados', COUNT(*) FROM employees
UNION ALL SELECT 'Insights', COUNT(*) FROM jarvis_insights;
" 2>/dev/null || echo "  ⚠️ PostgreSQL no accesible"

# Archivos de datos reales
echo ""
echo "📁 Archivos de datos reales:"
FACTURAS=$(find data/real/facturas -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')
MODELOS=$(find data/real/modelos-fiscales -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')
DOCS=$(find data/real/documentos -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')
CSV=$(ls data/real/datos/*.csv 2>/dev/null | wc -l | tr -d ' ')
echo "  📄 Facturas: $FACTURAS PDFs"
echo "  📋 Modelos fiscales: $MODELOS PDFs"
echo "  📁 Documentos: $DOCS PDFs"
echo "  📊 CSVs: $CSV archivos"

echo ""
echo "========================================="
