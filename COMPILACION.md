# 🛠️ Guía de Compilación - Homologador de Aplicaciones

Esta guía te ayudará a compilar el **Homologador de Aplicaciones** desde el código fuente descargado de GitHub.

## 📋 Requisitos Previos

### **🐍 Python 3.11 o superior**
```bash
# Verificar versión de Python
python --version
# O
python3 --version
```

### **📦 Git (opcional)**
Para clonar el repositorio:
```bash
git --version
```

## 🚀 Proceso de Compilación

### **PASO 1: Descargar el Proyecto**

#### Opción A: Clonar con Git
```bash
git clone https://github.com/Menm4lst/Homologador-apps.git
cd Homologador-apps
```

#### Opción B: Descargar ZIP
1. Ve a: https://github.com/Menm4lst/Homologador-apps
2. Clic en **"Code"** → **"Download ZIP"**
3. Extraer el archivo ZIP
4. Abrir terminal en la carpeta extraída

### **PASO 2: Configurar Entorno Virtual**

#### En Windows (PowerShell):
```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
& ".\.venv\Scripts\Activate.ps1"

# Si hay error de permisos, ejecutar:
Set-ExecutionPolicy -ExecutionScope CurrentUser -ExecutionPolicy RemoteSigned
```

#### En Linux/Mac:
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate
```

### **PASO 3: Instalar Dependencias**

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt

# Instalar PyInstaller para compilación
pip install pyinstaller
```

### **PASO 4: Verificar Instalación**

```bash
# Probar que el programa funciona en modo desarrollo
python -m homologador
```

**Credenciales por defecto:**
- **Usuario:** `admin`
- **Contraseña:** `admin123`

### **PASO 5: Compilar Ejecutable**

#### Compilación Básica:
```bash
pyinstaller --onefile --windowed --name "Homologador" homologador/__main__.py
```

#### Compilación Optimizada (Recomendada):
```bash
pyinstaller --onefile --windowed --name "Homologador" --clean --optimize=2 homologador/__main__.py
```

#### Compilación con Icono (si tienes un archivo .ico):
```bash
pyinstaller --onefile --windowed --name "Homologador" --icon="assets/icon.ico" homologador/__main__.py
```

### **PASO 6: Localizar el Ejecutable**

El archivo compilado estará en:
```
📁 dist/
  └── 🚀 Homologador.exe (Windows)
  └── 🚀 Homologador (Linux/Mac)
```

## 📦 Crear Paquete de Distribución

### **Opción 1: Paquete Autocontenido (Recomendado)**

```bash
# 1. Crear carpeta del paquete
mkdir Homologador_Distribucion

# 2. Copiar ejecutable
copy "dist/Homologador.exe" "Homologador_Distribucion/"
# En Linux/Mac: cp "dist/Homologador" "Homologador_Distribucion/"

# 3. Crear instrucciones
echo "Ejecutar Homologador.exe para iniciar el programa" > Homologador_Distribucion/README.txt
```

### **Opción 2: Paquete con Base de Datos Incluida**

Si quieres incluir datos de prueba o configuración inicial:

```bash
# 1. Ejecutar el programa una vez para crear la BD
python -m homologador
# (Cerrar después de que se cree homologador.db)

# 2. Crear paquete completo
mkdir Homologador_Completo
copy "dist/Homologador.exe" "Homologador_Completo/"
copy "homologador.db" "Homologador_Completo/"
mkdir "Homologador_Completo/backups"
```

## ⚠️ Solución de Problemas

### **Error: "No module named 'PyQt6'"**
```bash
pip install PyQt6
```

### **Error: "No module named 'pandas'"**
```bash
pip install pandas openpyxl
```

### **Error: "Permission denied" (Windows)**
```powershell
# Ejecutar PowerShell como Administrador
Set-ExecutionPolicy -ExecutionScope CurrentUser -ExecutionPolicy RemoteSigned
```

### **Error: "ModuleNotFoundError" al compilar**
```bash
# Limpiar caché y recompilar
pyinstaller --clean --onefile --windowed --name "Homologador" homologador/__main__.py
```

### **El ejecutable es muy grande**
Es normal. El ejecutable incluye:
- Python runtime (~40MB)
- PyQt6 (~30MB) 
- Pandas y NumPy (~20MB)
- Bibliotecas adicionales (~10MB)

**Tamaño esperado: 65-70 MB**

## 🔧 Compilación Avanzada

### **Para Desarrolladores: Compilación con Debug**
```bash
pyinstaller --onefile --console --name "Homologador_Debug" homologador/__main__.py
```

### **Compilación Multiplataforma**

#### Para Windows (desde Linux con Wine):
```bash
pip install pyinstaller[encryption]
pyinstaller --onefile --windowed --target-architecture=x86_64 homologador/__main__.py
```

#### Parámetros adicionales útiles:
```bash
--add-data "config/;config/"     # Incluir archivos de configuración
--hidden-import=module_name      # Forzar inclusión de módulos
--exclude-module=module_name     # Excluir módulos innecesarios
--upx-dir=/path/to/upx           # Comprimir ejecutable (requiere UPX)
```

## 📁 Estructura del Proyecto

```
Homologador-apps/
├── 📁 homologador/              # Código fuente principal
│   ├── 📁 core/                 # Lógica de negocio
│   ├── 📁 ui/                   # Interfaz de usuario
│   ├── 📁 data/                 # Esquemas y datos iniciales
│   └── 📄 __main__.py           # Punto de entrada
├── 📁 .venv/                    # Entorno virtual (se crea)
├── 📁 dist/                     # Ejecutables compilados (se crea)
├── 📁 build/                    # Archivos temporales (se crea)
├── 📄 requirements.txt          # Dependencias Python
├── 📄 README.md                 # Documentación principal
├── 📄 COMPILACION.md            # Esta guía
└── 📄 *.spec                    # Archivos de configuración PyInstaller
```

## 🎯 Verificación Final

Después de compilar, verifica que:

1. ✅ **El ejecutable se abre** sin errores
2. ✅ **La interfaz se muestra** correctamente
3. ✅ **Puedes hacer login** con `admin`/`admin123`
4. ✅ **La base de datos se crea** automáticamente
5. ✅ **Las funciones básicas funcionan** (crear usuario, homologación, etc.)

## 📞 Soporte

Si encuentras problemas durante la compilación:

1. **Revisa los requisitos** - Asegúrate de tener Python 3.11+
2. **Verifica las dependencias** - `pip list` para ver qué está instalado
3. **Consulta los logs** - PyInstaller muestra errores detallados
4. **Prueba en modo desarrollo** - `python -m homologador` debe funcionar primero
5. **Abre un Issue** en GitHub con los detalles del error

## 🏷️ Versiones

- **Versión mínima Python:** 3.11
- **Versión recomendada Python:** 3.11 o 3.12
- **Sistemas soportados:** Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+

---

**¡Listo! Con esta guía podrás compilar el Homologador de Aplicaciones desde el código fuente.** 🚀