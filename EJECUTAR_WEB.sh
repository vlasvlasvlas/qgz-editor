#!/bin/bash

clear
cat << "EOF"
================================================================
  🗺️  QGZ Editor - Interfaz Web
================================================================
EOF

echo ""
echo "Instalando dependencia..."
pip3 install -q flask

echo ""
echo "Iniciando servidor web..."
echo "La interfaz se abrirá automáticamente en tu navegador"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo "================================================================"
echo ""

python3 web_server.py
