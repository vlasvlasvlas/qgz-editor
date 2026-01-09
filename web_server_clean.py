#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor web simple para QGZ Editor
Levanta interfaz web para usar qgz_editor.py sin tocar la terminal
"""

from flask import Flask, render_template_string, request, jsonify, Response, stream_with_context
import os
import json
import subprocess
import time
from pathlib import Path

app = Flask(__name__)

# Directorio base
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / 'config.json'
DATA_IN = BASE_DIR / 'data_in'
DATA_OUT = BASE_DIR / 'data_out'

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
        .container { max-width: 1000px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 2rem; }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; }
        .card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card h2 { margin-bottom: 1.5rem; color: #333; font-size: 1.5rem; }
        .file-list { display: grid; gap: 0.75rem; margin-bottom: 1rem; }
        .file-item {
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            transition: all 0.2s;
        }
        .file-item:hover { background: #e9ecef; transform: translateX(4px); }
        .file-icon { font-size: 1.5rem; margin-right: 1rem; }
        .file-name { flex: 1; font-weight: 500; }
        .empty-state { text-align: center; padding: 3rem; color: #6c757d; }
        .upload-area {
            border: 2px dashed #dee2e6;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            background: #f8f9fa;
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-area:hover { border-color: #667eea; background: #f0f0ff; }
        .upload-area.drag-over { border-color: #28a745; background: #e6ffe6; }
        .rules-container { display: grid; gap: 1rem; }
        .rule-item {
            display: grid;
            grid-template-columns: 120px 1fr 1fr 40px;
            gap: 0.75rem;
            align-items: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .rule-item input, .rule-item select {
            padding: 0.5rem;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            font-size: 0.95rem;
        }
        .rule-item input:focus, .rule-item select:focus {
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
        .btn-success:hover { background: #218838; }
        .btn-small { padding: 0.4rem 0.8rem; font-size: 0.875rem; }
        .btn-danger { background: #dc3545; color: white; }
        .settings-grid { display: grid; gap: 1rem; margin-top: 1rem; }
        .setting-item { display: flex; align-items: center; gap: 1rem; }
        .setting-item label { flex: 0 0 150px; font-weight: 500; }
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
        .status-message.show { display: block; }
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗺️ QGZ Editor</h1>
            <p>Editor visual de proyectos QGIS</p>
        </div>
        
        <div class="card">
            <h2>📁 Archivos</h2>
            <div id="filesList" class="file-list"></div>
            <div class="upload-area" id="uploadArea">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📤</div>
                <div>Arrastra archivos .qgz aquí o haz clic para seleccionar</div>
                <input type="file" id="fileInput" multiple accept=".qgz" style="display: none;">
            </div>
        </div>
        
        <div class="card">
            <h2>⚙️ Configuración de Reemplazos</h2>
            <div id="rulesContainer" class="rules-container"></div>
            <button class="btn btn-primary btn-small" onclick="addRule()">+ Agregar Regla</button>
            <div class="settings-grid">
                <div class="setting-item">
                    <label>Sufijo de archivo:</label>
                    <input type="text" id="postfixInput" value="_MODIFICADO">
                </div>
            </div>
        </div>
        
        <div class="card">
            <button class="btn btn-success" onclick="processFiles()">▶️ PROCESAR ARCHIVOS</button>
            <div id="statusMessage" class="status-message"></div>
        </div>
    </div>
    
    <script>
        let rules = [];
        
        async function loadConfig() {
            const response = await fetch('/api/config');
            const config = await response.json();
            
            // Extraer reglas del formato de módulos
            if (config.modulos && config.modulos.reemplazo_texto) {
                rules = config.modulos.reemplazo_texto.reglas || [];
            } else if (config.reemplazos) {
                // Compatibilidad con formato viejo
                rules = config.reemplazos;
            } else {
                rules = [];
            }
            
            document.getElementById('postfixInput').value = config.postfijo || '_MODIFICADO';
            renderRules();
        }
        
        async function loadFiles() {
            const response = await fetch('/api/files');
            const data = await response.json();
            const container = document.getElementById('filesList');
            
            if (data.files.length === 0) {
                container.innerHTML = '<div class="empty-state">No hay archivos todavía. Arrastra archivos .qgz arriba.</div>';
                return;
            }
            
            container.innerHTML = data.files.map(file => `
                <div class="file-item">
                    <div class="file-icon">📄</div>
                    <div class="file-name">${file}</div>
                </div>
            `).join('');
        }
        
        function renderRules() {
            const container = document.getElementById('rulesContainer');
            
            if (rules.length === 0) {
                container.innerHTML = '<div class="empty-state">No hay reglas configuradas. Agrega una regla de reemplazo.</div>';
                return;
            }
            
            container.innerHTML = rules.map((rule, index) => `
                <div class="rule-item">
                    <select onchange="updateRule(${index}, 'tipo', this.value)">
                        <option value="ip" ${rule.tipo === 'ip' ? 'selected' : ''}>IP</option>
                        <option value="texto" ${rule.tipo === 'texto' ? 'selected' : ''}>Texto</option>
                    </select>
                    <input type="text" value="${rule.buscar}" placeholder="Buscar..." onchange="updateRule(${index}, 'buscar', this.value)">
                    <input type="text" value="${rule.reemplazar_por}" placeholder="Reemplazar por..." onchange="updateRule(${index}, 'reemplazar_por', this.value)">
                    <button class="btn btn-danger btn-small" onclick="removeRule(${index})">🗑️</button>
                </div>
            `).join('');
        }
        
        function addRule() {
            rules.push({ tipo: 'texto', buscar: '', reemplazar_por: '' });
            renderRules();
        }
        
        function removeRule(index) {
            rules.splice(index, 1);
            renderRules();
        }
        
        function updateRule(index, field, value) {
            rules[index][field] = value;
        }
        
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        uploadArea.onclick = () => fileInput.click();
        uploadArea.ondragover = (e) => { e.preventDefault(); uploadArea.classList.add('drag-over'); };
        uploadArea.ondragleave = () => { uploadArea.classList.remove('drag-over'); };
        uploadArea.ondrop = async (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.qgz'));
            await uploadFiles(files);
        };
        
        fileInput.onchange = async (e) => { await uploadFiles(Array.from(e.target.files)); };
        
        async function uploadFiles(files) {
            for (const file of files) {
                const formData = new FormData();
                formData.append('file', file);
                await fetch('/api/upload', { method: 'POST', body: formData });
            }
            loadFiles();
        }
        
        let refreshInterval = null;
        let isProcessing = false;
        
        async function processFiles() {
            if (isProcessing) return;
            isProcessing = true;
            
            const config = {
                modulos: {
                    reemplazo_texto: {
                        activo: rules.length > 0,
                        reglas: rules
                    }
                },
                postfijo: document.getElementById('postfixInput').value,
                carpeta_entrada: 'data_in',
                carpeta_salida: 'data_out'
            };
            
            await fetch('/api/save-config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            
            const statusEl = document.getElementById('statusMessage');
            statusEl.className = 'status-message show processing';
            statusEl.innerHTML = '<div style="font-weight: 600; margin-bottom: 0.5rem;"><span class="spinner">⏳</span> Procesando archivos...</div><div id="console" style="background: #1e1e1e; color: #d4d4d4; font-family: Courier New, monospace; font-size: 0.85rem; padding: 1rem; border-radius: 6px; max-height: 400px; overflow-y: auto; white-space: pre-wrap; margin-top: 0.5rem;">Iniciando proceso...\\n</div>';
            
            const consoleEl = document.getElementById('console');
            
            try {
                const eventSource = new EventSource('/api/process');
                let hasData = false;
                
                eventSource.onmessage = (event) => {
                    hasData = true;
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'log') {
                        consoleEl.textContent += data.message + '\\n';
                        consoleEl.scrollTop = consoleEl.scrollHeight;
                    } else if (data.type === 'success') {
                        eventSource.close();
                        statusEl.className = 'status-message show success';
                        statusEl.innerHTML = consoleEl.outerHTML + '<div style="margin-top: 1rem; font-weight: 600;">' + data.message + '</div>';
                        isProcessing = false;
                        loadFiles();
                    } else if (data.type === 'error') {
                        eventSource.close();
                        statusEl.className = 'status-message show error';
                        statusEl.innerHTML = consoleEl.outerHTML + '<div style="margin-top: 1rem; font-weight: 600;">' + data.message + '</div>';
                        isProcessing = false;
                    }
                };
                
                eventSource.onerror = () => {
                    eventSource.close();
                    if (!hasData) {
                        statusEl.className = 'status-message show error';
                        consoleEl.textContent += '\\n❌ Error: No se pudo conectar al proceso de streaming\\n';
                        consoleEl.textContent += 'Esto puede ocurrir si el proceso no genera output inmediatamente.\\n';
                    }
                    isProcessing = false;
                };
                
                // Timeout de seguridad
                setTimeout(() => {
                    if (isProcessing && !hasData) {
                        eventSource.close();
                        consoleEl.textContent += '\\n⏱️ Timeout: El proceso tardó demasiado en responder\\n';
                        statusEl.className = 'status-message show error';
                        isProcessing = false;
                    }
                }, 60000); // 60 segundos
                
            } catch (error) {
                statusEl.className = 'status-message show error';
                statusEl.innerHTML = '<div>❌ Error: ' + error.message + '</div>';
                isProcessing = false;
            }
        }
        
        loadConfig();
        loadFiles();
        refreshInterval = setInterval(() => {
            if (!isProcessing) {
                loadFiles();
            }
        }, 5000); // Cambiado a 5 segundos y solo si no está procesando
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/config')
def get_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return jsonify(config)
    except:
        return jsonify({
            'reemplazos': [],
            'postfijo': '_MODIFICADO',
            'carpeta_entrada': 'data_in',
            'carpeta_salida': 'data_out'
        })

@app.route('/api/files')
def get_files():
    try:
        files = [f for f in os.listdir(DATA_IN) if f.endswith('.qgz')]
        return jsonify({'files': files})
    except:
        return jsonify({'files': []})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and file.filename.endswith('.qgz'):
        filepath = DATA_IN / file.filename
        file.save(filepath)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/save-config', methods=['POST'])
def save_config():
    config = request.json
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    return jsonify({'success': True})

@app.route('/api/process', methods=['GET'])
def process():
    def generate():
        try:
            process = subprocess.Popen(
                ['python3', '-u', 'qgz_editor.py'],  # -u = unbuffered output
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # Sin buffer
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    yield f"data: {json.dumps({'type': 'log', 'message': line.rstrip()})}\\n\\n"
                    time.sleep(0.01)
            
            process.wait()
            
            if process.returncode == 0:
                yield f"data: {json.dumps({'type': 'success', 'message': '✅ Archivos procesados correctamente!'})}\\n\\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': '❌ Error al procesar archivos'})}\\n\\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'❌ Error: {str(e)}'})}\\n\\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    print("\\n" + "="*60)
    print("  🗺️  QGZ Editor - Interfaz Web")
    print("="*60)
    print("\\n  Abriendo navegador en http://localhost:8000")
    print("  Presiona Ctrl+C para detener\\n")
    print("="*60 + "\\n")
    
    import webbrowser
    import threading
    threading.Timer(1.5, lambda: webbrowser.open('http://localhost:8000')).start()
    
    app.run(host='127.0.0.1', port=8000, debug=False)
