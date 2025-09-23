[README.md](https://github.com/user-attachments/files/22408872/README.md)
# Homologador de Aplicaciones

Aplicación de escritorio en Python con PyQt6 para gestión de homologaciones de aplicaciones corporativas.

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
