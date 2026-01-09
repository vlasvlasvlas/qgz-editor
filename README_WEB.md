# 🌐 Interfaz Web - QGZ Editor

## ¿Qué es esto?

Una **interfaz web simple** para usar QGZ Editor desde el navegador, sin tocar la terminal ni editar JSON.

## 🚀 Cómo usar

### En Windows
1. Doble clic en `EJECUTAR_WEB.bat`
2. Se abrirá tu navegador automáticamente
3. ¡Listo para usar!

### En Linux/Mac
1. Haz doble clic en `EJECUTAR_WEB.sh` (o desde terminal: `./EJECUTAR_WEB.sh`)
2. Se abrirá tu navegador automáticamente
3. ¡Listo para usar!

## 📋 Características

✅ **Interfaz Visual**: Edita configuración sin tocar JSON  
✅ **Drag & Drop**: Arrastra archivos .qgz directo al navegador  
✅ **Editor de Reglas**: Agrega/elimina reemplazos visualmente  
✅ **Validación en Vivo**: Ve si las IPs son válidas mientras escribes  
✅ **Un Click**: Botón grande para procesar todos los archivos  
✅ **Sin Configuración**: Abre el navegador automáticamente  

## 🏗️ Archivos agregados

```
qgz-editor/
├── web_server.py          # Servidor web (1 solo archivo)
├── EJECUTAR_WEB.bat       # Doble click en Windows
├── EJECUTAR_WEB.sh        # Doble click en Linux/Mac
└── ... (resto igual)
```

## ⚙️ Cómo funciona

1. **El servidor web** (`web_server.py`) levanta una interfaz en `http://localhost:5000`
2. **Uses el código actual** - No modifica `qgz_editor.py` para nada
3. **Guarda la configuración** en `config.json` (igual que antes)
4. **Ejecuta el procesamiento** llamando a `qgz_editor.py` cuando haces click en "PROCESAR"

## 🔄 Compatibilidad

- ✅ Funciona CON o SIN la interfaz web
- ✅ Puedes seguir usando la terminal como antes
- ✅ El `config.json` es el mismo
- ✅ No rompe nada existente

## 📦 Dependencia

Solo necesita `flask` (se instala automáticamente al ejecutar):
```bash
pip install flask
```

## ❓ Preguntas Frecuentes

### ¿Puedo seguir usando la terminal?
¡Sí! Los scripts `EJECUTAR_WINDOWS.bat` y `EJECUTAR_LINUX_MAC.sh` originales siguen funcionando igual.

### ¿Se modifica qgz_editor.py?
No, sigue exactamente igual. `web_server.py` solo lo llama cuando procesas archivos.

### ¿Cómo detengo el servidor?
Presiona `Ctrl+C` en la ventana de terminal que se abrió.

### ¿Puedo cambiar el puerto?
Sí, edita `web_server.py` y cambia `port=5000` por otro número.

## 🎨 Preview

La interfaz tiene:
- 📁 **Sección de archivos**: Ver qué archivos .qgz están en `data_in/`
- ⚙️ **Editor de reglas**: Agregar/quitar/editar reemplazos
- ▶️ **Botón grande**: Procesar todos los archivos
- ✅ **Mensajes claros**: Te dice si funcionó o si hubo errores
