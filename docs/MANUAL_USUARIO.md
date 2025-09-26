# Manual de Usuario - Homologador de Aplicaciones

## Índice
1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Inicio de Sesión](#inicio-de-sesión)
4. [Funcionalidades Principales](#funcionalidades-principales)
5. [Gestión de Homologaciones](#gestión-de-homologaciones)
6. [Exportación de Datos](#exportación-de-datos)
7. [Solución de Problemas](#solución-de-problemas)

## Introducción

El **Homologador de Aplicaciones** es una herramienta de escritorio desarrollada en PyQt6 para gestionar el proceso de homologación de aplicaciones en entornos empresariales.

### Características Principales
- ✅ Gestión completa de homologaciones
- ✅ Sistema de autenticación de usuarios
- ✅ Filtros avanzados y búsqueda
- ✅ Panel de métricas y estadísticas
- ✅ Exportación a múltiples formatos
- ✅ Sistema de notificaciones
- ✅ Temas claro y oscuro
- ✅ Validación robusta de formularios

## Instalación

### Requisitos Previos
- Python 3.8 o superior
- Windows 10/11 (recomendado)

### Pasos de Instalación

1. **Descargar la aplicación**
   ```
   Descomprimir el archivo en una carpeta de su elección
   ```

2. **Ejecutar la aplicación**
   ```
   Hacer doble clic en ejecutar_homologador.py
   ```

3. **Primera ejecución**
   - La aplicación creará automáticamente la base de datos
   - Se configurarán los usuarios por defecto

## Inicio de Sesión

### Usuarios por Defecto

La aplicación viene con usuarios preconfigurados:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | Administrador |
| `user1` | `user123` | Usuario estándar |

### Proceso de Login

1. Ejecutar `ejecutar_homologador.py`
2. Ingrese sus credenciales en la pantalla de login
3. Haga clic en "Iniciar Sesión"

**💡 Tip:** Use las credenciales de admin para acceso completo a todas las funcionalidades.

## Funcionalidades Principales

### 1. Dashboard Principal

Al iniciar sesión, verá el dashboard principal con:
- **Lista de homologaciones**: Tabla con todas las homologaciones registradas
- **Panel de filtros**: Filtros avanzados para búsqueda
- **Panel de métricas**: Estadísticas en tiempo real
- **Barra de herramientas**: Acciones principales

### 2. Gestión de Usuarios (Solo Admin)

Los administradores pueden:
- Ver lista de usuarios registrados
- Crear nuevos usuarios
- Modificar roles y permisos
- Desactivar usuarios

### 3. Filtros y Búsqueda

#### Filtros Disponibles:
- **Búsqueda de texto**: Busque por nombre real o lógico
- **Filtro por fecha**: Rango de fechas de homologación
- **Filtro por repositorio**: AESA, APPS$, o todos
- **Sincronización KB**: Con o sin sincronización

#### Cómo usar los filtros:
1. Ingrese el texto de búsqueda en la barra superior
2. Seleccione filtros adicionales en el panel lateral
3. Los resultados se actualizan automáticamente

### 4. Panel de Métricas

El panel de métricas muestra:
- **Total de homologaciones**
- **Homologaciones por repositorio**
- **Tendencias mensuales**
- **Estadísticas de KB Sync**

## Gestión de Homologaciones

### Crear Nueva Homologación

1. Haga clic en **"Nueva Homologación"**
2. Complete el formulario:
   - **Nombre Real**: *(Obligatorio)* Nombre real de la aplicación
   - **Nombre Lógico**: *(Opcional)* Nombre interno o código
   - **URL KB**: *(Opcional)* Enlace a documentación
   - **Fecha de Homologación**: Fecha del proceso
   - **Repositorio**: Seleccione AESA, APPS$ o ninguno
   - **Versiones Previas**: Marque si existen versiones anteriores
   - **Sincronización KB**: Marque si sincroniza con Knowledge Base
   - **Detalles**: *(Opcional)* Información adicional

3. Haga clic en **"Guardar"**

### Validaciones del Formulario

El sistema valida automáticamente:
- ✅ **Nombre Real**: Mínimo 2 caracteres, máximo 255
- ✅ **Nombre Lógico**: Máximo 255 caracteres
- ✅ **URL KB**: Formato válido de URL
- ✅ **Detalles**: Máximo 5000 caracteres
- ✅ **Nombres duplicados**: Advertencia si ya existe

### Editar Homologación

1. Seleccione una fila en la tabla
2. Haga clic derecho → **"Editar"**
3. Modifique los campos necesarios
4. Haga clic en **"Guardar"**

### Eliminar Homologación

1. Seleccione una fila en la tabla
2. Haga clic derecho → **"Eliminar"**
3. Confirme la eliminación

**⚠️ Advertencia:** La eliminación es permanente y no se puede deshacer.

## Exportación de Datos

### Formatos Disponibles
- **Excel (.xlsx)**: Ideal para análisis y reportes
- **CSV**: Compatible con cualquier hoja de cálculo
- **JSON**: Para integración con otros sistemas

### Cómo Exportar

1. **Método 1 - Menú Principal:**
   - Haga clic en **"Archivo"** → **"Exportar"**
   - Seleccione el formato deseado

2. **Método 2 - Botón de Exportar:**
   - Haga clic en el botón **"Exportar"** en la barra de herramientas
   - Elija el formato

3. **Seleccionar ubicación:**
   - Elija dónde guardar el archivo
   - Confirme la exportación

### Datos Incluidos en la Exportación

La exportación incluye:
- Todos los campos de homologación
- Metadatos (fecha de creación, usuario creador)
- Información de auditoría

## Solución de Problemas

### Problemas Comunes

#### 1. No puedo iniciar sesión
**Síntomas:** Error al introducir credenciales
**Solución:**
- Verifique que está usando las credenciales correctas
- Usuarios por defecto: admin/admin123 o user1/user123
- Asegúrese de que no hay espacios extra

#### 2. La aplicación no inicia
**Síntomas:** Error al ejecutar `ejecutar_homologador.py`
**Solución:**
- Verifique que Python esté instalado
- Asegúrese de que PyQt6 esté instalado: `pip install PyQt6`
- Ejecute desde línea de comandos para ver errores detallados

#### 3. Error al guardar homologación
**Síntomas:** Mensaje de error al guardar
**Solución:**
- Revise que el nombre real no esté vacío
- Verifique que la URL tenga formato correcto
- Compruebe los límites de caracteres

#### 4. Los filtros no funcionan
**Síntomas:** Los filtros no muestran resultados
**Solución:**
- Borre los filtros y aplíquelos de nuevo
- Verifique que hay datos que coincidan con los criterios
- Reinicie la aplicación si persiste

#### 5. Error de base de datos
**Síntomas:** Errores relacionados con SQLite
**Solución:**
- Cierre la aplicación completamente
- Verifique que no hay otros procesos usando la base de datos
- Como último recurso, elimine `homologaciones.db` para recrearla

### Archivos de Log

La aplicación guarda logs en la carpeta `logs/`:
- `homologaciones.log`: Registro de todas las actividades y errores

Si necesita ayuda técnica, proporcione este archivo.

### Contacto de Soporte

Para problemas técnicos o consultas:
- Revise este manual primero
- Consulte los logs de error
- Contacte al administrador del sistema

## Funcionalidades Avanzadas

### Temas

La aplicación soporta dos temas:
- **Tema Claro**: Interfaz tradicional con colores claros
- **Tema Oscuro**: Interfaz moderna con colores oscuros

**Cambiar tema:** Menú Ver → Cambiar Tema

### Atajos de Teclado

| Atajo | Acción |
|-------|---------|
| `Ctrl+N` | Nueva homologación |
| `Ctrl+E` | Exportar datos |
| `Ctrl+F` | Enfocar búsqueda |
| `F5` | Actualizar lista |
| `Delete` | Eliminar seleccionado |

### Autoguardado de Borradores

El formulario de homologaciones guarda automáticamente borradores cada 30 segundos, evitando pérdida de datos.

---

## Notas de la Versión MVP

**Versión:** MVP 1.0
**Fecha:** Enero 2025

### Funcionalidades Incluidas
✅ Sistema de autenticación
✅ CRUD completo de homologaciones  
✅ Filtros y búsqueda avanzada
✅ Panel de métricas
✅ Exportación múltiple formato
✅ Validación robusta de formularios
✅ Sistema de manejo de errores
✅ Temas claro/oscuro
✅ Logging y auditoría

### Próximas Funcionalidades
🔄 Sincronización en tiempo real
🔄 Reportes avanzados
🔄 Integración con APIs externas
🔄 Notificaciones push
🔄 Backup automático

---

*Esta documentación está actualizada para la versión MVP del Homologador de Aplicaciones.*