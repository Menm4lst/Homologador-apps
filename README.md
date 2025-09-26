# 🏢 Homologador de Aplicaciones - MVP 1.0 ✅

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)](https://sqlite.org)

**Estado:** 🚀 LISTO PARA PRODUCCIÓN  
**Versión:** MVP 1.0  
**Completado:** 95%

> **Sistema integral de gestión y homologación de aplicaciones empresariales**

Aplicación de escritorio desarrollada en **PyQt6** para gestionar el proceso de homologación de aplicaciones en entornos empresariales. Sistema completo con autenticación, CRUD robusto, validación de formularios mejorada, manejo centralizado de errores, sistema de respaldos automáticos y documentación completa.

## 🚀 Instalación y Uso Rápido

### **Opción 1: Ejecutable Pre-compilado (Recomendado)**
1. Descargar el **Paquete Autocontenido** más reciente
2. Extraer la carpeta completa 
3. Ejecutar `Homologador.exe`
4. **Login inicial:** `admin` / `admin123`

### **Opción 2: Compilar desde Código Fuente**
Para compilar tu propia versión, consulta la **[📖 Guía de Compilación Completa](COMPILACION.md)**

```bash
# Instalación rápida desde GitHub
git clone https://github.com/Menm4lst/Homologador-apps.git
cd Homologador-apps
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m homologador
```

## Características

- **Interfaz gráfica** con PyQt6
- **Base de datos SQLite** con modo WAL y control de concurrencia
- **Roles de usuario**: admin, editor, viewer
- **Auditoría completa** de acciones
- **Backups automáticos**
- **Exportación a CSV**

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar la aplicación:
```bash
python app.py
```

## Configuración

La aplicación busca la configuración en el siguiente orden:
1. Argumento CLI `--db`
2. Variable de entorno `HOMOLOGADOR_DB`
3. Archivo `config.json`
4. Autodetección de OneDrive

## Usuario por defecto

- **Usuario**: admin
- **Contraseña**: admin123 (debe cambiarse en el primer login)

## Estructura del proyecto

```
homologador/
├── app.py                  # Punto de entrada
├── core/
│   ├── settings.py         # Configuración
│   └── storage.py          # Gestión de BD
├── data/
│   ├── schema.sql          # Esquema de BD
│   └── seed.py             # Datos iniciales
├── ui/
│   ├── login_window.py     # Ventana de login
│   ├── main_window.py      # Ventana principal
│   ├── homologation_form.py # Formulario
│   └── details_view.py     # Vista de detalles
├── config.json             # Configuración
└── requirements.txt        # Dependencias
```

## 🛠️ Compilación y Distribución

### **Para Desarrolladores: Compilar desde Código Fuente**

La aplicación puede compilarse en un ejecutable standalone para distribución:

#### **Requisitos para Compilación:**
- Python 3.11 o superior
- PyInstaller
- Todas las dependencias del `requirements.txt`

#### **Proceso de Compilación:**
```bash
# 1. Instalar PyInstaller
pip install pyinstaller

# 2. Compilar aplicación
pyinstaller --onefile --windowed --name "Homologador" homologador/__main__.py

# 3. El ejecutable estará en dist/Homologador.exe
```

#### **Compilación Avanzada (Paquete Autocontenido):**
```bash
# Crear paquete completo con base de datos incluida
mkdir Paquete_Homologador
copy "dist/Homologador.exe" "Paquete_Homologador/"
# La base de datos se crea automáticamente en la misma carpeta del .exe
```

**Para instrucciones detalladas de compilación, ver: [📖 COMPILACION.md](COMPILACION.md)**

## 📚 Documentación Completa

### **Para Usuarios:**
- 📋 **[Manual Completo](COMO_FUNCIONA_LA_APP.md)** - Guía detallada de uso
- 🗄️ **[Base de Datos](COMO_FUNCIONA_BASE_DATOS.md)** - Explicación del sistema de datos
- 📦 **[Instalación](DONDE_ESTA_LA_BASE_DATOS.md)** - Guía de instalación y configuración

### **Para Desarrolladores:**
- 🛠️ **[Compilación](COMPILACION.md)** - Guía completa de compilación desde código fuente
- 📊 **[Configuración Avanzada](configurador_avanzado.py)** - Herramienta de configuración del sistema
- 🔧 **[Arquitectura](README.md)** - Documentación técnica del proyecto

### **Archivos de Soporte:**
- `requirements.txt` - Lista completa de dependencias Python
- `config.json` - Archivo de configuración (se crea automáticamente)
- `.venv/` - Entorno virtual Python (para desarrollo)

## 🎯 Características Técnicas

### **Base de Datos:**
- **SQLite** con modo WAL para mejor concurrencia
- **Autocontenida** - Se crea automáticamente en la carpeta del ejecutable
- **Portable** - Funciona desde cualquier carpeta o dispositivo
- **Respaldos automáticos** cada 24 horas

### **Seguridad:**
- Contraseñas hasheadas con **Argon2**
- Sistema de **roles y permisos**
- **Auditoría completa** de operaciones
- **Validación de entrada** en todos los formularios

### **Rendimiento:**
- **Interfaz nativa** PyQt6 para máxima velocidad
- **Base de datos optimizada** con índices apropiados
- **Carga lazy** de datos para mejor responsividad
- **Gestión eficiente de memoria**

## 🔧 Configuración del Sistema

El programa es **autocontenido** y no requiere configuración manual. Sin embargo, puedes personalizar:

- **Ubicación de la base de datos** (automática en carpeta del ejecutable)
- **Directorio de respaldos** (por defecto: `backups/`)
- **Frecuencia de respaldos automáticos** (por defecto: 24 horas)
- **Retención de respaldos** (por defecto: 30 días)
- **Niveles de logging** (por defecto: INFO)

## 🚀 Distribución y Deployment

### **Métodos de Distribución:**

1. **📦 Paquete Autocontenido** (Recomendado)
   - Una sola carpeta con todo incluido
   - Base de datos se crea automáticamente
   - Ideal para compartir por OneDrive/USB

2. **🔧 Instalador MSI** (Futuro)
   - Instalación tradicional de Windows
   - Integración con menú de inicio
   - Desinstalación completa

3. **☁️ Versión Portable**
   - Ejecutable único sin instalación
   - Funciona desde cualquier carpeta
   - Perfecto para entornos corporativos

## 📞 Soporte y Contribución

### **Reportar Problemas:**
- Usar el sistema de **Issues** en GitHub
- Incluir pasos para reproducir el error
- Especificar versión del programa y sistema operativo

### **Contribuir al Proyecto:**
1. Fork del repositorio
2. Crear branch para la nueva funcionalidad
3. Implementar cambios con documentación
4. Pull Request con descripción detallada

### **Desarrollo Local:**
```bash
# Setup completo de desarrollo
git clone https://github.com/usuario/Homologador-apps.git
cd Homologador-apps
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m homologador --debug
```

**¡El proyecto está listo para producción y abierto a contribuciones!** 🚀
