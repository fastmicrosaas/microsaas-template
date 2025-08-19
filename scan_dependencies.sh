#!/usr/bin/env bash

set -euo pipefail

echo "🔍 Escaneando dependencias y código en busca de vulnerabilidades..."

# Verifica que los comandos estén disponibles
for cmd in pip-audit safety bandit; do
  if ! command -v $cmd &> /dev/null; then
    echo "❌ Error: '$cmd' no está instalado. Instálalo con:"
    echo "    pip install pip-audit safety bandit"
    exit 1
  fi
done

echo ""
echo "📦 Ejecutando pip-audit..."
pip-audit || echo "⚠️ pip-audit encontró problemas."

echo ""
echo "📦 Ejecutando safety..."
safety check || echo "⚠️ safety encontró problemas."

echo ""
echo "🔐 Ejecutando bandit (análisis de código estático)..."
bandit -r app || echo "⚠️ bandit encontró problemas."

echo ""
echo "✅ Escaneo completado."
