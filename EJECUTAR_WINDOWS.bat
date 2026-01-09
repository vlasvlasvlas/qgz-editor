@echo off
chcp 65001 >nul 2>&1
REM ============================================================================
REM                        QGZ EDITOR - Ejecutar en Windows
REM ============================================================================
REM 
REM  ¿QUÉ HACE ESTE PROGRAMA?
REM  -------------------------
REM  Edita proyectos QGIS (.qgz) de forma masiva: cambia IPs, textos, etc.
REM 
REM  ANTES DE EJECUTAR:
REM  ------------------
REM  1. Coloca tus archivos .qgz en la carpeta "data_in"
REM  2. Edita "config.json" con los cambios que quieres hacer
REM  3. Haz doble clic en este archivo
REM  4. Los archivos modificados aparecerán en "data_out"
REM
REM ============================================================================

echo.
echo ============================================================================
echo                   QGZ EDITOR - Editor de proyectos QGIS
echo ============================================================================
echo.
echo   Verificando que Python este instalado...
echo.

REM Intentar encontrar Python de diferentes formas
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Python encontrado
    echo.
    echo   Iniciando el programa...
    echo   -----------------------------------------------------------------------
    echo.
    python "%~dp0qgz_editor.py"
    goto :end
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Python3 encontrado
    echo.
    echo   Iniciando el programa...
    echo   -----------------------------------------------------------------------
    echo.
    python3 "%~dp0qgz_editor.py"
    goto :end
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Py launcher encontrado
    echo.
    echo   Iniciando el programa...
    echo   -----------------------------------------------------------------------
    echo.
    py "%~dp0qgz_editor.py"
    goto :end
)

REM Si no se encontró Python
echo.
echo   ============================================================================
echo   [ERROR] NO SE ENCONTRO PYTHON INSTALADO
echo   ============================================================================
echo.
echo   Para instalar Python en Windows:
echo.
echo   1. Abre tu navegador y ve a: https://www.python.org/downloads/
echo.
echo   2. Haz clic en el boton amarillo "Download Python 3.x.x"
echo.
echo   3. Ejecuta el instalador descargado
echo.
echo   4. MUY IMPORTANTE: Marca la casilla que dice:
echo      [X] "Add Python to PATH"
echo      (Esta en la parte de abajo de la ventana del instalador)
echo.
echo   5. Haz clic en "Install Now"
echo.
echo   6. Cuando termine, REINICIA tu computadora
echo.
echo   7. Vuelve a hacer doble clic en este archivo
echo.
echo   ============================================================================
echo.
pause
goto :eof

:end
echo.
echo ============================================================================
echo                         PROGRAMA FINALIZADO
echo ============================================================================
echo.
echo   Los archivos modificados estan en la carpeta "data_out"
echo.
pause
