#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           QGZ EDITOR                                          ║
║                                                                               ║
║  Este script procesa archivos .qgz (proyectos QGIS comprimidos) y permite     ║
║  hacer reemplazos masivos según la configuración en config.json               ║
║                                                                               ║
║  Autor: Script generado automáticamente                                       ║
║  Uso: python qgz_editor.py                                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import zipfile
import shutil
import tempfile
import re
from datetime import datetime

# Forzar flush automático para streaming en web
sys.stdout.reconfigure(line_buffering=True)


def es_ip_valida(ip):
    """
    Valida que una cadena sea una dirección IP válida (IPv4).
    
    Args:
        ip: Cadena a validar
        
    Returns:
        bool: True si es una IP válida, False si no
    """
    # Patrón para IPv4: 4 grupos de 1-3 dígitos separados por puntos
    patron_ip = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    
    match = re.match(patron_ip, ip.strip())
    if not match:
        return False
    
    # Verificar que cada octeto esté entre 0 y 255
    for grupo in match.groups():
        if int(grupo) > 255:
            return False
    
    return True


# Tipos de validación soportados
TIPOS_VALIDACION = {
    'ip': {
        'nombre': 'Dirección IP',
        'validador': es_ip_valida,
        'ejemplo': '192.168.1.100',
        'descripcion': 'Dirección IPv4 (formato: XXX.XXX.XXX.XXX)'
    },
    'texto': {
        'nombre': 'Texto libre',
        'validador': lambda x: len(x.strip()) > 0,
        'ejemplo': 'cualquier texto',
        'descripcion': 'Cualquier texto (no puede estar vacío)'
    }
}


def validar_valor_por_tipo(valor, tipo, campo_nombre, numero_reemplazo):
    """
    Valida un valor según su tipo configurado.
    
    Args:
        valor: El valor a validar
        tipo: El tipo de validación ('ip', 'texto', etc.)
        campo_nombre: Nombre del campo para mensajes de error
        numero_reemplazo: Número del reemplazo para mensajes
        
    Returns:
        bool: True si es válido, False si no
    """
    if tipo not in TIPOS_VALIDACION:
        print(f"\n❌ ERROR: Tipo de validación desconocido: '{tipo}'")
        print(f"   Tipos válidos: {', '.join(TIPOS_VALIDACION.keys())}")
        return False
    
    info_tipo = TIPOS_VALIDACION[tipo]
    
    if not info_tipo['validador'](valor):
        print(f"\n❌ ERROR: El {campo_nombre} en el reemplazo #{numero_reemplazo} no es válido")
        print(f"   Tipo esperado: {info_tipo['nombre']}")
        print(f"   Valor ingresado: '{valor}'")
        print(f"   👉 {info_tipo['descripcion']} (ej: {info_tipo['ejemplo']})")
        return False
    
    return True


def mostrar_banner():
    """Muestra el banner inicial del programa."""
    print("")
    print("=" * 70)
    print("   🗺️  QGZ EDITOR - Editor de proyectos QGIS")
    print("=" * 70)
    print(f"   📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("")
    print("▶ INICIANDO PROCESO...")
    print("")


def cargar_configuracion(ruta_config):
    """
    Carga el archivo de configuración JSON.
    
    Args:
        ruta_config: Ruta al archivo config.json
        
    Returns:
        dict: Configuración cargada o None si hay error
    """
    print("[PASO 1/4] 📂 Leyendo archivo de configuración...")
    print("           Ubicación: config.json")
    
    try:
        if not os.path.exists(ruta_config):
            print(f"\n❌ ERROR: No se encontró el archivo de configuración: {ruta_config}")
            print("   👉 Asegúrate de que existe el archivo 'config.json' en la misma carpeta del script.")
            return None
            
        with open(ruta_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validar campos requeridos
        campos_requeridos = ['modulos', 'postfijo', 'carpeta_entrada', 'carpeta_salida']
        for campo in campos_requeridos:
            if campo not in config:
                print(f"\n❌ ERROR: Falta el campo '{campo}' en config.json")
                return None
        
        # Verificar que hay al menos un módulo activo
        modulos_activos = [nombre for nombre, mod in config['modulos'].items() if mod.get('activo', False)]
        if not modulos_activos:
            print("\n❌ ERROR: No hay módulos activos en config.json")
            print("   👉 Activa al menos un módulo poniendo 'activo': true")
            return None
        
        print(f"   ✅ Módulos activos: {', '.join(modulos_activos)}")
        
        # Validar módulo de reemplazo_texto si está activo
        if 'reemplazo_texto' in config['modulos'] and config['modulos']['reemplazo_texto'].get('activo', False):
            modulo_reemplazo = config['modulos']['reemplazo_texto']
            reglas = modulo_reemplazo.get('reglas', [])
            
            if not reglas:
                print("\n❌ ERROR: El módulo 'reemplazo_texto' no tiene reglas configuradas")
                print("   👉 Agrega al menos una regla con 'buscar' y 'reemplazar_por'")
                return None
            
            # Validar cada regla
            for i, regla in enumerate(reglas):
                if 'buscar' not in regla or 'reemplazar_por' not in regla:
                    print(f"\n❌ ERROR: La regla #{i+1} no tiene 'buscar' o 'reemplazar_por'")
                    return None
                
                # Obtener el tipo de validación (por defecto 'texto' si no se especifica)
                tipo = regla.get('tipo', 'texto')
                
                valor_buscar = regla['buscar']
                valor_reemplazar = regla['reemplazar_por']
                
                # Validar según el tipo
                if not validar_valor_por_tipo(valor_buscar, tipo, "valor a buscar", i+1):
                    return None
                
                if not validar_valor_por_tipo(valor_reemplazar, tipo, "valor de reemplazo", i+1):
                    return None
                
                if valor_buscar == valor_reemplazar:
                    print(f"\n⚠️ ADVERTENCIA: La regla #{i+1} tiene el mismo valor para buscar y reemplazar")
                    print(f"   Valor: '{valor_buscar}'")
        
        print("   ✅ Configuración cargada correctamente")
        print("   ✅ Todos los valores han sido validados")
        return config
        
    except json.JSONDecodeError as e:
        print(f"\n❌ ERROR: El archivo config.json tiene un formato JSON inválido")
        print(f"   Detalle: {str(e)}")
        print("   👉 Revisa que las comas, comillas y llaves estén bien colocadas")
        return None
    except Exception as e:
        print(f"\n❌ ERROR inesperado al cargar configuración: {str(e)}")
        return None


def verificar_carpetas(config, directorio_base):
    """
    Verifica que las carpetas de entrada y salida existan.
    
    Args:
        config: Diccionario de configuración
        directorio_base: Directorio donde está el script
        
    Returns:
        tuple: (carpeta_entrada, carpeta_salida) o (None, None) si hay error
    """
    print("")
    print("[PASO 2/4] 📁 Verificando carpetas de trabajo...")
    
    carpeta_entrada = os.path.join(directorio_base, config['carpeta_entrada'])
    carpeta_salida = os.path.join(directorio_base, config['carpeta_salida'])
    
    # Verificar carpeta de entrada
    if not os.path.exists(carpeta_entrada):
        print(f"\n❌ ERROR: No existe la carpeta de entrada: {carpeta_entrada}")
        print(f"   👉 Crea la carpeta '{config['carpeta_entrada']}' y coloca los archivos .qgz dentro")
        return None, None
    
    # Crear carpeta de salida si no existe
    if not os.path.exists(carpeta_salida):
        try:
            os.makedirs(carpeta_salida)
            print(f"   📁 Carpeta de salida creada: {carpeta_salida}")
        except Exception as e:
            print(f"\n❌ ERROR: No se pudo crear la carpeta de salida: {str(e)}")
            return None, None
    
    print(f"   ✅ Carpeta entrada: {carpeta_entrada}")
    print(f"   ✅ Carpeta salida: {carpeta_salida}")
    
    return carpeta_entrada, carpeta_salida


def obtener_archivos_qgz(carpeta_entrada):
    """
    Obtiene la lista de archivos .qgz en la carpeta de entrada.
    
    Args:
        carpeta_entrada: Ruta a la carpeta con los archivos
        
    Returns:
        list: Lista de rutas a archivos .qgz
    """
    print("")
    print("[PASO 3/4] 🔍 Buscando archivos .qgz para procesar...")
    
    try:
        archivos = [f for f in os.listdir(carpeta_entrada) 
                   if f.lower().endswith('.qgz') and os.path.isfile(os.path.join(carpeta_entrada, f))]
        
        if not archivos:
            print(f"\n⚠️ No se encontraron archivos .qgz en: {carpeta_entrada}")
            print("   👉 Coloca los archivos .qgz que quieres procesar en esa carpeta")
            return []
        
        print(f"   ✅ Se encontraron {len(archivos)} archivo(s) .qgz:")
        for archivo in archivos:
            print(f"      • {archivo}")
        
        return archivos
        
    except Exception as e:
        print(f"\n❌ ERROR al buscar archivos: {str(e)}")
        return []


def aplicar_reemplazos_seguro(contenido, reemplazos):
    """
    Aplica los reemplazos de forma segura evitando duplicaciones.
    
    Esta función usa un enfoque de "marcadores temporales" para evitar
    que un reemplazo afecte a otro reemplazo posterior.
    
    Args:
        contenido: Texto donde hacer los reemplazos
        reemplazos: Lista de diccionarios con 'buscar' y 'reemplazar_por'
        
    Returns:
        tuple: (contenido_modificado, dict_con_conteos)
    """
    conteos = {}
    contenido_modificado = contenido
    
    # Primero, reemplazamos cada patrón por un marcador único temporal
    marcadores = {}
    for i, reemplazo in enumerate(reemplazos):
        buscar = reemplazo['buscar']
        reemplazar = reemplazo['reemplazar_por']
        
        # Crear un marcador único que no debería existir en el contenido
        marcador = f"<<<MARCADOR_TEMP_{i}_{hash(buscar)}>>>"
        marcadores[marcador] = reemplazar
        
        # Contar ocurrencias antes del reemplazo
        conteo = contenido_modificado.count(buscar)
        conteos[buscar] = conteo
        
        # Reemplazar por el marcador temporal
        if conteo > 0:
            contenido_modificado = contenido_modificado.replace(buscar, marcador)
    
    # Ahora reemplazamos todos los marcadores por sus valores finales
    for marcador, valor_final in marcadores.items():
        contenido_modificado = contenido_modificado.replace(marcador, valor_final)
    
    return contenido_modificado, conteos


def procesar_archivo_qgz(archivo_qgz, carpeta_entrada, carpeta_salida, config):
    """
    Procesa un archivo .qgz individual.
    
    Args:
        archivo_qgz: Nombre del archivo .qgz
        carpeta_entrada: Ruta a la carpeta de entrada
        carpeta_salida: Ruta a la carpeta de salida
        config: Diccionario de configuración
        
    Returns:
        bool: True si se procesó correctamente, False si hubo error
    """
    ruta_entrada = os.path.join(carpeta_entrada, archivo_qgz)
    
    # Crear nombre de archivo de salida con postfijo
    nombre_base = os.path.splitext(archivo_qgz)[0]
    nombre_salida = f"{nombre_base}{config['postfijo']}.qgz"
    ruta_salida = os.path.join(carpeta_salida, nombre_salida)
    
    # Verificar si el archivo de salida ya existe
    if os.path.exists(ruta_salida):
        print(f"   ⚠️ El archivo de salida ya existe, será sobrescrito: {nombre_salida}")
    
    # Crear directorio temporal para trabajar
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Paso 1: Descomprimir el archivo .qgz
        print(f"      → Descomprimiendo archivo .qgz...")
        try:
            with zipfile.ZipFile(ruta_entrada, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            print(f"      ✓ Archivo descomprimido correctamente")
        except zipfile.BadZipFile:
            print(f"      ✗ ERROR: El archivo no es un ZIP válido")
            return False
        except Exception as e:
            print(f"      ✗ ERROR al descomprimir: {str(e)}")
            return False
        
        # Paso 2: Buscar archivo .qgs dentro del contenido descomprimido
        print(f"      → Buscando archivos de proyecto (.qgs) dentro del .qgz...")
        archivos_qgs = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith('.qgs'):
                    archivos_qgs.append(os.path.join(root, file))
        
        if not archivos_qgs:
            print(f"      ✗ ERROR: No se encontró ningún archivo .qgs dentro del proyecto")
            return False
        
        print(f"      ✓ Se encontraron {len(archivos_qgs)} archivo(s) de proyecto")
        
        # Paso 3: Procesar cada archivo .qgs encontrado
        total_reemplazos = {}
        for ruta_qgs in archivos_qgs:
            nombre_qgs = os.path.basename(ruta_qgs)
            print(f"      → Leyendo contenido de: {nombre_qgs}")
            
            try:
                # Leer contenido del archivo .qgs
                with open(ruta_qgs, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                print(f"        ✓ Archivo leído ({len(contenido):,} caracteres)")
            except UnicodeDecodeError:
                # Intentar con otra codificación
                print(f"        → Reintentando con codificación alternativa...")
                try:
                    with open(ruta_qgs, 'r', encoding='latin-1') as f:
                        contenido = f.read()
                    print(f"        ✓ Archivo leído con codificación latin-1")
                except Exception as e:
                    print(f"        ✗ ERROR al leer: {str(e)}")
                    continue
            
            # Aplicar módulo de reemplazo_texto si está activo
            if 'reemplazo_texto' in config['modulos'] and config['modulos']['reemplazo_texto'].get('activo', False):
                reglas = config['modulos']['reemplazo_texto'].get('reglas', [])
                print(f"      → Aplicando {len(reglas)} regla(s) de reemplazo...")
                contenido_nuevo, conteos = aplicar_reemplazos_seguro(contenido, reglas)
                
                # Acumular conteos
                for clave, valor in conteos.items():
                    total_reemplazos[clave] = total_reemplazos.get(clave, 0) + valor
                    if valor > 0:
                        print(f"        ✓ '{clave}': {valor} coincidencia(s) encontrada(s)")
            else:
                contenido_nuevo = contenido
            
            # Guardar archivo modificado
            print(f"      → Guardando cambios en {nombre_qgs}...")
            try:
                with open(ruta_qgs, 'w', encoding='utf-8') as f:
                    f.write(contenido_nuevo)
                print(f"        ✓ Cambios guardados")
            except Exception as e:
                print(f"        ✗ ERROR al guardar: {str(e)}")
                return False
        
        # Mostrar resumen de reemplazos (solo si el módulo está activo)
        total_cambios = sum(total_reemplazos.values())
        if 'reemplazo_texto' in config['modulos'] and config['modulos']['reemplazo_texto'].get('activo', False):
            reglas = config['modulos']['reemplazo_texto'].get('reglas', [])
            print(f"")
            print(f"      ┌─ RESUMEN DE REEMPLAZOS ─┐")
            hay_reemplazos = False
            for regla in reglas:
                buscar = regla['buscar']
                conteo = total_reemplazos.get(buscar, 0)
                if conteo > 0:
                    hay_reemplazos = True
                    print(f"      │ '{buscar}' → '{regla['reemplazar_por']}': {conteo} veces")
            
            if not hay_reemplazos:
                print(f"      │ Sin coincidencias encontradas")
            else:
                print(f"      │ Total: {total_cambios} reemplazo(s)")
            print(f"      └──────────────────────────┘")
        
        # Paso 4: Crear nuevo archivo .qgz comprimido
        print(f"      → Comprimiendo proyecto modificado...")
        try:
            with zipfile.ZipFile(ruta_salida, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        ruta_completa = os.path.join(root, file)
                        ruta_relativa = os.path.relpath(ruta_completa, temp_dir)
                        zipf.write(ruta_completa, ruta_relativa)
            print(f"      ✓ Proyecto comprimido correctamente")
        except Exception as e:
            print(f"      ✗ ERROR al crear archivo de salida: {str(e)}")
            return False
        
        print(f"")
        print(f"   ✅ COMPLETADO → {nombre_salida}")
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR inesperado: {str(e)}")
        return False
        
    finally:
        # Limpiar directorio temporal
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def main():
    """Función principal del programa."""
    mostrar_banner()
    
    # Determinar directorio base (donde está el script)
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    ruta_config = os.path.join(directorio_base, 'config.json')
    
    print(f"📍 Directorio de trabajo: {directorio_base}\n")
    
    # Paso 1: Cargar configuración
    config = cargar_configuracion(ruta_config)
    if config is None:
        print("\n" + "=" * 70)
        print("❌ El programa no puede continuar debido a errores en la configuración.")
        print("=" * 70)
        if sys.stdin.isatty():
            input("\nPresiona ENTER para cerrar...")
        sys.exit(1)
    
    # Mostrar módulos activos y su configuración
    print("")
    print("   Módulos activos encontrados:")
    for nombre_modulo, modulo in config['modulos'].items():
        if modulo.get('activo', False):
            print(f"   ├── 📦 {nombre_modulo}")
            print(f"   │      {modulo.get('descripcion', '')}")
            if nombre_modulo == 'reemplazo_texto':
                reglas = modulo.get('reglas', [])
                print(f"   │      Reglas configuradas: {len(reglas)}")
                for i, regla in enumerate(reglas, 1):
                    print(f"   │        {i}. '{regla['buscar']}' → '{regla['reemplazar_por']}'")
    print(f"   └── Postfijo de salida: '{config['postfijo']}'")
    
    # Paso 2: Verificar carpetas
    carpeta_entrada, carpeta_salida = verificar_carpetas(config, directorio_base)
    if carpeta_entrada is None:
        print("\n" + "=" * 70)
        print("❌ El programa no puede continuar debido a errores en las carpetas.")
        print("=" * 70)
        if sys.stdin.isatty():
            input("\nPresiona ENTER para cerrar...")
        sys.exit(1)
    
    # Paso 3: Obtener lista de archivos .qgz
    archivos_qgz = obtener_archivos_qgz(carpeta_entrada)
    if not archivos_qgz:
        print("\n" + "=" * 70)
        print("⚠️ No hay archivos para procesar.")
        print("=" * 70)
        if sys.stdin.isatty():
            input("\nPresiona ENTER para cerrar...")
        sys.exit(0)
    
    # Paso 4: Procesar cada archivo
    print("")
    print("=" * 70)
    print("[PASO 4/4] 🔄 PROCESANDO ARCHIVOS")
    print("=" * 70)
    
    exitosos = 0
    fallidos = 0
    
    for i, archivo in enumerate(archivos_qgz, 1):
        print("")
        print(f"   ┌────────────────────────────────────────────────────────────────")
        print(f"   │ ARCHIVO {i} de {len(archivos_qgz)}: {archivo}")
        print(f"   └────────────────────────────────────────────────────────────────")
        
        try:
            if procesar_archivo_qgz(archivo, carpeta_entrada, carpeta_salida, config):
                exitosos += 1
            else:
                fallidos += 1
        except Exception as e:
            print(f"      ✗ ERROR no manejado: {str(e)}")
            fallidos += 1
    
    # Resumen final
    print("")
    print("=" * 70)
    print("▶ PROCESO FINALIZADO")
    print("=" * 70)
    print("")
    print("   ┌─────────────────────────────────────────────┐")
    print("   │            RESUMEN DE EJECUCIÓN            │")
    print("   ├─────────────────────────────────────────────┤")
    print(f"   │  ✅ Procesados correctamente: {exitosos:>13} │")
    print(f"   │  ❌ Con errores:              {fallidos:>13} │")
    print(f"   │  📁 Total archivos:           {len(archivos_qgz):>13} │")
    print("   └─────────────────────────────────────────────┘")
    print("")
    print(f"   📂 Los archivos modificados están en: {carpeta_salida}")
    print("")
    
    if fallidos > 0:
        print("   ⚠️ Algunos archivos tuvieron errores. Revisa los mensajes anteriores.")
    else:
        print("   ✅ Todos los archivos se procesaron correctamente.")
    
    print("")
    print("=" * 70)
    
    # Solo pedir ENTER si estamos en modo interactivo (no desde web)
    if sys.stdin.isatty():
        input("\nPresiona ENTER para cerrar...")


if __name__ == "__main__":
    main()
