#!/bin/bash
# ============================================================================
#                        QGZ EDITOR - Ejecutar en Linux/Mac
# ============================================================================
# 
#  ¿QUÉ HACE ESTE PROGRAMA?
#  -------------------------
#  Edita proyectos QGIS (.qgz) de forma masiva: cambia IPs, textos, etc.
# 
#  ANTES DE EJECUTAR:
#  ------------------
#  1. Coloca tus archivos .qgz en la carpeta "data_in"
#  2. Edita "config.json" con los cambios que quieres hacer
#  3. Ejecuta: ./EJECUTAR_LINUX_MAC.sh
#  4. Los archivos modificados aparecerán en "data_out"
#
#  PRIMERA VEZ:
#  ------------
#  Si tienes problemas de permisos, ejecuta primero:
#     chmod +x EJECUTAR_LINUX_MAC.sh
#
# ============================================================================

echo ""
echo "============================================================================"
echo "                  QGZ EDITOR - Editor de proyectos QGIS"
echo "============================================================================"
echo ""
echo "  Verificando que Python esté instalado..."
echo ""

# Obtener el directorio donde está este script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Intentar encontrar Python 3
if command -v python3 &> /dev/null; then
    echo "  [OK] Python3 encontrado"
    echo ""
    echo "  Iniciando el programa..."
    echo "  -----------------------------------------------------------------------"
    echo ""
    python3 "$SCRIPT_DIR/qgz_editor.py"
elif command -v python &> /dev/null; then
    # Verificar que es Python 3
    PYTHON_VERSION=$(python --version 2>&1 | grep -o '[0-9]' | head -1)
    if [ "$PYTHON_VERSION" -ge 3 ]; then
        echo "  [OK] Python encontrado (versión 3+)"
        echo ""
        echo "  Iniciando el programa..."
        echo "  -----------------------------------------------------------------------"
        echo ""
        python "$SCRIPT_DIR/qgz_editor.py"
    else
        echo ""
        echo "  ============================================================================"
        echo "  [ERROR] SE ENCONTRÓ PYTHON 2, PERO SE NECESITA PYTHON 3"
        echo "  ============================================================================"
        echo ""
        echo "  Para instalar Python 3:"
        echo ""
        echo "  En Ubuntu/Debian:"
        echo "     sudo apt update"
        echo "     sudo apt install python3"
        echo ""
        echo "  En Fedora:"
        echo "     sudo dnf install python3"
        echo ""
        echo "  En macOS (con Homebrew):"
        echo "     brew install python3"
        echo ""
        exit 1
    fi
else
    echo ""
    echo "  ============================================================================"
    echo "  [ERROR] NO SE ENCONTRÓ PYTHON INSTALADO"
    echo "  ============================================================================"
    echo ""
    echo "  Para instalar Python 3:"
    echo ""
    echo "  En Ubuntu/Debian:"
    echo "     sudo apt update"
    echo "     sudo apt install python3"
    echo ""
    echo "  En Fedora:"
    echo "     sudo dnf install python3"
    echo ""
    echo "  En macOS (con Homebrew):"
    echo "     brew install python3"
    echo ""
    echo "  O descárgalo de: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo ""
echo "============================================================================"
echo "                         PROGRAMA FINALIZADO"
echo "============================================================================"
echo ""
echo "  Los archivos modificados están en la carpeta 'data_out'"
echo ""
