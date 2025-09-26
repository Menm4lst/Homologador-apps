@echo off
title Instalador Homologador - Configuracion OneDrive
echo.
echo ========================================
echo    INSTALADOR HOMOLOGADOR v1.0
echo    Configuracion para OneDrive Compartido
echo ========================================
echo.

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  ADVERTENCIA: Se recomienda ejecutar como Administrador
    echo    Para mejor funcionamiento y permisos completos
    echo.
    timeout /t 3 >nul
)

echo 📁 Creando directorios necesarios...

REM Crear directorio en OneDrive del usuario
set "ONEDRIVE_PATH=%USERPROFILE%\OneDrive\HomologadorApp"
if not exist "%ONEDRIVE_PATH%" (
    mkdir "%ONEDRIVE_PATH%"
    echo ✅ Creado: %ONEDRIVE_PATH%
) else (
    echo ℹ️  Ya existe: %ONEDRIVE_PATH%
)

REM Crear directorio de backups
set "BACKUP_PATH=%ONEDRIVE_PATH%\backups"
if not exist "%BACKUP_PATH%" (
    mkdir "%BACKUP_PATH%"
    echo ✅ Creado: %BACKUP_PATH%
) else (
    echo ℹ️  Ya existe: %BACKUP_PATH%
)

echo.
echo 📋 Copiando archivos del programa...

REM Copiar ejecutable al escritorio
if exist "Homologador.exe" (
    copy "Homologador.exe" "%USERPROFILE%\Desktop\" >nul
    echo ✅ Homologador.exe copiado al escritorio
) else (
    echo ❌ ERROR: No se encuentra Homologador.exe
    pause
    exit /b 1
)

REM Copiar configuración
if exist "config_onedrive.json" (
    copy "config_onedrive.json" "%USERPROFILE%\Desktop\config.json" >nul
    echo ✅ Configuración copiada al escritorio
) else (
    echo ❌ ERROR: No se encuentra config_onedrive.json
    pause
    exit /b 1
)

echo.
echo 🔗 Creando acceso directo...

REM Crear acceso directo con PowerShell
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Homologador.lnk'); $Shortcut.TargetPath = '%USERPROFILE%\Desktop\Homologador.exe'; $Shortcut.WorkingDirectory = '%USERPROFILE%\Desktop'; $Shortcut.Description = 'Sistema Homologador de Aplicaciones'; $Shortcut.Save()}" 2>nul
if %errorLevel% equ 0 (
    echo ✅ Acceso directo creado en el escritorio
) else (
    echo ⚠️  No se pudo crear acceso directo automáticamente
)

echo.
echo ========================================
echo           ✅ INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo 📍 Archivos instalados:
echo    • %USERPROFILE%\Desktop\Homologador.exe
echo    • %USERPROFILE%\Desktop\Homologador.lnk
echo    • %USERPROFILE%\Desktop\config.json
echo.
echo 📁 Directorios OneDrive:
echo    • %ONEDRIVE_PATH%
echo    • %BACKUP_PATH%
echo.
echo ⚠️  IMPORTANTE - Configuración OneDrive:
echo    1. La carpeta 'HomologadorApp' debe estar COMPARTIDA
echo       en OneDrive entre ambos usuarios
echo    2. Asegurate de que OneDrive esté sincronizado
echo    3. NO usar el programa al mismo tiempo (puede corromper datos)
echo    4. El sistema hace backups automáticos cada 24 horas
echo.
echo 🚀 Para ejecutar:
echo    • Doble click en 'Homologador' del escritorio
echo    • Usuario: admin
echo    • Contraseña: admin123
echo.
echo ========================================

echo.
set /p "continuar=Presiona ENTER para continuar..."