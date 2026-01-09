# 🗺️ QGZ Editor

**Herramienta para editar proyectos QGIS (.qgz) de forma masiva y automática.**

---

## ✨ ¿Qué hace esta herramienta?

Si trabajas con QGIS y necesitas hacer cambios masivos en tus proyectos (cambiar IPs de servidores, modificar rutas, actualizar textos, etc.), esta herramienta te permite hacerlo de forma automática sin tener que abrir cada proyecto manualmente.

### 🎯 Características

| Característica | Descripción |
|---------|-------------|
| ⚡ **Procesamiento masivo** | Procesa múltiples archivos |
| 🛡️ **No destructivo** | No modifica los archivos originales, crea copias |
| ✅ **Validación** | Valida según el tipo (IP, texto, etc.) |
| 🔄 **Anti-duplicación** | Evita errores cuando un reemplazo podría afectar a otro |
| 💻 **Multiplataforma** | Funciona en Windows, Linux y Mac |
| 📦 **Sin dependencias externas** | Solo necesita Python 3.10 |
| 🌐 **Interfaz Web** | Incluye interfaz gráfica web opcional |
| 🔧 **Modular** | Diseñado para agregar más módulos de edición |

---

## 🐍 Requisitos

**Python 3.10** (obligatorio)

---

## 🚀 Instalación

### Windows

1. Descarga Python 3.10 desde: **https://www.python.org/downloads/release/python-31011/**
2. Ejecuta el instalador
3. **IMPORTANTE**: Marca la casilla **"Add Python to PATH"** ✅
4. Clic en "Install Now"
5. Descarga o clona este repositorio

### Linux

```bash
sudo apt install python3.10
```

### Mac

```bash
brew install python@3.10
```

---

## 📁 Estructura del proyecto

```
qgz-editor/
│
├── EJECUTAR_WINDOWS.bat      # Doble clic para ejecutar en Windows
├── EJECUTAR_LINUX_MAC.sh     # Script para Linux/Mac
├── qgz_editor.py             # Programa principal
├── web_server.py             # Interfaz web (opcional)
├── config.json               # ⭐ Configuración de módulos
├── requirements.txt          # Dependencias para interfaz web
│
├── data_in/                  # ⭐ PON AQUÍ tus archivos .qgz
│
└── data_out/                 # ⭐ AQUÍ aparecen los resultados
```

---

## 🚀 Cómo usar

### Opción 1: Interfaz Web (recomendado)

1. Instala Flask:
```bash
pip install flask
```

2. Ejecuta el servidor:
```bash
python3 web_server.py
```

3. Se abrirá automáticamente en tu navegador: http://localhost:8000

4. Desde la interfaz puedes:
   - Subir archivos .qgz
   - Ver archivos en data_in/
   - Configurar los módulos activos
   - Ejecutar el procesamiento
   - Ver el progreso en tiempo real

### Opción 2: Línea de comandos

#### Paso 1: Colocar tus archivos

Copia tus archivos `.qgz` a la carpeta **`data_in/`**

#### Paso 2: Configurar

Edita el archivo **`config.json`** (ver sección Configuración)

#### Paso 3: Ejecutar

**Windows:**
```
Doble clic en EJECUTAR_WINDOWS.bat
```

**Linux/Mac:**
```bash
chmod +x EJECUTAR_LINUX_MAC.sh   # Solo la primera vez
./EJECUTAR_LINUX_MAC.sh
```

#### Paso 4: Resultados

Los archivos modificados estarán en **`data_out/`**

---

## ⚙️ Configuración

El archivo `config.json` usa un sistema modular:

```json
{
    "modulos": {
        "reemplazo_texto": {
            "activo": true,
            "descripcion": "Reemplazo masivo de texto/IP en archivos del proyecto",
            "reglas": [
                {
                    "tipo": "ip",
                    "buscar": "192.168.0.1",
                    "reemplazar_por": "192.168.0.2"
                },
                {
                    "tipo": "texto",
                    "buscar": "/ruta/vieja",
                    "reemplazar_por": "/ruta/nueva"
                }
            ]
        }
    },
    "postfijo": "_MODIFICADO",
    "carpeta_entrada": "data_in",
    "carpeta_salida": "data_out"
}
```

### Módulos disponibles

| Módulo | Descripción | Estado |
|--------|-------------|--------|
| `reemplazo_texto` | Buscar y reemplazar texto/IPs en el proyecto | ✅ Disponible |

### Tipos de validación para reglas

| Tipo | Descripción | Ejemplo válido |
|------|-------------|----------------|
| `ip` | Dirección IPv4 válida | `192.168.1.100` |
| `texto` | Cualquier texto (no vacío) | `mi_servidor` |

### Opciones generales

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `postfijo` | Texto agregado al nombre del archivo de salida | `"_MODIFICADO"` |
| `carpeta_entrada` | Carpeta con archivos originales | `"data_in"` |
| `carpeta_salida` | Carpeta para resultados | `"data_out"` |

---

## ❓ Preguntas frecuentes

### ¿Se modifican los archivos originales?

**NO.** Los archivos originales en `data_in/` nunca se tocan. Siempre se crean copias nuevas en `data_out/`.

### ¿Qué pasa si ejecuto el programa dos veces?

Los archivos en `data_out/` se sobrescriben. Si quieres conservar versiones anteriores, muévelos a otra carpeta antes de ejecutar nuevamente.

### No encuentra archivos .qgz

Verifica que:
- Los archivos tienen extensión `.qgz` (no `.qgs` ni `.zip`)
- Están directamente en `data_in/`, no en subcarpetas
- La carpeta `data_in/` existe

### El archivo .bat no hace nada / se cierra inmediatamente

1. Abre una ventana de comandos (cmd)
2. Navega hasta la carpeta del proyecto:
   ```
   cd C:\ruta\a\qgz-editor
   ```
3. Ejecuta:
   ```
   python qgz_editor.py
   ```
4. Así podrás ver los mensajes de error

---

## 🛡️ Características de seguridad

- **Validación por tipo**: Verifica que todos los valores sean válidos antes de procesar
- **Sistema anti-duplicación**: Usa marcadores temporales para evitar reemplazos en cadena
- **Manejo de errores**: Si un archivo falla, continúa con los demás

---

## 📜 Licencia

Este proyecto es de uso libre.

---

**¿Preguntas?** Abre un issue en el repositorio.
