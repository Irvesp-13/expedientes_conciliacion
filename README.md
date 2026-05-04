# Sistema de Expedientes de Conciliación

## Requisitos Previos

- Python 3.11+
- MySQL 8.0+
- pip (gestor de paquetes de Python)

## Instalación sin Docker

### 1. Crear Base de Datos en MySQL

Abre MySQL y ejecuta:

```sql
CREATE DATABASE conciliacion CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Crear Entorno Virtual (opcional pero recomendado)

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

El archivo `.env` ya está configurado. Si necesitas cambiar valores:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=conciliacion
```

### 5. Realizar Migraciones

```bash
python manage.py migrate
```

### 6. Crear Superusuario (Administrador)

```bash
python manage.py createsuperuser
```

Sigue las instrucciones y proporciona usuario, email y contraseña.

### 7. Ejecutar el Servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: **http://localhost:8000**

## Acceder a la Aplicación

- **Sitio**: http://localhost:8000
- **Panel de Admin**: http://localhost:8000/admin

## Comandos Útiles

### Crear migraciones
```bash
python manage.py makemigrations
```

### Aplicar migraciones
```bash
python manage.py migrate
```

### Recopilar archivos estáticos
```bash
python manage.py collectstatic --noinput
```

### Abrir shell de Django
```bash
python manage.py shell
```

## Estructura del Proyecto

```
expedientes_conciliacion/
├── app/                          # Aplicación principal
│   ├── migrations/               # Migraciones de la BD
│   ├── static/                   # Archivos CSS, JS, fuentes
│   ├── templates/                # Plantillas HTML
│   ├── models.py                 # Modelos de datos
│   ├── views.py                  # Vistas
│   └── urls.py                   # Rutas
├── expedientes_conciliacion/     # Configuración del proyecto
│   ├── settings.py               # Configuración Django
│   ├── urls.py                   # Rutas principales
│   └── wsgi.py                   # Configuración WSGI
├── manage.py                      # Herramienta de gestión Django
├── requirements.txt               # Dependencias Python
└── .env                           # Variables de entorno
```

## Solución de Problemas

### "Cannot connect to database"
- Verifica que MySQL esté ejecutándose
- Comprueba las credenciales en `.env`
- Asegúrate de que la base de datos `conciliacion` existe

### "ModuleNotFoundError"
- Activa el entorno virtual
- Ejecuta `pip install -r requirements.txt` nuevamente

### Problemas con migraciones
```bash
# Revertir una migración
python manage.py migrate app 0001  # Volver a migración específica

# Ver estado de migraciones
python manage.py showmigrations
```

## Notas de Desarrollo

- El proyecto usa Django 5.1.7
- Base de datos: MySQL 8.0
- Autenticación: Django Auth
- Archivos estáticos: WhiteNoise

---
**Último actualizado**: Mayo 2026
