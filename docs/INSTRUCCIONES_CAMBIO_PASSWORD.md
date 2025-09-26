# 🔑 INSTRUCCIONES PARA PROBAR EL CAMBIO DE CONTRASEÑAS

## ✅ PROBLEMA RESUELTO
El error que causaba que la aplicación se cerrara al intentar cambiar contraseñas ha sido **COMPLETAMENTE CORREGIDO**.

## 🚀 CÓMO PROBAR LA FUNCIONALIDAD

### Paso 1: Ejecutar la Aplicación
```bash
python run_forced.py
```

### Paso 2: Iniciar Sesión  
- **Usuario**: admin, estebanquito, o prueba1
- **Contraseña**: admin123 (para todos)

### Paso 3: Acceder al Cambio de Contraseñas
Tienes **3 formas** de acceder:

#### 🎯 Opción A - Menú Usuario
1. Ve al menú superior: `Usuario`
2. Clic en: `🔑 Cambiar Mi Contraseña`

#### 🎯 Opción B - Atajo de Teclado  
- Presiona: `Ctrl + Shift + P`

#### 🎯 Opción C - Barra de Herramientas
- Clic en el botón: `🔑 Mi Contraseña`

### Paso 4: Cambiar Contraseña
1. **Contraseña Actual**: `admin123`
2. **Nueva Contraseña**: Crea una nueva o usa el botón `🎲 Generar`
3. **Confirmar**: Repite la nueva contraseña
4. Clic en: `🔄 Cambiar Contraseña`

## 🛡️ CARACTERÍSTICAS DEL SISTEMA

### ✅ Validaciones de Seguridad
- ✓ Mínimo 8 caracteres
- ✓ Al menos una minúscula (a-z)  
- ✓ Al menos una mayúscula (A-Z)
- ✓ Al menos un número (0-9)
- ✓ Símbolos especiales recomendados

### 🎨 Indicador Visual de Fortaleza
- 🔴 **Muy débil** (0-1 puntos)
- 🟡 **Débil** (2 puntos)
- 🔵 **Regular** (3 puntos) 
- 🟢 **Buena** (4 puntos)
- ⭐ **Muy fuerte** (5 puntos)

### 🎲 Generador Automático
- Contraseñas de 12 caracteres
- Incluye todos los tipos requeridos
- Completamente aleatorio y seguro

## 🎯 EJEMPLOS DE CONTRASEÑAS

### ✅ Contraseñas Válidas:
- `MiNueva2024!` (Muy fuerte - 5/5)
- `Segura123@` (Muy fuerte - 5/5)  
- `Test#2024$` (Muy fuerte - 5/5)

### ❌ Contraseñas Débiles:
- `password` (Muy débil - sin mayúsculas, números, símbolos)
- `12345678` (Débil - solo números)
- `PASSWORD` (Débil - sin minúsculas, números, símbolos)

## 🔄 FLUJO COMPLETO DE PRUEBA

1. **Ejecutar**: `python run_forced.py`
2. **Login**: admin / admin123  
3. **Cambiar**: `Usuario → Cambiar Mi Contraseña`
4. **Actual**: admin123
5. **Nueva**: MiNueva2024! (o genera una automática)
6. **Confirmar**: MiNueva2024!
7. **Guardar**: Clic en `🔄 Cambiar Contraseña`
8. **¡Éxito!**: Mensaje de confirmación

## 🎉 RESULTADO ESPERADO

Al completar el cambio:
- ✅ Mensaje de éxito  
- ✅ Aplicación sigue funcionando
- ✅ Nueva contraseña activa
- ✅ Opción de cerrar sesión para usar nueva contraseña

---

**🔧 Error anterior RESUELTO**: El problema de regex que causaba crashes ha sido completamente corregido.