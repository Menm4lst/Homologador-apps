# 🗄️ EXPLICACIÓN: Base de Datos del Homologador

## 📁 Estructura de Archivos

### Cuando instalas y ejecutas el programa:

```
📁 OneDrive/HomologadorApp/
  ├── 🗄️ homologador.db          ← Base de datos SQLite (datos reales)
  ├── 📁 backups/                ← Copias de seguridad automáticas
  │   ├── homologador_backup_2025-09-26_14-30-15.db
  │   ├── homologador_backup_2025-09-25_14-30-15.db
  │   └── ...más backups...
  └── 📄 logs/                   ← Archivos de registro

📁 Escritorio/
  ├── 🚀 Homologador.exe         ← Programa compilado (solo código)
  └── ⚙️ config.json            ← Configuración de dónde está la DB
```

## 🔄 Cómo Funciona

### 1. **Programa Ejecutable (Homologador.exe)**
- **Contenido**: Solo código de la aplicación
- **Tamaño**: 69 MB (incluye PyQt6, pandas, etc.)
- **NO contiene datos** - Solo la lógica del programa

### 2. **Base de Datos (homologador.db)**
- **Ubicación**: `OneDrive\HomologadorApp\homologador.db`
- **Contenido**: Todos tus datos (usuarios, aplicaciones, homologaciones)
- **Tamaño**: Variable según cantidad de datos (ej: 1-50 MB)
- **Formato**: SQLite - archivo estándar portable

### 3. **Configuración Automática**
El programa busca automáticamente la base de datos en:
1. Carpeta OneDrive configurada
2. Si no existe, la crea automáticamente
3. Si hay problemas, usa backups para recuperar

## ✅ VENTAJAS de Base de Datos Externa

### 🔄 **Sincronización OneDrive**
- ✅ La DB se sincroniza automáticamente entre equipos
- ✅ Ambos usuarios ven los mismos datos actualizados
- ✅ OneDrive maneja la sincronización en tiempo real

### 💾 **Backups Automáticos**
- ✅ Sistema crea backups cada 24 horas
- ✅ Retiene 30 días de backups automáticamente
- ✅ Recuperación automática si hay corrupción

### 🚀 **Portabilidad**
- ✅ Programa ejecutable funciona en cualquier PC
- ✅ Base de datos separada = fácil de respaldar
- ✅ Fácil migración entre equipos

### 🛡️ **Seguridad**
- ✅ Datos protegidos por OneDrive
- ✅ Encriptación automática en tránsito
- ✅ Historial de versiones de OneDrive

## ❌ Comparación: Base Embebida vs Externa

### 🚫 Si fuera EMBEBIDA (dentro del .exe):
- ❌ NO se sincronizaría entre equipos
- ❌ Cada instalación tendría datos separados
- ❌ Difícil hacer backups
- ❌ Programa gigante (100+ MB)

### ✅ Sistema ACTUAL (externa):
- ✅ Sincronización automática
- ✅ Datos compartidos entre equipos
- ✅ Backups independientes
- ✅ Programa eficiente

## 🔧 Ubicaciones Automáticas

### El programa busca la DB en orden:
1. `C:\Users\[Usuario]\OneDrive\HomologadorApp\homologador.db`
2. `C:\Users\[Usuario]\OneDrive - Personal\HomologadorApp\homologador.db`
3. `C:\Users\[Usuario]\OneDrive\Documentos\HomologadorApp\homologador.db`
4. Si no encuentra, crea nueva en la primera ubicación

## 📱 Acceso desde Móvil

### Como la DB está en OneDrive:
- 📱 **Lectura**: Puedes ver los datos desde móvil (OneDrive app)
- 💻 **Escritura**: Solo desde el programa de escritorio
- 🔄 **Sincronización**: Automática en todos los dispositivos

## 🆘 ¿Qué pasa si pierdo la base de datos?

### Sistema de Recuperación Automática:
1. **Backups locales**: 30 días de historial automático
2. **OneDrive versiones**: Historial de cambios
3. **Recuperación automática**: El programa detecta y restaura

### Comandos de emergencia:
```
# Ver backups disponibles
dir "C:\Users\[Usuario]\OneDrive\HomologadorApp\backups"

# El programa automáticamente usa el backup más reciente si detecta corrupción
```

## 💡 CONCLUSIÓN

- **NO está embebida** - La base de datos es un archivo separado
- **Sincronización perfecta** - OneDrive maneja todo automáticamente  
- **Datos seguros** - Sistema robusto de backups y recuperación
- **Portabilidad total** - Ejecutable funciona en cualquier PC
- **Acceso compartido** - Ambos usuarios ven los mismos datos actualizados