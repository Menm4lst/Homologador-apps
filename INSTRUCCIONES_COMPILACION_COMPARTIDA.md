# 📦 Guía de Compilación y Compartición del Homologador

## 🎯 Objetivo
Compilar el programa para compartir por pendrive y mantener la base de datos sincronizada vía OneDrive.

## 📋 Método Recomendado: OneDrive + Ejecutable Compilado

### 1. **Compilar el Programa**

```powershell
# Activar entorno virtual
& ".\.venv\Scripts\Activate.ps1"

# Instalar PyInstaller
pip install pyinstaller

# Compilar el programa
pyinstaller --onefile --windowed --name "Homologador" --icon="assets/icon.ico" homologador/__main__.py
```

### 2. **Configurar OneDrive para Compartir**

#### A. Crear Carpeta Compartida en OneDrive
1. Ve a tu OneDrive web (onedrive.com)
2. Crea una carpeta llamada `HomologadorApp`
3. Comparte la carpeta con la otra persona (permisos de edición)
4. Ambos deben sincronizar esta carpeta

#### B. Configurar el Programa para OneDrive
Crear archivo `config.json` junto al ejecutable:

```json
{
    "db_path": "C:\\Users\\{USERNAME}\\OneDrive\\HomologadorApp\\homologador.db",
    "backups_dir": "C:\\Users\\{USERNAME}\\OneDrive\\HomologadorApp\\backups\\",
    "auto_backup": true,
    "backup_retention_days": 30
}
```

### 3. **Paquete para Compartir**

Crear esta estructura en el pendrive:
```
📁 HomologadorApp/
  ├── 📄 Homologador.exe          (Tu programa compilado)
  ├── 📄 config.json              (Configuración OneDrive)
  ├── 📄 INSTALAR.bat             (Script de instalación)
  └── 📄 README.txt               (Instrucciones)
```

### 4. **Script de Instalación Automática**

Crear `INSTALAR.bat`:
```batch
@echo off
echo Configurando Homologador...

REM Crear directorio en OneDrive del usuario
set "ONEDRIVE_PATH=%USERPROFILE%\OneDrive\HomologadorApp"
if not exist "%ONEDRIVE_PATH%" mkdir "%ONEDRIVE_PATH%"

REM Copiar ejecutable y config
copy "Homologador.exe" "%USERPROFILE%\Desktop\"
copy "config.json" "%USERPROFILE%\Desktop\"

REM Crear acceso directo
echo Creando acceso directo...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Homologador.lnk'); $Shortcut.TargetPath = '%USERPROFILE%\Desktop\Homologador.exe'; $Shortcut.Save()"

echo.
echo ✅ Instalación completada!
echo ✅ Ejecutable en el escritorio
echo ✅ Configurado para OneDrive compartido
echo.
echo ⚠️  IMPORTANTE: Asegúrate de que la carpeta HomologadorApp
echo     esté compartida en OneDrive entre ambos usuarios
echo.
pause
```

## 🔄 Alternativas de Sincronización

### **Opción B: Base de Datos en Carpeta de Red**

Si tienen una red local compartida:

```json
{
    "db_path": "\\\\IP_SERVIDOR\\carpeta_compartida\\homologador.db",
    "backups_dir": "\\\\IP_SERVIDOR\\carpeta_compartida\\backups\\"
}
```

### **Opción C: Google Drive / Dropbox**

Similar a OneDrive pero cambiando las rutas:

```json
{
    "db_path": "C:\\Users\\{USERNAME}\\Google Drive\\HomologadorApp\\homologador.db",
    "backups_dir": "C:\\Users\\{USERNAME}\\Google Drive\\HomologadorApp\\backups\\"
}
```

## ⚠️ Consideraciones Importantes

### **Conflictos de Concurrencia**
- ❌ **NO usar ambos al mismo tiempo** (puede corromper la DB)
- ✅ **Coordinarse** para usar por turnos
- ✅ **El sistema de backups** protege contra corrupción

### **Sincronización**
- ⏱️ OneDrive sincroniza automáticamente cada pocos minutos
- 🔄 Los cambios se ven cuando OneDrive termine de sincronizar
- 📱 Usar la app móvil de OneDrive para verificar sincronización

### **Permisos**
- 📝 Ambos usuarios necesitan permisos de **edición** en la carpeta
- 🔒 El programa maneja automáticamente los permisos de archivos

## 🚀 Proceso de Instalación para el Otro Usuario

1. **Recibir el pendrive** con la carpeta `HomologadorApp`
2. **Ejecutar `INSTALAR.bat`** como administrador
3. **Configurar OneDrive** para sincronizar la carpeta compartida
4. **Coordinar uso** para evitar conflictos
5. **¡Listo!** - Los datos se mantienen sincronizados

## 🔧 Troubleshooting

### Si no se ve la base de datos actualizada:
1. Verificar que OneDrive esté sincronizado (icono verde)
2. Revisar permisos de la carpeta compartida
3. Reiniciar el programa para refrescar la conexión

### Si hay errores de base de datos:
1. El sistema de backups automático restaurará la última versión válida
2. Verificar que no estén ambos usuarios usando el programa simultáneamente

## ✅ Ventajas de este Método

- 🔄 **Sincronización automática** vía OneDrive
- 💾 **Backups automáticos** cada 24 horas
- 🛡️ **Protección contra corrupción** de datos
- 📱 **Acceso desde móvil** vía OneDrive (solo lectura)
- 🚀 **Fácil instalación** con script automático
- 💻 **Ejecutable standalone** - no necesita Python