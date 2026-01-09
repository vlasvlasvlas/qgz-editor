@echo off
cls
echo ================================================================
echo   🗺️  QGZ Editor - Interfaz Web
echo ================================================================
echo.
echo Instalando dependencia...
python -m pip install -q flask

echo.
echo Iniciando servidor web...
echo La interfaz se abrirá automáticamente en tu navegador
echo.
echo Presiona Ctrl+C para detener el servidor
echo ================================================================
echo.

python web_server.py

pause
