#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor web simple para QGZ Editor
Levanta interfaz web para usar qgz_editor.py sin tocar la terminal
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import os
import json
import subprocess
from pathlib import Path

app = Flask(__name__)

# Directorio base
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / 'config.json'
DATA_IN = BASE_DIR / 'data_in'
DATA_OUT = BASE_DIR / 'data_out'

# HTML de la interfaz (todo en uno)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🗺️ QGZ Editor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 2rem;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .card h2 {
            margin-bottom: 1.5rem;
            color: #333;
            font-size: 1.5rem;
        }
        
        .file-list {
            display: grid;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }
        
        .file-item {
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            transition: all 0.2s;
        }
        
        .file-item:hover {
            background: #e9ecef;
            transform: translateX(4px);
        }
        
        .file-icon {
            font-size: 1.5rem;
            margin-right: 1rem;
        }
        
        .file-name {
            flex: 1;
            font-weight: 500;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #6c757d;
        }
        
        .upload-area {
            border: 2px dashed #dee2e6;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            background: #f8f9fa;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .upload-area:hover {
            border-color: #667eea;
            background: #f0f0ff;
        }
        
        .upload-area.drag-over {
            border-color: #28a745;
            background: #e6ffe6;
        }
        
        .rules-container {
            display: grid;
            gap: 1rem;
        }
        
        .rule-item {
            display: grid;
            grid-template-columns: 120px 1fr 1fr 40px;
            gap: 0.75rem;
            align-items: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .rule-item input,
        .rule-item select {
            padding: 0.5rem;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            font-size: 0.95rem;
        }
        
        .rule-item input:focus,
        .rule-item select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-success {
            background: #28a745;
            color: white;
            width: 100%;
            padding: 1rem;
            font-size: 1.1rem;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .btn-small {
            padding: 0.4rem 0.8rem;
            font-size: 0.875rem;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .settings-grid {
            display: grid;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .setting-item {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .setting-item label {
            flex: 0 0 150px;
            font-weight: 500;
        }
        
        .setting-item input {
            flex: 1;
            padding: 0.5rem;
            border: 1px solid #dee2e6;
            border-radius: 6px;
        }
        
        .status-message {
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            display: none;
        }
        
        .status-message.show {
            display: block;
        }
        
        .status-message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status-message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status-message.processing {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .spinner {
            display: inline-block;
            animation: spin 1s linear infinite;
        }
        
        .modules-container {
            display: grid;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .module-item {
            display: flex;
            align-items: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            border: 2px solid transparent;
            transition: all 0.2s;
        }
        
        .module-item.active {
            border-color: #28a745;
            background: #e6ffe6;
        }
        
        .module-item.inactive {
            opacity: 0.6;
        }
        
        .module-toggle {
            margin-right: 1rem;
        }
        
        .module-toggle input {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        .module-info {
            flex: 1;
        }
        
        .module-name {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 0.25rem;
        }
        
        .module-description {
            color: #6c757d;
            font-size: 0.9rem;
        }
        
        .module-status {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .module-status.active {
            background: #28a745;
            color: white;
        }
        
        .module-status.inactive {
            background: #6c757d;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗺️ QGZ Editor</h1>
            <p>Editor visual de proyectos QGIS</p>
        </div>
        
        <!-- Archivos -->
        <div class="card">
            <h2>📁 Archivos</h2>
            <div id="filesList" class="file-list"></div>
            
            <div class="upload-area" id="uploadArea">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📤</div>
                <div>Arrastra archivos .qgz aquí o haz clic para seleccionar</div>
                <input type="file" id="fileInput" multiple accept=".qgz" style="display: none;">
            </div>
        </div>
        
        <!-- Módulos -->
        <div class="card">
            <h2>📦 Módulos de Procesamiento</h2>
            <div id="modulesContainer" class="modules-container"></div>
        </div>
        
        <!-- Configuración del módulo activo -->
        <div class="card" id="moduleConfigCard" style="display: none;">
            <h2>⚙️ Configuración: <span id="activeModuleName">Reemplazo de Texto</span></h2>
            <div id="rulesContainer" class="rules-container"></div>
            <button class="btn btn-primary btn-small" onclick="addRule()">+ Agregar Regla</button>
        </div>
        
        <!-- Opciones generales -->
        <div class="card">
            <h2>🔧 Opciones Generales</h2>
            <div class="settings-grid">
                <div class="setting-item">
                    <label>Sufijo de archivo:</label>
                    <input type="text" id="postfixInput" value="_MODIFICADO">
                </div>
            </div>
        </div>
        
        <!-- Procesar -->
        <div class="card">
            <button class="btn btn-success" onclick="processFiles()">▶️ PROCESAR ARCHIVOS</button>
            <div id="statusMessage" class="status-message"></div>
        </div>
    </div>
    
    <script>
        let modulos = {};
        let rules = [];
        
        // Definición de módulos disponibles
        const MODULOS_DISPONIBLES = {
            'reemplazo_texto': {
                nombre: 'Reemplazo de Texto',
                descripcion: 'Reemplazo masivo de texto/IP en archivos del proyecto',
                tieneConfig: true
            }
        };
        
        // Cargar configuración inicial
        async function loadConfig() {
            const response = await fetch('/api/config');
            const config = await response.json();
            
            // Compatibilidad con formato viejo
            if (config.reemplazos && !config.modulos) {
                modulos = {
                    'reemplazo_texto': {
                        activo: true,
                        descripcion: MODULOS_DISPONIBLES['reemplazo_texto'].descripcion,
                        reglas: config.reemplazos
                    }
                };
            } else {
                modulos = config.modulos || {};
            }
            
            // Asegurar que existan todos los módulos disponibles
            for (const [key, def] of Object.entries(MODULOS_DISPONIBLES)) {
                if (!modulos[key]) {
                    modulos[key] = {
                        activo: false,
                        descripcion: def.descripcion,
                        reglas: []
                    };
                }
            }
            
            rules = modulos['reemplazo_texto']?.reglas || [];
            document.getElementById('postfixInput').value = config.postfijo || '_MODIFICADO';
            
            renderModules();
            renderRules();
        }
        
        // Renderizar módulos
        function renderModules() {
            const container = document.getElementById('modulesContainer');
            
            container.innerHTML = Object.entries(MODULOS_DISPONIBLES).map(([key, def]) => {
                const modulo = modulos[key] || { activo: false };
                const activo = modulo.activo;
                
                return '<div class="module-item ' + (activo ? 'active' : 'inactive') + '">' +
                    '<div class="module-toggle">' +
                    '<input type="checkbox" ' + (activo ? 'checked' : '') + 
                    ' onchange="toggleModule(\\''+key+'\\', this.checked)" ' +
                    'title="' + (activo ? 'Desactivar módulo' : 'Activar módulo') + '">' +
                    '</div>' +
                    '<div class="module-info">' +
                    '<div class="module-name">' + def.nombre + '</div>' +
                    '<div class="module-description">' + def.descripcion + '</div>' +
                    '</div>' +
                    '<span class="module-status ' + (activo ? 'active' : 'inactive') + '">' +
                    (activo ? 'ACTIVO' : 'INACTIVO') +
                    '</span></div>';
            }).join('');
            
            // Mostrar/ocultar configuración del módulo de reemplazo
            const configCard = document.getElementById('moduleConfigCard');
            if (modulos['reemplazo_texto'] && modulos['reemplazo_texto'].activo) {
                configCard.style.display = 'block';
            } else {
                configCard.style.display = 'none';
            }
        }
        
        function toggleModule(key, activo) {
            if (!modulos[key]) {
                modulos[key] = {
                    activo: false,
                    descripcion: MODULOS_DISPONIBLES[key].descripcion,
                    reglas: []
                };
            }
            modulos[key].activo = activo;
            renderModules();
        }
        
        // Cargar lista de archivos
        async function loadFiles() {
            const response = await fetch('/api/files');
            const data = await response.json();
            
            const container = document.getElementById('filesList');
            
            if (data.files.length === 0) {
                container.innerHTML = '<div class="empty-state">No hay archivos en data_in/. Arrastra archivos .qgz arriba.</div>';
                return;
            }
            
            container.innerHTML = data.files.map(function(file) {
                return '<div class="file-item">' +
                    '<div class="file-icon">📄</div>' +
                    '<div class="file-name">' + file + '</div>' +
                    '</div>';
            }).join('');
        }
        
        // Renderizar reglas
        function renderRules() {
            const container = document.getElementById('rulesContainer');
            
            if (rules.length === 0) {
                container.innerHTML = '<div class="empty-state">No hay reglas configuradas. Agrega una regla de reemplazo.</div>';
                return;
            }
            
            container.innerHTML = rules.map(function(rule, index) {
                return '<div class="rule-item">' +
                    '<select onchange="updateRule(' + index + ', \\'tipo\\', this.value)">' +
                    '<option value="ip"' + (rule.tipo === 'ip' ? ' selected' : '') + '>IP</option>' +
                    '<option value="texto"' + (rule.tipo === 'texto' ? ' selected' : '') + '>Texto</option>' +
                    '</select>' +
                    '<input type="text" value="' + (rule.buscar || '') + '" placeholder="Buscar..." ' +
                    'onchange="updateRule(' + index + ', \\'buscar\\', this.value)">' +
                    '<input type="text" value="' + (rule.reemplazar_por || '') + '" placeholder="Reemplazar por..." ' +
                    'onchange="updateRule(' + index + ', \\'reemplazar_por\\', this.value)">' +
                    '<button class="btn btn-danger btn-small" onclick="removeRule(' + index + ')">🗑️</button>' +
                    '</div>';
            }).join('');
        }
        
        function addRule() {
            rules.push({
                tipo: 'texto',
                buscar: '',
                reemplazar_por: ''
            });
            renderRules();
        }
        
        function removeRule(index) {
            rules.splice(index, 1);
            renderRules();
        }
        
        function updateRule(index, field, value) {
            rules[index][field] = value;
        }
        
        // Upload de archivos
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        uploadArea.onclick = function() { fileInput.click(); };
        
        uploadArea.ondragover = function(e) {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        };
        
        uploadArea.ondragleave = function() {
            uploadArea.classList.remove('drag-over');
        };
        
        uploadArea.ondrop = async function(e) {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = Array.from(e.dataTransfer.files).filter(function(f) { return f.name.endsWith('.qgz'); });
            await uploadFiles(files);
        };
        
        fileInput.onchange = async function(e) {
            await uploadFiles(Array.from(e.target.files));
        };
        
        async function uploadFiles(files) {
            for (const file of files) {
                const formData = new FormData();
                formData.append('file', file);
                await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
            }
            loadFiles();
        }
        
        // Procesar archivos
        async function processFiles() {
            // Actualizar reglas en el módulo
            if (modulos['reemplazo_texto']) {
                modulos['reemplazo_texto'].reglas = rules;
            }
            
            const config = {
                modulos: modulos,
                postfijo: document.getElementById('postfixInput').value,
                carpeta_entrada: 'data_in',
                carpeta_salida: 'data_out'
            };
            
            // Primero guardar config
            await fetch('/api/save-config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            
            // Crear área de consola
            const statusEl = document.getElementById('statusMessage');
            statusEl.className = 'status-message show processing';
            statusEl.innerHTML = '<div id="statusHeader" style="font-weight: 600; margin-bottom: 0.5rem; font-size: 1.1rem;">' +
                '<span class="spinner">⏳</span> Ejecutando proceso...</div>' +
                '<div id="console" style="background: #0d1117; color: #c9d1d9; ' +
                "font-family: 'SF Mono', 'Monaco', 'Consolas', 'Courier New', monospace; " +
                'font-size: 0.8rem; line-height: 1.5; padding: 1rem; border-radius: 8px; ' +
                'max-height: 500px; overflow-y: auto; white-space: pre; margin-top: 0.5rem; ' +
                'border: 1px solid #30363d;"></div>';
            
            const consoleEl = document.getElementById('console');
            let lastMessage = '';
            let processSuccess = false;
            
            // Usar EventSource para streaming
            const eventSource = new EventSource('/api/process');
            
            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'log') {
                    consoleEl.textContent += data.message + '\\n';
                    consoleEl.scrollTop = consoleEl.scrollHeight;
                    lastMessage = data.message;
                    // Detectar éxito por el mensaje final
                    if (data.message.includes('procesaron correctamente') || data.message.includes('PROCESO FINALIZADO')) {
                        processSuccess = true;
                    }
                }
            };
            
            eventSource.onerror = function() {
                eventSource.close();
                const headerEl = document.getElementById('statusHeader');
                if (processSuccess) {
                    statusEl.className = 'status-message show success';
                    headerEl.innerHTML = '✅ Proceso completado correctamente';
                } else {
                    statusEl.className = 'status-message show error';
                    headerEl.innerHTML = '❌ Proceso terminado con errores';
                }
                loadFiles();
            };
        }
        
        // Inicializar
        loadConfig();
        loadFiles();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/config')
def get_config():
    """Obtener configuración actual"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return jsonify(config)
    except:
        return jsonify({
            'modulos': {
                'reemplazo_texto': {
                    'activo': True,
                    'descripcion': 'Reemplazo masivo de texto/IP en archivos del proyecto',
                    'reglas': []
                }
            },
            'postfijo': '_MODIFICADO',
            'carpeta_entrada': 'data_in',
            'carpeta_salida': 'data_out'
        })

@app.route('/api/files')
def get_files():
    """Listar archivos en data_in"""
    try:
        files = [f for f in os.listdir(DATA_IN) if f.endswith('.qgz')]
        return jsonify({'files': files})
    except:
        return jsonify({'files': []})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Subir archivo a data_in"""
    file = request.files['file']
    if file and file.filename.endswith('.qgz'):
        filepath = DATA_IN / file.filename
        file.save(filepath)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/save-config', methods=['POST'])
def save_config():
    """Guardar configuración"""
    config = request.json
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    return jsonify({'success': True})

@app.route('/api/process', methods=['GET'])
def process():
    """Procesar archivos con qgz_editor.py - streaming de output"""
    from flask import Response
    import time
    
    def generate():
        """Genera el output en tiempo real"""
        try:
            # Iniciar proceso con stdin cerrado
            proc = subprocess.Popen(
                ['python3', '-u', 'qgz_editor.py'],
                cwd=BASE_DIR,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Leer output línea por línea
            while True:
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    break
                if line:
                    yield f"data: {json.dumps({'type': 'log', 'message': line.rstrip()})}\n\n"
            
            # Leer cualquier output restante
            remaining = proc.stdout.read()
            if remaining:
                for line in remaining.strip().split('\n'):
                    if line:
                        yield f"data: {json.dumps({'type': 'log', 'message': line})}\n\n"
            
            proc.stdout.close()
            return_code = proc.wait()
            
            # Enviar resultado final
            if return_code == 0:
                yield f"data: {json.dumps({'type': 'done', 'status': 'success', 'message': 'Proceso completado correctamente'})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'done', 'status': 'error', 'message': 'El proceso terminó con errores'})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'type': 'done', 'status': 'error', 'message': f'Error: {str(e)}'})}\n\n"
    
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Connection'] = 'keep-alive'
    return response

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🗺️  QGZ Editor - Interfaz Web")
    print("="*60)
    print("\n  Abriendo navegador en http://localhost:8000")
    print("  Presiona Ctrl+C para detener\n")
    print("="*60 + "\n")
    
    # Abrir navegador automáticamente
    import webbrowser
    import threading
    threading.Timer(1.5, lambda: webbrowser.open('http://localhost:8000')).start()
    
    # Iniciar servidor
    app.run(host='127.0.0.1', port=8000, debug=False)
